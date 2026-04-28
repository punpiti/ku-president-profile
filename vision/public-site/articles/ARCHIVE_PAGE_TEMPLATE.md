# Archive Article Template

เอกสารนี้คือคู่มือการกรอก `articles_data/articles.json` และ build ออกมาเป็น static pages
สำหรับ archive บทความใน `docs/articles/`

ตอนนี้ workflow หลักไม่ใช่การแก้ HTML ตรง ๆ แล้ว แต่คือ:
1. เพิ่มหรือแก้ข้อมูลใน `articles_data/articles.json`
2. validate ข้อมูล
3. build ออกมาเป็น `docs/articles.html` และ `docs/articles/*.html`

## Workflow

ใช้ลำดับนี้ทุกครั้งเมื่อเพิ่มหรือแก้บทความ:

```bash
python3 scripts/validate_articles.py
python3 scripts/build_articles.py
```

หลังจากนั้นค่อยเปิดดูหน้าเว็บ:

```bash
bash scripts/run_local.sh
```

หมายเหตุเชิงสถาปัตยกรรม:
- ตอนนี้ builder ใช้ `full rebuild` ทุกครั้งโดยตั้งใจ
- เหตุผลคือการแก้บทความหนึ่งเรื่องอาจกระทบทั้งหน้า article ของตัวเอง, `articles.html`,
  `articles-data.js`, และ related articles ของเรื่องอื่น
- วิธีนี้ง่ายกว่าและปลอดภัยกว่าในช่วงที่จำนวนบทความยังไม่มาก
- ถ้าวันหน้าบทความเพิ่มขึ้นมากจริง ค่อยพิจารณา incremental build แบบระมัดระวัง

## โครงสร้างไฟล์

ฝั่งพัฒนาใช้ data source กลาง 1 ชุด และฝั่ง deploy จะถูก build ออกมาเป็น static HTML

โครงหลักตอนนี้:

1. ฐานข้อมูลบทความ
- path: `articles_data/articles.json`

2. script build
- path: `scripts/build_articles.py`

3. ไฟล์ผลลัพธ์สำหรับ deploy
- `docs/articles.html`
- `docs/articles/<slug>.html`

4. asset กลาง
- `docs/assets/archive-article.css`
- `docs/assets/articles-index.css`
- `docs/assets/archive-lightbox.js`
- `docs/assets/articles-data.js`

## โครงสร้างข้อมูลใน articles.json

แต่ละบทความเก็บข้อมูลหลักไว้ใน object เดียว เช่น:

- `slug`
- `page_title`
- `rewrite_title`
- `meta_description`
- `hero_subtitle`
- `category`
- `date`
- `source_url`
- `image`
- `image_index`
- `image_alt`
- `summary`
- `tags`
- `intro_paragraphs`
- `sections`
- `original_text`

`slug` คือ canonical id ของบทความ
- ต้องเป็น lowercase kebab-case
- ใช้เป็นชื่อไฟล์ output
- ใช้เป็น id ของ related articles
- ใช้เป็นตัวอ้างอิงหลักของระบบ

ข้อดีของวิธีนี้:
- แก้บทความจาก data เดียว
- generate หน้า article และ index ได้จาก source เดียว
- deploy ปลายทางยังเป็น static files

## การตั้งชื่อ

- `slug` ใช้ภาษาอังกฤษ kebab-case
- ชื่อไฟล์รูปควรสื่อความหมายและผูกกับบทความนั้น
- ถ้าเป็นภาพหลักของบทความ ให้ใช้ชื่อเดียวกับ `slug` เช่น `curriculum-llm-ep3.jpg`

ตัวอย่าง:
- article page: `docs/articles/curriculum-cycle-no-one-stops.html`
- image: `docs/assets/curriculum-cycle-no-one-stops.png`

## ข้อมูลที่ต้องเตรียม

ก่อนเพิ่มบทความใหม่ ให้เตรียม:

- `page title`
  - ใช้สำหรับ `<title>` และ title หลักของหน้า
- `rewrite title`
  - ใช้เป็นหัวข้อใหญ่ใน section `Rewritten Post`
- `hero subtitle`
  - สรุปสารของบทความ 2-4 บรรทัด
- `category`
  - เช่น `หลักสูตรและการเรียนรู้`
- `post date`
  - เก็บเป็น `YYYY-MM-DD`
  - ถ้าในโพสต์บอกว่า `4 วัน` ให้คำนวณย้อนจากวันปัจจุบันก่อน
- `tags`
  - ใช้ภาษาอังกฤษแบบสั้น เช่น `curriculum`, `governance`, `ai`
- `reference link`
  - ลิงก์ Facebook หรือแหล่งเดิม
- `original text`
  - เก็บตามต้นฉบับ อย่าแก้
- `image file`
  - ใช้รูปจากโพสต์หรือรูปที่เกี่ยวข้องกับบทความ

## Schema ที่ใช้อยู่ตอนนี้

แต่ละ article object ควรมี field เหล่านี้ครบ:

- `slug`
- `page_title`
- `rewrite_title`
- `meta_description`
- `hero_kicker`
- `hero_subtitle`
- `category`
- `date`
- `source_label`
- `source_url`
- `image`
- `image_index`
- `image_alt`
- `summary`
- `title_max`
- `subtitle_max`
- `tags`
- `intro_paragraphs`
- `sections`
- `original_text`

โครงของ `sections`:

```json
{
  "title": "หัวข้อย่อย หรือ null",
  "paragraphs": [
    "ย่อหน้า 1",
    "ย่อหน้า 2"
  ]
}
```

