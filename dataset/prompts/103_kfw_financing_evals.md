# 103 – KfW Financial Cooperation Evaluations (2013-2024)

**Goal:** Execute `dataset/kfw/acquisition_script.py` end-to-end to capture ≥900 KfW evaluation/thematic PDFs, bilingual variants, and metadata for SDGs 7/8/9/11/13 under `data/raw/kfw/`.

## Required Actions
1. **Configure `config.json`** with the final year range (2013-2024) and chunk size (max 200 docs per batch) to avoid timeouts.
2. **Implement evaluation servlet support** for both `EvaluationReportDownloadServlet` and `/blob/` URLs so no entries are skipped.
3. **Download + store** PDFs at `data/raw/kfw/documents/<year>/<doc_id>_<lang>.pdf`.
4. **Metadata & QA**:
   - Output `data/raw/kfw/metadata/kfw_metadata.jsonl` + `kfw_summary.csv` (counts by sector/region).
   - Generate `data/raw/kfw/logs/kfw_quality_report.json` with file sizes, page counts, language hints, financing volumes.
5. **Annual Reports**: fetch each yearly evaluation compendium and store under `documents/annual_reports/`.

## Acceptance Criteria
- ≥90% entries with financing volume + sector mapped to SDGs
- Documented handling of duplicate bilingual files
- Crawl log referencing number of retries/HTTP errors
