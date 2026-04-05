from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List


LABELS: List[str] = [
    "friendly",
    "confident",
    "arrogant",
    "sincere",
    "humorous",
    "cliche",
    "aggressive",
    "awkward_or_cringe",
]

# Mapping for localization keys
LABEL_LOCALIZATION_KEYS: Dict[str, str] = {
    "friendly": "label_friendly",
    "confident": "label_confident",
    "arrogant": "label_arrogant",
    "sincere": "label_sincere",
    "humorous": "label_humorous",
    "cliche": "label_cliche",
    "aggressive": "label_aggressive",
    "awkward_or_cringe": "label_awkward",
}


RUSSIAN_CLICHES: List[str] = [
    "люблю путешествовать",
    "вкусно поесть",
    "в активном поиске",
    "ищу без драмы",
    "не пиши, если",
    "умею в сарказм",
    "рост 180",
    "остальное при встрече",
    "обычный парень",
    "обычная девушка",
    "всё сложно",
    "здесь по приколу",
    "удиви меня",
    "люблю кино, музыку и прогулки",
]

ENGLISH_CLICHES: List[str] = [
    "love to travel",
    "foodie",
    "no drama",
    "don't message if",
    "sarcasm is my love language",
    "six feet tall",
    "everything in person",
    "here for fun",
    "netflix and chill",
    "prove me wrong",
]


PROTO_LABEL_TEXTS: Dict[str, List[str]] = {
    "friendly": [
        "Привет! Обожаю делиться хорошим настроением и поддерживать друзей.",
        "Always open to new people and warm conversations.",
    ],
    "confident": [
        "Чётко знаю, чего хочу от жизни и уверенно к этому иду.",
        "Focused professional who values bold plans.",
    ],
    "arrogant": [
        "Я лучше других и не терплю слабость.",
        "If you cannot keep up, don't waste my time.",
    ],
    "sincere": [
        "Говорю прямо, что чувствую, и ценю честность.",
        "I prefer honest communication and openness.",
    ],
    "humorous": [
        "Собираю коллекцию неловких шуток и люблю смеяться над собой.",
        "Sarcasm and witty banter are my daily vitamins.",
    ],
    "cliche": [
        "Люблю путешествовать и вкусно поесть, ищу без драмы.",
        "Just here for fun, love netflix and chill vibe.",
    ],
    "aggressive": [
        "Не подходи, если не идеален. Мне не нужны слабые.",
        "Swipe left if you are not perfect or waste my time.",
    ],
    "awkward_or_cringe": [
        "Здесь по приколу, удиви меня или проходи мимо.",
        "So random lol send me memes or go away.",
    ],
}


@dataclass
class Paths:
    model_dir: str = "models/rubert_tiny2_profile_classifier"
    tokenizer_dir: str = model_dir
    config_path: str = "models/rubert_tiny2_profile_classifier/config.json"
    thresholds_path: str = "models/rubert_tiny2_profile_classifier/thresholds.json"
    hf_repo_id: str | None = os.environ.get("DPA_MODEL_REPO_ID")
    hf_revision: str | None = os.environ.get("DPA_MODEL_REVISION")
    hf_cache_dir: str = os.environ.get("DPA_MODEL_CACHE", "models/hf_models")


@dataclass
class HeuristicThresholds:
    short_threshold: int = 40
    long_threshold: int = 320
    emoji_threshold: int = 4
    punctuation_threshold: int = 6
    negative_words: List[str] = field(
        default_factory=lambda: [
            "не люблю",
            "ненавижу",
            "устал",
            "надоел",
            "надоела",
            "хватит",
            "проблем",
            "должен",
            "должна",
        ]
    )
    demanding_patterns: List[str] = field(
        default_factory=lambda: [
            "не пиши, если",
            "обязан",
            "должен быть",
            "ожидаю",
            "только если",
            "если ты не",
            "без драмы",
        ]
    )


@dataclass
class ScoringWeights:
    positive: Dict[str, float] = field(
        default_factory=lambda: {
            "friendly": 15.0,
            "sincere": 18.0,
            "humorous": 12.0,
            "confident": 10.0,
        }
    )
    negative: Dict[str, float] = field(
        default_factory=lambda: {
            "arrogant": 15.0,
            "aggressive": 18.0,
            "cliche": 10.0,
            "awkward_or_cringe": 8.0,
        }
    )
    heuristic_penalties: Dict[str, float] = field(
        default_factory=lambda: {
            "too_short": 15.0,
            "too_long": 8.0,
            "too_generic": 10.0,
            "too_negative": 10.0,
            "too_demanding": 12.0,
            "overloaded_with_cliches": 10.0,
            "not_enough_personality": 10.0,
            "too_many_emojis": 6.0,
            "excessive_punctuation": 6.0,
        }
    )


PATHS = Paths()
HEURISTICS = HeuristicThresholds()
SCORING = ScoringWeights()

ZERO_SHOT_LABELS: Dict[str, str] = {
    "friendly": "звучит дружелюбно и открыто",
    "confident": "звучит уверенно и цельно",
    "arrogant": "выглядит высокомерно или снисходительно",
    "sincere": "похоже на искренний и честный тон",
    "humorous": "содержит лёгкий юмор и самоиронию",
    "cliche": "кажется шаблонным и предсказуемым",
    "aggressive": "звучит агрессивно или резко",
    "awkward_or_cringe": "смотрится кринжово или неловко",
}

ZERO_SHOT_TEMPLATE = "Этот текст анкеты {}."
ZERO_SHOT_MODEL = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
