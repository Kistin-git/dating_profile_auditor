from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from torch import nn
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .config import LABELS, PATHS, PROTO_LABEL_TEXTS
from .heuristics import HeuristicResult, run_heuristics
from .language_detection import LanguageDetectionResult, detect_language
from .preprocessing import preprocess_text
from .rewriting import RewriteGenerator, RewriteResult
from .scoring import ScoreResult, compute_score
from .utils import cosine_similarity


@dataclass
class PredictionResult:
    probabilities: Dict[str, float]
    classifier_name: str


class TransformerClassifier:
    def __init__(self, model_dir: str = PATHS.model_dir) -> None:
        path = Path(model_dir)
        if not path.exists():
            raise FileNotFoundError(f"Model directory {model_dir} not found")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model.eval()

    def predict(self, text: str) -> PredictionResult:
        encoded = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding="max_length",
        )
        with torch.no_grad():
            logits = self.model(**encoded).logits
            probs = torch.sigmoid(logits).cpu().numpy()[0]
        return PredictionResult(probabilities=dict(zip(LABELS, probs.tolist())), classifier_name="transformer")


class PrototypeSimilarityClassifier:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.encoder = SentenceTransformer(model_name)
        self.label_vectors = {
            label: self.encoder.encode(texts, convert_to_numpy=True)
            for label, texts in PROTO_LABEL_TEXTS.items()
        }

    def predict(self, text: str) -> PredictionResult:
        embedding = self.encoder.encode(text, convert_to_numpy=True)
        probabilities: Dict[str, float] = {}
        for label, vectors in self.label_vectors.items():
            sims = [cosine_similarity(embedding, vec) for vec in vectors]
            prob = float(np.clip((max(sims) + 1) / 2, 0, 1))
            probabilities[label] = prob
        return PredictionResult(probabilities=probabilities, classifier_name="prototype-similarity")


class DatingProfileClassifier:
    def __init__(self) -> None:
        if Path(PATHS.model_dir).exists():
            try:
                self.impl = TransformerClassifier(PATHS.model_dir)
            except Exception:
                self.impl = PrototypeSimilarityClassifier()
        else:
            self.impl = PrototypeSimilarityClassifier()

    def predict(self, text: str) -> PredictionResult:
        return self.impl.predict(text)


@dataclass
class AuditOutput:
    text: str
    language_detection: LanguageDetectionResult
    heuristics: HeuristicResult
    predictions: PredictionResult
    score: ScoreResult
    rewrites: RewriteResult
    truncated: bool


class DatingProfileAuditor:
    def __init__(self) -> None:
        self.classifier = DatingProfileClassifier()

    def analyze(self, text: str, ui_language: str = "ru") -> AuditOutput:
        preprocessed = preprocess_text(text)
        lang_detection = detect_language(preprocessed.text)
        heuristics = run_heuristics(preprocessed.text, lang_detection.language or "ru")
        predictions = self.classifier.predict(preprocessed.text)
        score = compute_score(predictions.probabilities, heuristics)
        rewrite_generator = RewriteGenerator().with_language(ui_language)
        rewrites = rewrite_generator.generate(preprocessed.text, heuristics)

        return AuditOutput(
            text=preprocessed.text,
            language_detection=lang_detection,
            heuristics=heuristics,
            predictions=predictions,
            score=score,
            rewrites=rewrites,
            truncated=preprocessed.was_truncated,
        )
