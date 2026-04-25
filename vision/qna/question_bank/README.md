# Q&A Question Bank README

ชุดนี้ใช้สำหรับเตรียมคำตอบสัมภาษณ์ / public hearing ของผู้สมัครอธิการบดี โดยแยกคำถามเป็นรายข้อ แล้วค่อย ๆ ขัดคำตอบให้คมขึ้นทีละหน้า

## เป้าหมาย

- เก็บคำถามสำคัญไว้เป็นรายข้อ
- ทำให้แต่ละข้อมีแกนคิดชัด และตอบได้จริงบนเวที
- แยก `logic หลังบ้าน` ออกจาก `ภาษาที่จะพูดจริง`
- มีหน้า static สำหรับเปิดอ่านเร็ว และมีไฟล์ `.md` สำหรับแก้ใน Codex

## โครงสร้างไฟล์

- `index.html`
  - หน้า dashboard หลัก
  - มี `Priority Queue`
  - มีการ์ดแยกตามหมวด
  - มีปุ่ม filter ตามสถานะ:
    - `ทั้งหมด`
    - `ผ่านแล้ว`
    - `มี draft ตั้งต้น`
    - `พร้อมปรับ`
- `index.md`
  - markdown index แบบแก้ไขง่าย
- `XX-*.md`
  - ไฟล์ต้นทางที่ใช้แก้ใน Codex
- `XX-*.html`
  - หน้า static สำหรับเปิดอ่านเร็ว
- `deep-dive-questions.md`
  - รวมคำถามเชิงลึกที่ AI อีกตัวช่วยตั้งเพิ่ม
- `generate-more-questions-prompt.md`
  - prompt ที่ใช้โยนให้ AI ตัวอื่นช่วยคิดคำถามใหม่

## รูปแบบของแต่ละคำถาม

โดยทั่วไป 1 ข้อจะมีส่วนเหล่านี้:

- `In My Head`
  - logic หลังบ้าน, สมมุติฐาน, framing, มุมคิดจริง
- `Option Box`
  - ประเด็นจาก source / draft เดิม / ข้ออื่นที่หยิบมาใช้ตอบได้
- `Answer I Will Actually Give`
  - โครงคำตอบหลัก
- `Version To Actually Say`
  - เวอร์ชันที่พร้อมพูด
- `45-60 Second Version`
  - เวอร์ชันสั้นสำหรับเวทีจริง
- `Support Notes`
  - ข้อควรระวัง / ของที่เสริมได้
- `Evaluation Prompt`
  - prompt สำหรับประเมินว่าคำตอบถึงระดับใช้งานจริงหรือยัง

## วิธีทำงานที่ใช้จริง

workflow ที่ใช้มาตลอดคือ:

1. เริ่มจาก `In My Head`
2. เติมหรือขัด `Option Box`
3. ยกเป็น `Answer I Will Actually Give`
4. ทำ `Version To Actually Say`
5. ทำ `45-60 Second Version`
6. ประเมินคะแนน
7. ถ้ายังไม่ถึงเป้า ขัดต่อจนเกิน `9`
8. mark เป็น `ผ่านแล้ว`
9. sync สถานะกลับไปที่ `index.md` และ `index.html`

## สิ่งที่ทำไปแล้ว

### 1. คำถามหลักชุดเดิม

มีการปั้นคำตอบครบและ mark `ผ่านแล้ว` ให้หลายข้อหลักแล้ว เช่น:

- `01` first-year priorities
- `02` AI governance speed
- `03` shared data trust
- `04` change resistance
- `07` not a dean / system leadership
- `08` faculty-level understanding
- `09` why you over others
- `12` ranking under constraints
- `13` digital university
- `14` new revenue sources
- `15` deficit and workforce
- `17` dean disagreement
- `19` board strategic governance
- `24` personal weakness

### 2. ปรับระบบหน้า index

ทำไปแล้ว:

- sync สถานะใน `index` ให้ตรงกับไฟล์คำถามจริง
- ทำสี badge ตามสถานะ
  - `ผ่านแล้ว` = เขียว
  - `พร้อมปรับ` = เหลือง
  - `มี draft ตั้งต้น` = ฟ้า
