# Category Report Template

ต้นแบบนี้เริ่มจากหน้าหมวด 1 `ด้านการบริหารทั่วไป` และถูกขยายใช้ครบทั้ง 7 หมวดแล้ว:

- หน้าเว็บ: `categories/<slug>.html`
- ข้อมูล: `data/categories/<slug>.json`
- สคริปต์สร้างข้อมูล: `scripts/build_category_report.py`
- กรอบวิสัยทัศน์: `data/vision_framework.json`
- ตัวแก้ข้อความไทยจาก PDF: `scripts/thai_pdf_cleaner.py`

Slug ที่ใช้:

1. `administration`
2. `academic-teaching`
3. `research-academic-service`
4. `student-development`
5. `human-resources`
6. `social-responsibility`
7. `revenue-generation`

## Data Pipeline

1. ใช้ `pdftotext -layout` เพื่อรักษาเลขหน้าและตำแหน่งใน PDF
2. ใช้ `pdftotext -raw` เป็นข้อความ override รายหมวด เพราะอ่านภาษาไทยได้ดีกว่า layout text ในหลายจุด
3. ผ่าน `thai_pdf_cleaner.py` เพื่อแก้คำเพี้ยนจาก PDF เช่น `ผู้นา -> ผู้นำ`, `จาเป็น -> จำเป็น`, `จากัด -> จำกัด`
4. แยกรายการ numbered items พร้อมเก็บ:
   - `document_item`: เลขข้อในเอกสาร
   - `page`: หน้า PDF
   - `sequence`: ลำดับรายการที่ parser แยกได้ในหมวด
   - `weight`: จำนวนอ้างอิง ใช้เลขในวงเล็บท้ายข้อ ถ้าไม่มีนับเป็น 1
   - `display` / `short_text`: ข้อความที่ clean แล้ว

## จำนวนอ้างอิง

ใช้คำว่า `จำนวนอ้างอิง` ทั้งหน้า

นิยาม:

> จำนวนอ้างอิง = จำนวนครั้งที่รายการนั้นแทนเสียงตอบใน PDF โดยใช้เลขในวงเล็บท้ายข้อ ถ้าไม่มีเลขในวงเล็บนับเป็น 1

ตัวอย่าง:

- `บริหารงานแบบธรรมาภิบาล... (46)` = จำนวนอ้างอิง 46
- ข้อที่ไม่มีวงเล็บ = จำนวนอ้างอิง 1
- การ์ดแสดงทั้ง `จำนวนอ้างอิงรวม` และ `จาก N ข้อ`

## Taxonomy ที่ใช้

ใน `scripts/build_category_report.py`

- `TOPIC_RULES`: tag/topic เช่น ธรรมาภิบาล, หลักสูตร, วิจัย, พัฒนานิสิต, บุคลากร, บทบาทต่อสังคม, รายได้
- `DESIRED_RULES`: ลักษณะพึงประสงค์ เช่น ซื่อสัตย์โปร่งใส, ยกระดับหลักสูตร, ผลักดันวิจัย, เข้าใจนิสิต, พัฒนาบุคลากร, สร้างรายได้
- `CONCERN_RULES`: ข้อกังวล เช่น ระบบพวกพ้อง, ขั้นตอนล่าช้า, หลักสูตรไม่ทันสมัย, งานวิจัยไม่ใช้ประโยชน์, สวัสดิการ, รายได้กระทบพันธกิจ
- `SENSITIVE_KEYWORDS`: ประเด็นละเอียดอ่อน
- `LESS_RELEVANT_KEYWORDS`: ประเด็นอื่นหรือหลุดจากโจทย์หมวดนั้น

ตอนนี้ใช้ rules กลางที่ครอบคลุมทั้ง 7 หมวด แต่ถ้าต้องการความแม่นยำสูงขึ้นควรแยก rules เฉพาะหมวดเป็น config ต่อไป

## Vision Alignment

