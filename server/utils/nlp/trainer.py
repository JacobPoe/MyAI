from datasets import load_dataset
from transformers import (
    GPT2Tokenizer,
    Trainer as T,
    TrainingArguments,
    GPT2LMHeadModel,
)

from utils.enums import Dataset

training_args = TrainingArguments(
    output_dir="./../../training_data/gpt2-finetuned",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    logging_dir="./../../logs",
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=2,
    prediction_loss_only=True,
)

tokenized_dataset = None
trainer: T


class Trainer:
    def __init__(self, model: GPT2LMHeadModel, tokenizer: GPT2Tokenizer):
        dataset = load_dataset(Dataset.MEGASCIENCE.value)
        self.tokenized_dataset = dataset.map(
            lambda batch: Trainer.format_dataset_batched(batch, tokenizer),
            batched=True,
        )

        self.trainer = T(
            model=model,
            args=training_args,
            train_dataset=self.tokenized_dataset["train"],
            eval_dataset=self.tokenized_dataset["validation"],
        )

    def init_training(self):
        self.trainer.train()

    @staticmethod
    def format_dataset_batched(batch, t: GPT2Tokenizer, max_length=512):
        prompts = [
            f"Subject: {s}\nSource: {src}\nReference Answer: {ra}\nQ: {q}\nA: {a}"
            for s, src, ra, q, a in zip(
                batch["subject"],
                batch["source"],
                batch["reference_answer"],
                batch["question"],
                batch["answer"],
            )
        ]

        tokenized = t(
            prompts,
            padding="max_length",
            truncation=True,
            max_length=max_length,
        )
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized
