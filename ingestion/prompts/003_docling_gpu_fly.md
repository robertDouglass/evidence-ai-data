# Prompt 003 – Docling GPU Validation on Fly

## Goal
Validate Docling/OCR on Fly with GPU for throughput. Keep local-first parity; do not alter Vespa/OpenSearch schemas.

## Prereqs
- Fly app for Docling exists; GPU machine type set in fly.toml (e.g., A10).
- Internal MinIO available: `http://evidenceai-minio.internal:9000`.

## Steps
1) **Deploy (cachebust)**
   - `flyctl deploy --build-arg CACHEBUST=$(date +%s) --build-only --no-cache` (if image changes needed).
2) **SSH & health**
   - `fly ssh console -a evidenceai-docling`
   - `nvidia-smi` to confirm GPU.
   - `curl -f http://localhost:<port>/health` (replace port if needed).
3) **Run a PDF**
   - Copy a real PDF from MinIO or curl a known sample.
   - Run Docling CLI/API to produce page images + markdown.
   - Verify outputs landed in MinIO (`documents-processed`, `document-images`).
4) **Performance note**
   - Capture elapsed time for a multi-page doc; compare to local CPU.
5) **Log**
   - `ingestion/WORKLOG.md` and `fly/WORKLOG.md`: commands, results, timings.

## Done when
- GPU confirmed, health OK, one PDF processed end-to-end with artifacts in MinIO, and timings recorded.
