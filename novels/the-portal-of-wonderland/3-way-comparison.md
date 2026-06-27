# 3-Way Comparison Demo: บทที่ 1

## ตัวอย่างเทียบ CN + EN + TH

```
CN (czbooks):        石牧
EN (WTR-LAB):        Shi Mu
TH (WTR-LAB Gemini): ชิมู่
✓ ของเรา:             ซือมู่  ← จาก CN 石 = shí → ซือ
```

```
CN:                  石亭
EN:                  Shi Ting
TH (WTR-LAB Gemini): ชิติง
✓ ของเรา:             ซือถิง
```

```
CN:                  成管事
EN:                  Steward Cheng
TH (WTR-LAB Gemini): ผู้ดูแลเฉิง
✓ ของเรา:             สจ๊วตเฉิง
```

```
CN:                  淬體
EN:                  Body Tempering
TH (WTR-LAB Gemini): ฝึกฝนร่างกาย (หรือค้าง ENG)
✓ ของเรา:             บำเพ็ญกาย
```

```
CN:                  武者
EN:                  Martial Artist
TH (WTR-LAB Gemini): นักศิลปะการต่อสู้
✓ ของเรา:             ยอดฝีมือ
```

```
CN:                  氣靈丹
EN:                  Qi Spirit Pill
TH (WTR-LAB Gemini): ยาเม็ดพลังปราณ
✓ ของเรา:             ยาชี่เทพ
```

## ตัวอย่างประโยค — 3-way เทียบ

### Opening Description
```diff
CN:  年紀不過十四的他，因為常年吹海風緣故，皮膚微微黑紅，但濃眉大眼

EN:  Only fourteen years old, his skin was slightly dark red from years of 
     exposure to the sea breeze, but he had thick eyebrows and large eyes

TH Gem: แม้จะอายุเพียงสิบสี่ปี ผิวของเขาก็มีสีแดงเข้มเล็กน้อยจากการสัมผัส
         ลมทะเลมานานหลายปี แต่เขาก็มีคิ้วหนาและดวงตาโต

✓ ของเรา: เขามีอายุเพียงสิบสี่ปีเท่านั้น ผิวแทนเข้มเพราะต้องลมทะเลมาหลายปี 
          ภายใต้คิ้วหนา ตาโต
```

### Shi Mu's refusal
```diff
CN:  "哼，你就算說的天花亂墜，也改變不了那人拋棄妻子的事情。不用再多說了。"

EN:  "Hmph, no matter how eloquently you speak, it won't change the fact 
      that he abandoned his wife. There's no need to say more."

TH Gem: "ฮึ่ม ต่อให้พูดจาไพเราะแค่ไหน ก็เปลี่ยนความจริงที่ว่าเขาละทิ้ง
          ภรรยาไปไม่ได้หรอก ไม่จำเป็นต้องพูดอะไรอีกแล้ว"

✓ ของเรา: "หึ! เจ้าจะพูดจางามเพียงใด ก็ไม่อาจลบความจริงที่เขาทิ้งแม่ข้าไป
           ได้ทั้งนั้น ไม่ต้องกล่าวอีก"
```

### Fist print on tree
```diff
CN:  "轟的一聲巨響，大樹一陣晃動，無數枝葉掉落而下，樹乾上赫然多出一個半寸深的拳印"

EN:  "With a loud 'boom,' the tree shook, countless branches and leaves fell, 
      and a half-inch deep fist print was clearly visible on the trunk."

TH Gem: "ต้นไม้สั่นสะเทือนด้วยเสียง 'ตูม' ดังสนั่น กิ่งก้านและใบไม้ร่วงหล่น
          นับไม่ถ้วน และรอยกำปั้นลึกครึ่งนิ้วก็ปรากฏให้เห็นชัดเจนบนลำต้น"

✓ ของเรา: "เสียง 'โครม' ดังสนั่นหวั่นไหว ต้นไม้ใหญ่สั่นสะเทือน กิ่งใบ
           ปลิวร่วงหล่นเป็นจำนวนมาก รอยหมัดลึกครึ่งนิ้วปรากฏเด่นชัดบนลำต้น"
```

---

## สรุปข้อดี 3-Way Workflow

| แหล่ง | ใช้ verify อะไร |
|-------|----------------|
| **CN** 🔴 | ชื่อตัวละครที่ถูกต้อง, ศัพท์เฉพาะ (淬體≠ฝึกฝนร่างกาย) |
| **EN** 🔵 | ความหมายประโยค, context ที่หายไปใน TH |
| **TH** 🟢 | base ประโยคไทย (ประหยัดงานแปล 80%) |

### Workflow ใหม่

```
Phase 1: Scout
├── raw-cn/ch001.txt  ← czbooks
├── raw-en/ch001.txt  ← WTR-LAB /en/
└── raw-th/ch001.txt  ← WTR-LAB /th/

Phase 2: Names (3-way)
├── CN → verify ชื่อจริง (石牧 = ซือมู่)
├── EN → จับคู่ชื่อ ENG (Shi Mu)
├── TH → สังเกตว่า WTR-LAB ใช้ชื่ออะไร
└── glossary.json → ใช้ CN verification

Phase 3: Translate/Polish
├── ใช้ raw-th เป็น base (ประหยัด 80%)
├── ใช้ EN เช็คว่า TH พลาดความหมายตรงไหน
├── ใช้ CN แก้ชื่อ + ศัพท์ให้ถูก
└── polish เป็นไทยธรรมชาติ

Phase 4: QC
├── ชื่อตรง CN? (石牧→ซือมู่, NOT ชิมู่)
├── ความหมายตรง EN?
└── ภาษาไทยเนียน?
```
