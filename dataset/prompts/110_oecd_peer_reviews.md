# 110 – OECD DAC Peer Reviews & Evaluation Insights

**Goal:** Operationalize the OECD acquisition scripts (now in `dataset/modules/oecd/`) and populate `data/raw/oecd/` with ≥200 open-access documents (peer reviews + Evaluation Insights) plus structured metadata.

## To-Do
1. **Relocate scripts**: confirm `dataset/modules/oecd` is on PYTHONPATH or run from that directory.
2. **Open-access crawl**: query the OECD iLibrary for open publications, download full PDFs into `data/raw/oecd/documents/peer_reviews/<country>/<year>/` and `.../eval_insights/<topic>/`.
3. **Metadata processing**: run `metadata_processor.py` to create `data/raw/oecd/metadata/oecd_dac_metadata.jsonl` and summary stats.
4. **Validation suite**: execute `validation_and_testing.py` (or equivalent) and store results/logs in `data/raw/oecd/logs/`.
5. **DOI/licensing file**: produce `data/raw/oecd/metadata/oecd_open_access_sources.csv` documenting DOI + license for each download.

## Acceptance Criteria
- ≥200 documents downloaded (log breakdown by peer review vs insights)
- Metadata fields include donor_country, sdg_focus, keywords, publication_year
- Validation log highlights any PDFs that required EPUB → PDF conversion
