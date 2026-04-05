from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def cosine_similarity(vec: np.ndarray, other: np.ndarray) -> float:
    denom = (np.linalg.norm(vec) * np.linalg.norm(other)) or 1e-8
    return float(np.dot(vec, other) / denom)


def load_json(path: str) -> Dict:
    path_obj = Path(path)
    if not path_obj.exists():
        return {}
    with path_obj.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Dict, path: str) -> None:
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with path_obj.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_probabilities(values: Sequence[float]) -> List[float]:
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return []
    arr = np.clip(arr, 0, None)
    total = arr.sum() or 1.0
    return list((arr / total).tolist())
