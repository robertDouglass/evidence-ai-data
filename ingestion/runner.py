#!/usr/bin/env python3
"""
Idempotent runner for document ingestion pipeline.

Orchestrates: manifest → page_pipeline → upload_to_minio → indexer
with state tracking for each document.

State is stored in SQLite at ingestion/state/pipeline.db
"""

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

ROOT = Path(__file__).resolve().parent.parent
STATE_DB = ROOT / "ingestion" / "state" / "pipeline.db"
MANIFEST_DEFAULT = ROOT / "ingestion" / "output" / "manifest.jsonl"


def init_db(db_path: Path) -> sqlite3.Connection:
    """Initialize state database with schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS doc_state (
            doc_id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'ready_for_processing',
            attempts INTEGER DEFAULT 0,
            notes TEXT,
            source_hash TEXT,
            processed_hash TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    return conn


def load_manifest(path: Path) -> Iterable[dict]:
    """Load manifest JSONL."""
    if not path.exists():
        return
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def get_file_hash(path: Path) -> str:
    """Get MD5 hash of file."""
    if not path.exists():
        return ""
    return hashlib.md5(path.read_bytes()).hexdigest()


def get_status(conn: sqlite3.Connection, doc_id: str) -> Optional[dict]:
    """Get document status from state store."""
    cur = conn.execute("SELECT * FROM doc_state WHERE doc_id = ?", (doc_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def set_status(conn: sqlite3.Connection, doc_id: str, status: str,
               notes: str = "", source_hash: str = "", processed_hash: str = "") -> None:
    """Set document status in state store."""
    now = datetime.utcnow().isoformat()
    existing = get_status(conn, doc_id)
    if existing:
        conn.execute("""
            UPDATE doc_state
            SET status = ?, notes = ?, source_hash = COALESCE(NULLIF(?, ''), source_hash),
                processed_hash = COALESCE(NULLIF(?, ''), processed_hash),
                attempts = attempts + 1, updated_at = ?
            WHERE doc_id = ?
        """, (status, notes, source_hash, processed_hash, now, doc_id))
    else:
        conn.execute("""
            INSERT INTO doc_state (doc_id, status, notes, source_hash, processed_hash,
                                   attempts, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        """, (doc_id, status, notes, source_hash, processed_hash, now, now))
    conn.commit()


def list_docs(conn: sqlite3.Connection, status: Optional[str] = None) -> List[dict]:
    """List documents, optionally filtered by status."""
    if status:
        cur = conn.execute("SELECT * FROM doc_state WHERE status = ? ORDER BY updated_at", (status,))
    else:
        cur = conn.execute("SELECT * FROM doc_state ORDER BY status, updated_at")
    return [dict(row) for row in cur.fetchall()]


def run_page_pipeline(doc_id: str, root: Path, manifest: Path) -> bool:
    """Run page pipeline for a document."""
    cmd = [
        sys.executable, str(root / "ingestion" / "page_pipeline.py"),
        "--root", str(root),
        "--manifest", str(manifest),
        "--doc-ids", doc_id
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [error] page_pipeline: {result.stderr}", file=sys.stderr)
        return False
    print(f"  {result.stdout.strip()}")
    return True


def run_upload(doc_id: str, root: Path, manifest: Path, endpoint: str) -> bool:
    """Run MinIO upload for a document."""
    cmd = [
        sys.executable, str(root / "ingestion" / "upload_to_minio.py"),
        "--root", str(root),
        "--manifest", str(manifest),
        "--doc-ids", doc_id,
        "--endpoint", endpoint
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [error] upload: {result.stderr}", file=sys.stderr)
        return False
    print(f"  {result.stdout.strip()}")
    return True


def check_artifacts_exist(doc_id: str, root: Path) -> bool:
    """Check if processed artifacts already exist."""
    processed_dir = root / "ingestion" / "output" / "processed" / doc_id
    md_file = processed_dir / f"{doc_id}.md"
    return md_file.exists()


def process_doc(conn: sqlite3.Connection, record: dict, root: Path, manifest: Path,
                skip_upload: bool = False, minio_endpoint: str = "") -> bool:
    """Process a single document through the pipeline."""
    doc_id = record.get("doc_id")
    if not doc_id:
        return False

    # Check current status
    state = get_status(conn, doc_id)
    current_status = state["status"] if state else "ready_for_processing"

    # Skip if already indexed
    if current_status == "indexed":
        print(f"[skip] {doc_id}: already indexed")
        return True

    # Get source file hash for idempotency
    local_path = record.get("local_path")
    source = record.get("source", "unknown").lower()
    pdf_path = root / "data" / "raw" / source / local_path if local_path else None
    source_hash = get_file_hash(pdf_path) if pdf_path else ""

    # Check if artifacts exist and hashes match (idempotent skip)
    if state and state.get("source_hash") == source_hash and check_artifacts_exist(doc_id, root):
        if current_status == "processed":
            print(f"[skip] {doc_id}: already processed (hash match)")
            if skip_upload:
                return True
            # Continue to upload
        elif current_status == "uploaded":
            print(f"[skip] {doc_id}: already uploaded")
            return True

    print(f"[processing] {doc_id}")

    # Step 1: Page pipeline
    if current_status in ("ready_for_processing", "error"):
        set_status(conn, doc_id, "processing", "Running page pipeline", source_hash)
        if not run_page_pipeline(doc_id, root, manifest):
            set_status(conn, doc_id, "error", "Page pipeline failed")
            return False
        processed_hash = get_file_hash(root / "ingestion" / "output" / "processed" / doc_id / f"{doc_id}.md")
        set_status(conn, doc_id, "processed", "Page pipeline complete", source_hash, processed_hash)

    # Step 2: Upload to MinIO
    if not skip_upload and minio_endpoint:
        state = get_status(conn, doc_id)
        if state and state["status"] == "processed":
            set_status(conn, doc_id, "uploading", "Uploading to MinIO")
            if not run_upload(doc_id, root, manifest, minio_endpoint):
                set_status(conn, doc_id, "error", "Upload failed")
                return False
            set_status(conn, doc_id, "uploaded", "Upload complete")

    # Step 3: Index (placeholder - would call indexer)
    # For now we mark as indexed if uploaded, or processed if no upload
    state = get_status(conn, doc_id)
    if state:
        if state["status"] == "uploaded":
            set_status(conn, doc_id, "indexed", "Indexing complete (placeholder)")
        elif state["status"] == "processed" and skip_upload:
            # If skipping upload, mark as processed (not indexed)
            pass

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Idempotent document ingestion runner")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DEFAULT, help="Manifest JSONL path")
    parser.add_argument("--db", type=Path, default=STATE_DB, help="State database path")
    parser.add_argument("--minio-endpoint", type=str,
                       default=os.environ.get("MINIO_ENDPOINT", "http://evidenceai-minio.internal:9000"),
                       help="MinIO endpoint URL")

    # CLI subcommands for state management
    subparsers = parser.add_subparsers(dest="command")

    # Run command (default)
    run_parser = subparsers.add_parser("run", help="Run pipeline")
    run_parser.add_argument("--doc-ids", type=str, default="", help="Comma-separated doc_ids (default: all)")
    run_parser.add_argument("--skip-upload", action="store_true", help="Skip MinIO upload step")
    run_parser.add_argument("--include-restricted", action="store_true", help="Include restricted documents")

    # Status commands
    list_parser = subparsers.add_parser("list", help="List documents by status")
    list_parser.add_argument("--status", type=str, help="Filter by status")

    get_parser = subparsers.add_parser("get", help="Get status of a document")
    get_parser.add_argument("doc_id", help="Document ID")

    set_parser = subparsers.add_parser("set", help="Set status of a document")
    set_parser.add_argument("doc_id", help="Document ID")
    set_parser.add_argument("status", help="New status")
    set_parser.add_argument("--notes", default="", help="Notes")

    reset_parser = subparsers.add_parser("reset", help="Reset document to ready_for_processing")
    reset_parser.add_argument("doc_id", help="Document ID")

    args = parser.parse_args()

    conn = init_db(args.db)

    # Handle subcommands
    if args.command == "list":
        docs = list_docs(conn, args.status if hasattr(args, 'status') else None)
        if not docs:
            print("No documents found")
            return
        for doc in docs:
            print(f"{doc['doc_id']}: {doc['status']} (attempts: {doc['attempts']}) {doc.get('notes', '')}")
        return

    if args.command == "get":
        state = get_status(conn, args.doc_id)
        if state:
            for k, v in state.items():
                print(f"  {k}: {v}")
        else:
            print(f"No state found for {args.doc_id}")
        return

    if args.command == "set":
        set_status(conn, args.doc_id, args.status, args.notes)
        print(f"Set {args.doc_id} to {args.status}")
        return

    if args.command == "reset":
        set_status(conn, args.doc_id, "ready_for_processing", "Manual reset")
        print(f"Reset {args.doc_id} to ready_for_processing")
        return

    # Default: run pipeline
    if not args.manifest.exists():
        print(f"Manifest not found: {args.manifest}")
        print("Run: python3 ingestion/manifest_builder.py --output ingestion/output/manifest.jsonl")
        sys.exit(1)

    doc_ids_str = getattr(args, 'doc_ids', '') or ''
    doc_ids = [d.strip() for d in doc_ids_str.split(",") if d.strip()] if doc_ids_str else None
    skip_upload = getattr(args, 'skip_upload', False)
    include_restricted = getattr(args, 'include_restricted', False)

    processed = 0
    failed = 0
    skipped = 0

    for record in load_manifest(args.manifest):
        doc_id = record.get("doc_id")
        if not doc_id:
            continue
        if doc_ids and doc_id not in doc_ids:
            continue

        # Skip restricted unless flag set
        if record.get("restricted") and not include_restricted:
            skipped += 1
            continue

        if process_doc(conn, record, args.root, args.manifest, skip_upload, args.minio_endpoint):
            processed += 1
        else:
            failed += 1

    print(f"\nSummary: {processed} processed, {failed} failed, {skipped} skipped (restricted)")

    # Show final status counts
    all_docs = list_docs(conn)
    status_counts = {}
    for doc in all_docs:
        status_counts[doc['status']] = status_counts.get(doc['status'], 0) + 1
    print("Status breakdown:", dict(status_counts))


if __name__ == "__main__":
    main()
