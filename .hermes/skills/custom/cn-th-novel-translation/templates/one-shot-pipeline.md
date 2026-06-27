# One-Shot Novel Translation Pipeline
# ใส่ URL → Hermes จัดการ Scout→Names→Translate→Polish→QC auto

## 🔧 ตั้งค่าก่อนเริ่ม
novel_name: "The Portal of Wonderland"
novel_id: 3463 (WTR-LAB)
book_id: u6ced (czbooks) 
total_chapters: 1131
cn_url: "https://czbooks.net/n/u6ced"
en_url: "https://wtr-lab.com/en/novel/3463/the-portal-of-wonderland"
th_url: "https://wtr-lab.com/th/novel/3463/the-portal-of-wonderland"
project_dir: "~/novels/the-portal-of-wonderland"

---

## ⚡ One-Shot Pipeline

### Phase 1: Scout (DS Flash)
```
delegate_task(
  goal=""
  Scout novel: {novel_name}
  - ไปที่ {cn_url} → ตรวจจำนวนบท
  - ไปที่ {en_url}/chapter-1 → เช็ค URL pattern
  - สร้าง project structure ที่ {project_dir}
  - ดึง raw-cn/ch001~003.txt จาก czbooks (ตัด login UI, ads)
  - ดึง raw-en/ch001~003.txt จาก WTR-LAB /en/ (ตัด Biquge ad, nav)
  - ดึง raw-th/ch001~003.txt จาก WTR-LAB /th/ (ตัด Biquge ad, nav)
  - สร้าง chapters.json
  - รายงาน: ดึงไปแล้ว 3/{total_chapters} บท
  "",
  model="deepseek-v4-flash",
  toolsets=["web", "browser", "terminal", "file"]
)
```

### Phase 2: Names Extraction (DS Flash)
```
delegate_task(
  goal=""
  Names extraction สำหรับ {novel_name}:
  1. อ่าน raw-cn/ch001~003.txt → scan ตัวละคร + ความถี่
  2. อ่าน raw-en/ch001~003.txt → จับคู่ชื่อ ENG
  3. อ่าน raw-th/ch001~003.txt → สังเกตชื่อที่ WTR-LAB ใช้
  4. CN → พินอิน → เสนอไทย โดยใช้ references/pinyin-to-thai-conventions.md
  5. อ่าน CN ตรวจศัพท์เฉพาะ (淬體→Body Tempering→ควรเป็นอะไร?)
  6. สร้างตารางเสนอ user verify:
     | CN | EN | WTR-LAB TH | เสนอไทย | Role | |
     |----|----|-----------|---------|------|---|
     | 石牧 | Shi Mu | ชิมู่ ✗ | ซือมู่ | main | |
     | 石亭 | Shi Ting | ชิติง ✗ | ซือถิง | side | |
     | 成管事 | Steward Cheng | ผู้ดูแลเฉิง | สจ๊วตเฉิง | side | |
     | 淬體 | Body Tempering | ฝึกฝนร่างกาย | บำเพ็ญกาย | term | |
     | 武者 | Martial Artist | นักศิลปะการต่อสู้ ✗ | ยอดฝีมือ | term | |
  7. รอ user verify → สร้าง glossary.json
  "",
  model="deepseek-v4-flash",
  context="ใช้ references/pinyin-to-thai-conventions.md เสนอชื่อไทย",
  toolsets=["terminal", "file"]
)
```

### ⏸ PAUSE: รอ user verify glossary.json

---