ใช้ `data/vision_framework.json` เป็นกรอบกลาง แบ่ง 5 กลุ่ม 17 ข้อ:

1. บริบท 4 ข้อ
2. บทบาท 3 ข้อ
3. เป้าหมาย 3 ข้อ
4. กลยุทธ์ 3 ข้อ
5. แผนสี่ปี 4 ข้อ

ทุก evidence มี `vision_alignment` จาก keyword matching รอบแรก

ในหน้าเว็บ ส่วนวิสัยทัศน์ต้องเรียงจากบนลงล่าง:

`บริบท -> บทบาท -> เป้าหมาย -> กลยุทธ์ -> แผนสี่ปี`

## Page Structure

ลำดับ section ในหน้า `categories/<slug>.html`:

1. Header + metrics
2. `ลักษณะทั่วไปตามจำนวนอ้างอิง` เปิดไว้
3. `Sankey: เส้นทางการจัดกลุ่ม` เปิดไว้
4. `ลักษณะพึงประสงค์ของอธิการบดี` เปิดไว้
5. `ความสอดคล้องกับวิสัยทัศน์` เปิดไว้
6. `ข้อกังวล` ย่อไว้ตอนเปิดหน้า
7. `ประเด็นละเอียดอ่อน` ย่อไว้ตอนเปิดหน้า
8. `ประเด็นอื่น` ย่อไว้ตอนเปิดหน้า
9. `ตารางหลักฐานทั้งหมด` ย่อไว้ตอนเปิดหน้า

ทุกหัวข้อหลักใช้ `<details>` และเริ่มต้นตามสถานะด้านบน

## Card Behavior

การ์ดย่อยที่มีรายการอ้างอิง:

- ใน `ลักษณะพึงประสงค์ของอธิการบดี` และ `ความสอดคล้องกับวิสัยทัศน์` ให้เปิดรายการอ้างอิง 3 รายการตั้งแต่โหลดหน้า
- ส่วนอื่นเริ่มย่อรายการอ้างอิง
- เมื่อขยายแล้วมีปุ่ม:
  - `ยุบทั้งหมด`
  - `ดูน้อยลง` ทีละ 3 รายการ
  - `ดูเพิ่ม` ทีละ 3 รายการ
  - `ขยายทั้งหมด`

## Sankey

ใช้ `d3` + `d3-sankey` จาก CDN:

- `https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js`
- `https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js`

มี fallback renderer ถ้า CDN โหลดไม่ได้

Sankey ของทุกหมวดแสดงเฉพาะรายการที่เป็น `ลักษณะพึงประสงค์`

ลำดับ flow:

`หมวด -> tag/topic -> ลักษณะพึงประสงค์ -> วิสัยทัศน์`

เหตุผลของ flow นี้:

- `tag/topic` คือประเด็นที่สกัดจากข้อความความคิดเห็นก่อน
- `ลักษณะพึงประสงค์` คือการสรุปเชิงตีความจากความคิดเห็นของบุคลากร
- `วิสัยทัศน์` คือปลายทางสำหรับดูความสอดคล้องกับกรอบของ รศ.ดร.พันธุ์ปิติ เปี่ยมสง่า

ข้อกำหนด:

- ไม่แสดง node `ไม่พบความสอดคล้อง`
- ฝั่งวิสัยทัศน์ต้องเรียง `บริบท, บทบาท, เป้าหมาย, กลยุทธ์, แผนสี่ปี`
- ใช้ `จำนวนอ้างอิง` เป็น value ของ link
- จำกัด node บางชั้นเพื่อให้อ่านง่าย และรวมเป็น `อื่น ๆ` เมื่อจำเป็น
- มี header กำกับคอลัมน์ใน SVG:
  - หน้า index: `หมวด`, `tag/topic`, `ลักษณะพึงประสงค์`, `วิสัยทัศน์`
  - หน้าหมวด: `หมวดนี้`, `tag/topic`, `ลักษณะพึงประสงค์`, `วิสัยทัศน์`
