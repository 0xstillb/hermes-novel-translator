---
name: cn-th-novel-translation
description: "แปลนิยายจีน → ไทย / อังกฤษ → ไทย ด้วย Hermes — parallel pipeline, 3 quality tiers, glossary state file ข้ามเครื่อง"
version: 3.1.0
platforms: [macos, linux, windows]
tags: [translation, novel, chinese, thai, pipeline, parallel, windows]
---

# แปลนิยายจีน → ไทย (v2.7)

รองรับสองโหมด:
- **โหมด A:** ต้นฉบับจีน (中文) → ไทย
- **โหมด B:** ต้นฉบับอังกฤษ (English ที่แปลจากจีนอีกที) → ไทย ← **คุณใช้โหมดนี้**

## ⚡ Quickstart Cheat Sheet

| ถ้าอยาก... | ใช้ workflow นี้ |
|-----------|----------------|
| **Best quality (3-Way CN+EN+TH)** | `ใช้ templates/one-shot-pipeline.md → ใส่ URL จบ` |
| **แปลด่วน** 1 บท | `อ่าน raw/ch001.txt → แปลไทย → บันทึก translated/ch001.md` |
| **คุณภาพดี** 2-step | Step 1 draft → Step 2 polish (section 6) |
| **เร็วสุด** parallel bulk | หั่น chunk → `delegate_task` 3-5 แปลพร้อมกัน |
| **เปิดโปรเจกต์ที่มีอยู่** | ไปที่ `~/novels/ชื่อเรื่อง/` → `.hermes.md` โหลด auto |
| **ตั้ง glossary.json** | `cp templates/glossary-template.json glossary.json` แล้วแก้ |
| **Auto-extract names** | `python3 {skill_dir}/scripts/auto-glossary.py raw/*.txt` |
| **ดูสถิติโปรเจกต์** | `python3 {skill_dir}/scripts/stats.py` |

## 🏆 Best Practice (3-Way + Qwen Max)

```bash
# 1. เปิด translator profile
translator chat

# 2. วาง templates/one-shot-pipeline.md
# เปลี่ยนชื่อนิยาย + URL → Hermes จัดการ Scout, Names, Translate, Polish, QC auto
# delegate_task ใช้ model override auto: DS Flash → Qwen Max → DS Flash

# หรือสั่งทีละ phase:
hermes config set model qwen3.7-max
hermes chat -q "อ่าน raw/ch001.txt → glossary.json → แปลไทย best quality
  → ใช้ thai-idiom-dict.md reference → polish รอบ 2 → บันทึก"
```

## 🏗️ Multi-Model Architecture (Comprehensive Design)

### Core Principle

```
┌─────────────────────────────────────────────────────────────┐
│          แต่ละงาน → Model ที่เหมาะกับงานนั้นๆ                │
│                                                              │
│  แทนที่จะใช้ model เดียวทำทุกอย่าง → แยกตามลักษณะงาน         │
│  → ประหยัดกว่า + quality ดีกว่า                              │
└─────────────────────────────────────────────────────────────┘
```

### Model Comparison Matrix (OpenCode Go)

| Model | ไทย | ENG | CN | Speed | Cost/Task | Request Limit/เดือน |
|-------|:---:|:---:|:--:|:-----:|:---------:|:------------------:|
| **deepseek-v4-flash** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | เร็ว | ถูกที่สุด | **158,150** |
| **deepseek-v4-pro** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | กลาง | ~2x Flash | 17,150 |
| **qwen3.7-plus** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | เร็ว | ~3x Flash | 16,300 |
| **qwen3.7-max** ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | กลาง | ~5x Flash | 4,300 |
| **kimi-k2.6** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | เร็ว | ~2x Flash | 5,750 |
| **minimax-m3** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | เร็ว | ~2x Flash | ~6,000 |

> **Key Insight:** ไม่มี model ไหนเก่งทุกด้าน — Qwen Max ไทยดีที่สุดแต่ request limit ต่ำ  
> DeepSeek Flash ใช้กับงาน量大ที่คุณภาพไทยไม่ใช่ bottleneck

### Five-Phase Model Mapping

```
┌──────────────────────────────────────────────────────────────────┐
│                         PIPELINE                                  │
├────────────┬───────────┬───────────┬──────────┬──────────────────┤
│  PHASE 1   │ PHASE 2   │ PHASE 3   │ PHASE 4  │ PHASE 5          │
│  SCOUT     │ NAMES     │ TRANSLATE │ POLISH   │ QC               │
├────────────┼───────────┼───────────┼──────────┼──────────────────┤
│ DS Flash   │ DS Flash  │ DS Flash  │ Qwen Max │ DS Flash         │
│             │           │           │          │                   │
│ แค่         │ แค่       │ Draft เอา │ เกลา     │ แค่ตรวจ          │
│ orchestrate│ scan text │ เนื้อหา    │ สำนวนไทย │ consistency      │
│ tools       │ ENG+CN    │ (ถูกที่สุด)│ (ต้องไทย)│ (ไม่ต้องคิดมาก)   │
└────────────┴───────────┴───────────┴──────────┴──────────────────┘

Token/Request Profile:
  Scout:    ~200 tok/req     × 5 req              = 1k tok
  Names:    ~5000 tok/req    × 50 req (20ch/batch) = 250k tok  
  Translate: ~6000 tok/req   × 1000 req           = 6M tok
  Polish:   ~4000 tok/req    × 1000 req           = 4M tok
  QC:       ~4000 tok/req    × 1000 req           = 4M tok
```

### Budget Allocation (OpenCode Go $60/month cap)

```
$60/month cap → จัดสรร:
  ├── Scout + Names:  ~$1   (DS Flash)
  ├── Draft:          ~$10  (DS Flash × 1000 req)
  ├── Polish:         ~$30  (Qwen Max × 1000 req)  ← 50% ของงบ
  └── QC:             ~$5   (DS Flash)
  └── เหลือ:          ~$14  (ไว้ใช้โค้ดอื่น)
```

### 3 Service Tiers

#### 🥇 Tier 1: Best Quality (สำหรับ publish / ลงเว็บ)

```yaml
Phase 1: deepseek-v4-flash    # Scout
Phase 2: deepseek-v4-flash    # Names
Phase 3: deepseek-v4-flash    # Draft
Phase 4: qwen3.7-max          # Polish ✅ ไทยดีสุด
Phase 5: deepseek-v4-flash    # QC
```

| Cost/1000 บท | ระยะเวลา | คุณภาพ |
|:------------:|:--------:|:------:|
| **ใน Go sub** | ~30 วัน | ✅✅✅ Thai เนียน |
| **Zen ~$30** | (polish 34 บท/วัน) | |

**กลยุทธ์ Qwen Max 4,300 req limit:**
```
Limit: 4,300 req/เดือน
  → 143 req/วัน
  → Polish 34 บท/วัน (batch 5 × 6.8 รอบ)
  → ครบ 1,000 บทใน 30 วันพอดี
```

#### 🥈 Tier 2: Balanced (คุณภาพดี ราคากลาง)

```yaml
Phase 1: deepseek-v4-flash    # Scout
Phase 2: deepseek-v4-flash    # Names
Phase 3: deepseek-v4-flash    # Draft
Phase 4: qwen3.7-plus         # Polish ✅ รองลงมา แต่ limit สูงกว่า
Phase 5: deepseek-v4-flash    # QC
```

| Cost/1000 บท | ระยะเวลา | คุณภาพ |
|:------------:|:--------:|:------:|
| **ใน Go sub** | ~15 วัน | ✅✅ Thai ดี |
| **Zen ~$3** | (polish 100 บท/วัน) | |

**Qwen Plus 16,300 req limit → ไม่ต้องกังวลเลย**

#### 🥉 Tier 3: Budget (ประหยัดสุด — DeepSeek Only)

```yaml
2-step DS Flash:
  Step 1: deepseek-v4-flash → draft
  Step 2: deepseek-v4-flash → polish (self-polish)
```

| Cost/1000 บท | ระยะเวลา | คุณภาพ |
|:------------:|:--------:|:------:|
| **ใน Go sub** | ~5 วัน | ✅ พอใช้ |
| **Zen ~$0.01** | | |

### Fallback Chain (เมื่อ model ถึง limit)

```
Primary Path:
  Draft:  deepseek-v4-flash (158k req)  → almost never hit
  Polish: qwen3.7-max      (4.3k req)  → HIT → fallback

Fallback Path (เมื่อ Qwen Max ถึง limit):
  1st: qwen3.7-plus         (16.3k req)  ✅ 
  2nd: deepseek-v4-pro      (17k req)    ✅
  3rd: kimi-k2.6            (5.7k req)   ✅
  4th: deepseek-v4-flash    (158k req)   ✅ (ประกัน)
```

### Tactical Switching (Batch-Level)

ไม่ต้องเปลี่ยนทั้งโปรเจกต์ — เปลี่ยนแค่ batch ปัจจุบัน:

```bash
# ถ้า Polish batch นี้ quality ไม่พอ
hermes config set model qwen3.7-max
# รัน polish batch

# ถ้า Qwen Max ติด limit → ลด level
hermes config set model qwen3.7-plus
# รัน polish batch ต่อ
```

### Hybrid Chapter Strategy

ไม่ต้องใช้ tier เดียวทั้งเรื่อง — **แยกตามความสำคัญของบท:**

