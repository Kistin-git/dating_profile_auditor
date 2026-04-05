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


SEED_PROFILES: List[Dict] = [
    {
        "text": "Люблю готовить рамен, бегаю по утрам и ищу того, кто смеётся громче меня.",
        "language": "ru",
        "friendly": 1,
        "sincere": 1,
        "humorous": 1,
        "confident": 0,
        "arrogant": 0,
        "cliche": 0,
        "aggressive": 0,
        "awkward_or_cringe": 0,
    },
    {
        "text": "Не трать моё время, если не амбициозен и не зарабатываешь больше меня.",
        "language": "ru",
        "friendly": 0,
        "sincere": 0,
        "humorous": 0,
        "confident": 1,
        "arrogant": 1,
        "cliche": 0,
        "aggressive": 1,
        "awkward_or_cringe": 0,
    },
    {
        "text": "Люблю путешествовать и вкусно поесть, ищу без драмы.",
        "language": "ru",
        "friendly": 0,
        "sincere": 0,
        "humorous": 0,
        "confident": 0,
        "arrogant": 0,
        "cliche": 1,
        "aggressive": 0,
        "awkward_or_cringe": 0,
    },
    {
        "text": "Just here for spontaneous city walks and museum dates.",
        "language": "en",
        "friendly": 1,
        "sincere": 1,
        "humorous": 0,
        "confident": 0,
        "arrogant": 0,
        "cliche": 0,
        "aggressive": 0,
        "awkward_or_cringe": 0,
    },
    {
        "text": "Swipe left unless you can cook better than me and never cancel plans.",
        "language": "en",
        "friendly": 0,
        "sincere": 0,
        "humorous": 0,
        "confident": 1,
        "arrogant": 1,
        "cliche": 0,
        "aggressive": 1,
        "awkward_or_cringe": 0,
    },
    {
        "text": "Здесь по приколу 🤪 удиви меня, иначе скучно.",
        "language": "ru",
        "friendly": 0,
        "sincere": 0,
        "humorous": 0,
        "confident": 0,
        "arrogant": 0,
        "cliche": 1,
        "aggressive": 0,
        "awkward_or_cringe": 1,
    },
]


CANDIDATE_EXTENSIONS = [
    ("и готовлю идеальный чизкейк", {"friendly": 1, "sincere": 1}),
    ("не пишите, если ищете просто переписку", {"aggressive": 1, "arrogant": 1}),
    ("мечтаю о кемперах и северных закатах", {"friendly": 1, "sincere": 1}),
    ("умение смеяться над собой обязательно", {"humorous": 1, "friendly": 1}),
    ("не люблю опоздания", {"confident": 1}),
    ("люблю порядок и списки задач", {"confident": 1}),
    ("ищу без драмы и игр", {"cliche": 1}),
    ("если не умеешь готовить, проходи мимо", {"aggressive": 1}),
    ("let's keep it fun and nerdy", {"humorous": 1, "friendly": 1}),
]


def augment_profile(row: Dict, num_variations: int) -> List[Dict]:
    variations = []
    for _ in range(num_variations):
        ext_text, ext_labels = random.choice(CANDIDATE_EXTENSIONS)
        new_row = row.copy()
        new_row["text"] = f"{row['text']} {ext_text}"
        for label, value in ext_labels.items():
            new_row[label] = max(new_row.get(label, 0), value)
        variations.append(new_row)
    return variations


def build_dataset(size: int = 240) -> pd.DataFrame:
    rows: List[Dict] = []
    while len(rows) < size:
        base = random.choice(SEED_PROFILES)
        rows.append(base.copy())
        rows.extend(augment_profile(base, 1))
    df = pd.DataFrame(rows[:size])
    df["length_bucket"] = pd.cut(df["text"].str.len(), bins=[0, 80, 200, 1000], labels=["short", "mid", "long"])
    df["has_emoji"] = df["text"].str.contains(r"[😀-🙏🌊✨🤪😂😍]")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Build synthetic dataset for dating profile auditor")
    parser.add_argument("--size", type=int, default=240)
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
