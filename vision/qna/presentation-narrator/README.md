# Presentation Narrator README

ชุดนี้เปลี่ยนมาใช้ workflow แบบ `markdown -> generated html`

- คู่มือกระบวนการปัจจุบัน: ไฟล์นี้
- log การเปลี่ยนกระบวนการ: [PROCESS_LOG.md](/home/punpiti/OneDrive/KU/president/vision/qna/presentation-narrator/PROCESS_LOG.md)

## Source of Truth

- แก้เนื้อหาที่ `SlideN.md`
- ใช้ `SlideN.html` เป็นหน้า static สำหรับเปิดอ่านเร็ว
- style และ interaction กลางอยู่ที่:
  - `presentation-narrator.css`
  - `presentation-narrator.js`

## โครงของแต่ละ Slide Markdown

แต่ละไฟล์ `SlideN.md` ควรมี section หลักดังนี้:

- `Slide Content`
- `In My Head`
- `Option Box`
- `Answer I Will Actually Give`
- `Version To Actually Say`
- `Suggest Note`

ความหมาย:

- `In My Head` = เสียงในหัว / logic หลังบ้าน / framing จริง
- `Option Box` = พื้นที่เก็บประเด็นที่ดึงมาจากเอกสารอื่นหรือ draft อื่น
- `Answer I Will Actually Give` = เนื้อหาหลักของสไลด์นี้ เขียนยาวได้ก่อน แต่ต้องผูกกับหน้าปัจจุบัน
- `Version To Actually Say` = เวอร์ชันพูดจริงที่ย่อจาก `Answer I Will Actually Give` ให้พอดีกับเวลา
- `Suggest Note` = อะไรที่ควรและไม่ควรทำตอนนำเสนอหน้านี้

## Generate HTML

จาก root ของ repo:

```bash
python3 vision/tools/generate_presentation_narrator.py
```

## Generate A4 Print Pack

ถ้าต้องการชุดสำหรับพิมพ์ A4 ที่รวมรูปสไลด์กับ `Version To Actually Say`:

```bash
python3 vision/tools/generate_presentation_narrator.py --print-pack
```

ไฟล์จะถูกสร้างที่:

- `vision/qna/presentation-narrator/print/presentation_narrator_a4.html`
- `vision/qna/presentation-narrator/print/presentation_narrator_a4.tex`
- `vision/qna/presentation-narrator/print/presentation_narrator_a4.pdf`

ถ้าต้อง migrate markdown เก่าให้เติม `Answer I Will Actually Give` และ `Suggest Note` ก่อน:

```bash
python3 vision/tools/generate_presentation_narrator.py --migrate-md
```

## Workflow ที่ควรใช้

1. เริ่มจาก `Slide Content` ให้ชัดก่อนว่าหน้านี้ทำหน้าที่อะไร
2. แก้ `In My Head` และ `Option Box` ใน `SlideN.md`
3. ใส่เวลาที่ควรใช้ของสไลด์ไว้ใน `Option Box`
4. เขียน `Answer I Will Actually Give`
5. สกัดเป็น `Version To Actually Say`
6. เขียน `Suggest Note` แบบ do/don't
7. รัน generator
8. เปิด `SlideN.html` เพื่อตรวจหน้าใช้งานจริง

## Workflow ที่ใช้กับ Slide 1

ใช้ลำดับนี้เป็นแม่แบบสำหรับพัฒนา slide อื่นต่อ:

1. เริ่มจาก `Slide Content`
กำหนดให้ชัดก่อนว่า slide หน้านั้น "ทำหน้าที่อะไร" ในเรื่องทั้งหมด ไม่ใช่แค่อ่านข้อความที่อยู่บนภาพ

2. เขียน `In My Head`
บันทึก intent จริงของ slide:
- หน้านี้ต้องการประกาศอะไร
- keyword อะไรที่ต้องฝังในหัวคนฟัง
- ถ้าพูดพลาด จะพลาดไปทางไหน

3. เติม `Option Box`
ใช้เก็บวัตถุดิบที่ยังเป็น draft:
- ประโยคทดลอง
- framing ทางเลือก
- เหตุผลเชิง perception
- bullet ที่ดึงมาจากเอกสารอื่น
- แหล่งที่มาของ bullet ถ้าหยิบมาจากไฟล์อื่น
- เวลาที่ควรใช้ของ slide นั้น

