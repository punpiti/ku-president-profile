# Public Web

โฟลเดอร์ `vision/public-site/` คือ source หลักของเว็บไซต์สาธารณะ `ku-president-profile`
deploy artifact จะถูกสร้างชั่วคราวที่ `.public-site-build/` แล้ว publish ไปที่ branch `gh-pages`

- หน้าแรกคือ `vision/public-site/index.html`
- หน้าเว็บหลักทั้งหมดที่ผู้ใช้เห็นอยู่ใน `vision/public-site/`
- บทความ archive ถูก build ออกมาเป็น static files ใต้ `vision/public-site/articles/`

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

- `vision/public-site/articles/*.html`

asset ของเว็บอยู่ที่:

- `vision/public-site/assets/`

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

- `vision/public-site/articles.html`
- `vision/public-site/articles/*.html`
- asset data ที่เกี่ยวข้องใน `vision/public-site/assets/`

## Local Preview

เปิดเว็บจาก source:

```bash
bash scripts/run_local.sh public
```

แล้วเปิด:

```text
http://127.0.0.1:8000/
```

ถ้ามีการแก้ข้อมูลบทความ ให้ build ก่อนแล้วค่อยเปิดดู

## What To Check Before Publish

ก่อน publish จริง ควรเช็กอย่างน้อย:

- nav ของทุกหน้าหลักใน `vision/public-site/`
- metadata สำคัญ เช่น title / description / og image
- asset ที่อ้างถึงว่ามีอยู่จริง
- หน้า `articles.html` และหน้า article ที่เพิ่ง build
- `robots.txt` และ `sitemap.xml` ถ้ามีการเปลี่ยนโครงหน้า

## Notes

- ถ้าจะประเมินสถานะของเว็บหลัก ให้ยึด `vision/public-site/` เป็นหลัก
- ก่อน deploy ให้รัน `bash scripts/build_public_site.sh` หรือ `bash scripts/deploy_github_pages.sh` เพื่อ build artifact และตรวจ safety gate
- ของในโฟลเดอร์อื่นอาจเป็น source note, tooling, หรืองานประกอบ แต่ไม่ใช่ตัวเว็บ public โดยตรง
