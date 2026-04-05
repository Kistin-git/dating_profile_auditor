from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from datasets import Dataset, DatasetDict
from sklearn.metrics import f1_score, precision_score, recall_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.config import LABELS
from src.utils import save_json, set_seed
from training.data_collator import MultiLabelDataCollator


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    probs = 1 / (1 + np.exp(-logits))
    preds = (probs > 0.5).astype(int)
    metrics = {
        "f1_micro": f1_score(labels, preds, average="micro", zero_division=0),
        "f1_macro": f1_score(labels, preds, average="macro", zero_division=0),
        "precision_micro": precision_score(labels, preds, average="micro", zero_division=0),
        "recall_micro": recall_score(labels, preds, average="micro", zero_division=0),
    }
    for idx, label in enumerate(LABELS):
        metrics[f"{label}_f1"] = f1_score(labels[:, idx], preds[:, idx], zero_division=0)
    return metrics


def encode_dataset(dataset: DatasetDict, tokenizer, max_length: int) -> DatasetDict:
    def tokenize_batch(batch):
        tokenized = tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=max_length,
        )
        labels = []
        for i in range(len(batch["text"])):
            labels.append([float(batch[label][i]) for label in LABELS])
        tokenized["labels"] = labels
        return tokenized

    return dataset.map(tokenize_batch, batched=True, remove_columns=[col for col in dataset["train"].column_names if col not in {"text"}])


def main() -> None:
    parser = argparse.ArgumentParser(description="Train dating profile auditor classifier")
    parser.add_argument("--dataset_path", type=str, default="data/synthetic_profiles.csv")
    parser.add_argument("--output_dir", type=str, default="models/rubert_tiny2_profile_classifier")
    parser.add_argument("--model_name", type=str, default="cointegrated/rubert-tiny2")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=5e-5)
    parser.add_argument("--max_length", type=int, default=256)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)

    data_path = Path(args.dataset_path)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset file {data_path} not found. Run training/dataset_builder.py first.")

    df = pd.read_csv(data_path)
    train_df = df.sample(frac=0.8, random_state=args.seed)
    remaining_df = df.drop(train_df.index)
    val_df = remaining_df.sample(frac=0.5, random_state=args.seed)
    test_df = remaining_df.drop(val_df.index)

    dataset = DatasetDict(
        {
            "train": Dataset.from_pandas(train_df.reset_index(drop=True)),
            "validation": Dataset.from_pandas(val_df.reset_index(drop=True)),
            "test": Dataset.from_pandas(test_df.reset_index(drop=True)),
        }
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    dataset = encode_dataset(dataset, tokenizer, args.max_length)
    data_collator = MultiLabelDataCollator(tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=len(LABELS),
        problem_type="multi_label_classification",
    )

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        logging_steps=50,
        report_to=[],
        seed=args.seed,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.evaluate(eval_dataset=dataset["validation"])

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    thresholds_path = output_dir / "thresholds.json"
    save_json({label: 0.5 for label in LABELS}, str(thresholds_path))
    (output_dir / "label_list.txt").write_text("\n".join(LABELS), encoding="utf-8")


if __name__ == "__main__":
    main()
