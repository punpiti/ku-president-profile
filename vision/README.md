# Vision Workspace Map

โฟลเดอร์ `vision/` ถูกแยกเป็นบทบาทหลักเพื่อให้ดูแล้วรู้ทันทีว่าอะไรคือ source, อะไรคือ app/workspace, และอะไรคือ tool

## Topology

```text
vision/
  sources/   # เอกสารต้นทางและ material ที่ใช้สร้างงานต่อ
  public-site/             # source ของเว็บไซต์ campaign ที่ตั้งใจ public
  qna/       # portal/working surface ฝั่ง Q&A
  question-bank/           # generated Q&A bank
  presentation-narrator/   # markdown-driven slide narrator
  tools/     # generator และ utility script เฉพาะของ vision
```

## Folder Roles

### `sources/`

ใช้เก็บต้นฉบับ ไม่ควรเอา generated HTML มาปน

- `sources/drafts/` = draft ระหว่างทาง
- `sources/final/` = final documents
- `sources/outline/` = slide outline และโครง narrative
- `sources/presentation/` = presentation source assets
- `sources/qna_raw/` = Q&A ดิบ, transcripts, working source ก่อนแตกเป็น question bank
- `sources/idea_bank.md` = editable note source ของ vision workspace
- เอกสารสมัครและเอกสารสรรหาหลักที่ไม่ใช่ vision source โดยตรง ให้เก็บใน `selection/`

### App/workspace folders

ใช้เป็นพื้นที่ app/workspace ที่เปิดใช้งานจริง

- `index.html` = portal เข้าแต่ละ tool จาก root ของ `vision/`
- `public-site/` = source ของเว็บไซต์ public; build เป็น local artifact แล้ว publish ไป `gh-pages`
- `qna/index.html` = legacy/shortcut portal ฝั่ง Q&A
- `question-bank/` = generated Q&A bank
- `presentation-narrator/` = markdown-driven slide narrator

กติกา:

- อย่าเอา raw `.docx/.txt` มากองใน `qna/` root
- ถ้าเป็น source ใหม่ ให้ลง `sources/qna_raw/`

### `tools/`

script เฉพาะสาย vision

- `tools/build_site.py`
- `tools/build_qna_bank.py`
- `tools/populate_question_bank_options.py`

## Working Rules

1. ถ้าเป็นเอกสารต้นฉบับ ให้ใส่ใน `sources/`
2. ถ้าเป็นหน้าเว็บหรือ workspace ที่เปิดใช้ ให้ใส่เป็นโฟลเดอร์ระดับเดียวกับ `qna/`
3. ถ้าเป็น generator/utility ให้ใส่ใน `tools/`
4. อย่าแก้ generated HTML ตรง ถ้ามี source/generator รองรับอยู่แล้ว

## Common Entry Points

- Vision portal: `vision/index.html`
- Public site source: `vision/public-site/index.html`
- Q&A portal: `vision/qna/index.html`
- Question bank: `vision/question-bank/index.html`
- Presentation narrator: `vision/presentation-narrator/index.html`
