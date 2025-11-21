# Ingestion Worklog

- 2025-11-22 Codex (GPT-5): Added INGESTION_PLAN.md with unified schema and multi-phase rollout; pending: schema update, manifest builder, Docling GPU test, test batch ingest.
- 2025-11-22 Codex (GPT-5): Implemented unified schema v2 (data/raw/metadata_schema.yaml), added SCHEMA.md reference, created manifest_builder.py. Added path fallback search, year inference, doc_type/lang defaults. Created stubs for missing BGR commodity/investigation and OECD files (to be replaced with real PDFs later), added IKI doc copy. Regenerated manifest (ingestion/output/manifest.jsonl) now has 0 restricted records; required fields populated with hashes/sizes (stubs included). Notes retain `publication_year_unknown` where applicable.
- 2025-11-22 Codex (GPT-5): Prompt 001 prep – added `ingestion/page_pipeline.py` (placeholder text extraction if PyPDF2 missing). Ran pipeline on 5 target docs (manifest doc_ids: IKI-EVAL-2025-001, WB-CLIM-D34442285/277/284/292); generated processed markdown + copied PDFs under ingestion/output/processed/. Pillow not installed, so images were skipped. Added `ingestion/upload_to_minio.py` (not yet executed; requires boto3/MinIO access). Pending: generate images (install Pillow) and upload + index subset into Vespa/OpenSearch once indexer manifest support is ready.

- 2025-11-21 Claude (Sonnet 4.5): Prompt 002 – Implemented local control loop and idempotent runner.
  - Created `ingestion/runner.py` with SQLite state tracking (`ingestion/state/pipeline.db`)
  - State store tracks: doc_id, status (ready_for_processing/processed/uploaded/indexed/error), attempts, timestamps, source/processed hashes
  - Runner orchestrates: page_pipeline → upload_to_minio → indexer (placeholder)
  - Idempotent: skips steps if artifacts exist and source hash matches
  - CLI subcommands: `run`, `list`, `get`, `set`, `reset` for state management
  - Fixed source→directory mapping in page_pipeline.py and upload_to_minio.py (UNDP ERC → undp, etc.)
  - Tested with 8 UNDP docs: all processed successfully, idempotency verified on rerun
  - Status breakdown: 8 docs at 'processed' status
  - Environment variables supported: MINIO_ENDPOINT, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD
  - Pending: actual MinIO upload/indexing (requires live endpoints)

## Template for new entries
- YYYY-MM-DD Name: [Activity] - [Result/notes]. Include doc counts, errors, endpoints used, and links to manifests or validation artifacts.
