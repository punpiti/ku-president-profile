#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.md"
PRINT_DIR = ROOT / "print"
OUT_MD = PRINT_DIR / "question_bank_priority_queue.md"
OUT_PDF = PRINT_DIR / "question_bank_priority_queue.pdf"

SECTIONS = [
    "Answer I Will Actually Give",
    "In My Head",
    "Option Box",
    "Support Notes",
]


def read(path):
    return path.read_text(encoding="utf-8")


def priority_queue_items(index_text):
    in_queue = False
    queue_number = 0
    for line in index_text.splitlines():
        if line.startswith("## "):
            in_queue = line.strip() == "## Priority Queue"
            continue
        if not in_queue or not line.startswith("- "):
            continue

        queue_number += 1
        if "ผ่านแล้ว" not in line:
            continue

        edit_match = re.search(r"\[edit\]\((\./[^)]+\.md)\)", line)
        if not edit_match:
            continue

        yield queue_number, edit_match.group(1).removeprefix("./")


def metadata(md_text):
    title = md_text.splitlines()[0].removeprefix("# ").strip()
    meta = {"Question": title}
    for line in md_text.splitlines()[1:12]:
        match = re.match(r"- ([^:]+):\s*(.*)", line)
        if match:
            meta[match.group(1)] = match.group(2).strip()
    return meta


def section(md_text, name):
    pattern = rf"^## {re.escape(name)}\s*$"
    match = re.search(pattern, md_text, flags=re.MULTILINE)
    if not match:
        return "_ไม่มีข้อมูลใน section นี้_"

    start = match.end()
    next_match = re.search(r"^## .*$", md_text[start:], flags=re.MULTILINE)
    end = start + next_match.start() if next_match else len(md_text)
    content = md_text[start:end].strip()
    return content or "_ไม่มีข้อมูลใน section นี้_"


def question_number(filename):
    match = re.match(r"(\d+)-", filename)
    return match.group(1) if match else filename


def main():
    PRINT_DIR.mkdir(parents=True, exist_ok=True)
    index_text = read(INDEX)
    items = list(priority_queue_items(index_text))

    lines = [
        "---",
        "title: ข้อที่ผ่านแล้วตามลำดับ Priority Queue",
        "lang: th",
        "mainfont: Sarabun",
        "monofont: Sarabun",
        "fontsize: 11pt",
        "geometry: margin=18mm",
        "papersize: a4",
        "---",
        "",
        f"รวม {len(items)} ข้อที่ mark `ผ่านแล้ว` จาก Priority Queue",
        "",
    ]

    for queue_no, filename in items:
        path = ROOT / filename
        md_text = read(path)
        meta = metadata(md_text)

        lines.extend(
            [
                r"\newpage",
                "",
                f"# Queue {queue_no}: Question {question_number(filename)}",
                "",
                f"- ลำดับใน queue: {queue_no}",
                f"- หมายเลขคำถาม: {question_number(filename)}",
                f"- กลุ่มของคำถาม: {meta.get('Category', '')}",
                f"- คำถาม: {meta.get('Question', '')}",
                "",
            ]
        )

        for name in SECTIONS:
            lines.extend([f"## {name}", "", section(md_text, name), ""])

    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    if shutil.which("pandoc"):
        subprocess.run(
            [
                "pandoc",
                str(OUT_MD),
                "--pdf-engine=xelatex",
                "-o",
                str(OUT_PDF),
            ],
            check=True,
            cwd=ROOT,
        )
        print(OUT_PDF.relative_to(ROOT))
    print(OUT_MD.relative_to(ROOT))
    print(len(items))


if __name__ == "__main__":
    main()
