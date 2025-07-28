import json
import os

from services.env import EnvService, EnvVars
from utils.logger import Logger, LogLevel

from datasets import load_dataset, concatenate_datasets
from transformers import (
    GPT2Tokenizer,
    Trainer as T,
    TrainingArguments,
    GPT2LMHeadModel,
)

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

trainer: T


class Trainer:
    def __init__(self, model: GPT2LMHeadModel, tokenizer: GPT2Tokenizer):
        Logger.log(LogLevel.INFO, "Initializing Trainer...")

        dataset_configs = Trainer.load_dataset_configs()
        dataset = Trainer.combine_datasets(dataset_configs)
        tokenized_dataset = Trainer.tokenize_dataset(dataset, tokenizer)

        self.trainer = T(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset["train"],
            eval_dataset=tokenized_dataset["test"],
        )
        Logger.log(LogLevel.INFO, "Trainer initialized successfully.")


    def __del__(self):
        Logger.log(LogLevel.INFO, "Destroying Trainer instance...")
        if self.trainer is not None:
            try:
                self.trainer.save_model()
            except Exception as e:
                Logger.log(LogLevel.ERROR, f"Error saving model: {e}")
        Logger.log(LogLevel.INFO, "Trainer instance destroyed.")

    def init_training(self):
        self.trainer.train()

    @staticmethod
    def tokenize_dataset(dataset, t: GPT2Tokenizer):
        def tokenize_function(examples):
            # Tokenize the text, pad to max_length, and truncate if necessary
            tokenized = t(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=EnvService.get_int(EnvVars.MAX_LENGTH.value),
            )
            # For language modeling, the labels are the input_ids themselves
            tokenized["labels"] = tokenized["input_ids"].copy()
            return tokenized

        return dataset.map(tokenize_function, batched=True)

    @staticmethod
    def combine_datasets(configs):
        all_datasets = []
        for config in configs:
            dataset = load_dataset(config.get("hf_id"), config.get("config_type"), split=config.get("split", "train"))

            # Format the text for each example into a new 'text' column
            def format_batch(batch):
                pattern = config.get("pattern")
                columns = config.get("columns")
                formatted_texts = []
                num_examples = len(batch[columns[0]])
                for i in range(num_examples):
                    values = []
                    for col in columns:
                        val = batch[col][i]
                        if isinstance(val, dict) and 'text' in val:
                            # Take the first answer if it's a list
                            values.append(val['text'][0] if isinstance(val['text'], list) and val['text'] else "")
                        else:
                            values.append(str(val))
                    formatted_texts.append(pattern.format(*values))
                return {"text": formatted_texts}

            formatted_dataset = dataset.map(format_batch, batched=True)
            all_datasets.append(formatted_dataset)

        concatenated_dataset = concatenate_datasets(all_datasets)
        return concatenated_dataset.train_test_split(test_size=0.1, seed=67)

    @staticmethod
    def load_dataset_configs():
        datasets_path = os.path.join(
            os.path.abspath(os.path.join(__file__, "../../..")),
            "datasets.json"
        )
        with open(datasets_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

