# Prompt 04 – WMO State of the Global Climate Series

**Objective**: Collect the annual WMO “State of the Global Climate” reports (at least 2020–2024) plus associated Extremes/Indicators supplements.

**Process**
1. Source URLs: https://wmo.int/publication-series/state-of-global-climate-<YEAR>. Follow the “View Report” link to download the PDF.
2. Save under `data/reports/wmo/state_of_climate/` with `WMO_State_of_Global_Climate_<YEAR>.pdf`.
3. If supplements exist (Indicators dashboard, Extremes), store as `WMO_State_of_Global_Climate_<YEAR>_<Supplement>.pdf`.
4. Append manifest entries with `source_id=wmo/state_of_climate/<year>`, `document_type=report`, `split` = `main` or `supplement`, license `WMO Terms`.
5. Note key content focus in `notes` (e.g., “Annual temperature anomalies, extremes, socio-economic impacts”).
6. Validate PDF integrity (open + check file size) before committing.

**Result**
- Multi-year WMO reports mirrored locally with metadata ready for RAG citations.
