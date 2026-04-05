from __future__ import annotations

import re

import random
from dataclasses import dataclass

from .heuristics import HeuristicResult

HARSH_PATTERNS = [
    r"не пиши, если[^.?!]*",
    r"swipe left[^.?!]*",
    r"не трать моё время[^.?!]*",
]


WRAP_SEGMENTS = {
    "ru": [
        "Добавляю чуть больше тепла:",
        "Чуть больше иронии:",
        "Более уверенная подача:",
        "Хочу делиться маленькими открытиями и хорошим настроением.",
        "Иногда для счастья достаточно странной шутки и вкусного ужина.",
        "Ценю людей, которые знают, чего хотят, и действуют честно.",
    ],
    "en": [
        "A warmer tone:",
        "Let’s add humor:",
        "More confident:",
        "Looking to share cozy rituals and uplifting energy.",
        "Turns out bad puns and pancakes solve half of life's issues.",
        "I value people who know what they want and act kindly.",
    ],
}


RANDOM_TEMPLATES = {
    "ru": {
        "warmer": [
            "Теплее звучит так: {core} Люблю слушать истории и делиться уютными привычками.",
            "Добавляю солнечный штрих: {core} Хочу строить связь без спешки и с заботой.",
            "Более душевно: {core} Пусть в переписке будет больше тепла и поддержки.",
        ],
        "funny": [
            "Немного самоиронии: {core} Смеюсь над странными ситуациями и коллекционирую мемы.",
            "Добавим лёгкий абсурд: {core} Верю, что худшие каламбуры делают вечер лучше.",
            "Больше улыбок: {core} Всегда найду шутку, чтобы разбавить будни.",
        ],
        "confident": [
            "Более уверенная подача: {core} Отношусь к жизни осознанно и честно проговариваю желания.",
            "Чёткая версия: {core} Ценю действия, уважение и инициативу.",
            "Собранный вариант: {core} Мне важно видеть взаимный фокус и открытость.",
        ],
    },
    "en": {
        "warmer": [
            "A softer vibe: {core} I care about small rituals and gentle conversations.",
            "Cozy rewrite: {core} I'd love to share warmth, playlists, and calm evenings.",
            "More heartfelt: {core} Let's build something kind without rushing.",
        ],
        "funny": [
            "Humor boost: {core} I quote sitcoms at random and believe in chaotic giggles.",
            "Goofier take: {core} Bad puns plus pancakes equal my love language.",
            "Witty remix: {core} I like turning awkward moments into shared jokes.",
        ],
        "confident": [
            "Sharper tone: {core} I know what I’m building and respect the same energy.",
            "Focused edition: {core} Honesty, ambition, and empathy go first for me.",
            "Bold rewrite: {core} Let’s skip games and talk goals openly.",
        ],
    },
}


def _strip_patterns(text: str, language: str) -> str:
    cleaned = text
    for pattern in HARSH_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    for segment in WRAP_SEGMENTS.get(language, []):
        cleaned = re.sub(re.escape(segment), "", cleaned).strip()
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
        self.language = language if language in RANDOM_TEMPLATES else "ru"

    def with_language(self, language: str) -> "RewriteGenerator":
        self.language = language if language in RANDOM_TEMPLATES else "ru"
        return self

    def generate(self, text: str, heuristics: HeuristicResult | None = None) -> RewriteResult:
        core = _strip_patterns(text, self.language)
        if heuristics and heuristics.cliche_hits:
            replacements = " ".join(
                f"Переформулировал клише «{c}»" if self.language == "ru" else f"Rephrased cliché \"{c}\""
                for c in heuristics.cliche_hits[:2]
            )
            core = f"{core} {replacements}".strip()
        core = _ensure_period(core)
        lang_templates = RANDOM_TEMPLATES[self.language]
        return RewriteResult(
            warmer=random.choice(lang_templates["warmer"]).format(core=core),
            funny=random.choice(lang_templates["funny"]).format(core=core),
            confident=random.choice(lang_templates["confident"]).format(core=core),
        )
