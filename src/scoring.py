from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .config import LABEL_LOCALIZATION_KEYS, SCORING
from .heuristics import HeuristicResult
from .localization import get_text


@dataclass
class ScoreResult:
    score: int
    explanation: Dict[str, str]
    contributions: Dict[str, float]


def _format_label_list(labels: List[str], lang: str) -> str:
    if not labels:
        return ""
    localized = [get_text(lang, LABEL_LOCALIZATION_KEYS[label]) for label in labels]
    return ", ".join(localized)


def build_explanation(lang: str, positives: List[str], negatives: List[str], diag_keys: List[str]) -> str:
    parts: List[str] = []
    if positives:
        parts.append(
            get_text(lang, "analysis_ready")
            + " "
            + get_text(lang, "tone_section")
            + ": "
            + _format_label_list(positives, lang)
        )
    if negatives:
        parts.append("Однако наблюдаются: " + _format_label_list(negatives, lang) if lang == "ru" else "However detected: " + _format_label_list(negatives, lang))
    if diag_keys:
        diag_texts = [get_text(lang, key) for key in diag_keys[:2]]
        if lang == "ru":
            parts.append("Внимание: " + ", ".join(diag_texts))
        else:
            parts.append("Attention: " + ", ".join(diag_texts))
    if not parts:
        return get_text(lang, "analysis_ready")
    return " ".join(parts)


def compute_score(probabilities: Dict[str, float], heuristics: HeuristicResult) -> ScoreResult:
    base = 50.0
    contributions: Dict[str, float] = {}

    for label, weight in SCORING.positive.items():
        value = probabilities.get(label, 0.0) * weight
        base += value
        contributions[label] = value
    for label, weight in SCORING.negative.items():
        value = probabilities.get(label, 0.0) * weight
        base -= value
        contributions[label] = contributions.get(label, 0.0) - value
    for diag in heuristics.diagnostics:
        penalty = SCORING.heuristic_penalties.get(diag.key, 0.0)
        base -= penalty
        contributions[diag.key] = -penalty

    score = max(0, min(100, int(round(base))))
    positives = sorted(
        [label for label in SCORING.positive if probabilities.get(label, 0.0) > 0.45],
        key=lambda lbl: probabilities.get(lbl, 0.0),
        reverse=True,
    )
    negatives = sorted(
        [label for label in SCORING.negative if probabilities.get(label, 0.0) > 0.35],
        key=lambda lbl: probabilities.get(lbl, 0.0),
        reverse=True,
    )
    diag_keys = [diag.key for diag in heuristics.diagnostics]

    explanation = {
        "ru": build_explanation("ru", positives, negatives, diag_keys),
        "en": build_explanation("en", positives, negatives, diag_keys),
    }
    return ScoreResult(score=score, explanation=explanation, contributions=contributions)
