# Hermes Novel Translator

แปลนิยายจีน → ไทย / อังกฤษ → ไทย ด้วย Hermes Agent — parallel pipeline, 3 quality tiers, glossary state file ข้ามเครื่อง

## โครงสร้าง

```
hermes-novel-translator/
├── .hermes/skills/custom/cn-th-novel-translation/   # Hermes Skill หลัก
│   ├── SKILL.md                                      # วิธีการใช้ + pipeline ทั้งหมด
│   ├── references/                                   # ข้อมูลอ้างอิง (พินอิน, สำนวนไทย, ฯลฯ)
│   ├── scripts/                                      # utility scripts (glossary, stats)
│   └── templates/                                    # pipeline templates (one-shot, glossary)
├── novels/the-portal-of-wonderland/                  # ตัวอย่างโปรเจกต์นิยาย
└── setup-windows.bat                                 # Setup script สำหรับ Windows USB
```

## เริ่มต้นใช้งาน

```bash
# 1. ติดตั้ง skill
cp -r .hermes/skills/custom/cn-th-novel-translation ~/.hermes/skills/custom/

# 2. สร้าง translator profile
hermes profile create translator --clone
hermes --profile translator config set model deepseek-v4-flash

# 3. เปิด translator chat
translator chat
# หรือ
hermes --profile translator
```

## Pipeline (3 Tiers)

| Tier | คุณภาพ | ราคา/1000ch | เหมาะกับ |
|------|--------|:-----------:|----------|
| 🥇 Best | Thai เนียน | ~$45 | publish / ลงเว็บ |
| 🥈 Balanced | Thai ดี | ~$18 | อ่านทั่วไป |
| 🥉 Budget | พอใช้ | ~$15 | แปลด่วน |

ดูรายละเอียดเพิ่มเติมใน `skill/cn-th-novel-translation/SKILL.md`

## Windows Quick Setup (USB)

วาง `setup-windows.bat` และ `hermes-novel-translator-pack.zip` ไว้ใน USB
ดับเบิลคลิก `setup-windows.bat` — มันจะแตกไฟล์ skill + sample novel ไปที่ `%USERPROFILE%` อัตโนมัติ

## ตัวอย่างการแปล (The Portal of Wonderland)

```
novels/the-portal-of-wonderland/
├── .hermes.md               # task config + name/term conventions
├── raw-cn/ch001.txt         # ต้นฉบับจีน
├── raw/ch001.txt            # ต้นฉบับอังกฤษ (แปลจากจีนอีกที)
├── raw-th/ch001.txt         # ตัวอย่างไทยจาก WTR-LAB
└── translated/ch001.md      # ฉบับแปลไทย (output)
```
