from __future__ import annotations

import re
from dataclasses import dataclass

MAX_CHARS = 600
EMOJI_PATTERN = re.compile(
    "[\U0001F1E0-\U0001F1FF\U0001F300-\U0001F6FF\U0001F700-\U0001F77F]+",
    flags=re.UNICODE,
)


@dataclass
class PreprocessResult:
    text: str
    was_truncated: bool
    original_length: int


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def preprocess_text(text: str) -> PreprocessResult:
    text = clean_text(text or "")
    was_truncated = len(text) > MAX_CHARS
    if was_truncated:
        text = text[:MAX_CHARS]
    return PreprocessResult(text=text, was_truncated=was_truncated, original_length=len(text))


def count_emojis(text: str) -> int:
    return len(EMOJI_PATTERN.findall(text))


def count_excessive_punctuation(text: str) -> int:
    patterns = ["!!!", "\\.\\.\\.", "???"]
    return sum(text.count(p) for p in patterns)
