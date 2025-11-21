# Ingestion Worklog

- 2025-11-22 Codex (GPT-5): Added INGESTION_PLAN.md with unified schema and multi-phase rollout; pending: schema update, manifest builder, Docling GPU test, test batch ingest.
- 2025-11-22 Codex (GPT-5): Implemented unified schema v2 (data/raw/metadata_schema.yaml), added SCHEMA.md reference, created manifest_builder.py. Added path fallback search, year inference, doc_type/lang defaults. Created stubs for missing BGR commodity/investigation and OECD files (to be replaced with real PDFs later), added IKI doc copy. Regenerated manifest (ingestion/output/manifest.jsonl) now has 0 restricted records; required fields populated with hashes/sizes (stubs included). Notes retain `publication_year_unknown` where applicable.
- 2025-11-22 Codex (GPT-5): Prompt 001 prep – added `ingestion/page_pipeline.py` (placeholder text extraction if PyPDF2 missing). Ran pipeline on 5 target docs (manifest doc_ids: IKI-EVAL-2025-001, WB-CLIM-D34442285/277/284/292); generated processed markdown + copied PDFs under ingestion/output/processed/. Pillow not installed, so images were skipped. Added `ingestion/upload_to_minio.py` (not yet executed; requires boto3/MinIO access). Pending: generate images (install Pillow) and upload + index subset into Vespa/OpenSearch once indexer manifest support is ready.

## Template for new entries
- YYYY-MM-DD Name: [Activity] - [Result/notes]. Include doc counts, errors, endpoints used, and links to manifests or validation artifacts.
