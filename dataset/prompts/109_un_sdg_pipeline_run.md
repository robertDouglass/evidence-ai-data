# 109 – UN SDG Monitoring Pipeline (Production Run)

**Goal:** Execute `acquire_un_sdg.py` (and tests) against the live SDG Knowledge Platform to ingest ≥800 documents (GSDR chapters, VNRs, thematic briefs) into `data/raw/un_sdg/`.

## Steps
1. **Finalize configuration**: specify the BMZ priority country list and year range (2016-2024) in the script settings/env vars.
2. **Run tests** (`python test_un_sdg_acquisition.py`) and capture the output into `data/raw/un_sdg/logs/un_sdg_tests.log`.
3. **Full acquisition**: `python acquire_un_sdg.py --pages 15` (or equivalent) with rate limiting; log progress to `data/raw/un_sdg/logs/un_sdg_crawl.log`.
4. **Storage**: place PDFs under `data/raw/un_sdg/documents/<document_type>/<year>/` and YAML metadata under `data/raw/un_sdg/metadata/` (one file per doc plus consolidated JSONL).
5. **Coverage report**: generate `data/raw/un_sdg/logs/un_sdg_summary.md` detailing counts per doc_type, country, SDG focus, and any failed downloads.

## Acceptance Criteria
- ≥800 documents saved locally with valid metadata
- YAML metadata includes `doc_id`, `document_type`, `country_or_region`, `sdg_focus`, `publication_year`, `issuing_body`
- Logs note API failures + retries
