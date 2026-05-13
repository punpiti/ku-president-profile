# KU President Workspace Map

repo นี้ตอนนี้แยกเป็น 4 ก้อนงานหลัก:

```text
president/
  vision/         # งานวิสัยทัศน์แบบ self-contained รวม public-site source
  selection/      # เอกสารและข้อมูลประกอบการสรรหา/สมัคร
  research_award/ # โปรเจคเว็บอีกชุดที่แยกอิสระ
```

## Workspace Roles

### `vision/`

workspace หลักของงานวิสัยทัศน์

- source อยู่ใน `vision/sources/`
- public website source อยู่ใน `vision/public-site/`
- local-only private workspaces are intentionally ignored by Git until they are distilled into public material
- tool เฉพาะของ vision อยู่ใน `vision/tools/`

อ่านเพิ่ม: `vision/README.md`

### GitHub Pages

- local entry: `bash scripts/run_local.sh public`
- deploy entry: `bash scripts/deploy_github_pages.sh`
- source: `vision/public-site/`
- local build artifact: `.public-site-build/`
- publish target: `gh-pages` branch root

อ่านเพิ่ม: `vision/public-site/README.md`

### `selection/`

วัสดุประกอบการสรรหาและเอกสารสมัครที่ไม่ใช่ตัวงาน vision โดยตรง

- `selection/application/` = ใบสมัคร draft/submission
- `selection/reference/` = ประกาศ ระเบียบ ยุทธศาสตร์ ข้อมูลมหาวิทยาลัย
- `selection/profiles/` = profile/cv วัสดุรายบุคคล
- `selection/calendar/` = schedule และไฟล์นัดหมาย
- `selection/media/` = รูปและ asset สนับสนุน

อ่านเพิ่ม: `selection/README.md`

### `research_award/`

เว็บอีกโปรเจคที่แยกจากงาน president vision/public site

- local entry: `bash scripts/run_local.sh award`
- live URL: `https://punpiti.github.io/research-award-insights/`
- status check: `bash scripts/check_research_award_pages.sh`
- อย่าเดา URL publish จาก remote ของ parent repo; โปรเจคนี้ publish เป็น standalone Pages site ชื่อ `research-award-insights`

อ่านเพิ่ม: `research_award/README.md`

## Common Commands

```bash
bash scripts/list_projects.sh
bash scripts/run_local.sh
bash scripts/run_local.sh public
bash scripts/run_local.sh vision
bash scripts/run_local.sh award
```

## Working Rule

1. ถ้าเป็นงานวิสัยทัศน์ ให้ลงใน `vision/`
2. ถ้าเป็น public website ที่จะ publish จริง ให้ลงใน `vision/public-site/` แล้ว publish ผ่าน `gh-pages` branch ด้วย script
3. ถ้าเป็นเอกสารประกอบการสมัคร/สรรหา ให้ลงใน `selection/`
4. ถ้าเป็นงานเว็บอีกก้อนที่ไม่เกี่ยวกับสองข้อบน ให้แยกเป็น project folder ของตัวเอง
