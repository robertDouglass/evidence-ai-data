# Prompt 002 – Local Control Loop & Idempotent Runner

## Goal
Build a minimal local orchestrator to drive manifest → page prep → upload → index steps with idempotency and status tracking. Keep it local-first; do not deploy to Fly.

## Inputs
- Manifest: `ingestion/output/manifest.jsonl`
- Scripts to (add or verify):
  - `ingestion/page_pipeline.py`
  - `ingestion/upload_to_minio.py`
  - `ingestion/runner.py` (or Make targets)
- State store: simple JSONL/SQLite or CSV in `ingestion/state/` (new)

## Steps
1) **State tracking**
   - Create a small state store (e.g., SQLite or JSONL) with fields: `doc_id`, `status` (`ready_for_processing`, `processed`, `indexed`, `error`), `attempts`, `notes`, timestamps.
   - Add CLI functions to set/get status and list pending docs.
2) **Runner**
   - `ingestion/runner.py` orchestrates: page pipeline (Docling) → upload → indexer call, per doc_id or small batch.
   - Idempotent: skip steps if artifacts already exist and hashes match.
   - Retryable: safe to rerun on failures.
3) **Hooks**
   - Use environment variables for endpoints/buckets; default to Fly internal URLs.
   - Allow `--include-restricted` toggle; default skips `restricted=true` if any remain.
4) **Test**
   - Drive the same sample subset from Prompt 001 through the runner.
   - Confirm statuses advance to `indexed`.
5) **Log**
   - Record in `ingestion/WORKLOG.md`: runner tested, docs/pages processed, failures/resolutions.

## Done when
- Runner exists and can process a batch idempotently end-to-end locally.
- State store reflects accurate statuses.