```yaml
Chapter Type:
  ✅ บทสำคัญ (เปิดเรื่อง, ตอนจบ, เปิดตัวละครสำคัญ, plot twist):
    Draft:  deepseek-v4-flash
    Polish: qwen3.7-max            # ลงเงินกับตอนสำคัญ

  ✅ บททั่วไป (ฝึกวิชา, เดินทาง, เก็บสมุนไพร):
    Draft:  deepseek-v4-flash
    Polish: qwen3.7-plus           # พอใช้ได้

  ✅ บท filter (บรรยาย, ฟิลเลอร์):
    deepseek-v4-flash 2-step       # DS Flash polish เอง ไม่เปลือง Qwen
```

**สัดส่วนในนิยาย 1 เรื่อง (1,000 บท):**
```
บทสำคัญ:     100 บท  (10%)  → Qwen Max
บททั่วไป:    600 บท  (60%)  → Qwen Plus
ฟิลเลอร์:    300 บท  (30%)  → DS Flash 2-step

รวม Qwen Max usage:  100 req  (2.3% ของ limit) ✅
รวม Qwen Plus usage: 600 req  (3.7% ของ limit) ✅
```

### Request Budget Management

```yaml
Monthly Limit ($60 cap / model request limits):

DS Flash (158k req):
  Scout:        5     req  (0.003%)
  Names:        50    req  (0.03%)
  Draft:        1000  req  (0.6%)
  QC:           1000  req  (0.6%)
  DS Polish:    300   req  (0.2%)
  -------------------------------------
  Total:        2355  req  (1.5%)  ✅ เหลือเพียบ

Qwen Max (4.3k req):
  Polish สำคัญ:  100   req  (2.3%)  ✅
  (เหลือ 4,200 req สำหรับงานอื่น)

Qwen Plus (16.3k req):
  Polish ทั่วไป: 600   req  (3.7%)  ✅
```

### Daily Schedule (30 วัน จบ 1000 บท)

```yaml
เช้า (DS Flash Zone — Draft):
  07:00-09:00   Draft batch × 5 (34 บท)    → 100 req
  
บ่าย (Mix Zone):
  13:00-14:00   Polish batch × 5 (Qwen Max) → 4 บทสำคัญ
  14:00-16:00   Polish batch × 5 (Qwen Plus) → 30 บาทั่วไป
  
เย็น (DS Flash Zone — QC):
  18:00-19:00   QC batch × 5 (DS Flash)     → 34 บท
  
รวม/วัน: Draft 34 + Polish 34 + QC 34 = ~100 req
รวม 30 วัน: 3,000 req → 15% of DS Flash, 70% of Qwen Max ✅
```

### Profile + Model Integration

```yaml
translator profile:
  default_model: deepseek-v4-flash    # ใช้ทุกงานยกเว้น polish
  
  # เวลา polish → เปลี่ยน model ชั่วคราว
  workflow:
    draft:  hermes config set model deepseek-v4-flash
    polish: hermes config set model qwen3.7-max
    qc:     hermes config set model deepseek-v4-flash
```

