# 106 – BGR Georesource & Climate Publications

**Goal:** Replace the empty progress tracker with real acquisitions: scrape ≥200 BGR reports (groundwater, mining, climate risk, commodity news) into `data/raw/bgr/`.

## Steps
1. **Finish Phase 1 exploration** (already outlined) and document available filters + pagination in a short note stored in `data/raw/bgr/logs/bgr_filters.md`. Request BGR’s digital unit for an authenticated download channel (preferred: Geoportal CSW endpoint or bulk ZIP per topic) because `/Publikationen/...pdf?__blob=publicationFile` links require session cookies.
2. **Pilot download (first 50 docs)** once the API/token is issued to validate the URL templates, then scale topic by topic until ≥200 PDFs are stored under `data/raw/bgr/documents/<topic>/<year>/`.
3. **Metadata schema**: implement `data/raw/bgr/metadata/bgr_metadata.jsonl` capturing topic, region, SDG tags, document type, language, pages.
4. **Commodity Top News**: capture at least 30 SDG-relevant issues and store them separately under `documents/commodity_top_news/`.
5. **Status memo**: summarize counts + outstanding blockers in `data/raw/bgr/logs/bgr_status_<date>.md`.

## KPIs
- ≥200 PDFs downloaded this sprint (log total)
- At least 3 topics represented (groundwater, mining, climate risk)
- ≤5% documents missing SDG tags or page counts
