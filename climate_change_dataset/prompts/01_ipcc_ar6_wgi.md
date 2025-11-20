# Prompt 01 – IPCC AR6 Working Group I (Physical Science Basis)

**Goal**: Download and catalog every chapter, Summary for Policymakers (SPM), and Technical Summary PDF from the official IPCC AR6 WGI repository.

**Tasks**
1. Use https://www.ipcc.ch/report/ar6/wg1/ (and linked download subpages) to identify the full list of PDFs (chapters, annexes, SPM, Technical Summary).
2. Save files under `data/reports/ipcc/ar6_wgI/` with the naming pattern `IPCC_AR6_WGI_<Section>_<Short_Title>.pdf`.
3. For each file compute SHA256, capture page count (via `pdfinfo`) and add a manifest row with:
   - `source_id`: `ipcc/ar6/wgI/<section>`
   - `title`: exact IPCC title
   - `document_type`: `report`
   - `split`: `chapter` / `spm` / `technical_summary`
   - `download_url`: direct PDF link from ipcc.ch
   - `license`: `IPCC Terms of Use`
   - `notes`: 1-line scope description.
4. Do **not** redownload files already mirrored; skip when `metadata/manifest.csv` already lists the file+A hash.

**Deliverables**
- All AR6 WGI PDFs stored locally and tracked in Git LFS.
- Updated `metadata/manifest.csv` rows for each section.
- Brief summary in PR/commit note enumerating how many WGI documents were added.
