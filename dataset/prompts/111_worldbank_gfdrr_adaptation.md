# 111 – World Bank & GFDRR Climate Adaptation Evidence

**Goal:** Run a large-scale pull of Implementation Completion Reports, Impact Evaluations, and GFDRR studies related to climate adaptation/resilience (≥1,000 PDFs) and store them under `data/raw/worldbank/`.

## Execution Plan
1. **World Bank API**: use `https://search.worldbank.org/api/v2/wds` with filters (`topic_exact:Climate Change`, `doctype_exact:Implementation Completion Report|Impact Evaluation|Policy Research Working Paper`) and iterate offsets until exhaustion.
2. **Downloads**: save PDFs as `data/raw/worldbank/documents/wb_icr/<repnb>.pdf` (or relevant subfolders). Capture multi-volume docs as `<repnb>_vol2.pdf`, etc.
3. **GFDRR**: scrape the GFDRR publications page filtered for reports and ingest them under `documents/gfdrr/` with consistent naming.
4. **Metadata**: produce `data/raw/worldbank/metadata/worldbank_climate_metadata.jsonl` capturing doc_type, country, region, project_id, SDG tags, publication_year, license.
5. **QA logs**: record download failures and large annexes (skip raw data annexes) in `data/raw/worldbank/logs/worldbank_crawl.log` and a JSON summary.

## Success Metrics
- ≥1,000 documents stored (log breakdown by doc_type)
- 100% of entries have `project_id` (repnb) and `country` fields
- Clear record of skipped annexes/PII
