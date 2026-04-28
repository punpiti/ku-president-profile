# Scripts

สคริปต์ในโฟลเดอร์นี้ใช้เป็น repo-level entry point สำหรับหลาย workspace ใน repo นี้

- `vision/public-site/` = public website source
- `.public-site-build/` = local deploy artifact generated from `vision/public-site/`
- `vision/` = vision workspace

งาน `research-award-insights` แยกออกไปเป็นโปรเจคของตัวเองที่ `../research-award-insights` และมี run/deploy scripts แยกในโฟลเดอร์นั้น

ถ้าต้องการดูรายการโปรเจคแบบย่อ:

```bash
bash scripts/list_projects.sh
```

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

รัน local web server

public website source จาก `vision/public-site/`

```bash
bash scripts/run_local.sh public
```

vision Q&A portal:

```bash
bash scripts/run_local.sh vision
```

ถ้าไม่ใส่ target สคริปต์จะขึ้น help และลิสต์โปรเจคที่เลือกได้:

```bash
bash scripts/run_local.sh
```

กำหนดพอร์ตเองได้:

```bash
bash scripts/run_local.sh 9000
```

หรือระบุ target กับ port พร้อมกัน:

```bash
bash scripts/run_local.sh vision 9000
```

หรือใช้ environment variable:

```bash
PORT=9000 HOST=0.0.0.0 bash scripts/run_local.sh
```

target ที่รองรับตอนนี้:

- `public`, `public-site`, `site` -> `vision/public-site/`
- `public-build`, `deploy-artifact` -> `.public-site-build/`
- `vision`, `vision-qna`, `qna` -> `vision/`
- `question-bank`, `question_bank` -> `vision/question-bank/`
- `presentation-narrator`, `presentation_narrator` -> `vision/presentation-narrator/`
- relative path หรือ absolute path ของ directory ที่มี `index.html`

หมายเหตุ: งาน research award publish เป็น standalone GitHub Pages site ที่ `https://punpiti.github.io/research-award-insights/` ไม่ใช่ path ใต้ `ku-president-profile`

## GitHub Pages deployment

เช็กความพร้อมก่อน deploy:

```bash
bash scripts/deploy_github_pages.sh
```

คำสั่ง deploy จะ build `vision/public-site/` ไป `.public-site-build/` ผ่าน allowlist และรัน safety check ก่อนเสมอ

ถ้าพร้อมและต้องการ publish artifact ไป branch `gh-pages`:

```bash
bash scripts/deploy_github_pages.sh --push
```

สคริปต์ถูกออกแบบให้ใช้ได้บนหลายเครื่อง โดยอ้างอิง path จากตำแหน่งของสคริปต์เอง ไม่ผูกกับชื่อเครื่องหรือ path ตายตัว
