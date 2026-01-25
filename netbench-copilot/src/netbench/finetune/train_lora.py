from __future__ import annotations

import json
from pathlib import Path


def run_lora(dataset_path: Path, val_path: Path, model_id: str, out_dir: Path) -> None:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
        from peft import LoraConfig, get_peft_model
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Optional finetune deps not installed. Install extras: uv sync --extra finetune"
        ) from exc

    def load_texts(path: Path) -> list[str]:
        texts = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            parts = [msg["content"] for msg in payload.get("messages", [])]
            texts.append("\n".join(parts))
        return texts

    train_texts = load_texts(dataset_path)
    val_texts = load_texts(val_path)

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)

    lora_config = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, bias="none")
    model = get_peft_model(model, lora_config)

    def tokenize(texts: list[str]):
        return tokenizer(texts, truncation=True, padding="max_length", max_length=256)

    train_enc = tokenize(train_texts)
    val_enc = tokenize(val_texts)

    class SimpleDataset(torch.utils.data.Dataset):
        def __init__(self, enc):
            self.enc = enc

        def __len__(self):
            return len(self.enc["input_ids"])

        def __getitem__(self, idx):
            item = {k: torch.tensor(v[idx]) for k, v in self.enc.items()}
            item["labels"] = item["input_ids"].clone()
            return item

    train_ds = SimpleDataset(train_enc)
    val_ds = SimpleDataset(val_enc)

    out_dir.mkdir(parents=True, exist_ok=True)
    args = TrainingArguments(
        output_dir=str(out_dir),
        num_train_epochs=1,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        eval_strategy="steps",
        eval_steps=5,
        logging_steps=5,
        save_steps=5,
        max_steps=5,
    )

    trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=val_ds)
    trainer.train()
    model.save_pretrained(out_dir / "adapter")
    tokenizer.save_pretrained(out_dir / "adapter")