### Architecture Diagram (Full)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRANSLATOR PROFILE                                │
│  model: deepseek-v4-flash (default)                                  │
│  skill: cn-th-novel-translation (auto-load)                          │
│  SOUL: Novel Translator Identity                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Pipeline Orchestrator (main session)                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  PHASE 1: SCOUT                                              │   │
│  │  ├─ model: deepseek-v4-flash                                 │   │
│  │  ├─ cronjob(background)                                       │   │
│  │  └─ output: raw/*.txt, chapters.json                         │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  PHASE 2: NAMES                                              │   │
│  │  ├─ model: deepseek-v4-flash                                 │   │
│  │  ├─ delegate_task(batch 20)                                  │   │
│  │  └─ output: proposed-names.json → user verify → glossary.json│   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  PHASE 3: TRANSLATE (Draft)                                  │   │
│  │  ├─ model: deepseek-v4-flash ← ถูกที่สุด + ENG แม่น          │   │
│  │  ├─ delegate_task ×5 parallel                                │   │
│  │  └─ output: translated/*-draft.md                            │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  PHASE 4: POLISH                                             │   │
│  │  ├─ model: qwen3.7-max (สำคัญ) / qwen3.7-plus (ทั่วไป)      │   │
│  │  │         / deepseek-v4-flash (ฟิลเลอร์)                     │   │
│  │  ├─ delegate_task ×5 parallel                                │   │
│  │  └─ output: translated/*.md                                  │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  PHASE 5: QC                                                 │   │
│  │  ├─ model: deepseek-v4-flash                                 │   │
│  │  ├─ delegate_task ×5 parallel                                │   │
│  │  └─ output: qc-report/*.md                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Summary Decision Tree

```
เป็นสมาชิก OpenCode Go ($10/เดือน) หรือไม่?
├── ใช่ → ใช้ Tier 1 (Qwen Max polish) 
│         → $10/เดือนแปลได้ 1000+ บาท
│         → แค่ระวัง Qwen Max 4.3k req = ~30 วัน
│         → ถ้าเกิน → Fallback Qwen Plus
│
└── ไม่ → ใช้ Zen pay-per-token
        ├── งบ $3/1000 บาท → Tier 2 (Qwen Plus)
        └── งบ $0.01/1000 บาท → Tier 3 (DS Flash)
```

### Key Takeaways

| หลักการ | คำอธิบาย |
|---------|---------|
| **1 model ≠ 1 workflow** | Scout/Names/Draft/QC → DS Flash, Polish → Qwen |
| **Polish คือ bottleneck** | ลงเงินกับ polish เพราะตรงนี้決定คุณภาพไทย |
| **Fallback chain เสมอ** | Qwen Max → Plus → Pro → Flash |
| **Hybrid ตามความสำคัญ** | บทสำคัญ Qwen Max, บททั่วไป Qwen Plus, ฟิลเลอร์ Flash |
| **Request budget monitor** | 4.3k/เดือนของ Qwen Max → วางแผนดีๆ |
| **Profile translator** | default DS Flash → เปลี่ยนเฉพาะตอน polish |

---

## 🤖 Agent Pipeline (Multi-Agent Architecture)

ออกแบบมาให้ลด context waste + เพิ่มความเร็ว โดยแยกงานเป็น agent ย่อย orchestrate ด้วย Hermes `delegate_task` + `cronjob`

```ascii
┌──────────────────────────────────────────────────────────┐
│              Hermes Main Session (Orchestrator)           │
│  — ควบคุม pipeline ทั้ง 5 Phase                           │
│  — รอ user verify Names                                  │
│  — สั่ง translate/polish/QC แบบ parallel                  │
└────┬──────┬──────┬──────┬──────┬─────────────────────────┘
     │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│Scout│ │Names│ │Trans│ │Polish│ │ QC  │
│Agent│ │Agent│ │Agent│ │Agent │ │Agent│
│ ×1  │ │ ×1  │ │ ×5  │ │ ×5   │ │ ×5  │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘
```

### Phase 1: Scout Agent

ใช้ `cronjob` หรือ `terminal(background)` — ทำงานนาน, ทำครั้งเดียวจบ:

```bash
cronjob(
  action="create",
  name="novel-scout",
  schedule="once",  # รันครั้งเดียว
  prompt=""
  คุณคือ Scout Agent
  ไปที่ https://wtr-lab.com/en/novel/3463/the-portal-of-wonderland
  1. เช็คจำนวนบททั้งหมด
  2. ดึงทุกบท → บันทึกเป็น raw/ch001.txt ถึง chXXX.txt
  3. ถ้ามี CN → ดึง raw-cn/ch001.txt...
  4. สร้าง chapters.json { total, extracted, missing }
  5. รายงานผลกลับมา
  "",
  skills=["cn-th-novel-translation"],
  model="deepseek-v4-flash"
)
```

หรือถ้าอยากรันใน background session:

```bash
terminal(
  command="hermes -s cn-th-novel-translation -q 'scout novel 1131 chapters from WTR-LAB'",
  background=true,
  notify_on_complete=true,
  timeout=600
)
```

### Phase 2: Names Extractor Agent

ใช้ `delegate_task` — scan 10-20 บทต่อครั้ง → ชน CN/ENG → เสนอไทย:

```markdown
delegate_task(
  goal=""
  อ่าน raw/ch001.txt ถึง raw/ch020.txt:
  1. สกัดชื่อตัวละครทั้งหมด (นับความถี่)
  2. ถ้ามี raw-cn/ → ชนชื่อ ENG ↔ CN
  3. CN → พินอิน → เสนอไทย ตาม references/pinyin-to-thai-conventions.md
  4. จัดกลุ่ม: protagonist / major / side / minor
  5. สรุปเป็นตาราง: ENG Name | Freq | CN | เสนอไทย | Role

  output เป็นไฟล์ proposed-names.json (รอ user verify ก่อน Phase 3)
  "",
  context="glossary.json template อยู่ที่ templates/glossary-template.json",
  toolsets=["terminal", "file"]
)
```

**ทำซ้ำ batch ละ 20 บทจนครบทุกบท → user verify ครั้งเดียว → glossary.json สมบูรณ์**

### Phase 3: Translate Agents (Parallel)

เมื่อ glossary.json verified → ใช้ `delegate_task` ส่งแปลทีละ 5 บท:

```markdown
# สั่ง translate batch
delegate_task(
  tasks=[
    {
      "goal": "อ่าน raw/ch001.txt → แปลไทย draft → บันทึก translated/ch001-draft.md",
      "context": "glossary.json มีอยู่ที่ ./glossary.json อ่านก่อนแปล ห้ามเดาชื่อเอง"
    },
    {
      "goal": "อ่าน raw/ch002.txt → แปลไทย draft → บันทึก translated/ch002-draft.md",
      "context": "ใช้ glossary.json เดียวกัน"
    },
    {
      "goal": "อ่าน raw/ch003.txt → แปลไทย draft → บันทึก translated/ch003-draft.md",
      "context": "ใช้ glossary.json เดียวกัน"
    },
    {
      "goal": "อ่าน raw/ch004.txt → แปลไทย draft → บันทึก translated/ch004-draft.md",
      "context": "ใช้ glossary.json เดียวกัน"
    },
    {
      "goal": "อ่าน raw/ch005.txt → แปลไทย draft → บันทึก translated/ch005-draft.md",
      "context": "ใช้ glossary.json เดียวกัน"
    }
  ],
  toolsets=["terminal", "file"],
  model="deepseek-v4-flash"
)
```

**ทำซ้ำ batch ละ 5 บท → 1000 บท = 200 batch → แต่ละ batch ใช้เวลาไม่กี่นาที**

### Phase 4: Polish Agents (Parallel)

หลังจาก draft ทั้งหมดเสร็จ → polish parallel:

```markdown
delegate_task(
  tasks=[
    {
      "goal": "อ่าน translated/ch001-draft.md → polish สำนวนไทย → บันทึก translated/ch001.md",
      "context": "ใช้กฎ: 1. ตัดของ 2. สลับคำซ้ำ 3. เปลี่ยนคำเชื่อม 4. ปรับบทสนทนา"
    },
    {
      "goal": "อ่าน translated/ch002-draft.md → polish → translated/ch002.md",
      "context": "ใช้กฎเดียวกัน"
    },
    # ... สูงสุด 5 tasks ต่อ batch
  ],
  toolsets=["terminal", "file"],
  model="qwen3.7-max"  # หรือ deepseek-v4-flash ถ้าประหยัด
)
```

### Phase 5: QC Agents (Parallel)

ตรวจ final ก่อน publish:

```markdown
delegate_task(
  tasks=[
    {
      "goal": ""
      QC บทที่ 1:
      - [ ] ชื่อตรง glossary?
      - [ ] ศัพท์เฉพาะตรง?
      - [ ] ไม่มี ENG ติด?
      - [ ] ภาษาไทยธรรมชาติ?
      บันทึกผลเป็น qc-report/ch001.md
      ""
    },
    # ... batch ละ 5-10 บท
  ],
  toolsets=["terminal", "file"],
  model="deepseek-v4-flash"
)
```

### 🏗️ Pipeline Orchestration (สั่งรันทีเดียว)

```markdown
## One-Shot Pipeline
1. Scout all chapters → chapters.json
2. Names extraction (batch 20) → proposed-names.json
   → WAIT: user verify names
   → user สร้าง glossary.json
3. Translate batch (batch 5) → drafts ทั้งหมด
4. Polish batch (batch 5) → finals ทั้งหมด
5. QC batch (batch 10) → reports ทั้งหมด
6. รายงานสรุป: แปลไป X/Y บท, error N, ชื่อใหม่ M
```

### ⚠️ Pipeline Constraints

| ข้อ | วิธีการ |
|----|--------|
| **delegate_task max concurrent** | 3 agents ต่อ user (configurable) |
| **แต่ละ agent ไม่มี memory** | ใส่ glossary + rules ใน `context` ทุกครั้ง |
| **Name consistency ข้าม batch** | verified glossary.json → agent ทั้งหมดใช้ร่วม |
| **Token/request limit** | DeepSeek Flash 158k req/เดือน → batch 5 agents × 200 batch = 1000 req = 0.6% ✅ |
| **Session timeout** | แต่ละ agent < 5 นาที → batch เล็กพอ |

### 📋 Pipeline Template (copy-paste ready)

```markdown
## สั่งรันทั้ง Pipeline สำหรับนิยายเรื่องใหม่

1. Scout:
   [cronjob หรือ terminal background]
   "scout novel จาก URL → ดึง raw ทั้งหมด"

2. Names:
   delegate_task (batch 10-20 บท) → เสนอชื่อ → ผม verify
   
3. Translate All:
   for batch in 1..total/5:
     delegate_task x 5 → draft
   
4. Polish All:
   for batch in 1..total/5:  
     delegate_task x 5 → final

5. QC:
   delegate_task x 5 → qc-report
   → แก้ของที่มีปัญหา
```

```
┌──────────────────────────────────────────────────────────┐
│  Phase 1: SCOUT  — เช็คบททั้งหมด 1-END + extract raw     │
├──────────────────────────────────────────────────────────┤
│  Phase 2: NAMES  — สกัดชื่อจาก raw ทั้งหมด → ชน CN/ENG  │
│              → verify ชื่อไทย → glossary.json สมบูรณ์    │
├──────────────────────────────────────────────────────────┤
│  Phase 3: TRANSLATE — ใช้ glossary เท่านั้น → ไม่มี       │
│              ชื่อใหม่กลางเรื่อง                           │
└──────────────────────────────────────────────────────────┘
```

### Phase 1: Scout (ตรวจบททั้งหมด + Extract Raw)

ก่อนแปลแม้แต่คำเดียว — ให้สแกนทั้งเล่มก่อน:

```markdown
## Scout Prompt
1. เช็คจำนวนบททั้งหมดของนิยายเรื่องนี้ (source URL หรือ file)
2. ดึงเนื้อหาทุกบท → บันทึกเป็น raw/ch001.txt, raw/ch002.txt...
3. ถ้ามีต้นฉบับจีนด้วย → บันทึกแยก raw-cn/ch001.txt, raw-cn/ch002.txt...
4. สร้าง chapters.json:
   { "total": 1131, "extracted": [1, 2, 3, ...], "missing": [], "last_check": "2026-06-27" }
```

```bash
# โครงสร้างเมื่อ Phase 1 เสร็จ
novels/my-novel/
├── raw/          # ENG ต้นฉบับ
│   ├── ch001.txt
│   ├── ch002.txt
│   └── ...
├── raw-cn/       # CN ต้นฉบับ (optional)
│   ├── ch001.txt
│   ├── ch002.txt
│   └── ...
└── chapters.json # index ทั้งหมด
```

### Phase 2: Names (สกัดชื่อจาก Raw ทั้งเล่ม → ชน CN/ENG → Verify)

อ่าน **ทุกบท** ก่อน → หาชื่อทั้งหมด → verify กับผู้ใช้ครั้งเดียว → glossary.json สมบูรณ์:

```markdown
## Name Extraction Prompt
อ่าน raw/ch001.txt ถึง chXXX.txt ทั้งหมด:
1. สกัดชื่อตัวละครทั้งหมด (นับความถี่ — ยิ่งถี่ยิ่งสำคัญ)
2. จัดกลุ่ม: protagonist / major / minor
3. ถ้ามี raw-cn/ → จับคู่ชื่อ ENG ↔ CN:
   - "Shi Mu" → 石牧 → พินอิน Shí Mù → ไทย: **ซือมู่** ✅
   - "Shi Ting" → 石亭 → พินอิน Shí Tíng → ไทย: **ซือถิง** ✅
4. ถ้าไม่มี CN → เสนอชื่อไทยจากพินอินที่คาดเดา → ให้ user verify
5. สรุปเป็นตารางเสนอ user:
```

**ตารางที่ Hermes เสนอให้ user verify:**

```
| ENG Name | Freq | CN (ถ้ามี) | เสนอไทย | Role | Verify |
|----------|------|-----------|---------|------|--------|
| Shi Mu   | 250  | 石牧       | ซือมู่   | main | ✅     |
| Shi Ting | 40   | 石亭       | ซือถิง   | side | ✅     |
| Jin Cheng| 15   | 成管事     | สจ๊วตเฉิง| side | ✅     |
| Fragrant | 20   | 香珠       | เซียงจู?| main | ? ต้องเลือก |
| Pearl    |      |           | หรือ หงซือ? |     |        |
```

**กติกา:**
- User verify **ครั้งเดียว** ก่อนเริ่ม Phase 3
- เมื่อ verify → glossary.json complete → **ห้ามเปลี่ยนชื่อระหว่างเรื่อง**
- ถ้าผ่านไป 20 บทแล้วเจอชื่อใหม่ → เพิ่มใน glossary และแจ้ง user

### Phase 3: Translate (ใช้ Glossary ที่ Verify แล้ว)

เมื่อ glossary.json สมบูรณ์แล้ว — เริ่มแปลโดยไม่ต้องกลัวชื่อเพี้ยน:

```markdown
อ่าน raw/chXXX.txt แปลไทย:
- ใช้ glossary.json เท่านั้น (ห้ามเดาชื่อใหม่เอง)
- ถ้าเจอชื่อที่ไม่อยู่ใน glossary → หยุด + ถาม user
- หลังแปล → self-review (section 12)
- อัพเดท chapters.json
```

**ข้อดีของ 3-Phase workflow:**
- ✅ ชื่อ consistent ทั้งเล่ม (ไม่ต้องแก้ย้อนหลัง)
- ✅ user verify **ครั้งเดียว** ไม่ใช่ทุกบท
- ✅ ถ้ามี CN + ENG → accuracy สูงสุด
- ✅ Phase 2 ใช้ token แค่ scan ไม่ต้องแปล
- ✅ Phase 3 smooth ไม่สะดุด

---

## Phase 1.5: Source Scout (Quick Chapter Scan)

สำหรับ web novel — ก่อน extract ต้องรู้ก่อนว่ามีกี่บท:

```markdown
## Source Scout Prompt
1. ไปที่ novel listing page
2. scan จำนวนบททั้งหมด
3. หา chapter links → บันทึกเป็น chapters.json
4. ระบุว่ามีบทใหม่ตั้งแต่ตรวจครั้งล่าสุดหรือไม่
5. ถ้ามี → ดึงเฉพาะบทใหม่ (ไม่ต้องทำซ้ำ)

# result example
{ "total": 1131, "latest_extracted": 3, "new_chapters": [4], "source": "https://wtr-lab.com/en/novel/3463/the-portal-of-wonderland" }
```

---

## เลือกโหมดตามต้นฉบับ

### โหมด A: ต้นฉบับจีน → ไทย
ใช้เมื่อมี text ภาษาจีนโดยตรง ต้องใช้ model ที่แม่นจีน
```bash
hermes model --provider openrouter --model anthropic/claude-sonnet-4
```

### โหมด B: ต้นฉบับอังกฤษ (ENG → TH) ← **แนะนำ**
ใช้เมื่อมี English translation อยู่แล้ว — **DeepSeek ที่ใช้อยู่ก็พอ** ไม่ต้องเปลี่ยน model
ข้อควรระวัง: ชื่อคน/สถานที่อาจถูกทับศัพท์ในแบบอังกฤษ → ต้องถอดกลับเป็นเสียงพินอินแล้วเขียนแบบไทย

## ขั้นตอนการทำงาน

### 1. ตั้งค่าโปรเจกต์
```bash
mkdir -p novels/<ชื่อเรื่อง>
cd novels/<ชื่อเรื่อง>
touch .hermes.md
```

ตัวอย่าง `.hermes.md` สำหรับโหมด B (ENG→TH):

```markdown
# แปลนิยาย ENG → TH

## ภารกิจ
คุณคือนักแปลนิยายจีนที่ถูกแปลเป็นอังกฤษอีกที
→ แปลกลับมาเป็นไทย ให้อ่านลื่นเหมือนนิยายไทย

## กฎการแปล
- แปลจากอังกฤษเป็นไทย语言的ธรรมชาติ อ่านลื่น
- **ชื่อตัวละคร:** ดูจาก spelling อังกฤษ → ถอดเป็นเสียงพินอิน → เขียนแบบไทย
  เช่น: Zhang Xiaofan → จางเสี่ยวฝาน, Lin Wan'er → หลินหวานเอ๋อร์
  ถ้าชื่อจีนที่ถูก Anglicized (เช่น "Dragon Emperor") → แปลความหมาย "จักรพรรดิมังกร"
- **ชื่อสถานที่/สำนัก:** แปลความหมาย
  เช่น: "Green Cloud Sect" → สำนักเมฆาเขียว, "Heavenly Court" → ราชสำนักสวรรค์
- **ศัพท์เฉพาะ:** ใช้แบบที่คนไทยเข้าใจ
  เช่น: "cultivation" → บำเพ็ญเซียน, "qi" → พลังชี่, "spiritual energy" → พลังปราณ
- ถ้าอังกฤษใช้คำทับศัพท์จีนอยู่แล้ว (เช่น "yin-yang", "dantian") → ใช้คำที่คนไทยรู้จัก
- รักษาอารมณ์ scene — ภาษาไทยต้องมีชีวิต
- อย่าเติมเนื้อความที่ไม่มี
- อ่านออกเสียงในใจก่อนส่ง — ต้องลื่นเหมือนคนไทยเขียน
```

### 2. เตรียมไฟล์ต้นฉบับ
```bash
raw/              # ต้นฉบับอังกฤษ (แต่ละบท)
translated/       # ผลลัพธ์ภาษาไทย
glossary.md       # (optional) เก็บรายชื่อกันลืม
```

### 2b. ดึงเนื้อหาจากเว็บ novel (WTR-LAB และที่คล้ายกัน)

สำหรับ WTR-LAB โดยเฉพาะ — ทุกคำนามเป็น inline button โครงสร้างซับซ้อน:

```javascript
// ใช้ browser_console expression เพื่อดึง content จริง
(() => {
  const containers = document.querySelectorAll('[class*="content"], [class*="chapter"], [class*="reading"], [class*="article"]');
  let text = '';
  for (const c of containers) text += c.innerText + '\n---\n';
  return text || document.body.innerText;
})()
```

**โฆษณาที่ต้องตัด:**
- "Biquge www.xbiquge.tw, the fastest update to the [title]!" → อยู่หลังชื่อบทเสมอ
- "(Haha, celebrating nationwide, new book released!!!)" → ป้ายผู้แต่ง
- "Problematic ad? Report it here" / "You can disable popup ads..." → UI junk
- "You can disable popup ads by becoming a contributor. Become a contributor"
- Navigation elements: "Prev / Next / Ch. X / 0.09% / Contents"

รายละเอียดเต็มๆ: ดู `references/wtr-lab-extraction.md`
สำหรับ model ทั้งหมดที่มีใน provider ปัจจุบัน: ดู `references/opencode-go-models.md`
สำหรับ Fine-Tuning model: ดู `references/fine-tuning-guide.md`
สำหรับ Translation Memory: ดู `references/translation-memory.md`

### 3. แปลทีละบท — Prompt สำหรับโหมด B (ENG→TH)
```
อ่าน raw/ch001.txt แล้วแปลไทย:
- บันทึกเป็น translated/ch001.md
- ชื่อตัวละคร: [ชื่ออังกฤษ] → [ชื่อไทยแบบพินอิน]
- ดู references/pinyin-to-thai-conventions.md สำหรับกฎถอดเสียง
- ถ้าไม่แน่ใจชื่อ ให้เสนอ 2-3 แบบให้เลือก
- หลังแปลเสร็จ list glossary ที่เจอในบทนี้
```

### 4. Bulk (หลายบทพร้อมกัน) — เหมาะกับ ENG→TH โดยเฉพาะ
เพราะ DeepSeek + bulk ไม่ต้องเปลี่ยน model:

```
ขอใช้ delegate_task แปล 3 บทพร้อมกัน:
1. raw/ch001.txt → translated/ch001.md
2. raw/ch002.txt → translated/ch002.md
3. raw/ch003.txt → translated/ch003.md
- ใช้กฎ name convention:
  - "Zhang" → จาง, "Li" → หลี่, "Wang" → หวัง
  - เคล็ดวิชา → แปลความหมาย
- แต่ละบทต้อง glossary ของตัวเองด้วย
```

### 5. จัดการ Glossary

#### 5a. Memory (session-crossing, เครื่องเดียว)
```markdown
memory(
  target="memory",
  action="add",
  content="ชื่อตัวละคร CN→TH: Zhang Xiaofan→จางเสี่ยวฝาน, Lin Wan'er→หลินหวานเอ๋อร์"
)

เช็คชื่อเก่าก่อนแปลบทใหม่:
session_search(query="Zhang Xiaofan") → ดูว่าเคยแปลไว้ยังไง
```

#### 5b. glossary.json (sync ข้ามเครื่อง — แนะนำ!)
สร้าง `glossary.json` ในโปรเจกต์ root — ใช้ Git sync ได้ ไม่ต้องพึ่ง memory:

```json
{
  "characters": {
    "Shi Mu": {
      "cn": "石牧",
      "pinyin": "Shí Mù",
      "th": "ซือมู่",
      "role": "protagonist",
      "first_seen": "ch001"
    },
    "Shi Ting": {
      "cn": "石亭",
      "pinyin": "Shí Tíng",
      "th": "ซือถิง",
      "role": "father",
      "first_seen": "ch001"
    },
    "Steward Cheng": {
      "cn": "成管事",
      "pinyin": "Chéng Guǎn Shì",
      "th": "สจ๊วตเฉิง",
      "role": "steward"
    }
  },
  "terms": {
    "Body Tempering": { "th": "บำเพ็ญกาย", "cn": "淬體", "note": "ฝึกกาย" },
    "Qi perception": { "th": "รับรู้พลังชี่", "cn": "氣感" },
    "True Qi": { "th": "พลังแท้จริง", "cn": "真氣" },
    "Meridians": { "th": "เส้นลมปราณ", "cn": "經脈" },
    "Qi Spirit Pill": { "th": "ยาชี่เทพ", "cn": "氣靈丹" },
    "Houtian / Acquired": { "th": "แปรธาตุ", "cn": "後天" },
    "Innate": { "th": "กำเนิด", "cn": "先天" }
  },
  "chapters": {
    "ch001": { "status": "done", "source": "raw/ch001.txt", "target": "translated/ch001.md", "word_count": 1200 },
    "ch002": { "status": "pending" }
  }
}
```

เวลาสั่ง Hermes แปลบทใหม่ — ให้อ่าน glossary.json ก่อน แล้วค่อยเริ่ม เพื่อ consistency ข้ามบท

### 6. 2-Step Workflow: แปล → Polish (Improve Quality ประหยัด Model)

แทนที่จะแปลรอบเดียว ให้แบ่งเป็น 2 steps — ช่วยให้สำนวนไทยดีขึ้น โดยใช้ token เพิ่มแค่ ~15%:

**Step 1 — Draft:** แปลตรงๆ เอาเนื้อหาครบ
```
อ่าน raw/ch001.txt
แปลเป็นไทย draft ยังไม่ต้องเกลา
ใช้ glossary จาก glossary.json (ถ้ามี)
บันทึกเป็น translated/ch001-draft.md
```

**Step 2 — Polish:** เกลาสำนวนให้เป็นไทย
```
อ่าน translated/ch001-draft.md
Polish ให้เป็นไทยธรรมชาติ:
- ตัดโครงสร้าง ENG (relative clause, passive voice)
- เปลี่ยนคำเชื่อม: แล้ว→ครั้น, ก็→จึง
- ปรับคำพูดตัวละครให้สมบทบาท
- แก้คำซ้ำซาก (ชายชราชุดน้ำเงิน→เขาผู้นั้น/อีกฝ่าย)
- ตรวจว่าไม่มีคำติด ENG
บันทึกเป็น translated/ch001.md
```

**Why 2-step?** Round 2 สั้นกว่า Round 1 หลายเท่า (input = draft ไม่ใช่ raw ทั้งบท)  
คุ้มค่ากว่าใช้ model แพงแปลทั้งรอบ

### 7. Parallel Chunked Translation (speed boost)

จาก `translate-book-parallel` บน hub — แบ่ง 1 บทเป็น chunks เล็ก → delegate_task แปลพร้อมกัน:

```markdown
บทที่ยาวมาก (5000+ words) → หั่นเป็น 3-4 chunks → ส่ง delegate_task แปล parallel

delegate_task(
  tasks=[
    {"goal": "แปลส่วนที่ 1 (ถึงย่อหน้า 'Come back in 3 days') → output_part1.md",
     "context": "ใช้กฎ: Shi Mu→ซือมู่, Body Tempering→บำเพ็ญกาย, ..."},
    {"goal": "แปลส่วนที่ 2 (จากย่อหน้า 'Steward Cheng...' ถึง 'Evening at grave') → output_part2.md",
     "context": "ใช้กฎเดียวกัน"},
    {"goal": "แปลส่วนที่ 3 (จาก 'Boxing practice' จบบท) → output_part3.md",
     "context": "ใช้กฎเดียวกัน"}
  ]
)
→ merge output_part*.md → translated/ch001.md
→ round 2: polish entire chapter
```

ข้อดี: เร็วกว่า 2-3x ไม่เปลือง context window  
ข้อควรระวัง: แต่ละ chunk เริ่มจาก zero context → ต้องใส่ glossary + rules ใน context

### 8. 3-Mode Quality Levels (จาก baoyu-translate)

| Mode | Token Cost | Quality | When |
|------|-----------|---------|------|
| **Quick** | ประหยัด | ได้ใจความ พลาดสำนวน | แปลคร่าว ยังไม่final |
| **Normal** | ปานกลาง | ใช้ glossary + ปรับโครงสร้าง vocab | รอบ draft ปกติ |
| **Refined** | ~2x | polish publication-ready | รอบ final |

Workflow จริง:
```
Quick: แปล raw → draft
Normal: ปรับ draft ใช้ glossary
Refined (เฉพาะบทสำคัญ): polish สำนวน + เช็คชื่อ + เช็ค timeline
```

### 9. Quality Assessment Checklist

หลังแปลจบทุกบท เช็ค:

- [ ] เนื้อหาครบทุกฉาก? (เทียบกับ raw)
- [ ] ชื่อตัวละคร consistent กับ glossary?
- [ ] ศัพท์เฉพาะตรงกัน?
- [ ] สุดท้าย polish: ไม่มีศัพท์ ENG ติด, ความเป็นไทย?
- [ ] ถ้ามี Chinese original → เช็คชื่อซ้ำ

### 10. Cron Job สำหรับ连载อัตโนมัติ
ถ้ามีนิยายที่อัพเดทเป็นตอนทุกวัน ตั้ง cron job ให้ Hermes ไปดึง + แปลอัตโนมัติ:

```
cronjob(
  action="create",
  name="webnovel-chapter-watch",
  schedule="every 12h",
  prompt="เช็คว่า https://novel-site.com/my-novel/chapter-{latest+1} มีเนื้อหาใหม่ไหม
    ถ้ามี → ดึงเนื้อหา → บันทึก raw/chXXX.txt
    → แปลไทย → translated/chXXX.md
    → อัพเดท glossary
    → รายงานผมว่าบทที่ XXX แปลเสร็จ"
)
```

## ความต่างระหว่าง โหมด A (จีน→ไทย) vs โหมด B (ENG→ไทย)

| หัวข้อ | โหมด A จีน→ไทย | โหมด B ENG→ไทย |
|--------|----------------|-----------------|
| Model ที่แนะนำ | Claude, GPT-4o, Gemini | DeepSeek ก็พอ (ใช้ตอนนี้ได้เลย) |
| การจัดการชื่อ | จีน→พินอิน→ไทยตรงๆ | อังกฤษ→ต้องเดาพินอิน→ไทย |
| ความแม่นยำ | ได้ต้นฉบับตรง ไม่ตกหล่น | อาจพลาด nuance ที่ต้นฉบับจีน |
| ความง่าย | ยาก — ต้อง model แม่นจีน | ง่าย — model ทั่วไปแปลอังกฤษ→ไทยแม่น |
| ข้อควรระวัง | 中文 idioms, 文言 | ชื่อที่ Anglicized อาจเพี้ยน |
| ราคา | แพงกว่า (Claude/GPT) | ถูก (DeepSeek) |

## Pitfalls / Tips

### พินอิน→ไทย — กับดักที่พบบ่อย (อ้างอิง full table: `references/pinyin-to-thai-conventions.md`)

| พินอิน | ❌ ผิด | ✅ ถูก | เหตุผล |
|--------|-------|-------|--------|
| Shi (ซือ) | ชื่อ / สื่อ | **ซือ** | shi- = retroflex → **ซ** ไม่ใช่ ส (สื่อ) ไม่ใช่ ช (ชื่อ) |
| Qi (ชี่) | ชี | ชี่ | qi- พินอินคือ ชี่ ไม่ใช่ ชี |
| Xi (ซี) | ชี/ซี่ | ซี | xi- = ซี ไม่ใช่ ชี |
| Zhi (จือ) | จี | จือ | zhi- = จือ ไม่ใช่ ซี |
| Yu (หยู) | ยู | หยู/ยฺหวี่ | yu = หยู, yue = เยว่ |
| Ang (อัง) | อ่าง | อัง | ang = อัง, not อ่าง |

⚠️ จำง่ายๆ: "Shi" ในพินอินออกเสียง **ซือ** (เหมือน สือ) — NEVER ชื่อ, ชี, หรือซี
⚠️ จำง่ายๆ: "Qi" คือ **ชี่** (มีไม้โท) — NOT ชี (สามัญ)

### โหมด B เฉพาะ
- **ชื่อที่ Anglicized** — "Woodcutter Zhang" → "Zhang คนตัดฟืน" ไม่ใช่ "Woodcutter" เป็นชื่อ ✗
- **ชื่อที่มี hyphen** — "Xiao-Yan" → เสี่ยวเหยียน (ไม่ใช่ เสี่ยว-ยาน)
- **ชื่อที่ English แผลง** — "Victor Zhang" → วิกเตอร์ จาง (Zhang ยังเป็น จาง) — อย่าลืมจีนนามสกุล
- **Name order** — จีน: นามสกุลขึ้นก่อน (Shi Mu = สือ มู่ = นามสกุล สือ, ชื่อต้น มู่)

### Vocabulary Traps (Common Mistakes)

#### "ยุทธศาสตร์" ≠ "ยุทธ์" — คำนี้พลาดบ่อยมาก
```diff
- ❌ สำนักยุทธศาสตร์  (ยุทธศาสตร์ = strategy / military science)
+ ✅ สำนักยุทธ์        (ยุทธ์ = martial arts)

- ❌ วิทยายุทธศาสตร์  
+ ✅ วิทยายุทธ์
```
**จำง่ายๆ:** ยุทธศาสตร์ = แผนการรบ (strategic) — ใช้ในกระทรวงกลาโหม  
ยุทธ์ = วิชาการต่อสู้ (martial) — ใช้ในนิยายกำลังภายใน  
"สำนักยุทธ์" = school of martial arts, NOT "school of strategy"

#### Interjection / Onomatopoeia Mapping
| ENG | ❌ ผิด | ✅ ถูก | เพราะ |
|-----|-------|-------|-------|
| Ahem! (ไอ) | แหะๆ | **อะแฮ่ม!** | แหะๆ = hesitating laugh, not clearing throat |
| Hmph! (snort) | ฮึม | **หึ!** | ฮึม = humming, หึ = contempt |
| Boom! (impact) | บูม | **โครม!** | บูม = too English-sounding |
| Whoosh! (speed) | วูบ | **วาบ!** | วูบ = faint/dizzy, วาบ = fast flash |
| Plop | ตูม | **ตุ๊บ** | ตูม = big splash, ตุ๊บ = small splash |

#### Time Expression — เช็คจาก CN เสมอ
| CN Idiom | ความหมาย | ✅ ไทย |
|----------|---------|--------|
| 一盞茶工夫 | ~15 นาที (เวลาจิบชา) | **เพียงชั่วเวลาจิบชา** |
| 一刻鐘 | 15 นาที (ทางการ) | **สิบห้านาที** หรือ **หนึ่งเค่อ** |
| 一柱香 | ~30 นาที (เวลาจุดธูป) | **ชั่วเวลาจุดธูป** |
| 半柱香 | ~15 นาที | **ครึ่งชั่วเวลาจุดธูป** |
| 一炷香 | ~30 นาที | **ชั่วเวลาจุดธูป** |

⚠️ **อย่าใช้ "15 นาที" แทน 一盞茶工夫** — ทำลายบรรยากาศจีน  
⚠️ ตรวจ EN "quarter of an hour" = 15 นาที, NOT 1 ชม. หรือ ครึ่งชม.

#### "นักศิลปะการต่อสู้" เป็นคำผิด
```diff
- ❌ นักศิลปะการต่อสู้ (Martial Artist)
+ ✅ ยอดฝีมือ / ผู้ฝึกยุทธ์
```
"นักศิลปะการต่อสู้" เป็นคำทางการ แปลตรงตัวจาก "martial artist" —  
ไม่ใช้ในนิยายไทยจีน ควรใช้ **"ยอดฝีมือ"** แทน

### ทั่วไป
- **อย่าแปลทั้งเล่มในรอบเดียว** — context window จำกัด, แปลทีละ 1-3 บท
- **ตรวจชื่อซ้ำ** — ใช้ `session_search(query="ชื่อ")` ก่อนแปลต่อ
- **DeepSeek ที่ใช้อยู่แปล ENG→TH ได้ดีอยู่แล้ว** — ลองก่อน ไม่ต้องรีบเปลี่ยน provider
- **เทียบกับต้นฉบับจีนถ้ามี** — ถ้าสงสัยชื่อ ให้หา raw Chinese ช่วยตรวจ
- **ตั้ง glossary ไว้ใน .hermes.md** — เปิด session ใหม่ใน path นั้น Hermes โหลดกฎให้อัตโนมัติ
- **ใช memory เก็บ glossary ข้าม session** — แต่ย้ำว่าต้อง verify ทุกครั้ง (memory อาจล้าสมัย)

### Time Accuracy (สําคัญ!)
- EN "a quarter of an hour" = 15 นาที (NOT ครึ่งชั่วโมง หรือ หนึ่งชั่วโมง)
- EN "half an hour" = ครึ่งชั่วโมง (30 นาที)
- EN "an hour later" = หนึ่งชั่วโมงต่อมา
- ⚠️ ตรวจเวลาใน EN ให้ดี — ตีความผิดเปลี่ยนความหมายของ scene

### Onomatopoeia / Interjection Accuracy
- "Ahem!" (clearing throat) = **"อะแฮ่ม!"** — NOT "แหะๆ" (แหะๆ = hesitating laugh)
- "Hmph!" (snort) = **"หึ!"** — NOT "ฮึม"
- "Boom!" (loud impact) = **"โครม!"** — NOT "บูม" (too English)
- "Whoosh!" (fast movement) = **"วาบ!"** — NOT "วูบ" (วูบ = faint/dizzy)

### Clean .md Format for EPUB
- บทแปลต้องมีแค่ **H1 header + เนื้อหา** — ไม่มี glossary/summary ติดท้ายบท
- ถ้าต้องการ glossary → เก็บแยกใน `glossary.json`
- .md ที่สะอาดเอาไปทํา EPUB ได้ทันที:
  ```bash
  pandoc translated/ch*.md -o novel.epub --toc
  ```

### ถอน ads จาก novel site
รูปแบบ site-by-site มีใน references/:
- WTR-LAB → references/wtr-lab-extraction.md
- Biquge / xbiquge → มี "Biquge www.xbiquge.tw" ad หลังชื่อบทเสมอ

## 🔀 3-Way Workflow: CN + EN + TH (Robust Translation)

**Best practice:** ใช้ทั้ง 3 แหล่งเพื่อ quality สูงสุด

```diff
- ก่อน: EN raw → แปลไทย → polish (100% effort)
+ หลัง: TH base + EN verify + CN ตรวจชื่อ → polish (20% effort)
```

```
WTR-LAB /en/  ─→ EN (Gemini-enhanced translation)
WTR-LAB /th/  ─→ TH (Gemini-only translation, พอใช้เป็น base)
czbooks.net   ─→ CN (ต้นฉบับจริง ใช้ verify ชื่อ)
```

### Three-Way Comparison Table

| 源头 | CN (czbooks) | EN (WTR-LAB) | TH (WTR-LAB Gemini) | ✅ ของเรา |
|------|-------------|--------------|-------------------|---------|
| **ชื่อตัวเอก** | 石牧 | Shi Mu | ชิมู่ ❌ | **ซือมู่** ✅ |
| **พ่อ** | 石亭 | Shi Ting | ชิติง ❌ | **ซือถิง** ✅ |
| **สจ๊วต** | 成管事 | Steward Cheng | ผู้ดูแลเฉิง | **สจ๊วตเฉิง** ✅ |
| **ตระกูล** | 金家 | Jin Family | ตระกูลจิน | **ตระกูลจิ้น** |
| **วิชา** | 淬體 | Body Tempering | ฝึกฝนร่างกาย / ENG ค้าง | **บำเพ็ญกาย** |
| **ยศ** | 武者 | Martial Artist | นักศิลปะการต่อสู้ ❌ | **ยอดฝีมือ** ✅ |
| **ยา** | 氣靈丹 | Qi Spirit Pill | ยาเม็ดพลังปราณ | **ยาชี่เทพ** |
| **แคว้น** | 大齊 | Great Qi | ต้าฉี | **ราชวงศ์ฉีใหญ่** |

### Workflow

```
Phase 1: Scout
├── raw-cn/ch001.txt  ← czbooks.net (CN ต้นฉบับ)
├── raw-en/ch001.txt  ← WTR-LAB /en/ (Gemini EN)
└── raw-th/ch001.txt  ← WTR-LAB /th/ (Gemini TH base)

Phase 2: 3-Way Names
├── CN → verify ชื่อจริง (石牧 → ซือมู่, NOT ชิมู่)
├── EN → จับคู่ชื่อ ENG (Shi Mu)
├── TH → สังเกตใช้ผิด
└── glossary.json → ใช้ CN verification

Phase 3: Translate/Polish
├── ใช้ raw-th เป็น base → แก้ชื่อ + ศัพท์
├── CN ตรวจชื่อ
├── EN ตรวจความหมาย
└── polish เป็นไทยธรรมชาติ

Phase 4: QC (Self-Review)
├── ชื่อตรง CN?
├── ความหมายตรง EN?
└── ภาษาไทยเนียน?
```

### Prompt 3-Way Translation

```markdown
3-Way Polish บทนี้:

1. อ่าน raw-cn/ch001.txt  → ดูชื่อจีนจริง + ศัพท์
2. อ่าน raw-en/ch001.txt  → ดูความหมาย ENG
3. อ่าน raw-th/ch001.txt  → base ภาษาไทย

แก้ไข:
- แก้ชื่อจากต้นฉบับ CN (NOT ชิมู่ → ซือมู่)
- แก้ศัพท์เฉพาะ (NOT นักศิลปะการต่อสู้ → ยอดฝีมือ)
- polish สำนวนไทยให้เนียนขึ้น
- ใช้ glossary.json เป็น reference

บันทึกเป็น translated/ch001.md
```

### Fresh Setup Guide (เครื่องใหม่ / Profile ใหม่)

```bash
# ===== 1. ติดตั้ง Hermes =====
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# ===== 2. ตั้งค่า API key =====
# ถ้าใช้ OpenCode Go:
hermes auth add opencode-go   # หรือใส่ OPENCODE_GO_API_KEY ใน .env

# ===== 3. ดึง Skill จาก GitHub =====
git clone https://github.com/0xstillb/hermes-novel-translator.git /tmp/htranslator
cp -r /tmp/htranslator ~/.hermes/skills/custom/hermes-novel-translator
hermes skills list   # ตรวจสอบ

# ===== 4. สร้าง Profile =====
hermes profile create translator --clone --description \
  "Novel CN→TH translator. Default: DS Flash. Polish: Qwen Max"
  
# ===== 5. ตั้งค่า Profile =====
hermes --profile translator config set model deepseek-v4-flash
hermes --profile translator config set skills.default '["hermes-novel-translator"]'

# 6. แก้ไข SOUL.md identity
cat > ~/.hermes/profiles/translator/SOUL.md << 'EOF'
# Novel Translator Profile
คุณคือนักแปลนิยายจีน → ไทย
ใช้ pipeline 5 Phase, glossary ก่อนเริ่มทุกครั้ง
EOF

# ===== 7. ทดสอบ =====
translator chat
# หรือ
hermes --profile translator

# ===== 8. (Optional) Sync project =====
git clone <novel-repo-url> ~/novels/<ชื่อเรื่อง>
cd ~/novels/<ชื่อเรื่อง>
cp ~/.hermes/skills/custom/hermes-novel-translator/templates/glossary-template.json ./glossary.json
touch .hermes.md
```

### One-Liner Setup (copy-paste ready)

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash && \
git clone https://github.com/0xstillb/hermes-novel-translator.git /tmp/htranslator && \
cp -r /tmp/htranslator ~/.hermes/skills/custom/hermes-novel-translator && \
hermes profile create translator --clone && \
hermes --profile translator config set model deepseek-v4-flash && \
hermes --profile translator config set skills.default '["hermes-novel-translator"]' && \
echo "✅ พร้อม! ใช้: translator chat"
```

### After Setup — สั่งงานแรก

```bash
translator chat -q "
สวัสดี นี่คือ translator profile ใช่มั้ย?
โหลด skill hermes-novel-translator แล้วหรือยัง?
"
```

ย้ายโปรเจกต์ + skill ไปอีกเครื่อง:

```bash
# 1. ติดตั้ง Hermes (ทุก OS)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 2. ถ้า skill ถูก publish → install จาก hub
hermes skills install cn-th-novel-translation

# หรือถ้ายังไม่ publish → copy ตรงๆ
cp -r ~/.hermes/skills/custom/cn-th-novel-translation ~/Desktop/
# เครื่องใหม่
cp -r ~/Desktop/cn-th-novel-translation ~/.hermes/skills/custom/
hermes skills list   # verify

# 3. โอนโปรเจกต์ (ใช้ Git หรือ scp)
git clone <repo-url> ~/novels/the-portal-of-wonderland
# หรือ
scp -r user@old-machine:~/novels/the-portal-of-wonderland ~/novels/

# 4. ตั้งค่า model/provider
hermes model

# 5. ไฟล์ glossary.json + .hermes.md มากับโปรเจกต์ (sync ได้)
# แต่ memory ไม่มา → ต้อง rebuild โดยให้ Hermes อ่าน glossary.json
```

### Windows-Specific Notes

#### การติดตั้ง Hermes บน Windows
```powershell
# PowerShell (run as Admin)
winget install HermesAgent  # หรือใช้ scoop/choco
# หรือลงด้วย curl
curl -fsSL https://hermes-agent.nousresearch.com/install.ps1 | powershell -c -
```

#### Path differences
```powershell
# Hermes path บน Windows
%USERPROFILE%\.hermes\skills\custom\cn-th-novel-translation\
# หรือใช้ forward slash ก็ได้
C:/Users/B/.hermes/skills/custom/cn-th-novel-translation/

# โปรเจกต์
C:/Users/B/novels/the-portal-of-wonderland/
├── raw/
├── translated/
└── glossary.json
```

#### เปิดไฟล์ preview
```powershell
# แทน open (macOS) → ใช้ start (Windows)
start translated/ch001.md
```

#### Terminal differences
```powershell
# Unix: mkdir -p novels/{raw,translated}
# Windows PowerShell:
mkdir novels/raw, novels/translated -Force

# Unix: touch .hermes.md
# Windows PowerShell:
New-Item .hermes.md -Force
```

#### Chocolatey/Scoop (optional)
```powershell
# ถ้าติดตั้ง Git for Windows + Git Bash → ใช้คำสั่ง Unix ได้หมด
# แนะนำให้ใช้ Git Bash หรือ WSL สำหรับ workflow นี้
```

#### Hermes Desktop App บน Windows
- มี GUI เหมือน macOS version
- ปุ่ม Preview ใช้เปิดไฟล์ด้วย Notepad++ / VS Code / edge
- Terminal ในตัวใช้ PowerShell ได้

#### Note: WSL vs Native Windows
```powershell
# Hermes ทำงานได้ทั้งสองแบบ:
# - Native Windows PowerShell (cmd/pwsh)
# - WSL2 (Linux subsystem)

# WSL แนะนำเพราะคำสั่งตรงกับ Unix ทุกอย่าง
wsl --install ubuntu
# แล้วทำตามขั้นตอน Linux ปกติ

# หรือใช้ Git Bash (มี Git for Windows)
# Git Bash รองรับ bash command ได้
```

แนะนำให้ใช้ Git เก็บทั้งโปรเจกต์ + glossary.json — `.hermes.md` ก็แชร์ข้ามเครื่องได้

### Model Cost-Benefit สำหรับแปลนิยาย ENG→TH

#### ถ้าใช้ opencode-go provider (20 models มีให้)
| Model | ไทย Quality | Cost | เหมาะกับ |
|-------|:---------:|:----:|---------|
| **qwen3.7-max** 🥇 | ✅✅ ดี | ปานกลาง | แปลรอบเดียว/ polish |
| **deepseek-v4-pro** | ✅ พอใช้ | กลาง | upgrade จาก flash |
| **qwen3.7-plus** 🥉 | ✅✅ ดี | ถูกกว่า max | ประหยัด+ดี |
| **kimi-k2.6** | ✅ พอใช้ | กลาง | จีน→ไทย |
| **minimax-m3** | ✅ | ถูก | ทั่วไป |
| **deepseek-v4-flash** (ปัจจุบัน) | ✅ พอใช้ | ถูกมาก | Draft |

รุ่น model ทั้งหมด: ดู `references/opencode-go-models.md`

#### ถ้าใช้ OpenRouter / provider อื่น
| Model | ไทย Quality | Cost | เหมาะกับ |
|-------|:---------:|:----:|---------|
| DeepSeek V4 Flash | พอใช้ | ถูกมาก | Draft ~$0.001/บท |
| Gemini 2.5 Flash | ✅ ดี | ถูก (บาง provider ฟรี) | Step 2 polish |
| Claude 3 Haiku | ✅✅ ดี | ~1/15 Sonnet | Polish |
| GPT-4o mini | ✅✅ ดี | ~1/10 GPT-4o | รอบเดียว |
| Claude Sonnet 4 | ✅✅✅ ดีสุด | ~10x DeepSeek | Final พิเศษ |
| GPT-4o | ✅✅✅ ดีสุด | ~15x DeepSeek | Final พิเศษ |

**กลยุทธ์สำหรับ opencode-go (ประหยัด + quality):**
```bash
# 1. DeepSeek V4 Flash แปล draft (ถูกสุดใน opencode-go)
hermes config set model deepseek-v4-flash
hermes chat -q "แปล raw/ch001 → draft"

# 2. Qwen 3.7 Max polish (multilingual ดีกว่า DeepSeek)
hermes config set model qwen3.7-max
hermes chat -q "อ่าน draft แล้ว polish สำนวนไทย"

# หรือลอง Qwen แปลรอบเดียวเลย
hermes config set model qwen3.7-max
hermes chat -q "อ่าน raw/ch001 → แปลไทย → บันทึก translated/ch001.md"
```

### Few-Shot Examples — Before/After

ให้ Hermes เห็นตัวอย่างก่อนเริ่มงานทุกครั้ง:

#### Example 1: Opening Description
```
EN: "Only fourteen years old, his skin was slightly dark red from years of exposure to the sea breeze, but he had thick eyebrows and large eyes, and was half a head taller than most peers."

❌ Before (แปลตรง):
อายุแค่สิบสี่ ผิวคล้ำเล็กน้อยจากลมทะเล แต่คิ้วหนาตาโตและสูงกว่าคนอื่นครึ่งหัว

✅ After (ไทยธรรมชาติ):
เขามีอายุเพียงสิบสี่ปีเท่านั้น ผิวแทนเข้มเพราะต้องลมทะเลมาหลายปี ภายใต้คิ้วหนา ตาโต รูปร่างสูงกว่าคนวัยเดียวกันเกือบครึ่งศีรษะ
```

#### Example 2: Dialogue + Emotion
```
EN: "'Hmph, no matter how eloquently you speak, it won't change the fact that he abandoned his wife. There's no need to say more,' the young man snorted coldly."

❌ Before:
"ฮึม ไม่ว่าคุณจะพูดเก่งแค่ไหน มันก็เปลี่ยนความจริงที่ว่าเขาทิ้งภรรยาไม่ได้  ไม่ต้องพูดอีก" ชายหนุ่มหัวเราะเย็นชา

✅ After:
"หึ! เจ้าจะพูดจางามเพียงใด ก็ไม่อาจลบความจริงที่เขาทิ้งแม่ข้าไปได้ทั้งนั้น ไม่ต้องกล่าวอีก" เด็กหนุ่มหัวเราะเยียบเย็น
```

#### Example 3: Action Scene
```
EN: "With a loud 'boom,' the tree shook, countless branches and leaves fell, and a half-inch deep fist print was clearly visible on the trunk."

❌ Before:
เสียง "บูม" ดัง ต้นไม้สั่น กิ่งและใบไม้ร่วงหล่น และรอยหมัดลึกครึ่งนิ้วปรากฏบนลำต้น

✅ After:
เสียง "โครม" ดังสนั่นหวั่นไหว ต้นไม้ใหญ่สั่นสะเทือน กิ่งใบปลิวร่วงหล่นเป็นจำนวนมาก รอยหมัดลึกครึ่งนิ้วปรากฏเด่นชัดบนลำต้น
```

#### Example 4: Character Reference (Avoid Repetition)
```
EN line 1: "The blue-shirted old man finally frowned upon hearing this."
EN line 2: "…" the blue-shirted old man revealed the greatest leverage.

❌ Before (ซ้ำ):
"ชายชราชุดน้ำเงิน..." "...ชายชราชุดน้ำเงิน..."

✅ After (สลับ):
"คนแก่ชุดน้ำเงินเริ่มขมวดคิ้ว..." "...เขาผู้นั้นเปิดไพ่ตาย..."
```

---

### Genre-Specific Term Base

ใช้เป็น reference เวลาแปล — เข้า genre ไหน ใช้ term นั้น:

#### Xianxia (仙侠 / เซียน)
| English | 中文 | ไทย |
|---------|------|------|
| cultivation | 修仙/修炼 | บำเพ็ญ / การฝึกปรือ |
| qi / spiritual energy | 灵气/真气 | พลังชี่ / ปราณ |
| foundation establishment | 筑基 | สร้างฐาน |
| core formation | 结丹 | ก่อเกิดแดนทอง |
| nascent soul | 元婴 | กำเนิดวิญญาณ |
| tribulation | 天劫 | ภัยเทพ / ฟ้าลิขิต |
| immortal | 仙人 | เซียน / อมตะ |
| spiritual root | 灵根 | กระดูกวิญญาณ |
| medicinal pill / elixir | 丹药 | ยาเม็ด / ยาวิเศษ |
| alchemist | 炼丹师 | นักปรุงยา |
| flying sword | 飞剑 | กระบี่บิน |
| jade slip / jade scroll | 玉简 | ม้วนหยก |
| divine sense / spirit sense | 神识 | สัมผัสวิญญาณ |
| realm / stage | 境界 | ขั้น / ระดับ |
| breakthrough | 突破 | ทะลวง / 突破 |
| secluded meditation | 闭关 | ปิดด่าน |

#### Wuxia (武侠 / กำลังภายใน)
| English | 中文 | ไทย |
|---------|------|------|
| inner strength / internal energy | 内力 | กำลังภายใน |
| martial arts | 武功 | วิทยายุทธ์ / ยุทธ์ (NOT ยุทธศาสตร์) |
| sect | 门派 | สำนัก |
| clan | 家族 | ตระกูล |
| master | 师父 | อาจารย์ |
| disciple | 弟子 | ศิษย์ |
| technique | 招式 | กระบวนท่า / วิชา |
| secret manual | 秘籍 | คัมภีร์ / ตำรา |
| qi deviation | 走火入魔 | พลังชี่พลิกผัน |
| light skill / lightness skill | 轻功 | วิชาเบาค้างฟ้า |
| palm strike | 掌法 | ฝ่ามือ |
| fist technique | 拳法 | กระบวนหมัด |
| sabre / blade | 刀 | กระบี่ (กว้าง) / ดาบ |
| sword | 剑 | กระบี่ |
| tournament | 比武大会 | ประลองยุทธ์ |
| envoy / messenger | 使者 | ทูต |
| elder | 长老 | ผู้อาวุโส |
| sect leader | 掌门 | เจ้าสำนัก |

#### Xuanhuan (玄幻 / แฟนตาซีจีน)
| English | 中文 | ไทย |
|---------|------|------|
| magic beast | 魔兽 | สัตว์อสูร / สัตว์เวท |
| spirit beast | 灵兽 | สัตว์วิญญาณ |
| dimension / plane | 位面 | มิติ / ภพ |
| artifact / magic weapon | 法宝 | อาวุธวิญญาณ |
| soul | 灵魂 | วิญญาณ |
| bloodline | 血脉 | สายเลือด |
| inheritance | 传承 | มรดก / การสืบทอด |
| ancient | 远古/上古 | โบราณกาล / ปฐมกาล |
| divine | 神 | ศักดิ์สิทธิ์ / ทวยเทพ |
| demon | 魔 | อสูร / มาร |
| undead | 亡灵 | อมนุษย์ |
| contract / pact | 契约 | สัญญา / พันธสัญญา |
| forbidden technique | 禁术 | วิชาต้องห้าม |
| barrier / formation | 阵法 | แผนผัง / อาคม |
| teleportation array | 传送阵 | แผนผังเคลื่อนย้าย |
| storage ring | 储物戒 | แหวนเก็บของ |

---

### Self-Review Protocol

หลังแปลจบทุกครั้ง Hermes ต้องตรวจสอบตัวเอง (ใช้ `references/thai-idiom-dict.md` เป็น reference):

```markdown
## Self-Review Checklist (Execute After Every Chapter)

Step 1 — Scan Names:
- scan ทั้งไฟล์ที่แปล → list ชื่อตัวละครทั้งหมด
- เทียบกับ glossary.json → มีชื่อไหนที่ตรงกัน?
- ถ้าไม่ตรง → ต้องแก้กลับ
- ถ้าเป็นชื่อใหม่ → แจ้ง user + เสนอให้เพิ่มใน glossary

Step 2 — Scan Terms:
- scan ศัพท์เฉพาะ → ใช้คำเดียวกันทั้งบท?
- มีคำ ENG ติดมาหรือเปล่า? (เช่น เรียก "pill" หรือ "meridian" ทิ้งไว้)

Step 3 — Scan Natural Flow:
- scan "ของ" → ตัดทุกตัวที่ไม่จำเป็น
- scan "พูด" → มีซ้ำเกิน 3 ครั้งหรือเปล่า? → สลับ
- scan "ชายชราชุดน้ำเงิน" → มีซ้ำเป็นหางว่าวไหม?
- scan ความยาวประโยค → มีประโยคที่ยืดแบบ ENG หรือเปล่า?

Step 4 — Final Read:
- อ่านออกเสียงในใจทั้งบท → ตรงไหนสะดุด?
- ตรงไหนยังฟังดูเป็น "คำแปล" อยู่? → แก้
```

### Name Extraction Pre-Processing

ก่อนแปล — ควรสกัดรายชื่อตัวละครจาก raw text ก่อนเสมอ:

```markdown
## Workflow: Name Extraction Pass

1. Scan raw text → list ชื่ออังกฤษทั้งหมด (นับความถี่)
2. สำหรับชื่อใหม่ที่มีความถี่สูง:
   a. เสนอตัวเลือก: "เจอชื่อ 'Chen' อยากให้ใช้ → เฉิน หรือ เฉิน?"
   b. หรือขอให้ user verify ทุกชื่อก่อนแปล
3. ถ้ามี Chinese original → เทียบชื่อ
4. เมื่อชื่อ verified → เริ่มแปล
5. หลังแปล → อัพเดท glossary.json

Prompt:
```
อ่าน raw/ch001.txt แล้ว list ชื่อตัวละครทั้งหมดที่เจอ
จัดกลุ่ม:
- Known (มีใน glossary.json แล้ว)
- New (ต้องเสนอผู้ใช้เลือก)
เสนอแบบนี้:
  Known: [ชื่อไทย], [ชื่อไทย]...
  New: "Chen" → เฉิน / สุย? / เจิน?
  New: "Liu" → หลิว / ลิ่ว?
```
```

#### โครงสร้างประโยค
- ✅ **ไทยธรรมชาติ:** "เขามีอายุสิบสี่ปี ผิวคล้ำ..." / "เมื่อครานั้น..."
- ❌ **อย่าลอก ENG:** "อายุแค่สิบสี่ ผิวคล้ำเล็กน้อย..." → ใช้ "มีอายุ", มีโครงสร้างแบบไทย
- ✅ ใช้คำเชื่อม: **เมื่อ...ก็, ครั้น..., ทว่า..., เวลานี้, ฝ่าย..., แล้ว...จึง**
- ✅ ใช้คำบอกเวลา: **ครานั้น, บัดนั้น, ยามนี้, ในขณะนั้น**
- ✅ **อย่าใช้คำว่า "ของ" เกินจำเป็น** — "สีหน้าของซือมู่" → "สีหน้าซือมู่"

#### บทสนทนา
- ผู้ใหญ่/เจ้านาย: **"เจ้า..."**, **"กระนั้นหรือ"**, **"หรือว่า"**
- คนรับใช้/ผู้น้อย: **"ขอรับ", "เจ้าค่ะ", "ข้าน้อย", "กระหม่อม"**
- ชาวบ้าน: **"นะ", "สิ", "หรอ", "จ้า"**
- หลากคำพูด: **"เอ่ย", "เอ่ยขึ้น", "ว่า", "ตอบกลับ", "ย้อน", "กล่าว"** — อย่าใช้ "พูด" ซ้ำ
- ✅ "..." → "..." หรือ **เปลี่ยนเป็น "ครู่หนึ่ง" / "นานเท่าใดไม่รู้"**

#### คำเลียนเสียง (Onomatopoeia)
| ENG | ไทย |
|-----|------|
| whoosh / flash | วาบ / ฟู่ / ปรู๊ด |
| boom | เปรี้ยง / โครม / ดังสนั่น |
| crack-crack | กร็อบแกร็บ |
| plop | ตุ๊บ / ตูม |
| splash | ซ่า / กระเซ็น |
| swish | ฟิ้ว |

#### การอ้างถึงตัวละคร — อย่าซ้ำ
- "the blue-shirted old man" → **"ชายชราสีน้ำเงิน" "คนแก่ชุดน้ำเงิน" "เขาผู้นั้น" "อีกฝ่าย" "สจ๊วตเฉิง"** (สลับ)
- "the young man" → **"ซือมู่", "อีกฝ่าย", "เขา", "เด็กหนุ่ม"** (สลับ)
- อย่าใช้วลียาวซ้ำกันทุกย่อหน้า — ทำให้เสียอรรถรส

### เช็คชื่อจาก Chinese Original (Critical Habit!)

ทุกครั้งที่แปลชื่อตัวละครจาก English source:

1. หา Chinese original ก่อน — czbooks.net แหล่งที่ใช้ได้ดี
2. ดูตัวจีนจริง → หาพินอิน → ถอดไทยตาม `references/pinyin-to-thai-conventions.md`
3. โดยเฉพาะชื่อพินอินที่ขึ้นต้น **sh** → **ซ** (retroflex), **q** → **ช** (aspirated), **x** → **ซ/ส** (alveolo-palatal)
4. ตัวอย่าง: "Shi Mu" อังกฤษ → เช็ค 石牧 → พินอิน Shí Mù → **ซือมู่** (NOT ชื่อมู่, NOT สือมู่)
5. Save ชื่อที่ verify แล้วใน glossary.json + memory

#### ตัวอย่างการตรวจสอบ
```
English says: "Shi Mu"
→ ค้นหา Chinese original (czbooks.net หรือ novel site) → 石牧
→ 石 = shí (sh = ซ) → ซือ
→ 牧 = mù → มู่
→ สรุป: ซือมู่
→ Verify: NOT ชื่อมู่ (sh- ≠ ch-), NOT สือ (s ≠ sh)
```

⚠️ **Don't guess pinyin from English spelling!**  
"Shi" ใน English สะกดแบบนี้ อ่านว่า ซือ — แต่ "Shi" ใน "Ship" อ่านว่า ชิ —  
คนละเสียงกัน ใช้ Chinese original เสมอ!
