# Prompt 08 – USGS Climate Science Publications

**Goal**: Pull a curated batch of USGS climate-related publications (white papers, fact sheets, technical inputs) from https://pubs.usgs.gov/ and https://www.usgs.gov/science/science-explorer/climate.

**Actions**
1. Use the Publications Warehouse API (`https://pubs.er.usgs.gov/pubs-services/publication/?text=climate%20change&mimeType=pdf`) to list recent works (filter by year/geography as needed).
2. Download at least 50 unique PDFs across topics (sea-level rise, wildfire, water, ecosystems).
3. Place them under `data/reports/usgs/<short_slug>/`.
4. Update manifest rows:
   - `source_id = usgs/<slug>`
   - `title = Publication title`
   - `document_type = report`
   - `split = main`
   - `license = USGS Public Domain`
   - `notes = short abstract or subject`.
5. Keep the USGS citation info (authors, DOI) in a sidecar JSON or include in notes for easy referencing.
6. Avoid duplicates: check file hashes before saving.

**Outcome**
- A sizeable stack of USGS-authored climate science PDFs with metadata ready for RAG indexing.