4. ใส่เวลาใน `Option Box`
ให้มีบรรทัด `เวลาที่ควรใช้: ... นาที จากทั้งหมด 15 นาที`
เพื่อบังคับให้บทพูดสัมพันธ์กับเวลาจริงบนเวที

5. เขียน `Answer I Will Actually Give`
กติกาคือ:
- ต้องอธิบาย "สารของ slide หน้านี้"
- ไม่พูดกว้างเกินจนกลายเป็นอธิบายทั้ง presentation
- ผูกกับบทบาทของ slide โดยตรง
- ให้เขียนเยอะได้ก่อน แล้วค่อยย่อทีหลัง
- ควรใส่บรรทัดเวลาที่ใช้ได้ไว้ต้น section ด้วย

สำหรับ Slide 1:
- ใช้เป็นหน้า framing
- ประกาศ identity และแกนหลักของทั้งชุด
- ไม่ให้กลายเป็นหน้าแนะนำตัวหรือ recap CV

6. สกัดเป็น `Version To Actually Say`
ย่อมาจาก `Answer I Will Actually Give` โดยต้อง:
- พูดได้จริงในเวลาที่กำหนด
- อ่านลื่นตอนพูดบนเวที
- ไม่ใช้คำย่อที่ฟังสะดุด เช่นใช้ `มหาวิทยาลัยเกษตรศาสตร์` แทน `KU`
- ควรใส่บรรทัดเวลาที่ใช้ได้ไว้ต้น section ด้วย

7. เขียน `Suggest Note` เป็น do/don't
ไม่ใช้ข้อความ generic
แต่ให้ derive จาก `In My Head` และ `Option Box` ของหน้านั้นโดยตรง

8. ตรวจใน HTML
รัน:

```bash
python3 vision/tools/generate_presentation_narrator.py
```

แล้วเปิด `SlideN.html` เพื่อตรวจว่า:
- flow อ่านง่ายไหม
- `Version To Actually Say` พูดได้จริงไหม
- do/don't ใช้งานได้จริงไหม

9. ค่อย mark status เป็น `ผ่านแล้ว`
Definition of done:
- หน้าที่ของ slide ชัด
- `Answer I Will Actually Give` ผูกกับ slide นั้นจริง
- `Version To Actually Say` พอดีกับเวลา
- `Suggest Note` เป็น do/don't ที่ใช้ได้จริง
- เปิด HTML แล้วเห็นภาพพร้อมใช้

## Workflow ที่ยืนยันแล้วจาก Slide 1 ถึง Slide 5

หลังจากทำจริงต่อเนื่องถึง `Slide 5` workflow ที่ใช้ได้ผลมีลำดับดังนี้:

1. เปิด `SlideN.md` และดูภาพสไลด์จริงควบคู่กัน
2. แกะข้อความจากภาพไปใส่ `Slide Content` ให้ตรงกับ slide จริงที่สุด
3. เติม `In My Head` เพื่อบันทึก logic หรือความหมายที่อยู่หลังสไลด์
4. ค้นข้อมูลจากชุดสมัครและชุดถามตอบ แล้วสกัดสิ่งที่ “หยิบไปพูดต่อได้จริง” ไปใส่ `Option Box`
5. ใช้ `In My Head` และ `Option Box` เป็นฐานในการสร้าง `What I'll Use`
6. เติม `Answer I Will Actually Give` เป็นเวอร์ชันเต็มกว่า
7. กลั่นเป็น `Version To Actually Say` ให้พอดีกับเวลาของ slide
8. เขียน `Suggest Note` แบบเฉพาะสไลด์นั้น ไม่ใช้ note generic ถ้าสไลด์เริ่มนิ่งแล้ว
9. รัน generator และเปิด `SlideN.html` เพื่อตรวจหน้าใช้งานจริง
10. ถ้าสาร, framing, ภาษาพูด, และ HTML ลงตัวแล้ว ค่อยเปลี่ยนสถานะเป็น `ผ่านแล้ว`

