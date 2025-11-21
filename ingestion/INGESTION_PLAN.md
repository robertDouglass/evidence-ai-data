# EvidenceAI Ingestion Plan (Vespa + OpenSearch)

Plan for preparing and ingesting the corpus with the unified schema. Tooling and logs live in this `evidence-ai-data` repo; runtime indexers live in `evidence-ai`.

## Worklog (append entries)
- 2025-11-22 Codex (GPT-5): Drafted unified schema, multi-phase plan, and Docling GPU validation steps.
- TODO: Record schema finalization, manifest runs, Docling GPU tests, test-batch ingest, full ingest, and Fly deployments.

## Target Services & Buckets
- Vespa: `http://evidenceai-vespa.internal:8080`
- OpenSearch: `http://evidenceai-opensearch.internal:9200`
- MinIO: `http://evidenceai-minio.internal:9000` (`admin` / `dev_minio_password_change_in_prod`)
- Buckets: `documents-raw`, `documents-processed`, `document-images`

## Unified Schema (document-level)
- ids: `doc_id`, `source`, `title`, `subtitle?`, `file_hash_sha256`, `file_size_bytes`, `mime_type`, `original_url`, `local_path`, `downloaded_at`
- publication/time: `publication_date`, `publication_year`, `timeframe_start`, `timeframe_end`
- geography: `countries` (ISO2 list), `regions` (SSA/MENA/APAC/EUR/LAC/NA/Global/Multi), `admin1?`
- taxonomy: `document_type` (evaluation/policy_brief/technical_report/research_paper/annual_report/assessment/impact_report/concept_note/synthesis/other), `thematic_area` (controlled list), `sector_tags`, `sdg_tags` (SDG1–SDG17), `keywords`
- language: `language` (ISO 639-1), `alt_languages`
- quality/safety: `extraction_quality`, `text_extracted`, `pii_flag`, `restricted`, `exclude_from_search`, `license`, `quality_checked`
- counts: `page_count`, `word_count`, `image_count?`
- org/people: `organisation`, `implementing_partners`, `authors`
- summaries: `executive_summary`, `abstract`, `notes`
- relationships: `related_ids`, `bilingual_of`
- processing: `processed_date`, `version`, `pipeline_run_id`

## Page-Level Schema (inherited fields +)
- ids: `page_id={doc_id}_{page_num:04d}`, `doc_id`, `page_num`
- content: `page_text`, `text_snippet`, `chunk_id` (if grouping), `chunk_index`
- media: `s3_image_url`, `s3_markdown_url`, `s3_pdf_url`, `ocr_confidence?`
- embeddings: Vespa `colpali_embedding` tensor<float>(d_token[1031], dim[128]); OpenSearch `text_embedding` (384-d), `colpali_mean` (128-d)
- filters copied from doc: `source`, `organisation`, `document_type`, `regions`, `countries`, `thematic_area`, `sector_tags`, `sdg_tags`, `language`, `publication_year`, `restricted`, `exclude_from_search`, `license`
- audit: `indexed_at`, `file_hash_sha256`

## Multi-Phase Implementation
1) **Schema Finalization** (done)
   - `data/raw/metadata_schema.yaml` (v2), `ingestion/SCHEMA.md` with vocab/examples.
2) **Manifest Normalizer** (done)
   - `ingestion/manifest_builder.py` → `ingestion/output/manifest.jsonl` (0 restricted); infers paths/hashes/years and defaults doc_type/lang/title.
3) **Page Prep Pipeline (local)**
   - Build `ingestion/page_pipeline.py` to run Docling/OCR from manifest PDFs → per-page markdown/text + images; output to `documents-processed/{doc_id}/...` and `document-images/{doc_id}/...`.
4) **Staging to MinIO**
   - Build `ingestion/upload_to_minio.py` to push raw PDFs, processed outputs, and images to MinIO buckets; preserve hashes. Verify via `mc ls` or API.
5) **Sample Batch Ingest** (Prompt 001)
   - Follow `ingestion/prompts/001_sample_batch_ingest.md` to index 8–10 real PDFs into live Vespa/OpenSearch; log results.
6) **Local Control Loop** (Prompt 002)
   - Build `ingestion/runner.py` + state store to orchestrate manifest → page prep → upload → index idempotently; track statuses.
7) **Docling GPU Validation (Fly)** (Prompt 003)
   - Confirm GPU, health, one PDF processed into MinIO; record timings; log.
8) **Fly Worker Orchestration** (Prompt 004)
   - Minimal Fly worker to consume doc_ids, run Docling on GPU, trigger indexer, and track statuses.
9) **Ingress Extensions** (Prompt 005)
   - Design/implement upload endpoints and online-source fetchers writing to MinIO, normalizing metadata, and enqueueing processing with gating.
10) **Full Batch**
   - After prompts 001–004 validated, run full manifest (skip/replace stubs as needed); monitor stats/errors and log completion.

## Execution Notes
- Keep ingestion scripts here (`ingestion/`); runtime indexing stays in `evidence-ai`.
- Use internal endpoints on Fly for Vespa/OpenSearch/MinIO; add env overrides for local vs Fly.
- Avoid committing secrets; use Fly secrets for any deployed jobs.
- Prefer small, logged batches; capture metrics (docs/pages indexed, failures) in `ingestion/WORKLOG.md`.
