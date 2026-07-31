"""
Convert PDF files to plain Markdown text.

Usage:
    python pdf_to_md.py path/to/file.pdf
    python pdf_to_md.py path/to/folder

If a folder is given, every .pdf inside it is converted.
Each PDF gets a matching .md file written next to it.
"""

import sys
from pathlib import Path

import pdfplumber


def convert_pdf(pdf_path: Path) -> Path:
    md_path = pdf_path.with_suffix(".md")
    lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines.append(text.strip())
            if i < len(pdf.pages):
                lines.append("\n---\n")

    md_path.write_text("\n\n".join(lines), encoding="utf-8")
    return md_path


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_md.py <file.pdf | folder>")
        sys.exit(1)

    target = Path(sys.argv[1])

    if target.is_dir():
        pdfs = sorted(target.glob("*.pdf"))
        if not pdfs:
            print(f"No PDF files found in {target}")
            sys.exit(1)
    elif target.is_file() and target.suffix.lower() == ".pdf":
        pdfs = [target]
    else:
        print(f"Not a PDF file or folder: {target}")
        sys.exit(1)

    for pdf_path in pdfs:
        md_path = convert_pdf(pdf_path)
        print(f"Converted: {pdf_path.name} -> {md_path.name}")


if __name__ == "__main__":
    main()
