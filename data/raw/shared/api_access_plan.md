# API & Credential Access Plan (BMZ, BGR, UNDP ERC, IKI)
**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

## 1. BMZ Evaluations & Country Concepts
- **Current blocker:** HTML crawl endpoints return 404/connection resets; CMS requires authenticated API calls (see `data/raw/bmz/logs/bmz_crawl_20251119_154500.log`).
- **Ask BMZ IT:** Provide the evaluation listing API (e.g. `https://www.bmz.de/api/txevaluation?page=<n>&perPage=<m>`) or a sitemap export plus authentication (API key, Basic auth, or IP allow list). Confirm query params and rate limits.
- **After access:** Load credentials via env vars and update `bmz_acquisition.py` to write PDFs/metadata directly into `data/raw/bmz/...`.

## 2. BGR Georesource & Climate Publications
- **Current blocker:** `...pdf?__blob=publicationFile` links require session cookies; no PDFs exist yet in `data/raw/bgr/documents/` (metadata created via `scraper_v3.py`).
- **Ask BGR Geoportal/Digital Unit:** Supply an authenticated download channel (e.g., CSW/WMS API, bulk ZIP, or tokenized links) for the report series and Commodity Top News. Include credentials and examples for topic/year filters.
- **After access:** Replace the synthetic importer with a true downloader storing files under `data/raw/bgr/documents/<topic>/<year>/` and update metadata accordingly.

## 3. UNDP Evaluation Resource Centre (ERC)
- **Current blocker:** Anonymous API calls (`https://erc.undp.org/api/documents`) return 404; placeholder PDFs remain (log: `data/raw/undp/logs/undp_acquisition.log`).
- **Ask UNDP ERC Support:** Issue API credentials (API key/OAuth client) or bulk export. Provide request limits, filter options, and download URL patterns (PDF + management response). Specify required headers/cookies.
- **After access:** Update the ERC acquisition script to pull real data into `data/raw/undp/documents/<region>/<year>/` and refresh `undp_erc_metadata.*`.

## 4. IKI Media Library (Evaluations)
- **Current blocker:** Public Next.js pages throttle scripted crawls; only sample WWF PDFs available.
- **Ask BMUV/IKI Team:** Provide backend API, CSV export, or authenticated token for the media library evaluation catalog (including file URLs) plus allowed request rates.
- **After access:** Integrate the endpoint/token into `scrape_iki_mass_ingest.py` so ≥300 evaluations can be downloaded with metadata + QA logs.

---
**Implementation Notes**
- Store all credentials in local `.env` files (never commit). Load via environment variables inside each script.
- Update the corresponding prompts once endpoints/keys are available.
- After ingestion succeeds, rerun `data/raw/shared/dedup_service.py` and refresh `benchmark_counts.csv` to reflect new totals.
