#!/usr/bin/env python3
"""
Manifest builder for EvidenceAI ingestion.

Scans data/raw/<source>/metadata files, normalizes fields to the unified schema (v2),
computes local paths + SHA256/file sizes when binaries exist, and writes a manifest JSONL.

Usage:
  python manifest_builder.py --root .. --output ingestion/output/manifest.jsonl

Defaults assume this script is run from the repo root and that binaries live in data/raw/<source>/documents/.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

ROOT_DEFAULT = Path(__file__).resolve().parent.parent
CONTROLLED_REGIONS = {
    "ssa": "SSA",
    "sub-saharan africa": "SSA",
    "africa": "SSA",
    "mena": "MENA",
    "middle east": "MENA",
    "apac": "APAC",
    "asia": "APAC",
    "eur": "EUR",
    "europe": "EUR",
    "lac": "LAC",
    "latin america": "LAC",
    "na": "NA",
    "north america": "NA",
    "global": "Global",
    "multi": "Multi",
}

CONTROLLED_LANGS = {"en", "de", "fr", "es", "pt", "ar", "zh", "other"}


def load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def load_csv(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {k: v for k, v in row.items() if v != ""}


def sha256_file(path: Path) -> Tuple[Optional[str], Optional[int]]:
    if not path.exists() or not path.is_file():
        return None, None
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def norm_language(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    value = raw.lower().split("-")[0]
    return value if value in CONTROLLED_LANGS else "other"


def norm_regions(raw: Any) -> List[str]:
    if not raw:
        return []
    if isinstance(raw, str):
        items = [raw]
    elif isinstance(raw, list):
        items = raw
    else:
        return []
    out: List[str] = []
    for item in items:
        key = str(item).lower().strip()
        region = CONTROLLED_REGIONS.get(key)
        if region and region not in out:
            out.append(region)
    return out


def norm_sdg_tags(raw: Any) -> List[str]:
    if not raw:
        return []
    tags: List[str] = []
    items = raw if isinstance(raw, list) else [raw]
    for item in items:
        s = str(item).strip()
        if s.isdigit():
            s = f"SDG{s}"
        if s.upper().startswith("SDG"):
            s = s.upper()
        else:
            continue
        if s not in tags:
            tags.append(s)
    return tags


def infer_year(record: Dict[str, Any], local_path: Optional[str]) -> Optional[int]:
    """Try to infer a publication year (2000-2100) from known fields or paths."""
    import re

    candidates = [
        record.get("publication_year"),
        record.get("year"),
        record.get("publication_date"),
        record.get("doc_id"),
        record.get("title"),
        record.get("original_url") or record.get("url"),
        local_path,
    ]
    for c in candidates:
        if not c:
            continue
        if isinstance(c, int):
            if 2000 <= c <= 2100:
                return c
            continue
        text = str(c)
        for match in re.findall(r"(20\\d{2})", text):
            year = int(match)
            if 2000 <= year <= 2100:
                return year
    return None


def find_file_by_doc_id(root: Path, source: str, doc_id: str) -> Optional[str]:
    """
    Search for a file under data/raw/<source>/documents that contains the doc_id in its name.
    Returns relative path (documents/...) if found.
    """
    docs_root = root / "data" / "raw" / source / "documents"
    if not docs_root.exists():
        return None
    for path in docs_root.rglob("*"):
        if path.is_file() and doc_id in path.name:
            rel = path.relative_to(root / "data" / "raw" / source)
            return str(rel).replace("\\", "/")
    return None


def ensure_local_path(record: Dict[str, Any], source: str, root: Path) -> Optional[str]:
    """
    Normalize file path to relative under data/raw/<source>/documents/.
    """
    candidates: List[str] = []
    for key in ("local_path", "file_path", "pdfurl", "pdf_url", "filename"):
        value = record.get(key)
        if value:
            candidates.append(str(value))
    for c in candidates:
        c_path = c.replace("\\", "/")
        if "data/raw" in c_path:
            # Trim everything up to source/documents
            parts = c_path.split(f"{source}/documents/", maxsplit=1)
            if len(parts) == 2:
                return f"documents/{parts[1]}"
        if c_path.startswith("documents/"):
            return c_path
    # Fallback: try to find a file named with doc_id under documents
    doc_id = record.get("doc_id") or record.get("document_id")
    if doc_id:
        return find_file_by_doc_id(root, source, doc_id)
    return None


def normalize_record(record: Dict[str, Any], source: str, root: Path) -> Optional[Dict[str, Any]]:
    doc_id = record.get("doc_id") or record.get("document_id")
    if not doc_id:
        return None

    local_path = ensure_local_path(record, source, root)
    doc_path = root / "data" / "raw" / source / (local_path or "")

    file_hash, file_size = sha256_file(doc_path) if local_path else (None, None)

    language = norm_language(record.get("language")) or "other"
    document_type = (
        record.get("document_type")
        or record.get("doc_type")
        or record.get("document_series")
        or record.get("topic")
        or "other"
    )
    title = record.get("title") or record.get("project_name") or record.get("filename") or doc_id
    publication_year = infer_year(record, local_path)

    normalized = {
        "doc_id": doc_id,
        "source": record.get("source") or source,
        "title": title,
        "subtitle": record.get("subtitle"),
        "original_url": record.get("url") or record.get("document_url"),
        "local_path": local_path,
        "file_hash_sha256": record.get("file_hash_sha256") or file_hash,
        "file_size_bytes": record.get("file_size_bytes") or file_size,
        "mime_type": record.get("mime_type"),
        "downloaded_at": record.get("downloaded_at") or record.get("harvested_date"),
        "publication_date": record.get("publication_date"),
        "publication_year": publication_year,
        "timeframe_start": record.get("timeframe_start"),
        "timeframe_end": record.get("timeframe_end"),
        "document_type": document_type,
        "thematic_area": record.get("thematic_area"),
        "sector_tags": record.get("sector_tags") or record.get("themes"),
        "sdg_tags": norm_sdg_tags(record.get("sdg_tags")),
        "keywords": record.get("keywords"),
        "countries": record.get("countries") or record.get("country"),
        "regions": norm_regions(record.get("region") or record.get("regions") or record.get("region_covered")),
        "admin1": record.get("admin1"),
        "language": language,
        "alt_languages": record.get("alt_languages"),
        "organisation": record.get("organisation") or record.get("donor_country"),
        "implementing_partners": record.get("implementing_partners"),
        "authors": record.get("authors"),
        "license": record.get("license"),
        "page_count": record.get("page_count"),
        "word_count": record.get("word_count"),
        "image_count": record.get("image_count"),
        "text_extracted": record.get("text_extracted"),
        "extraction_quality": record.get("extraction_quality"),
        "pii_flag": record.get("pii_flag") or False,
        "restricted": record.get("restricted") or False,
        "exclude_from_search": record.get("exclude_from_search") or False,
        "quality_checked": record.get("quality_checked"),
        "executive_summary": record.get("executive_summary"),
        "abstract": record.get("abstract"),
        "notes": record.get("notes"),
        "related_ids": record.get("related_ids"),
        "bilingual_of": record.get("bilingual_of"),
        "processed_date": record.get("processed_date"),
        "version": record.get("version") or "2.0",
        "pipeline_run_id": record.get("pipeline_run_id"),
    }

    notes: List[str] = []
    if normalized["publication_year"] is None:
        normalized["publication_year"] = 0
        notes.append("publication_year_unknown")

    required_missing: Set[str] = set()
    for field in ("doc_id", "source", "title", "publication_year", "document_type", "language", "local_path", "file_hash_sha256"):
        if normalized.get(field) in (None, "", []):
            required_missing.add(field)

    if required_missing:
        normalized["restricted"] = True
        normalized["exclude_from_search"] = True
        notes.append(f"missing_required:{sorted(required_missing)}")

    if notes:
        normalized["notes"] = "; ".join(notes)

    return normalized


def iter_metadata_files(root: Path) -> Iterable[Tuple[str, Path]]:
    meta_root = root / "data" / "raw"
    for source_dir in meta_root.iterdir():
        if not source_dir.is_dir():
            continue
        source = source_dir.name
        meta_dir = source_dir / "metadata"
        if not meta_dir.exists():
            continue
        for path in meta_dir.iterdir():
            if path.suffix.lower() in {".jsonl", ".csv"}:
                yield source, path


def load_records_for_source(source: str, path: Path) -> Iterable[Dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        yield from load_jsonl(path)
    elif path.suffix.lower() == ".csv":
        yield from load_csv(path)


def build_manifest(root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    count_in = 0
    count_out = 0
    with output.open("w") as out_f:
        for source, meta_path in iter_metadata_files(root):
            for record in load_records_for_source(source, meta_path):
                count_in += 1
                normalized = normalize_record(record, source, root)
                if not normalized:
                    continue
                out_f.write(json.dumps(normalized, ensure_ascii=False) + "\n")
                count_out += 1
    print(f"Wrote {count_out} records (from {count_in} inputs) to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build unified manifest from data/raw/*/metadata files.")
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT, help="Repo root containing data/raw")
    parser.add_argument("--output", type=Path, default=ROOT_DEFAULT / "ingestion" / "output" / "manifest.jsonl", help="Output manifest path")
    args = parser.parse_args()
    build_manifest(args.root, args.output)


if __name__ == "__main__":
    main()
