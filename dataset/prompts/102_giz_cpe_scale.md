# 102 – GIZ Central Project Evaluations (2020-2024 Bulk Download)

**Goal:** Use `acquire_giz_cpe.py` to harvest the entire 2020-2024 CPE catalog (≥900 PDFs) with verified metadata in `data/raw/giz/`.

## Immediate Tasks
1. **Enable JSON/REST access**: inspect the network tab for `/services/REST/` calls and request pages sequentially until no new IDs remain; fall back to HTML pagination only if the API is blocked.
2. **Automate file downloads** (DE+EN) and store as `data/raw/giz/documents/<year>/giz_cpe_<doc_id>_<lang>.pdf`.
3. **Metadata pipeline**: write to `data/raw/giz/metadata/giz_cpe_metadata.jsonl` plus `giz_registry.csv` capturing doc_id, partner country, SDG tags, and evaluation ratings.
4. **Quality checks**: generate `data/raw/giz/logs/giz_qc_report.json` summarizing missing fields, page-count validation (>20 pages), and duplicates.

## Delivery Checklist
- ✅ ≥900 PDFs downloaded (log actual count)
- ✅ Metadata coverage for commissioning unit, partner country, thematic cluster, SDGs
- ✅ README describing any countries/sectors still missing
- ✅ Evidence of deduplication across bilingual pairs
