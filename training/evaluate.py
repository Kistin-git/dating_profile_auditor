from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.config import LABELS
from training.train import compute_metrics, encode_dataset
from training.data_collator import MultiLabelDataCollator


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate trained dating profile auditor")
    parser.add_argument("--dataset_path", type=str, default="data/synthetic_profiles.csv")
    parser.add_argument("--model_dir", type=str, default="models/rubert_tiny2_profile_classifier")
    parser.add_argument("--split", type=str, default="test", choices=["train", "validation", "test"])
    parser.add_argument("--max_length", type=int, default=256)
    args = parser.parse_args()

    model_dir = Path(args.model_dir)
    if not model_dir.exists():
        raise FileNotFoundError(f"Model directory {model_dir} not found.")

    df = pd.read_csv(args.dataset_path)
    train_df = df.sample(frac=0.8, random_state=42)
    remaining = df.drop(train_df.index)
    val_df = remaining.sample(frac=0.5, random_state=42)
    test_df = remaining.drop(val_df.index)

    dataset = DatasetDict(
        {
            "train": Dataset.from_pandas(train_df.reset_index(drop=True)),
            "validation": Dataset.from_pandas(val_df.reset_index(drop=True)),
            "test": Dataset.from_pandas(test_df.reset_index(drop=True)),
        }
    )

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    encoded = encode_dataset(dataset, tokenizer, args.max_length)[args.split]

    data_collator = MultiLabelDataCollator(tokenizer)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir, num_labels=len(LABELS))
    training_args = TrainingArguments(output_dir="outputs/eval", per_device_eval_batch_size=8, report_to=[])

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    metrics = trainer.evaluate(eval_dataset=encoded)
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
