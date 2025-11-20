# 104 – DEval Publications (2015-2024 Archive Backfill)

**Goal:** Extend `acquire_deval_publications.py` to crawl the full DEval archive (2015 onwards), not just the current landing page, and ingest ≥400 unique PDFs into `data/raw/deval/` this week.

## Blocking Issues Identified
- Current script only sees the first 16 cards and saves everything under 2025.
- Author/commissioning body fields are mostly empty.

## Fix & Execute
1. **Pagination discovery**: sniff underlying API parameters (`?page=`, `?limit=`) or scrape year/category archives so every publication slug is queued.
2. **Dual-language handling**: when both DE/EN versions exist, store them as separate PDFs but share a `base_id` and cross-reference via `related_ids`.
3. **Metadata enrichment**: parse detail pages for authors, commissioning bodies, and SDG keywords; update JSON schema accordingly.
4. **Historical sweep**: iterate years 2015-2024, storing PDFs inside `data/raw/deval/documents/<series>/<year>/` and metadata JSONL in `data/raw/deval/metadata/deval_metadata.jsonl`.
5. **Progress report**: write `data/raw/deval/logs/deval_backfill_report.md` with counts per series/year and any inaccessible URLs.

## Success Definition
- ≥400 new documents (beyond the initial 16) with valid metadata
- `authors` and `commissioning_body` populated for ≥70% of entries
- Documented retry/backoff strategy + list of unresolved failures
