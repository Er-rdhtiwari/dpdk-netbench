from __future__ import annotations

from pathlib import Path


def eval_lora(adapter_dir: Path, model_id: str) -> None:
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Optional finetune deps not installed. Install extras: uv sync --extra finetune"
        ) from exc

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    base_model = AutoModelForCausalLM.from_pretrained(model_id)
    lora_model = PeftModel.from_pretrained(base_model, adapter_dir)

    prompt = "Summarize the throughput metric."
    inputs = tokenizer(prompt, return_tensors="pt")
    base_out = base_model.generate(**inputs, max_new_tokens=20)
    lora_out = lora_model.generate(**inputs, max_new_tokens=20)

    print("Base:", tokenizer.decode(base_out[0], skip_special_tokens=True))
    print("LoRA:", tokenizer.decode(lora_out[0], skip_special_tokens=True))