- เพิ่มปุ่ม filter ใน `index.html`

### 3. ปรับหน้า static ของคำถาม

ทำไปแล้ว:

- เติม `How To Use This Page` ให้ชัดขึ้น
- อธิบายความหมายของ `In My Head` และ `Option Box`
- แนะนำให้เปิดไฟล์ `.md` ใน Codex ถ้าจะปรับจริง เพราะเร็วกว่า
- ใช้ pattern เดียวกันสำหรับ `Copy Prompt`
- พับ `Reference v1/v2` ในหน้า html ที่เกี่ยวข้อง

### 4. เพิ่ม prompt สำหรับหา “คำถามใหม่”

สร้างไว้แล้วที่:

- [generate-more-questions-prompt.md](./generate-more-questions-prompt.md)

หน้าที่ของไฟล์นี้:

- สรุปว่ามีคำถามอะไร “ครอบคลุมไปแล้ว”
- ส่งต่อให้ AI อีกตัวช่วยคิดคำถามเพิ่ม
- บังคับไม่ให้ rephrase คำถามเดิม

### 5. เพิ่มชุด Deep-Dive Questions

หลังจากได้คำถามใหม่จาก AI อีกตัวแล้ว:

- เก็บชุดรวมไว้ที่ [deep-dive-questions.md](./deep-dive-questions.md)
- ทำหน้า static ที่ [deep-dive-questions.html](./deep-dive-questions.html)

และคัด `best 5` ขึ้นมาเป็นข้อแยก พร้อมใส่ใน `Priority Queue` แล้ว:

- `25` The Ecosystem Orchestrator
- `26` The Legal & Ethical Frontier
- `27` The Multi-Campus Equity
- `28` Non-Academic Staff Victimization
- `29` Bureaucratic Speed Trap

สถานะล่าสุดของชุดนี้:

- `25` มี draft ตั้งต้น และปั้นคำตอบไปไกลแล้ว
- `26` ผ่านแล้ว
- `27` ผ่านแล้ว
- `28` มี draft ตั้งต้น
- `29` มี draft ตั้งต้น

## งานล่าสุดที่เพิ่งทำ

รอบล่าสุดมีงานหลักดังนี้:

- แยก `best 5` ออกเป็นไฟล์ `.md` และ `.html` รายข้อ
- ยกคำตอบเต็มให้ข้อ `25`, `26`, `27`
- ปิดข้อ `26` และ `27`
- เพิ่ม filter ตามสถานะใน `index.html`

## หลักคิดที่ใช้ในงานชุดนี้

- ไม่เขียนคำตอบแบบ generic
- ให้ `In My Head` เป็นฐานคิดจริง
- ให้ `Option Box` เป็นคลังประเด็นที่หยิบใช้ได้
- ให้ `Version To Actually Say` ฟังเป็นคนจริง ไม่ใช่เอกสารราชการ
- คำตอบที่ดีต้อง:
  - จำง่าย
  - มี framing ชัด
  - มีโครง 3 เรื่องถ้าเป็นไปได้
  - มีความเป็นผู้บริหาร
  - ไม่ดูแข็งหรือล้ำเส้นเกินบริบท

## ถ้าจะทำต่อจากจุดนี้

วิธีที่เร็วที่สุดคือ:

1. เปิด [index.html](./index.html)
2. filter ดูข้อที่ยังไม่เขียว
3. เปิดไฟล์ `.md` ของข้อนั้น
4. เติม `In My Head` ก่อน
5. แล้วค่อยยกเป็นคำตอบเต็ม

ถ้าจะต่อจาก deep-dive:

- ทำ `28` หรือ `29` ต่อได้เลย
- หรือกลับไปเก็บข้อเก่าที่ยังเป็น `พร้อมปรับ`

## หมายเหตุ

- หน้า static ใช้อ่านเร็ว
- ถ้าจะปรับจริง ให้แก้ไฟล์ `.md` เป็นหลัก
- ถ้ามีการ mark สถานะใหม่ ต้อง sync กลับไปที่:
  - `index.md`
  - `index.html`
