# Prompt 02 – IPCC AR6 Working Group III (Mitigation)

**Goal**: Mirror the complete AR6 WGIII chapter set, SPM, and annexes.

**Steps**
1. Navigate https://www.ipcc.ch/report/ar6/wg3/ and enumerate every downloadable PDF (chapters, glossary, annex, SPM).
2. Store under `data/reports/ipcc/ar6_wgIII/` using `IPCC_AR6_WGIII_<Section>_<Short_Title>.pdf`.
3. Before downloading, check `metadata/manifest.csv` for existing `ipcc/ar6/wgIII/*` entries to avoid duplicates.
4. After each download, run `pdfinfo` to capture metadata, compute SHA256, and append a manifest row (`document_type=report`, `split` describing the section, license `IPCC Terms of Use`).
5. Verify each PDF opens and matches the official IPCC checksum (if published).

**Output**
- Locally stored WGIII PDFs tracked via Git LFS.
- Manifest rows for every WGIII section.
- Short summary in commit/PR referencing the number of files + any noteworthy download notes.