### Phase 3: Translate Batch (Qwen Max)
```
delegate_task(
  tasks=[
    {
      "goal": ""
      แปลไทยบทที่ {i}:
      - อ่าน glossary.json → ใช้ชื่อตาม glossary เท่านั้น
      - อ่าน references/thai-idiom-dict.md → ใช้สำนวนไทย
      - อ่าน raw-en/ch{str(i).zfill(3)}.txt → แปลไทย
      - ภาษาไทยธรรมชาติ อ่านลื่น
      - เสร็จ → QC: ชื่อตรง? ศัพท์ตรง? ไม่มี ENG ติด?
      - บันทึก translated/ch{str(i).zfill(3)}.md
      - อัพเดท chapters.json
      "",
      "context": "glossary.json อยู่ที่ project root",
      "model": "qwen3.7-max",
      "toolsets": ["terminal", "file"]
    }
    for i in range(start, end+1)
  ]
)
```

### Phase 4: Polish Batch (Qwen Max)
```
delegate_task(
  tasks=[
    {
      "goal": ""
      Polish รอบ 2 สำหรับบทที่ {i}:
      - อ่าน translated/ch{str(i).zfill(3)}.md
      - เกลาสำนวนไทย:
        * ตัด "ของ" ที่ไม่จำเป็น
        * เปลี่ยนคำเชื่อม (แล้ว→ครั้น, ก็→จึง)
        * สลับคำเรียกตัวละคร (อย่าซ้ำ)
        * ปรับคำพูดให้สมบทบาท
        * ตรวจ onomatopoeia (โครม/วาบ/ฟู่)
      - ไม่แก้ชื่อ (ใช้ตาม glossary)
      - อ่านออกเสียงในใจ → ตรงไหนสะดุดแก้
      - บันทึกทับ translated/ch{str(i).zfill(3)}.md
      "",
      "context": "glossary.json + thai-idiom-dict.md",
      "model": "qwen3.7-max",
      "toolsets": ["terminal", "file"]
    }
    for i in range(start, end+1)
  ]
)
```

### Phase 5: QC Batch (DS Flash)
```
delegate_task(
  tasks=[
    {
      "goal": ""
      QC บทที่ {i}:
      - [ ] ชื่อตัวละครตรง glossary?
      - [ ] ศัพท์เฉพาะตรง?
      - [ ] ไม่มีคำ ENG ติด?
      - [ ] ภาษาไทยธรรมชาติ?
      - [ ] "ของ" เกินจำเป็น?
      - [ ] คำพูดสมบทบาท?
      - [ ] onomatopoeia ถูก?
      บันทึกเป็น qc-report/ch{str(i).zfill(3)}.md
      "",
      "model": "deepseek-v4-flash",
      "toolsets": ["terminal", "file"]
    }
    for i in range(start, end+1)
  ]
)
```

---

## 🚀 วิธีเริ่ม (Copy-Paste Ready)

### 1) สร้างโปรเจกต์
```
run pipeline ตาม template สำหรับ {novel_name}
- เริ่ม Phase 1 Scout ก่อน
- แล้ว Phase 2 Names
- รอ verify glossary
- แปล batch 5 บทแรก
```

### 2) แปลต่อ batch ถัดไป
```
pipeline continue {novel_name} 
- แปลบทที่ 6-10
- batch ละ 5 บท
```

### 3) Cron job รายวัน
```
cronjob(
  name="novel-auto-translate",
  schedule="every 12h",
  model="qwen3.7-max",            # ← cron job ก็ override model ได้
  skills=["hermes-novel-translator"],
  prompt=""
    pipeline continue {novel_name}
    แปล batch ถัดไป 5 บท
    รายงาน progress
  "
)
```

---

## 📊 Model Usage Summary

| Phase | Model | Req/1000ch |
|-------|-------|:----------:|
| Scout | deepseek-v4-flash | 5 |
| Names | deepseek-v4-flash | 10 |
| Translate | **qwen3.7-max** | 1000 |
| Polish | **qwen3.7-max** | 1000 |
| QC | deepseek-v4-flash | 1000 |
| **Qwen Max รวม** | | **2000 req** |

Qwen Max 4,300 req/limit → ใช้ 46% ✅  
DS Flash 158k req → ใช้ 1.3% ✅
