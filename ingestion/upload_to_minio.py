#!/usr/bin/env python3
"""
Upload processed artifacts to MinIO.

Sources:
- Raw PDFs: data/raw/<source>/documents/... (manifest local_path)
- Processed text: ingestion/output/processed/{doc_id}/...
- Images: ingestion/output/images/{doc_id}/... (if present)

Destinations (buckets):
- documents-raw/{source}/{doc_id}.pdf
- documents-processed/{doc_id}/{doc_id}.pdf and {doc_id}.md plus pages/*
- document-images/{doc_id}/page_###.png
"""

import argparse
import json
import os
from pathlib import Path
from typing import Iterable

try:
    import boto3
except ImportError:
    boto3 = None


ROOT_DEFAULT = Path(__file__).resolve().parent.parent
MANIFEST_DEFAULT = ROOT_DEFAULT / "ingestion" / "output" / "manifest.jsonl"


SOURCE_DIR_MAP = {
    "UNDP ERC": "undp",
    "BGR Commodity Top News": "bgr",
    "BGR Investigation": "bgr",
    "iki": "iki",
    "oecd": "oecd",
}


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


def ensure_bucket(s3_client, name: str) -> None:
    try:
        s3_client.head_bucket(Bucket=name)
    except s3_client.exceptions.NoSuchBucket:
        s3_client.create_bucket(Bucket=name)


def upload_file(s3_client, bucket: str, key: str, path: Path) -> None:
    s3_client.upload_file(str(path), bucket, key)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload PDFs and processed artifacts to MinIO")
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT, help="Repo root")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DEFAULT, help="Manifest JSONL path")
    parser.add_argument("--processed-root", type=Path, default=ROOT_DEFAULT / "ingestion" / "output" / "processed", help="Processed output root")
    parser.add_argument("--images-root", type=Path, default=ROOT_DEFAULT / "ingestion" / "output" / "images", help="Images root")
    parser.add_argument("--doc-ids", type=str, default="", help="Comma-separated doc_ids to upload (default: all)")
    parser.add_argument("--endpoint", type=str, default=os.environ.get("MINIO_ENDPOINT", "http://evidenceai-minio.internal:9000"))
    parser.add_argument("--access-key", type=str, default=os.environ.get("MINIO_ROOT_USER", "admin"))
    parser.add_argument("--secret-key", type=str, default=os.environ.get("MINIO_ROOT_PASSWORD", "dev_minio_password_change_in_prod"))
    parser.add_argument("--region", type=str, default=os.environ.get("MINIO_REGION", "us-east-1"))
    parser.add_argument("--bucket-raw", type=str, default="documents-raw")
    parser.add_argument("--bucket-processed", type=str, default="documents-processed")
    parser.add_argument("--bucket-images", type=str, default="document-images")
    args = parser.parse_args()

    if boto3 is None:
        print("boto3 not installed; cannot upload to MinIO")
        return

    s3_client = boto3.client(
        "s3",
        endpoint_url=args.endpoint,
        aws_access_key_id=args.access_key,
        aws_secret_access_key=args.secret_key,
        region_name=args.region,
    )

    for bucket in (args.bucket_raw, args.bucket_processed, args.bucket_images):
        try:
            ensure_bucket(s3_client, bucket)
        except Exception:
            pass

    doc_ids = [d.strip() for d in args.doc_ids.split(",") if d.strip()] if args.doc_ids else None

    count = 0
    for rec in load_manifest(args.manifest):
        doc_id = rec.get("doc_id")
        if not doc_id:
            continue
        if doc_ids and doc_id not in doc_ids:
            continue
        source = rec.get("source", "unknown")
        source_dir = SOURCE_DIR_MAP.get(source, source.lower().replace(" ", "_"))
        local_path = rec.get("local_path")
        if local_path:
            pdf_path = args.root / "data" / "raw" / source_dir / local_path
            if pdf_path.exists():
                key = f"{source}/{doc_id}.pdf"
                upload_file(s3_client, args.bucket_raw, key, pdf_path)
        # processed
        proc_dir = args.processed_root / doc_id
        if proc_dir.exists():
            # upload combined markdown
            md_path = proc_dir / f"{doc_id}.md"
            if md_path.exists():
                upload_file(s3_client, args.bucket_processed, f"{doc_id}/{doc_id}.md", md_path)
            pdf_proc = proc_dir / f"{doc_id}.pdf"
            if pdf_proc.exists():
                upload_file(s3_client, args.bucket_processed, f"{doc_id}/{doc_id}.pdf", pdf_proc)
            pages_dir = proc_dir / "pages"
            if pages_dir.exists():
                for page_file in pages_dir.glob("*.md"):
                    upload_file(s3_client, args.bucket_processed, f"{doc_id}/pages/{page_file.name}", page_file)
        # images
        img_dir = args.images_root / doc_id
        if img_dir.exists():
            for img_file in img_dir.glob("*.png"):
                upload_file(s3_client, args.bucket_images, f"{doc_id}/{img_file.name}", img_file)
        count += 1
    print(f"Uploaded artifacts for {count} documents (where present)")


if __name__ == "__main__":
    main()
