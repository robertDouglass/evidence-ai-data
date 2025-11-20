# 101 – BMZ Evaluations & Country Concepts (Full Crawl)

**Goal:** Move beyond mock runs and download the full 2015-2025 BMZ evaluation corpus (evaluations, Länderstrategien, SDG briefs) into `data/raw/bmz/` with at least 800 unique PDFs + JSONL metadata.

## Immediate Tasks
1. **Implement pagination + sitemap crawl** inside `bmz_acquisition.py` so it iterates through all evaluation portal pages and every country page listed under `/laender`.
2. **Run production crawl** (no `--mock-data`). Use exponential backoff (429 aware) and persist raw HTML snapshots for failed pages under `data/raw/bmz/logs/`. This requires access to BMZ’s authenticated evaluation API or sitemap export (request base URL + credentials from BMZ IT, e.g., `https://www.bmz.de/api/txevaluation?page=<n>&perPage=50`).
3. **Metadata export:** Append to `data/raw/bmz/metadata/bmz_metadata.jsonl` (one record per document) and create a summary CSV with counts per year, document_type, SDG.
4. **PII guardrail:** Integrate regex scan (names, emails) and mark `pii_flag=true` in metadata for routing to the anonymization queue. Do **not** skip the document unless required by BMZ licensing.

## Storage Expectations
- Documents: `data/raw/bmz/documents/<year>/<doc_id>.pdf`
- Metadata: `data/raw/bmz/metadata/bmz_metadata.jsonl`, `bmz_summary.csv`
- Logs & crawl manifests: `data/raw/bmz/logs/bmz_crawl_<timestamp>.log`

## Quality Targets
- ≥95% of records with populated `publication_year`, `focus_country_region`, `sdg_tags`
- Deduplicate by SHA256 hash but keep both language variants when content differs
- Provide `data/raw/bmz/metadata/README_bmz_status.md` summarizing totals + notable gaps