## หลักแยกบทบาทของแต่ละ Section

- `Slide Content`
  - ต้องอิงจากภาพสไลด์จริงก่อน
  - ใช้เก็บข้อความที่อยู่บน slide ไม่ใส่ interpretation ปนเข้าไป
- `In My Head`
  - ใช้เก็บความหมาย, น้ำหนัก, และ logic หลังบ้าน
  - ไม่จำเป็นต้องเป็นภาษาพูดจริง
- `Option Box`
  - ใช้เก็บวัตถุดิบจาก repo เช่นใบสมัคร, ชุดถามตอบ, draft อื่น
  - ไม่ควรเป็นแค่หัวข้อสั้น ๆ แต่ควรเป็น material ที่หยิบไปขยายความได้จริง
- `Answer I Will Actually Give`
  - เป็นเวอร์ชันเต็มที่เก็บ logic ของสไลด์
  - ใช้ดูว่า “ถ้าจะพูดหน้านี้จริง ๆ ควรพูดอะไร”
- `Version To Actually Say`
  - เป็นเวอร์ชันพูดจริงที่สั้นและลื่นกว่า
  - ต้องสัมพันธ์กับเวลาที่กำหนดของ slide
- `Suggest Note`
  - ใช้เตือนว่าอะไรควรย้ำ และไม่ควรพาสไลด์หลุดไปทางไหน

## สิ่งที่ยืนยันจากการทำ Slide 5

- ต้องแกะ `Slide Content` จากภาพจริงก่อน แล้วค่อยตีความ
- ประโยคที่ “น่าพูด” และแปล slide ได้ชัด ควรถูกดันขึ้นจาก `In My Head` หรือ `Option Box` ไปอยู่ใน `Answer` และ `Version`
- `Option Box` ที่ดีควรมีทั้ง framing, ตัวอย่างโจทย์ประเทศ, implementation, และผลกระทบ ไม่ใช่แค่ keyword
- เมื่อสไลด์ผ่านแล้ว หน้า viewer ควรช่วยให้เห็น “ภาพ + สารหลัก” ก่อนอย่างอื่น

## Rule of Thumb

- `Answer I Will Actually Give` = สารของ slide นี้
- `Version To Actually Say` = เวอร์ชันพูดจริงตามเวลา
- `Suggest Note` = do/don't จาก ideas ของ slide นั้น
- ถ้า slide `ผ่านแล้ว`
  - viewer จะวาง `Answer I Will Actually Give` ไว้ใกล้รูป
  - การ์ด `Slide` จะกินพื้นที่กว้างขึ้นใน layout หลัก
  - `Ideas` card จะถูกซ่อนไปเลย
  - `What I'll Use` จะเหลือ `Version To Actually Say` กับ `Suggest Note`
  - `Answer I Will Actually Give` จะเปิดแบบขยาย
  - `Version To Actually Say` จะเริ่มแบบย่อ
- ถ้ายังไม่ `ผ่านแล้ว`
  - viewer จะคง layout ปกติ
  - เปิดทุกการ์ดเป็นค่าเริ่มต้น

## Practical Notes

- status ของแต่ละหน้าให้แก้ที่ `SlideN.md` เท่านั้น แล้วค่อย regenerate
- `index.html` ถูก generate จากสถานะใน `Slide*.md` แล้ว จึงไม่ควรแก้มือที่ index HTML ตรง ๆ
- `Slide Carousel` ใน viewer พับเก็บได้ และจำสถานะเปิด/ปิดข้ามหน้า
- README นี้ยังเป็น working process และควรอัปเดตต่อได้เมื่อ workflow ลงตัวขึ้น
- ถ้ามีการเปลี่ยนกติกาการทำงาน ให้จดทั้ง “อะไรเปลี่ยน” และ “เปลี่ยนเพราะอะไร” ลงใน `PROCESS_LOG.md`

## หมายเหตุ

- ไม่ควรแก้ `SlideN.html` ตรง ๆ ยกเว้นกำลังปรับ template
- ถ้าปรับ layout, ให้แก้ที่ `presentation-narrator.css`, `presentation-narrator.js` หรือ `vision/tools/generate_presentation_narrator.py`
