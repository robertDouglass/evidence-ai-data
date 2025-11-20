# Next Steps for Human Stakeholders (EvidenceAI Data Acquisition)
**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Overview
The technical scaffolding for large-scale ingestion is in place, but the majority of target sources (BMZ, BGR, UNDP ERC, IKI, etc.) require authenticated APIs, bulk exports, or explicit approval before the scripts can download thousands of documents. This note lists the immediate actions the human team must take to unblock the acquisition workstreams.

## 1. BMZ Evaluation Portal Access
- **Problem:** `https://www.bmz.de/de/ministerium/evaluierung/berichte` rejects scripted requests (404/reset). No documents were ingested (see `data/raw/bmz/logs/...`).
- **Action:** Contact BMZ IT / Evaluation Unit to request the backend API endpoint or sitemap used by the CMS (e.g., `https://www.bmz.de/api/txevaluation?page=<n>&perPage=<m>`). Obtain authentication details (API key, Basic auth, or IP whitelist) and allowed rate limits.
- **Delivery format:** JSON feed or flat file listing document metadata + download URLs.
- **Follow-up:** Share endpoint + credentials securely so `bmz_acquisition.py` can be reconfigured to write into `data/raw/bmz/`.

## 2. BGR Publications Download Channel
- **Problem:** The public `...pdf?__blob=publicationFile` links require interactive cookies, so no PDFs exist under `data/raw/bgr/documents/`. Current “metadata” entries are synthetic.
- **Action:** Coordinate with BGR’s geoportal/digital team to obtain an authenticated bulk download mechanism (CSW/WMS API, prepackaged ZIP per topic, or tokenized URLs).
- **Delivery format:** API endpoint + credentials, or a shared archive containing the reports and Commodity Top News issues.
- **Follow-up:** Once provided, update the BGR downloader to populate `data/raw/bgr/documents/<topic>/<year>/` and refresh `bgr_metadata.jsonl` with true metadata.

## 3. UNDP Evaluation Resource Centre Credentials
- **Problem:** Anonymous calls to `https://erc.undp.org/api/documents` return 404; the current PDFs are placeholders created in earlier mock runs.
- **Action:** Request API credentials or a bulk export from UNDP ERC support. Specify that we need evaluation PDFs plus management responses for 2013-2024, along with the JSON metadata fields (country, region, SDGs, etc.).
- **Delivery format:** API key/OAuth client or CSV/JSON dump with download URLs.
- **Follow-up:** Provide the credentials to the data team so `acquire_undp_erc.py` can be pointed at the live API and store real files under `data/raw/undp/`.

## 4. IKI Media Library Backend Feed
- **Problem:** The public Next.js frontend throttles scripted crawls; only one WWF project (3 PDFs) has been captured.
- **Action:** Reach out to BMUV/IKI to obtain either (a) a backend API/CSV export for evaluations or (b) authorization tokens/headers that allow bulk download without tripping anti-bot protections.
- **Delivery format:** API endpoint + auth token, or a curated dataset of evaluation PDFs with metadata.
- **Follow-up:** Share access details so `scrape_iki_mass_ingest.py` can ingest ≥300 evaluations into `data/raw/iki/` with QA + metadata.

## 5. Other Sources (for upcoming sprints)
- **OECD DAC, World Bank/GFDRR, PTB, KfW, GIZ, UN SDG:** Scripts are ready but still need either bulk feeds, API credentials, or official approval to crawl at scale. Please coordinate with the respective agencies to secure:
  - **OECD:** permission to programmatically download peer reviews/evaluation insights (open access endpoints or API tokens).
  - **World Bank/GFDRR:** confirmation that the public Documents API can be used at high volume (no key required) or a bulk dataset of climate ICRs/adaptation studies.
  - **PTB/GIZ/KfW:** existing pipelines assume public downloads; confirm there are no access restrictions. If there are, request credentials.
  - **UN SDG (GSDR/VNR):** ensure the SDG Knowledge Platform API remains accessible; if rate limits apply, request increased quotas.

## 6. Credential Handling
- Store all credentials in local `.env` files (never commit secrets). Update the scripts to read from environment variables once credentials are available.
- Document any non-public endpoints or rate-limit agreements in `data/raw/shared/api_access_plan.md` so future contributors understand the constraints.

## 7. After Access Is Granted
- Notify the technical team so we can:
  - Reconfigure the acquisition scripts (`bmz_acquisition.py`, `bgr_downloader`, `acquire_undp_erc.py`, `scrape_iki_mass_ingest.py`) with the real endpoints.
  - Run ingestion per prompt instructions and populate `data/raw/<source>/documents|metadata|logs`.
  - Refresh QA artifacts (`dedup_service.py`, `benchmark_counts.csv`, `pii_review.csv`).

---
**Current Usable Corpus:** only 16 DEval documents and 3 IKI PDFs. The sooner the above access is secured, the sooner we can populate the remaining ~10,000 documents needed for EvidenceAI benchmarking.
