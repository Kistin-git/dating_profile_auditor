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


RANDOM_TEMPLATES = {
    "ru": {
        "warmer": {
            "prefixes": [
                "Люблю слушать истории и делиться уютными привычками.",
                "Собираю маленькие радости каждый день.",
                "Теплота и поддержка для меня важнее показушных жестов.",
            ],
            "suffixes": [
                "Буду рада знакомству без спешки.",
                "Пусть в переписке будет больше заботы и внимания.",
                "Хочу делиться хорошим настроением и маленькими открытиями.",
            ],
        },
        "funny": {
            "prefixes": [
                "Всегда найду шутку, чтобы разбавить будни.",
                "Люблю самоиронию и ситкомы.",
                "Коллекционирую неловкие моменты и превращаю их в смех.",
            ],
            "suffixes": [
                "Если умеешь смеяться над собой — точно поладим.",
                "Давай обмениваться мемами и странными историями.",
                "Мне важно, чтобы переписка была живой и лёгкой.",
            ],
        },
        "confident": {
            "prefixes": [
                "Говорю честно и без кружев.",
                "Ценю конкретику и взаимное уважение.",
                "Умею держать фокус на главном.",
            ],
            "suffixes": [
                "Давай сразу обсуждать цели без игр.",
                "Уважаю инициативность и честность в диалоге.",
                "Хочу видеть взаимный интерес и готовность действовать.",
            ],
        },
    },
    "en": {
        "warmer": {
            "prefixes": [
                "I care about small rituals and thoughtful gestures.",
                "Warm energy and empathy first, hype later.",
                "Slow conversations over coffee are my thing.",
            ],
            "suffixes": [
                "Let’s keep things kind and unhurried.",
                "Looking for someone who enjoys cozy evenings too.",
                "Would love to share playlists, laughs, and calm mornings.",
            ],
        },
        "funny": {
            "prefixes": [
                "I quote sitcoms in random moments.",
                "Sarcasm and memes are my defense mechanism.",
                "I firmly believe awkward stories make the best jokes.",
            ],
            "suffixes": [
                "Laugh at weird situations with me.",
                "Let’s trade memes and chaotic giggles.",
                "Humor is the best icebreaker, agree?",
            ],
        },
        "confident": {
            "prefixes": [
                "I speak my mind and mean it.",
                "Clarity, respect, and momentum are must-haves.",
                "I know my goals and appreciate the same energy.",
            ],
            "suffixes": [
                "Let’s skip games and keep it real.",
                "If you value ambition with empathy, say hi.",
                "Honesty and initiative will always win me over.",
            ],
        },
    },
}


CRITICAL_PATTERNS = {
    "ru": ["обосрал", "обосралась", "ненавижу себя", "я плохой", "я ужасный"],
    "en": ["i messed up", "i'm trash", "hate myself"],
}


RESET_CORES = {
    "ru": [
        "Ценю спокойное общение, увлекаюсь чтением и велопрогулками.",
        "Люблю прогулки по городу, честные разговоры и людей с самоиронией.",
    ],
    "en": [
        "I enjoy honest chats, morning coffee walks, and people with humor.",
        "Kind conversations, slow playlists, and spontaneous trips are my thing.",
    ],
}


PROFANITY_PATTERNS = {
    "ru": [
        r"\bмудил\w*",
        r"\bмудак\w*",
        r"\bмудач\w*",
        r"\bебан\w*",
        r"\bсука\w*",
        r"\bгандон\w*",
        r"\bговн\w*",
        r"\bдолба\w*",
        r"\bидиот\w*",
        r"\bподлец\w*",
        r"\bхер\w*",
        r"\bчерт\b",
    ],
    "en": [
        r"\bidiot\b",
        r"\bjerk\b",
        r"\basshole\b",
        r"\btrash\b",
        r"\bfool\b",
    ],
}

SENSITIVE_PATTERNS = {
    "ru": [
        r"\bпорно\b",
        r"\bporno\b",
        r"\bсекс\b",
        r"\bsex\b",
        r"\bочко\b",
        r"\bжопа\b",
    ],
    "en": [
        r"\bporn\b",
        r"\bporno\b",
        r"\bsex\b",
        r"\bbutt\b",
    ],
}


def _strip_patterns(text: str, language: str) -> str:
    cleaned = text
    for pattern in HARSH_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _ensure_period(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    return text if text.endswith((".", "!", "?")) else text + "."


def _sanitize_text(text: str, language: str) -> str:
    filtered_sentences = []
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    profane_patterns = PROFANITY_PATTERNS.get(language, []) + SENSITIVE_PATTERNS.get(language, [])
    for sentence in sentences:
        lowered = sentence.lower()
        if any(re.search(pattern, lowered) for pattern in profane_patterns):
            continue
        normalized = " ".join(sentence.split())
        if normalized and normalized not in filtered_sentences:
            filtered_sentences.append(normalized)
    cleaned = " ".join(filtered_sentences)
    return cleaned.strip()


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

    def _needs_reset(self, text: str, heuristics: HeuristicResult | None) -> bool:
        patterns = CRITICAL_PATTERNS.get(self.language, [])
        lowered = text.lower()
        if any(pattern in lowered for pattern in patterns):
            return True
        if heuristics and any(diag.key == "diag_too_negative" for diag in heuristics.diagnostics):
            return True
        return False

    def _compose(self, variant: str, core: str) -> str:
        template = RANDOM_TEMPLATES[self.language][variant]
        prefix = random.choice(template["prefixes"])
        suffix = random.choice(template["suffixes"])
        return " ".join(part for part in [prefix, core, suffix] if part).strip()

    def generate(self, text: str, heuristics: HeuristicResult | None = None) -> RewriteResult:
        core = _strip_patterns(text, self.language)
        if self._needs_reset(core, heuristics):
            core = random.choice(RESET_CORES[self.language])
        elif heuristics and heuristics.cliche_hits:
            replacements = " ".join(
                f"Переформулировал клише «{c}»" if self.language == "ru" else f"Rephrased cliché \"{c}\""
                for c in heuristics.cliche_hits[:2]
            )
            core = f"{core} {replacements}".strip()
        core = _ensure_period(core)
        core = _sanitize_text(core, self.language)
        if not core:
            core = random.choice(RESET_CORES[self.language])
        return RewriteResult(
            warmer=self._compose("warmer", core),
            funny=self._compose("funny", core),
            confident=self._compose("confident", core),
        )
