# WTR-LAB Novel Extraction Guide

WTR-LAB (wtr-lab.com) เป็น novel reading site ที่โครงสร้าง HTML ซับซ้อน:
- ทุกคำนามเป็น `<button>` clickable vocabulary
- เนื้อหาจริงซ่อนใน `<span>` + `<generic>` containers
- มีโฆษณาแทรก 3 จุด

## การดึง Content

### วิธีที่ 1: JavaScript extraction (แนะนำ)

ใช้ `browser_console` ใน Hermes:

```javascript
(() => {
  const containers = document.querySelectorAll(
    '[class*="content"], [class*="chapter"], [class*="reading"], [class*="article"]'
  );
  let text = '';
  for (const c of containers) text += c.innerText + '\n---\n';
  return text || document.body.innerText;
})()
```

### วิธีที่ 2: web_extract

ใช้งานได้บางส่วน — มักได้ summary สั้นๆ หรือเนื้อหาที่ถูกตัด
ใช้กับ WTR-LAB แล้วได้เฉพาะ Ch 1-3 summary

## โฆษณาที่ต้องตัด

ที่อยู่หลังเนื้อหา chapter เสมอ (มองจาก output text):

| รูปแบบโฆษณา | ตำแหน่ง |
|-------------|---------|
| `"Biquge www.xbiquge.tw, the fastest update to the [title]!"` | บรรทัดแรกหลังชื่อบท |
| `"(Haha, celebrating nationwide, new book released!!!)"` | ท้ายเนื้อหา ก่อน footer |
| `"Problematic ad? Report it here"` | ท้ายเนื้อหา |
| `"You can disable popup ads by becoming a contributor. Become a contributor"` | ท้ายเนื้อหา |
| `"Prev / Ch. X / 1131 / 0.09% / Next"` | ทั้ง header + footer nav |
| `"Web / Web+ / AI"`  | รูปแบบ reader toggle |

## Steps ที่แนะนำ

1. `browser_navigate(url)` → โหลดหน้า
2. `browser_console(expression=js_code)` → ดึง content
3. `write_file(path="raw/chXXX.txt")` → บันทึก raw (ตัด ads)
4. ตรวจเช็ค Chinese original ที่ czbooks.net ก่อนถอดชื่อไทย
5. `write_file(path="translated/chXXX.md")` → บันทึกบทแปล

## Site Pattern (Generic)

```yaml
URL Pattern: https://wtr-lab.com/en/novel/{novel_id}/{slug}/chapter-{n}
Chinese original (if available): https://czbooks.net/n/{id}/

Steps:
1. Get novel_id + total chapters from listing page
2. Download ch001..chN sequentially
3. Cross-reference Chinese original on czbooks.net for name verification
```
