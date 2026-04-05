from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

from .config import (
    ENGLISH_CLICHES,
    HEURISTICS,
    RUSSIAN_CLICHES,
)
from .preprocessing import count_emojis, count_excessive_punctuation


@dataclass
class Diagnostic:
    key: str
    metadata: Dict[str, float] | None = None


@dataclass
class HeuristicResult:
    diagnostics: List[Diagnostic]
    cliche_hits: List[str]
    stats: Dict[str, float]


NEGATIVE_WORDS_RE = re.compile("|".join(re.escape(w) for w in HEURISTICS.negative_words), re.IGNORECASE)
DEMANDING_RE = re.compile("|".join(re.escape(w) for w in HEURISTICS.demanding_patterns), re.IGNORECASE)

PRONOUNS = {
    "я",
    "мы",
    "меня",
    "мне",
    "мой",
    "моя",
    "мои",
    "нас",
    "нам",
    "наш",
    "наша",
    "ты",
    "тебя",
    "тебе",
    "вы",
    "вам",
    "me",
    "my",
    "i",
    "we",
    "us",
    "our",
    "myself",
}


def tokenize(text: str) -> List[str]:
    return [token for token in re.split(r"[^A-Za-zА-Яа-яЁё0-9]+", text) if token]


def detect_cliches(text: str, lang: str) -> List[str]:
    cliches = RUSSIAN_CLICHES if lang == "ru" else ENGLISH_CLICHES
    hits = []
    lower_text = text.lower()
    for phrase in cliches:
        if phrase in lower_text:
            hits.append(phrase)
    return hits


def run_heuristics(text: str, lang: str = "ru") -> HeuristicResult:
    diagnostics: List[Diagnostic] = []
    cliche_hits = detect_cliches(text, lang)
    tokens = tokenize(text)
    unique_tokens = set(tokens)
    emoji_count = count_emojis(text)
    punctuation_score = count_excessive_punctuation(text) + max(text.count("!") - 3, 0)
    pronoun_hits = sum(1 for token in tokens if token.lower() in PRONOUNS)

    if len(text) < HEURISTICS.short_threshold:
        diagnostics.append(Diagnostic("diag_too_short"))
    if len(text) > HEURISTICS.long_threshold:
        diagnostics.append(Diagnostic("diag_too_long"))
    if cliche_hits:
        diagnostics.append(Diagnostic("diag_too_generic", {"cliche_count": len(cliche_hits)}))
    if len(cliche_hits) >= 2:
        diagnostics.append(Diagnostic("diag_overloaded_with_cliches", {"cliche_count": len(cliche_hits)}))
    if NEGATIVE_WORDS_RE.search(text):
        diagnostics.append(Diagnostic("diag_too_negative"))
    if DEMANDING_RE.search(text):
        diagnostics.append(Diagnostic("diag_too_demanding"))
    if emoji_count >= HEURISTICS.emoji_threshold:
        diagnostics.append(Diagnostic("diag_too_many_emojis", {"emoji_count": emoji_count}))
    if punctuation_score >= HEURISTICS.punctuation_threshold:
        diagnostics.append(Diagnostic("diag_excessive_punctuation"))
    if len(unique_tokens) < 10 or len(tokens) / (len(unique_tokens) + 1) > 2.5:
        diagnostics.append(Diagnostic("diag_not_enough_personality"))
    if len(tokens) > 160 and pronoun_hits < 3:
        diagnostics.append(Diagnostic("diag_not_a_bio"))

    stats = {
        "token_count": len(tokens),
        "unique_tokens": len(unique_tokens),
        "emoji_count": emoji_count,
        "cliche_count": len(cliche_hits),
        "pronoun_hits": pronoun_hits,
    }
    return HeuristicResult(diagnostics=diagnostics, cliche_hits=cliche_hits, stats=stats)
