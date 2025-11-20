# Prompt 05 – UNEP Emissions Gap Reports (2010–2025)

**Goal**: Download every UNEP Emissions Gap Report plus appendices/addenda.

**Steps**
1. Use https://unepccc.org/emissions-gap-reports/ (and older archive pages) to gather links for 2010–2025 editions.
2. Store files under `data/reports/unep/emissions_gap/` named `UNEP_Emissions_Gap_Report_<YEAR>.pdf`.
3. Capture any supplemental chapters or data annexes separately (e.g., `..._<Supplement>.pdf`).
4. For each document, update `metadata/manifest.csv`:
   - `source_id = unep/emissions_gap/<year>[#supplement]`
   - `title = Emissions Gap Report <YEAR>: <subtitle>`
   - `document_type = report`
   - `split = main` or `supplement`
   - `download_url =` canonical UNEP URL.
   - `notes = summarize key scope (mitigation ambition, NDC gap, etc.)`
5. Cite license/terms exactly as provided on the download site (typically “© United Nations Environment Programme”).
6. Prior to downloading, check for existing files to avoid duplicates.

**Deliverables**
- 15+ UNEP PDFs mirrored with metadata referencing their original URLs.
