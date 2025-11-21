# Prompt 004 – Fly Worker Orchestration (Processing → Indexing)

## Goal
Create a minimal Fly worker that consumes manifest entries, runs Docling (GPU) for page prep, and signals the indexer to push to Vespa/OpenSearch. Introduce basic control-plane state.

## Prereqs
- Prompts 001–003 completed locally; schemas stable; manifest validated.
- Fly endpoints: MinIO, Vespa, OpenSearch live and healthy.

## Steps
1) **State store**
   - Simple Postgres table or durable JSON-in-MinIO to track `doc_id`, `status` (`uploaded`, `processed`, `indexed`, `error`), timestamps, notes.
2) **Worker service**
   - Fly app that:
     - Consumes a queue/list of doc_ids (from manifest or state).
     - Runs Docling on GPU to produce page artifacts (writes to MinIO).
     - Marks status `processed` with page_count/quality.
3) **Indexer trigger**
   - After `processed`, call the existing indexer (or emit an event) to push to Vespa/OpenSearch.
   - Update status to `indexed` with counts; on failure, set `error` + reason.
4) **Ingress hooks (stub)**
   - Add a simple endpoint/Cron to enqueue doc_ids from the manifest for now (external/system uploads come later).
5) **Observability**
   - Basic logs/metrics for processed/indexed counts and failures.
6) **Test**
   - Enqueue a few doc_ids; confirm statuses and artifacts in MinIO; Vespa/OpenSearch receive pages.
7) **Log**
   - Record design/commands/results in WORKLOGs.

## Done when
- Fly worker processes and indexes a small batch end-to-end using live services, with status transitions visible.
