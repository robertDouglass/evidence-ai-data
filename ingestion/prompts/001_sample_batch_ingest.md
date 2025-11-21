# Prompt 001 – Sample Batch Ingest (Local → Vespa/OpenSearch)

## Goal
Ingest a small, real subset (8–10 PDFs) from the corpus using the unified manifest, produce page artifacts, upload to MinIO, and index into live Vespa/OpenSearch without changing Fly deployments. Capture results in WORKLOGs.

## Inputs
- Manifest: `ingestion/output/manifest.jsonl` (latest, 0 restricted)
- Buckets/Endpoints (Fly internal):
  - MinIO: `http://evidenceai-minio.internal:9000` (`admin` / `dev_minio_password_change_in_prod`)
  - Vespa: `http://evidenceai-vespa.internal:8080`
  - OpenSearch: `http://evidenceai-opensearch.internal:9200`
- Target subset: pick ~8–10 real PDFs (avoid stubs), e.g.:
  - IKI (1), World Bank (2), DEval (2–3), OECD (1), PTB (1), UNDP (1 optional)

## Steps
1) **Generate/refresh manifest (if needed)**
   - `python3 ingestion/manifest_builder.py --output ingestion/output/manifest.jsonl`
   - Verify `restricted=0`.
2) **Implement/verify page pipeline (local)**
   - `ingestion/page_pipeline.py` (Docling/OCR → page images + markdown/text) — if missing, add it using the schema in `SCHEMA.md`.
   - Ensure outputs land under `documents-processed/{doc_id}/...` and `document-images/{doc_id}/...`.
3) **Implement/verify uploader**
   - `ingestion/upload_to_minio.py` to push raw PDFs, processed md/pdf, and images to MinIO buckets (`documents-raw`, `documents-processed`, `document-images`).
4) **Indexing**
   - Update `evidence-ai/apps/colpali/etl/indexer.py` to read the manifest (not Postgres) and push:
     - Vespa: full ColPali tensor per page.
     - OpenSearch: BM25 text, MiniLM text embeddings, mean-pooled ColPali (128-d).
   - Run indexing against live endpoints; constrain to the chosen subset.
5) **Validate**
   - Vespa doc/page counters; OpenSearch index stats.
   - Run a few sample queries (text + visual) to ensure hits.
6) **Log results**
   - `ingestion/WORKLOG.md` (what ran, docs/pages indexed, any errors).
   - If relevant, add brief validation notes to `fly/WORKLOG.md` (no redeploys).

## Done when
- Sample subset fully indexed in Vespa/OpenSearch.
- Logs include counts and any issues. Prompt 001 marked complete in worklog.