ข้อกำหนดสำคัญ:
- `tags` ต้องไม่ว่าง
- `intro_paragraphs` ต้องไม่ว่าง
- `sections` ต้องไม่ว่าง
- `source_url` ต้องเป็น URL จริง
- `image` และ `image_index` ต้องชี้ไปยังไฟล์ที่มีอยู่จริง

## Validator

validator อยู่ที่:
- `scripts/validate_articles.py`

validator จะเช็ก:
- slug ไม่ซ้ำ
- slug อยู่ในรูป kebab-case
- field ที่จำเป็นมีครบ
- type ของ field ถูกต้อง
- `date` เป็น `YYYY-MM-DD`
- `source_url` เป็น URL
- path ของรูปมีอยู่จริง
- `tags`, `intro_paragraphs`, `sections` ไม่ว่าง
- `sections[].paragraphs` มีแต่ข้อความที่ไม่ว่าง

ถ้า validator ไม่ผ่าน ห้าม build ต่อ

## โครงหน้า article ที่ build ออกมา

หน้า article ใช้ลำดับนี้:

1. `hero`
- `Archive`
- title หลักของหน้า
- hero subtitle
- pills:
  - หมวด
  - วันที่โพสต์
  - ที่มา
- tag row

2. `Rewritten Post`
- มี `rewrite title`
- ช่วงเปิดเรื่องเป็น `lead-split`
  - ซ้าย: รูป
  - ขวา: 1-2 ย่อหน้าแรก
- หลังจากนั้น เนื้อหาไหลเต็มความกว้าง
- ใส่ subtitle คั่นระหว่างช่วงสำคัญ
- ครอบคำสำคัญด้วย `<span class="key-term">...</span>`

3. `Original`
- แสดง `ลิงก์อ้างอิง:` บรรทัดเดียวกับปุ่ม Facebook
- เก็บข้อความต้นฉบับไว้ใน `<details>` และเริ่มแบบย่อ

4. `บทความอื่นที่เกี่ยวข้อง`
- ใช้ container ว่างสำหรับให้ JS เติมรายการอัตโนมัติจาก tag
- ต้องใส่ `data-current-slug` และ `data-current-tags`

## กติกาของ Rewritten Post

- ย่อหน้าแรก 1-2 ย่อหน้า ไม่ต้องมี subtitle
- หลังจากนั้น ถ้าบทความยาว ให้ใส่ subtitle คั่นเพื่อคุมจังหวะการอ่าน
- subtitle ควรเป็นประโยคที่ดึงความสนใจ ไม่ใช่ label แห้ง ๆ
- rewrite ต้องเรียบเรียงใหม่ให้เป็นภาษาเว็บ
- original ต้องเก็บตามต้นฉบับ

## กติกาของรูป

- รูปหลักใช้ใน 2 ที่:
  - หน้า article
  - thumbnail ใน `articles.html`

- หน้า article:
  - วางรูปไว้ซ้ายใน `lead-split`
  - คลิกรูปแล้วเปิด popup lightbox
  - ใส่ caption สั้น ๆ เช่น `คลิกรูปเพื่อดูภาพขยายใหญ่`

- หน้า `articles.html`:
  - ใช้รูปเดียวกันเป็น thumbnail
  - ใช้ `object-fit: contain`
  - ยอมให้มีขอบขาวเพื่อไม่ crop ภาพ

## กติกาของ Original

- ไม่ต้องมีข้อความเกริ่นยาว
- แสดงแค่:
  - `ลิงก์อ้างอิง:`
  - ปุ่ม Facebook ไอคอน `f`
  - กล่อง `<details>` ของ original

- ลิงก์ Facebook:
  - เปิดแท็บใหม่
  - ไม่แสดง URL ดิบ

## กติกาของ tag

tag ใช้เพื่อ:
- filter ภายหลัง
- หา related articles
- ช่วยจัดหมวดเชิงความคิด

แนวทางตั้ง tag:
- ใช้ lowercase
- ใช้ภาษาอังกฤษ
- 3-6 tag ต่อบทความ
- อย่าตั้ง tag ซ้ำซ้อนเกินไป

ตัวอย่าง:
- `curriculum`
- `governance`
- `resource-allocation`
- `university-reform`
- `teaching-and-learning`

## วิธีเพิ่มบทความใหม่

1. เพิ่ม object ใหม่ใน `articles_data/articles.json`

2. ระบุข้อมูลหลักให้ครบ
- title
- rewrite title
- category
- date
- tags
- image path
- source url
- summary
- rewritten content
- original content

3. validate

```bash
python3 scripts/validate_articles.py
```

4. build

```bash
python3 scripts/build_articles.py
```

5. ตรวจ 5 จุดสำคัญ
- รูปขึ้นทั้งใน article และ index
- lightbox เปิดได้
- ปุ่ม Facebook เปิดแท็บใหม่
- original เริ่มต้นแบบ collapse
- related articles แสดงผลจาก tag ได้

## จุดที่ควรทำต่อในอนาคต

- ถ้าต้องการแก้บทความแบบอ่านง่ายขึ้น ค่อยแยก rewritten/original ออกเป็นไฟล์ content ต่อบทความ
- ถ้ามีบทความมากขึ้นมาก ค่อยเปลี่ยนจาก JSON + Python script ไปเป็น markdown + generator เต็มรูปแบบ
- เพิ่ม schema version หรือ tag vocabulary กลางถ้าจำนวนบทความโตมาก

## ต้นแบบปัจจุบัน

ต้นแบบอ้างอิง:
- `docs/articles/curriculum-cycle-no-one-stops.html`
- `docs/articles.html`
