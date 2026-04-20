# Scripts

สคริปต์ในโฟลเดอร์นี้ใช้สำหรับรัน static web ใน repo นี้ โดยค่า default ยังเป็น public webpage จาก `docs/`

## Local development

ถ้ามีการแก้บทความใน data source กลาง ให้ build ก่อน:

```bash
python3 scripts/build_articles.py
```

ถ้าต้องการปรับชื่อรูปบทความให้ตรงกับ `slug` แบบอัตโนมัติ:

```bash
python3 scripts/migrate_article_images.py
```

สคริปต์จะ preview เฉพาะรายการที่เป็นรูปไม่แชร์กัน ถ้าต้องการเขียนไฟล์จริงให้ใช้:

```bash
python3 scripts/migrate_article_images.py --apply
```

ถ้าต้องการเก็บชื่อไฟล์เดิมไว้ด้วยและสร้างไฟล์ใหม่เพิ่ม:

```bash
python3 scripts/migrate_article_images.py --apply --copy
```

ตัว validator จะบังคับว่า:

- ถ้ารูปหลักของบทความไม่ถูกแชร์กับบทความอื่น ชื่อไฟล์ต้องเป็น `assets/<slug>.<ext>`
- `image` และ `image_index` ต้องชี้ไปยัง asset เดียวกัน
- ถ้าเป็นรูป shared image สามารถคงชื่อกลางไว้ได้

รัน local web server เพื่อดูเว็บจาก `docs/`

```bash
bash scripts/run_local.sh
```

ถ้าต้องการเปิด question bank:

```bash
bash scripts/run_local.sh qna
```

กำหนดพอร์ตเองได้:

```bash
bash scripts/run_local.sh 9000
```

หรือระบุ target กับ port พร้อมกัน:

```bash
bash scripts/run_local.sh qna 9000
```

หรือใช้ environment variable:

```bash
PORT=9000 HOST=0.0.0.0 bash scripts/run_local.sh
```

target ที่รองรับตอนนี้:

- `site` -> `docs/`
- `qna` หรือ `question_bank` -> `vision/qna/question_bank/`
- relative path หรือ absolute path ของ directory ที่มี `index.html`

## GitHub Pages deployment

เช็กความพร้อมก่อน deploy:

```bash
bash scripts/deploy_github_pages.sh
```

ถ้าพร้อมและต้องการ push branch ปัจจุบันขึ้น GitHub:

```bash
bash scripts/deploy_github_pages.sh --push
```

สคริปต์ถูกออกแบบให้ใช้ได้บนหลายเครื่อง โดยอ้างอิง path จากตำแหน่งของสคริปต์เอง ไม่ผูกกับชื่อเครื่องหรือ path ตายตัว
