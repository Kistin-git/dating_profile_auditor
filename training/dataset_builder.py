from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.config import LABELS
from src.utils import set_seed


ARCHETYPES: List[Dict] = [
    {
        "id": "warm_ru",
        "language": "ru",
        "text": "Люблю ранние завтраки, велопрогулки и разговоры без телефона.",
        "labels": {"friendly": 1, "sincere": 1, "humorous": 0, "confident": 0},
    },
    {
        "id": "funny_ru",
        "language": "ru",
        "text": "Соревнуюсь в плохих шутках и могу пересказать весь 'Офис'.",
        "labels": {"humorous": 1, "friendly": 1, "awkward_or_cringe": 0},
    },
    {
        "id": "demanding_ru",
        "language": "ru",
        "text": "Без амбиций и цели не пишите: я ценю людей, которые растут.",
        "labels": {"confident": 1, "arrogant": 1, "aggressive": 0},
    },
    {
        "id": "cliche_ru",
        "language": "ru",
        "text": "Люблю путешествовать, закаты и вкусно поесть.",
        "labels": {"cliche": 1},
    },
    {
        "id": "awkward_ru",
        "language": "ru",
        "text": "Здесь по приколу, удиви меня или пролистывай дальше.",
        "labels": {"awkward_or_cringe": 1, "cliche": 1},
    },
    {
        "id": "aggressive_ru",
        "language": "ru",
        "text": "Хватит людей без целей: если только лежишь на диване — мимо.",
        "labels": {"aggressive": 1, "arrogant": 1},
    },
    {
        "id": "confident_ru",
        "language": "ru",
        "text": "Инженер, люблю запускать проекты и ценю честные разговоры.",
        "labels": {"confident": 1, "friendly": 1},
    },
    {
        "id": "warm_en",
        "language": "en",
        "text": "Coffee geek, dog person and believer in gentle mornings.",
        "labels": {"friendly": 1, "sincere": 1},
    },
    {
        "id": "funny_en",
        "language": "en",
        "text": "Recovering meme hoarder, fluent in sarcasm and midnight pancakes.",
        "labels": {"humorous": 1, "friendly": 1},
    },
    {
        "id": "demanding_en",
        "language": "en",
        "text": "Swipe left unless you're proactive, tall, and know your goals.",
        "labels": {"confident": 1, "arrogant": 1},
    },
]


MODIFIERS = {
    "warm": {
        "phrases": [
            "ищу человека, который ценит маленькие ритуалы",
            "верю, что забота в деталях",
            "looking for someone kind and curious",
        ],
        "labels": {"friendly": 1, "sincere": 1},
    },
    "humor": {
        "phrases": [
            "умею смеяться над собой и над странными датами",
            "bad jokes and good playlists are my love language",
        ],
        "labels": {"humorous": 1},
    },
    "demanding": {
        "phrases": [
            "не трать моё время, если не готов к диалогу",
            "don't text unless you keep promises",
        ],
        "labels": {"arrogant": 1, "aggressive": 1},
    },
    "cliche": {
        "phrases": [
            "люблю кино, музыку и прогулки",
            "foodie, sunsets, travel",
        ],
        "labels": {"cliche": 1},
    },
    "emoji": {
        "phrases": [
            "🌊🌊🌊",
            "😅✨",
            "😂🔥",
        ],
        "labels": {},
    },
}


NEGATIVE_PATTERNS = ["не люблю", "надоел", "устал", "don't"]
DEMAND_PATTERNS = ["не пиши", "обязан", "only if", "must be"]


def extend_text(base: str, additions: List[str]) -> str:
    return " ".join([base] + additions)


def synthesize(seed: Dict) -> Dict:
    text = seed["text"]
    labels = {label: 0 for label in LABELS}
    for label, value in seed["labels"].items():
        labels[label] = value

    extra_chunks: List[str] = []
    chosen_mods = random.sample(list(MODIFIERS.keys()), k=random.randint(1, 3))
    for mod in chosen_mods:
        phrase = random.choice(MODIFIERS[mod]["phrases"])
        extra_chunks.append(phrase)
        for label, value in MODIFIERS[mod]["labels"].items():
            labels[label] = max(labels[label], value)

    if random.random() < 0.25:
        cliche_phrase = random.choice(MODIFIERS["cliche"]["phrases"])
        extra_chunks.append(cliche_phrase)
        labels["cliche"] = 1
    if random.random() < 0.18:
        emoji = random.choice(MODIFIERS["emoji"]["phrases"])
        extra_chunks.append(emoji)

    final_text = extend_text(text, extra_chunks)
    return {
        "text": final_text,
        "language": seed["language"],
        "source": seed["id"],
        **labels,
    }


def calc_metadata(row: Dict) -> Dict:
    text = row["text"]
    length = len(text)
    length_bucket = "short" if length < 90 else "mid" if length < 220 else "long"
    has_emoji = any(ch for ch in text if ch in "😀😁😂🤣😅😊😍😘🤪🤔😎💫✨🔥🌊❤️")
    has_negative = any(pattern in text.lower() for pattern in NEGATIVE_PATTERNS)
    has_demands = any(pattern in text.lower() for pattern in DEMAND_PATTERNS)
    cliche_count = sum(1 for phrase in MODIFIERS["cliche"]["phrases"] if phrase.lower() in text.lower())
    return {
        **row,
        "length_bucket": length_bucket,
        "has_emoji": has_emoji,
        "has_negative_patterns": has_negative,
        "has_demands": has_demands,
        "cliche_count": cliche_count,
    }


def build_dataset(size: int = 500) -> pd.DataFrame:
    rows: List[Dict] = []
    cursor = 0
    while len(rows) < size:
        seed = ARCHETYPES[cursor % len(ARCHETYPES)]
        cursor += 1
        rows.append(calc_metadata(synthesize(seed)))
    df = pd.DataFrame(rows[: size])
    ordered_cols = ["text", "language", "source"] + LABELS + [
        "length_bucket",
        "has_emoji",
        "has_negative_patterns",
        "has_demands",
        "cliche_count",
    ]
    return df[ordered_cols]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build enhanced synthetic dataset for dating profile auditor")
    parser.add_argument("--size", type=int, default=600)
    parser.add_argument("--output_dir", type=str, default="data")
    args = parser.parse_args()

    set_seed(42)
    df = build_dataset(args.size)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = output_dir / "synthetic_profiles.csv"
    df.to_csv(dataset_path, index=False)
    print(f"Saved dataset with {len(df)} rows to {dataset_path}")


if __name__ == "__main__":
    main()