- ไม่มีปุ่ม `ดูภาพใหญ่` แล้ว เพราะ fullscreen ทำให้ selection/link rendering ของ Sankey เพี้ยนในบางกรณี
- มีปุ่ม `ล้างการเลือก`
- ข้อความกำกับ node ต้องไม่หายเมื่อมี selection; ให้จางเฉพาะกล่อง/เส้นที่ไม่เกี่ยวข้อง ไม่ลด opacity ทั้ง node group

Default selection:

- หน้า index เลือก `เข้าใจนิสิตและพัฒนาคุณภาพชีวิต`
- หน้าหมวดเลือก `desired_characteristics[0].name` ของหมวดนั้น หรือ “ลักษณะพึงประสงค์ที่โดดเด่นที่สุดของหมวด”

การกระจายน้ำหนักเพื่อกันยอดพอง:

- `หมวด -> tag/topic`: กระจายตามจำนวน topic ของ evidence
- `tag/topic -> ลักษณะพึงประสงค์`: กระจายตามจำนวน desired tags ภายใต้ topic นั้น
- `ลักษณะพึงประสงค์ -> วิสัยทัศน์`: กระจายตามจำนวน desired tags และจำนวน vision alignment ของ evidence

## Visual Style

ใช้ `#006664` เป็นสีหลัก

ปรับแล้วในหมวด 1:

- header gradient โทนเขียวมิ้นต์
- H1, metric, button, tag ใช้ `#006664`
- card/panel มีสีพื้นอ่อนและ shadow
- bar chart ใช้ gradient หลายสี
- Sankey ใช้ palette สดขึ้น แต่ยังยึด `#006664` เป็นฐาน

## Files For Each Category

ไฟล์ที่สร้างแล้ว:

- `categories/administration.html`
- `categories/academic-teaching.html`
- `categories/research-academic-service.html`
- `categories/student-development.html`
- `categories/human-resources.html`
- `categories/social-responsibility.html`
- `categories/revenue-generation.html`

ทุกหน้าใช้ JavaScript เดียวกัน โดยอ่าน slug จากชื่อไฟล์และโหลด `../data/categories/<slug>.json`

เมื่อต้อง regenerate:

```bash
python3 scripts/build_category_report.py
python3 -m json.tool data/categories/<slug>.json >/tmp/check.json
node --check /tmp/extracted-inline-script.js
```

## Known Caveats

- Alignment กับวิสัยทัศน์ยังเป็น keyword matching รอบแรก ต้อง review ด้วยสายตา
- Cleaner เป็น dictionary-based ไม่ใช่ OCR เต็มรูปแบบ
- `document_item` ในเอกสารอาจซ้ำข้าม sub-section; จึงต้องแสดงคู่กับ `page` และ `sequence`
- จำนวนอ้างอิงไม่ใช่จำนวนคนโดยตรงเสมอไป แต่เป็น representation จากสรุป PDF ตามเลขในวงเล็บ

## Deploy Notes

ไฟล์ทดลอง/working copy อยู่ที่ `desired_qualifications/` แต่ไฟล์ source ที่ deploy จริงอยู่ที่:

`../vision/public-site/desired-qualifications/`

deploy artifact สร้างไว้ที่:

`../.public-site-build/desired-qualifications/`

เมื่อต้อง deploy:

1. sync change จาก `desired_qualifications/` ไปที่ `../vision/public-site/desired-qualifications/`
2. รัน `scripts/build_public_site.sh`
3. ตรวจ `node --check` สำหรับ JS ที่แก้
4. commit เฉพาะ `vision/public-site/desired-qualifications`
5. push `main`
6. publish `.public-site-build/` ไป branch `gh-pages`

deploy ล่าสุดหลังถอดปุ่ม fullscreen ของ Sankey:

- source commit `11b052f` - `Remove Sankey fullscreen control`
- deploy commit `a4a6e1b` - `Publish public site`
- public URL: `https://punpiti.github.io/ku-president-profile/desired-qualifications/`
