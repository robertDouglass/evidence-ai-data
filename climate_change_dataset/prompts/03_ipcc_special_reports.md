# Prompt 03 – IPCC Special & Methodology Reports

**Scope**
- SR1.5, SRCCL, SROCC, Cities Special Report (when available), 2019 Refinement to 2006 Guidelines, Methodology for Short-Lived Climate Forcers, and AR6 Synthesis Report.

**Instructions**
1. For each report, use its landing page under https://www.ipcc.ch/reports/ to collect all PDF assets (SPM, full report, annexes).
2. Save them under `data/reports/ipcc/special_reports/<REPORT_CODE>/`.
3. Filenames: `IPCC_<REPORT_CODE>_<Section>.pdf`.
4. Capture metadata in `metadata/manifest.csv`:
   - `source_id`: `ipcc/special/<report_code>/<section>`
   - `title`: official section title
   - `document_type`: `report`
   - `split`: `spm`, `full_report`, `annex`, etc.
   - `notes`: highlight whether the document covers mitigation, adaptation, physical science, etc.
5. Respect IPCC download servers; avoid parallel downloads >3 at a time.
6. If a PDF already exists locally (matching filename/hash), skip and confirm manifest row is present.

**Deliverable**
- Populated `data/reports/ipcc/special_reports/` with every selected report and manifest entries ready for RAG ingestion.
