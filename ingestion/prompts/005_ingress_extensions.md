# Prompt 005 – Ingress Extensions (Online Sources & User Uploads)

## Goal
Define and implement ingestion entry points for external sources and user uploads, reusing the unified schema and Fly worker pipeline.

## Steps
1) **User upload flow**
   - Design API/endpoint or signed-URL flow to receive PDFs + optional metadata JSON.
   - Write binaries to MinIO `documents-raw/uploads/<user>/<doc_id>.pdf`; store metadata stub and enqueue for processing.
   - Default `restricted=true` until QA/PII checks pass.
2) **Online sources**
   - Add fetcher templates that pull binaries + metadata and write to MinIO `documents-raw/<source>/...`.
   - Emit manifest entries or enqueue doc_ids directly.
3) **Metadata normalization**
   - Reuse manifest builder logic on Fly: normalize fields, compute hash/size, set status `uploaded`.
4) **Triggers**
   - Wire uploads/fetchers to enqueue the Fly worker (Prompt 004).
   - Add rate limits and dedup by hash/doc_id.
5) **Security & gating**
   - Require auth/ACL for uploads; flag restricted/PII; allow manual approval before indexing.
6) **Test**
   - Simulate one user upload and one external fetch; ensure they flow through to `processed`/`indexed`.
7) **Log**
   - Document endpoints, commands, and results in WORKLOGs.

## Done when
- Upload + external fetch paths land binaries in MinIO, normalize metadata, and flow through the Fly worker/indexer with gating.
