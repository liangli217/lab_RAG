#!/usr/bin/env python3
"""
Utility for converting PDFs into UTF-8 text files using PyMuPDF.

Example:
    python3 scripts/pdf_to_text.py input-datasets text-datasets
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import fitz  # type: ignore
except ImportError as exc:
    raise SystemExit(
        "PyMuPDF is required for this script. Install it with 'pip install pymupdf'."
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDFs to plain text files using PyMuPDF."
    )
    parser.add_argument(
        "pdf_dir",
        type=Path,
        help="Directory containing input PDF files.",
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Directory where extracted text files will be written.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing text files. Defaults to skipping existing outputs.",
    )
    parser.add_argument(
        "--page-break",
        action="store_true",
        help="Insert '---' markers between pages in the output text.",
    )
    return parser.parse_args()


def extract_text_from_pdf(
    pdf_path: Path, output_path: Path, insert_page_break: bool, overwrite: bool
) -> None:
    if output_path.exists() and not overwrite:
        print(f"[skip] {output_path} exists (use --overwrite to regenerate)")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    page_text_chunks: list[str] = []

    with fitz.open(pdf_path) as doc:
        for page_index, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if not text.strip():
                print(f"[warn] Page {page_index} in {pdf_path.name} yielded no text")
            page_text_chunks.append(text)

    if insert_page_break:
        separator = "\n\n---\n\n"
        text_content = separator.join(page_text_chunks)
    else:
        text_content = "\n".join(page_text_chunks)

    output_path.write_text(text_content, encoding="utf-8")
    print(f"[done] {pdf_path.name} -> {output_path}")


def main() -> int:
    args = parse_args()

    if not args.pdf_dir.is_dir():
        print(f"Input directory not found: {args.pdf_dir}", file=sys.stderr)
        return 1

    pdf_files = sorted(args.pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found under {args.pdf_dir}", file=sys.stderr)
        return 1

    for pdf_path in pdf_files:
        output_path = args.output_dir / f"{pdf_path.stem}.txt"
        try:
            extract_text_from_pdf(
                pdf_path=pdf_path,
                output_path=output_path,
                insert_page_break=args.page_break,
                overwrite=args.overwrite,
            )
        except Exception as error:
            print(f"[error] Failed to process {pdf_path.name}: {error}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
