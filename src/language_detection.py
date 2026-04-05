from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 13

SupportedLang = Literal["ru", "en", "other"]


@dataclass
class LanguageDetectionResult:
    language: SupportedLang
    probability: float


def detect_language(text: str) -> LanguageDetectionResult:
    normalized = (text or "").strip()
    if not normalized:
        return LanguageDetectionResult(language="ru", probability=1.0)
    try:
        candidates = detect_langs(normalized)
    except LangDetectException:
        return LanguageDetectionResult(language="other", probability=0.0)
    best = max(candidates, key=lambda lang: lang.prob)
    lang = "ru" if best.lang in {"ru", "uk", "bg"} else "en" if best.lang in {"en"} else "other"
    return LanguageDetectionResult(language=lang, probability=best.prob)
