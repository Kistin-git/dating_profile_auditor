from __future__ import annotations

import re
from dataclasses import dataclass

from .heuristics import HeuristicResult

HARSH_PATTERNS = [
    r"не пиши, если[^.?!]*",
    r"swipe left[^.?!]*",
    r"не трать моё время[^.?!]*",
]


TEMPLATES = {
    "ru": {
        "warmer": "Добавляю чуть больше тепла: {core} Хочу делиться маленькими открытиями и хорошим настроением.",
        "funny": "Чуть больше иронии: {core} Иногда для счастья достаточно странной шутки и вкусного ужина.",
        "confident": "Более уверенная подача: {core} Ценю людей, которые знают, чего хотят, и действуют честно.",
    },
    "en": {
        "warmer": "A warmer tone: {core} Looking to share cozy rituals and uplifting energy.",
        "funny": "Let’s add humor: {core} Turns out bad puns and pancakes solve half of life's issues.",
        "confident": "More confident: {core} I value people who know what they want and act kindly.",
    },
}


def _strip_patterns(text: str) -> str:
    cleaned = text
    for pattern in HARSH_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _ensure_period(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    return text if text.endswith((".", "!", "?")) else text + "."


@dataclass
class RewriteResult:
    warmer: str
    funny: str
    confident: str


class RewriteGenerator:
    def __init__(self, language: str = "ru") -> None:
        self.language = language if language in TEMPLATES else "ru"

    def with_language(self, language: str) -> "RewriteGenerator":
        self.language = language if language in TEMPLATES else "ru"
        return self

    def generate(self, text: str, heuristics: HeuristicResult | None = None) -> RewriteResult:
        core = _strip_patterns(text)
        if heuristics and heuristics.cliche_hits:
            replacements = " ".join(
                f"Переформулировал клише «{c}»" if self.language == "ru" else f"Rephrased cliché \"{c}\""
                for c in heuristics.cliche_hits[:2]
            )
            core = f"{core} {replacements}".strip()
        core = _ensure_period(core)
        lang_templates = TEMPLATES[self.language]
        return RewriteResult(
            warmer=lang_templates["warmer"].format(core=core),
            funny=lang_templates["funny"].format(core=core),
            confident=lang_templates["confident"].format(core=core),
        )
