# Translation Memory สำหรับนิยายจีน → ไทย

## คืออะไร
TM เก็บประโยคที่แปลแล้ว → เวลาเจอประโยคเดิมในบทอื่น → ใช้คำแปลเดิม → consistent ทั้งเรื่อง

## วิธีใช้

### 1. สร้าง translation-memory.json ในโปรเจกต์ root

```json
{
  "phrases": {
    "a cold glint flashed through his eyes": {
      "th": "แววตาเยียบเย็นวาบผ่าน",
      "first_seen": "ch001",
      "count": 12
    },
    "in the blink of an eye": {
      "th": "ชั่วพริบตา",
      "first_seen": "ch001",
      "count": 15
    },
    "his expression changed slightly": {
      "th": "สีหน้าแปรเปลี่ยนเล็กน้อย",
      "first_seen": "ch003",
      "count": 8
    },
    "before anyone could react": {
      "th": "ไม่ทันตั้งตัว",
      "first_seen": "ch005",
      "count": 6
    },
    "with a loud boom": {
      "th": "เสียงโครมดังสนั่น",
      "first_seen": "ch001",
      "count": 9
    }
  },
  "character_actions": {
    "Shi Mu cupped his fists": {
      "th": "ซือมู่ประสานมือคำนับ",
      "count": 3
    },
    "Shi Mu frowned slightly": {
      "th": "ซือมู่ขมวดคิ้วน้อยๆ",
      "count": 7
    },
    "Shi Mu fell silent": {
      "th": "ซือมู่นิ่งเงียบ",
      "count": 5
    }
  }
}
```

### 2. ก่อนแปลบทใหม่ — ให้ Hermes อ่าน TM

```markdown
## Workflow
1. อ่าน translation-memory.json — รู้ว่าประโยคซ้ำๆ เคยแปลว่ายังไง
2. อ่าน glossary.json — รู้ชื่อตัวละคร
3. แปล raw/chXXX.txt — ใช้ TM + glossary เป็น reference
4. หลังแปล — เพิ่มประโยคใหม่ที่เจอเข้า TM
```

### 3. ประโยคที่ควรเก็บ

| ควรเก็บ | ไม่ควรเก็บ |
|---------|-----------|
| ประโยคซ้ำที่เจอบ่อย (in the blink of an eye) | บทสนทนายาวเฉพาะตัวละคร |
| คำบรรยายท่าทาง (frowned, cupped fists) | บรรยายสิ่งของที่ไม่ซ้ำ |
| คำเชื่อมบอกเวลา/ลำดับ | ชื่อเฉพาะ (เก็บใน glossary.json) |
| คำอุทาน (Hmph!, Damn it!) | plot-specific content |

### 4. การสะสม TM (Auto)

หลัง QC แต่ละบท — ให้ Hermes scan หาประโยคที่ควรเก็บ:

```markdown
## หลัง QC บทนี้:
1. scan translated/chXXX.md → หาประโยคที่ควรเพิ่มใน TM
2. เช็ค TM → ถ้ายังไม่มี → เพิ่ม
3. ถ้ามี → update count
```

### ประโยชน์
- ✅ consistent ข้ามบท (ch001 ≠ ch050 สำหรับประโยคเดียวกัน)
- ✅ ลด workload ของ Hermes (ไม่ต้องคิดใหม่)
- ✅ สะสมไปเรื่อยๆ — ยิ่งแปลยิ่งเร็ว
