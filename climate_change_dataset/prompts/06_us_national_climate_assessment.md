# Prompt 06 – U.S. National Climate Assessments (NCA1–NCA5)

**Purpose**: Build a local mirror of the U.S. National Climate Assessment reports (full volumes + chapters) for NCAs 1 through 5.

**Instructions**
1. Access https://www.globalchange.gov/nca5 (and archives for earlier NCAs via https://www.globalchange.gov/nca*) — if DNS blocks appear, use the NOAA/USGCRP mirror or the open data download packages.
2. Download chapter PDFs (NCA5 has 32+ chapters; earlier NCAs fewer). Start with Synthesis + Overview + national chapters. Save to `data/reports/us/nca<N>/`.
3. Filenames: `US_NCA<N>_CH<##>_<Short_Title>.pdf`.
4. After each download, compute SHA256 and update `metadata/manifest.csv` with:
   - `source_id = us/nca<N>/ch<##>`
   - `title = NCA<N> Chapter <##>: <Full Title>`
   - `document_type = report`
   - `split = chapter`
   - `license = USGCRP Terms` (quote the exact notice from site)
   - `notes = region/sector focus`
5. If direct download is blocked, use the GitHub release archives (NCA5 is mirrored at https://github.com/GlobalChange/nca5-content).
6. Keep chapter batches small to ease review (e.g., commit every 5–6 chapters).

**Expected Output**
- A growing library of US climate assessment PDFs with manifest entries for each chapter.
