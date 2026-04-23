# Public Web

โฟลเดอร์ `docs/` คือ source หลักของเว็บไซต์สาธารณะ `ku-president-profile` ที่ใช้สำหรับ deploy ขึ้น GitHub Pages

- หน้าแรกคือ `docs/index.html`
- หน้าเว็บหลักทั้งหมดที่ผู้ใช้เห็นอยู่ใน `docs/`
- บทความ archive ถูก build ออกมาเป็น static files ใต้ `docs/articles/`

## Current Structure

หน้าเว็บหลักที่มีอยู่ตอนนี้:

- `index.html`
  - landing page / entry point ของเว็บไซต์
- `context.html`
  - หน้า `บริบท`
- `roles.html`
  - หน้า `บทบาท`
- `goals.html`
  - หน้า `เป้าหมาย`
- `strategy.html`
  - หน้า `กลไก`
- `four-year-plan.html`
  - หน้า `แผนสี่ปี`
- `qa.html`
  - หน้า `ถาม-ตอบ`
- `about.html`
  - หน้า `แนะนำตัว`
- `articles.html`
  - หน้า index ของบทความทั้งหมด
- `article-browsing.html`
  - หน้า browse บทความแบบสำรวจหัวข้อ

บทความแต่ละเรื่องถูก build ออกมาอยู่ที่:

- `docs/articles/*.html`

asset ของเว็บอยู่ที่:

- `docs/assets/`

## Articles Workflow

ระบบบทความไม่ได้แก้ HTML ตรงเป็นหลัก แต่ใช้ data source กลางแล้ว build ออกมาเป็น static pages

source หลัก:

- `articles_data/articles.json`

script ที่เกี่ยวข้อง:

- `scripts/validate_articles.py`
- `scripts/build_articles.py`

workflow:

```bash
python3 scripts/validate_articles.py
python3 scripts/build_articles.py
```

ผลลัพธ์จะถูก update ที่:

- `docs/articles.html`
- `docs/articles/*.html`
- asset data ที่เกี่ยวข้องใน `docs/assets/`

## Local Preview

เปิดเว็บจาก `docs/`:

```bash
bash scripts/run_local.sh
```

แล้วเปิด:

```text
http://127.0.0.1:8000/
```

ถ้ามีการแก้ข้อมูลบทความ ให้ build ก่อนแล้วค่อยเปิดดู

## What To Check Before Publish

ก่อน publish จริง ควรเช็กอย่างน้อย:

- nav ของทุกหน้าหลักใน `docs/`
- metadata สำคัญ เช่น title / description / og image
- asset ที่อ้างถึงว่ามีอยู่จริง
- หน้า `articles.html` และหน้า article ที่เพิ่ง build
- `robots.txt` และ `sitemap.xml` ถ้ามีการเปลี่ยนโครงหน้า

## Notes

- ถ้าจะประเมินสถานะของเว็บหลัก ให้ยึด `docs/` เป็นหลัก
- ของในโฟลเดอร์อื่นอาจเป็น source note, tooling, หรืองานประกอบ แต่ไม่ใช่ตัวเว็บ public โดยตรง
