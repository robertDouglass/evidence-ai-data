#!/usr/bin/env python3
"""
Page preparation pipeline.

Given a manifest JSONL, load PDFs, extract per-page text, and emit:
- Processed markdown per document (concatenated page texts).
- Per-page text files.
- Simple per-page placeholder images (if Pillow is available).

Outputs land under:
- ingestion/output/processed/{doc_id}/{doc_id}.md
- ingestion/output/processed/{doc_id}/pages/page_{###}.md
- ingestion/output/images/{doc_id}/page_{###}.png (if images enabled)

This is a local step to prepare artifacts before uploading to MinIO.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List, Optional

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None


ROOT_DEFAULT = Path(__file__).resolve().parent.parent
MANIFEST_DEFAULT = ROOT_DEFAULT / "ingestion" / "output" / "manifest.jsonl"


def load_manifest(path: Path) -> Iterable[dict]:
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def extract_pages(pdf_path: Path) -> List[str]:
    """
    Extract per-page text. If PyPDF2 is unavailable, emit a single placeholder page.
    """
    if PdfReader is None:
        return ["[placeholder text extracted: PyPDF2 not installed]"]
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(text)
    if not pages:
        pages = ["[no text extracted]"]
    return pages


def write_page_texts(doc_id: str, pages: List[str], out_dir: Path) -> None:
    pages_dir = out_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    for idx, text in enumerate(pages, start=1):
        page_path = pages_dir / f"page_{idx:03d}.md"
        page_path.write_text(text)
    # combined markdown
    combined = "\n\n---\n\n".join(pages)
    (out_dir / f"{doc_id}.md").write_text(combined)


def write_placeholder_images(doc_id: str, pages: List[str], out_dir: Path) -> None:
    if Image is None or ImageDraw is None:
        print("Pillow not installed; skipping image generation", file=sys.stderr)
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    for idx, _ in enumerate(pages, start=1):
        img = Image.new("RGB", (800, 1000), color=(245, 245, 245))
        draw = ImageDraw.Draw(img)
        draw.text((40, 40), f"{doc_id} page {idx}", fill=(0, 0, 0))
        img.save(out_dir / f"page_{idx:03d}.png")


def process_doc(record: dict, root: Path, processed_root: Path, images_root: Path, generate_images: bool) -> bool:
    local_path = record.get("local_path")
    doc_id = record.get("doc_id")
    if not local_path or not doc_id:
        return False
    pdf_path = root / "data" / "raw" / record["source"] / local_path
    if not pdf_path.exists():
        print(f"[skip] {doc_id}: missing {pdf_path}", file=sys.stderr)
        return False
    try:
        pages = extract_pages(pdf_path)
    except Exception as e:
        print(f"[error] {doc_id}: failed to extract text: {e}", file=sys.stderr)
        return False

    out_dir = processed_root / doc_id
    out_dir.mkdir(parents=True, exist_ok=True)
    write_page_texts(doc_id, pages, out_dir)

    # copy original PDF into processed folder for convenience
    try:
        target_pdf = out_dir / f"{doc_id}.pdf"
        target_pdf.write_bytes(pdf_path.read_bytes())
    except Exception:
        pass

    if generate_images:
        write_placeholder_images(doc_id, pages, images_root / doc_id)

    print(f"[ok] {doc_id}: wrote {len(pages)} pages")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate per-page text/images from manifest PDFs.")
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT, help="Repo root (contains data/raw)")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DEFAULT, help="Manifest JSONL path")
    parser.add_argument("--doc-ids", type=str, default="", help="Comma-separated doc_ids to process (default: all)")
    parser.add_argument("--processed-root", type=Path, default=ROOT_DEFAULT / "ingestion" / "output" / "processed", help="Output root for processed text")
    parser.add_argument("--images-root", type=Path, default=ROOT_DEFAULT / "ingestion" / "output" / "images", help="Output root for images")
    parser.add_argument("--images", action="store_true", help="Generate placeholder images (requires Pillow)")
    args = parser.parse_args()

    doc_ids = [d.strip() for d in args.doc_ids.split(",") if d.strip()] if args.doc_ids else None

    count = 0
    for rec in load_manifest(args.manifest):
        if doc_ids and rec.get("doc_id") not in doc_ids:
            continue
        if process_doc(rec, args.root, args.processed_root, args.images_root, args.images):
            count += 1
    print(f"Completed {count} documents")


if __name__ == "__main__":
    main()
