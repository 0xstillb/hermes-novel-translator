# Fine-Tuning Guide — CN→TH Novel Translation

## ควรทำ Fine-Tune หรือไม่?

| ปัจจัย | ควรทำ | ไม่ควรทำ |
|-------|-------|---------|
| จำนวนบท | 5,000+ | < 1,000 |
| คุณภาพที่ต้องการ | ระดับตีพิมพ์ | อ่านเพลิน |
| มี GPU หรืองบ | ✅ มี | ❌ ไม่ |
| มีคู่ประโยค CN/EN→TH | 500+ คู่ | 0 คู่ |

**สำหรับ workflow ปัจจุบัน (Skill + Glossary + TM):**
ยังไม่จำเป็น — Skill + TM address 80% ของปัญหา Fine-tune address อีก 20% ที่เหลือ

---

## ทางเลือก: LoRA (ถูก เร็ว)

Train adapter ขนาด ~1GB แทนทั้ง model ~20GB

| Spec | ค่า |
|------|-----|
| Cost | ~$5-10/รอบ (RunPod, HuggingFace, Colab) |
| GPU | RTX 3090 24GB พอ |
| เวลา | ~2-4 ชม. |
| Data | 200-500 คู่ประโยค |

### 1. เตรียม Data

Format: JSONL (Alpaca-style)

```jsonl
{"instruction": "แปลจีนเป็นไทย", "input": "石牧盯着树干上的拳印", "output": "ซือมู่จ้องรอยหมัดบนลำต้น"}
{"instruction": "แปลจีนเป็นไทย", "input": "少年沉默了起来", "output": "เด็กหนุ่มเงียบไปครู่หนึ่ง"}
{"instruction": "Translate English to Thai", "input": "Shi Mu stared at the fist print", "output": "ซือมู่จ้องรอยหมัดบนลำต้น"}
```

**แหล่ง data:** ใช้บทที่แปลแล้ว — 1 บท ≈ 20-30 คู่ → 50 บท = 1000-1500 คู่

### 2. ใช้ Unsloth (Colab-friendly)

```python
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-7B",
    max_seq_length=2048, load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(model, r=16,
    target_modules=["q_proj","k_proj","v_proj","o_proj"],
    lora_alpha=16, lora_dropout=0,
)
# Train ด้วย data JSONL ของคุณ
from trl import SFTTrainer
trainer = SFTTrainer(model=model, tokenizer=tokenizer,
    train_dataset=dataset,
    args=TrainingArguments(max_steps=100, learning_rate=2e-4,
        output_dir="cn-th-lora"),
)
trainer.train()
model.save_pretrained("cn-th-lora-final")
```

### 3. Model ที่แนะนำ

| Model | ขนาด | Thai | LoRA ง่าย |
|-------|:----:|:----:|:---------:|
| **Qwen 2.5 7B** ⭐ | 7B | ✅ | ✅ Unsloth |
| **DeepSeek V2 Lite** | 16B | ⭐⭐ | ✅ |
| **Llama 3.1 8B** | 8B | ⭐ | ✅ ง่ายสุด |

### 4. ใช้ LoRA กับ Hermes

```bash
vllm serve Qwen/Qwen2.5-7B --enable-lora --lora-modules cn-th=/path/to/lora
hermes config set model qwen2.5-7b+cn-th
hermes config set model.base_url http://localhost:8000/v1
```

### คำแนะนำ

1. อย่า Fine-Tune ตอนนี้ — Skill + Glossary + TM ก็เพียงพอ
2. แปลไปสัก 50 บท → สะสม training data แล้วค่อย LoRA
3. ใช้ Unsloth + Colab (free) → ทดสอบก่อน
