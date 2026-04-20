# Public Webpage

โฟลเดอร์นี้ใช้สำหรับเว็บไซต์สาธารณะที่จะ deploy ขึ้น GitHub Pages

- แยกจาก `vision/site/` โดยตั้งใจ
- ใช้ `docs/index.html` เป็นหน้าแรก
- เหมาะกับการตั้งค่า GitHub Pages ให้ publish จากโฟลเดอร์ `docs/`

## สถานะล่าสุด

- `index.html`
  - redesign เป็น landing page เชิงวิสัยทัศน์
  - ใช้เนื้อหา `Vision Part 1 -- Status`
  - มี splash / intro screen ตอนเข้าเว็บ
  - เมนูด้านบนตอนนี้คือ `บริบท / บทบาท / เป้าหมาย / กลยุทธ์ / แผนสี่ปี / บทความ / แนะนำตัว`
- `roles.html`
  - สร้างหน้า `บทบาท` แล้ว
  - มี 3 บทบาทเชิงยุทธศาสตร์
  - ใส่สไลด์จริงของบทบาท 1-3 แล้ว
  - บทบาท 3 มี thumbnail 3 รูปย่อย และกดดู popup รูปใหญ่ได้
- `goals.html`
  - สร้างหน้า `เป้าหมาย` แล้ว
  - ใช้รูป `goal-1-slide.JPG` ถึง `goal-3-slide.JPG` เป็นภาพหลักขนาดใหญ่
- `four-year-plan.html`
  - สร้างหน้า `แผนสี่ปี` แล้ว
  - ใช้รูป `4-year-plan-slide.JPG` เป็นภาพหลัก
- `articles.html`
  - สร้างหน้า `บทความ` แล้ว
  - ใช้เป็นพื้นที่รวมบทความและข้อเขียนประกอบวิสัยทัศน์
  - build จาก data source กลางด้วย `scripts/build_articles.py`
- `scripts/run_local.sh`
  - ใช้เปิด local dev server จาก `docs/` เป็นค่า default
  - ถ้าจะเปิดชุด question bank ให้ใช้ `bash scripts/run_local.sh qna`
- `scripts/deploy_github_pages.sh`
  - ใช้เช็กความพร้อมและ push ขึ้น GitHub Pages

## ไฟล์สำคัญตอนนี้

- `docs/index.html`
  - หน้า `บริบท` / landing page
- `docs/roles.html`
  - หน้า `บทบาท`
- `docs/goals.html`
  - หน้า `เป้าหมาย`
- `docs/four-year-plan.html`
  - หน้า `แผนสี่ปี`
- `docs/articles.html`
  - หน้า `บทความ`
- `articles_data/articles.json`
  - data source กลางของบทความทั้งหมด
- `scripts/build_articles.py`
  - build หน้า `articles.html` และ `docs/articles/*.html` จาก data source
- `docs/assets/role-1-slide.JPG`
- `docs/assets/role-2-slide.JPG`
- `docs/assets/role-3-slide.JPG`
- `docs/assets/goal-1-slide.JPG`
- `docs/assets/goal-2-slide.JPG`
- `docs/assets/goal-3-slide.JPG`
- `docs/assets/4-year-plan-slide.JPG`

## สิ่งที่ยังต้องทำต่อ

- สร้าง `docs/strategy.html`
  - ตอนนี้เมนู `กลยุทธ์` ยังไม่มีหน้า
- สร้าง `docs/about.html`
  - หน้า `แนะนำตัว` ยังไม่มี
- เติมข้อความย่อยของบทบาท 3 สำหรับ `3.1 / 3.2 / 3.3`
  - ตอนนี้มีรูปแล้ว แต่ยังไม่มี text อธิบายใต้แต่ละรูป
- พิจารณาว่าจะคง splash screen ไว้หรือไม่
  - ตอนนี้มี checkbox `ไม่แสดงอีกใน session นี้`
- ทบทวนข้อความ footer / disclaimer ก่อน deploy จริง
- ตรวจทุกเมนูและลิงก์ก่อน publish

## วิธีเปิดดูเว็บตอนนี้

ถ้ามีการแก้บทความ ให้ build ก่อน:

```bash
python3 scripts/build_articles.py
```

```bash
bash scripts/run_local.sh
```

แล้วเปิด:

```text
http://127.0.0.1:8000/
```
