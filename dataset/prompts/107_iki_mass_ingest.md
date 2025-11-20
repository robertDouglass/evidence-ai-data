# 107 – IKI Climate/Biodiversity Evaluations (Quality-Gated Mass Ingest)

**Goal:** Scale the IKI scraper beyond the WWF sample to ≥300 evaluation reports, while enforcing stricter content filters so we avoid promotional assets. Store everything under `data/raw/iki/`.

## Tasks
1. **Update scraper filters**: only accept entries tagged as Evaluation/Report/Learning (exclude “Campaign”, “Event”, etc.) and inspect the `__NEXT_DATA__` JSON for `categories`.
2. **Content validation**: run NLP keyword checks ("evaluation", "results", "lessons", "recommendations") before downloading; log skipped promotional PDFs in `data/raw/iki/logs/iki_skip_log.csv`.
3. **Full crawl**: once BMUV/IKI provides the authenticated media-library API or bulk feed (the public Next.js endpoints throttle bots), paginate through the entire catalog (~70+ pages) and store PDFs at `data/raw/iki/documents/<region>/<year>/`.
4. **Metadata CSV/JSON**: write to `data/raw/iki/metadata/iki_evaluations_metadata.csv` and `iki_evaluations_metadata.jsonl` with doc_id, implementing partner, funding amount (if available), SDGs.
5. **QA rerun**: re-run `quality_check_iki.py` and ensure ≥90% of documents pass content validation. Save report to `data/raw/iki/logs/iki_quality_report.json`.

## Output Summary
Provide `data/raw/iki/logs/iki_execution_summary.md` describing total docs, pass rate, issues, and next steps.
