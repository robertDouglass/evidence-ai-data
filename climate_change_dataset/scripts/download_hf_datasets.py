#!/usr/bin/env python3
"""Download curated Hugging Face climate datasets and build a manifest."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from datasets import load_dataset

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "huggingface"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "metadata" / "manifest.csv"


DATASETS = [
    {
        "id": "mteb/climate-fever-v2",
        "title": "MTEB Climate-FEVER v2",
        "license": "CC-BY-SA-4.0",
        "url": "https://huggingface.co/datasets/mteb/climate-fever-v2",
        "notes": "Fact-checking retrieval corpus for climate claims.",
    },
    {
        "id": "climatebert/climate_sentiment",
        "title": "ClimateBERT Sentiment Dataset",
        "license": "CC-BY 4.0",
        "url": "https://huggingface.co/datasets/climatebert/climate_sentiment",
        "notes": "Climate-related risk vs opportunity paragraphs with sentiment labels.",
    },
    {
        "id": "rony/climate-change-MRC",
        "title": "Climate Bot MRC",
        "license": "MIT",
        "url": "https://huggingface.co/datasets/rony/climate-change-MRC",
        "notes": "Machine reading comprehension samples from IJCAI-ECAI 2022 demo.",
    },
    {
        "id": "climedataset/CliME",
        "title": "CliME Multimodal Climate Discourse Dataset",
        "license": "CC-BY 4.0",
        "url": "https://huggingface.co/datasets/climedataset/CliME",
        "notes": "Social-media style climate messaging with optional images.",
    },
]


def sha256sum(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def make_json_serializable(obj: Any) -> Any:
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, list):
        return [make_json_serializable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    return str(obj)


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_existing_manifest() -> tuple[list[Dict[str, str]], Dict[tuple[str, str], Dict[str, str]]]:
    if not MANIFEST_PATH.exists():
        return [], {}
    with MANIFEST_PATH.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    index: Dict[tuple[str, str], Dict[str, str]] = {}
    for row in rows:
        index[(row["source_id"], row["split"])] = row
    return rows, index


def dataset_fully_ingested(dataset_id: str, index: Dict[tuple[str, str], Dict[str, str]]) -> bool:
    entries = [row for (src, _), row in index.items() if src == dataset_id]
    if not entries:
        return False
    for row in entries:
        path = PROJECT_ROOT / row["file_path"]
        if not path.exists():
            return False
    return True


def dump_split(dataset_id: str, split_name: str, split) -> Dict[str, Any]:
    output_dir = DATA_DIR / dataset_id.replace("/", "_")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{split_name}.jsonl"

    count = 0
    with output_file.open("w", encoding="utf-8") as fh:
        for example in split:
            json.dump(make_json_serializable(example), fh, ensure_ascii=False)
            fh.write("\n")
            count += 1

    return {
        "path": output_file,
        "count": count,
        "size": output_file.stat().st_size,
        "sha256": sha256sum(output_file),
    }


def main() -> None:
    ensure_data_dir()
    manifest_rows, manifest_index = load_existing_manifest()

    for ds_meta in DATASETS:
        if dataset_fully_ingested(ds_meta["id"], manifest_index):
            print(f"Skipping {ds_meta['id']} (already present).")
            continue

        print(f"Downloading {ds_meta['id']} ...")
        dataset_dict = load_dataset(ds_meta["id"])
        for split_name, split in dataset_dict.items():
            key = (ds_meta["id"], split_name)
            existing_entry = manifest_index.get(key)
            if existing_entry:
                existing_path = PROJECT_ROOT / existing_entry["file_path"]
                if existing_path.exists():
                    print(f"  - Split '{split_name}' already stored ({existing_path}), skipping.")
                    continue
            stats = dump_split(ds_meta["id"], split_name, split)
            new_row = {
                "source_id": ds_meta["id"],
                "title": ds_meta["title"],
                "document_type": "dataset",
                "split": split_name,
                "items_count": stats["count"],
                "file_path": str(stats["path"].relative_to(PROJECT_ROOT)),
                "file_size_bytes": str(stats["size"]),
                "sha256": stats["sha256"],
                "download_url": ds_meta["url"],
                "license": ds_meta["license"],
                "notes": ds_meta["notes"],
            }
            manifest_rows.append(new_row)
            manifest_index[key] = new_row

    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "source_id",
                "title",
                "document_type",
                "split",
                "items_count",
                "file_path",
                "file_size_bytes",
                "sha256",
                "download_url",
                "license",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"Manifest written to {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
