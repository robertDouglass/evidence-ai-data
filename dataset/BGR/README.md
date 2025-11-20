# BGR Publication Dataset

## Overview
This directory contains publications from BGR (Bundesanstalt für Geowissenschaften und Rohstoffe), focusing on:
- Sustainable mining and mining governance
- Groundwater management
- Climate risk analytics and geoscience data

**Goal:** Acquire ~650 publications (2013-2024) supporting SDGs 6, 12, 13, 15.

## Directory Structure

```
BGR/
├── README.md                    # This file
├── metadata_schema.json         # JSON Schema for metadata validation
├── metadata_registry.jsonl      # Registry of all acquired publications (JSONL format)
├── pdfs/                        # Downloaded PDF files
│   └── bgr_<topic>_<year>_<slug>.pdf
├── metadata/                    # Individual metadata JSON files (one per publication)
│   └── BGR-<series>-YYYY-###.json
└── raw_pages/                   # Raw HTML/text from repository pages (for reference)
```

## Metadata Schema

All publications must follow the schema defined in `metadata_schema.json`. Key fields:

- **doc_id**: Unique identifier (BGR-<series>-YYYY-###)
- **title**: Publication title
- **year**: Publication year (2013-2024)
- **language**: en, de, or bilingual
- **topic**: groundwater, mining_governance, geo_risk, sustainable_mining, climate_risk, other
- **document_type**: report, technical_brief, policy_brief, evaluation, research_paper
- **pages**: Must be ≥ 10
- **sdg_tags**: Array of relevant SDGs (SDG_6, SDG_12, SDG_13, SDG_15)
- **url**: Source URL
- **pdf_url**: Direct PDF download URL
- **pdf_filename**: Standardized filename (bgr_<topic>_<year>_<slug>.pdf)
- **abstract**: Publication abstract/summary
- **keywords**: Subject keywords
- **quality_checked**: Boolean indicating if quality criteria met
- **related_ids**: Links to related versions (e.g., bilingual versions)

## Quality Criteria

✓ Minimum 10 pages
✓ Policy- or evaluation-focused (not raw datasets without narrative)
✓ Metadata includes series/issue for referencing
✓ For bilingual reports: keep both versions, link via related_ids

## Acquisition Workflow

1. **Search BGR Repository**
   - URL: https://www.bgr.bund.de/EN/Themen/Publikationen/publikationen_node_en.html
   - Use repository search with filters: Type=Reports, Topic=International Cooperation
   - Iterate through pages using `?q=&page=` parameters

2. **Extract Data**
   - Title, authors, year, language
   - Download PDF and save with standardized filename
   - Extract abstract, ISBN, keywords from detail page
   - Document URL and PDF URL

3. **Create Metadata File**
   - Save individual JSON file: `metadata/BGR-<series>-YYYY-###.json`
   - Add entry to `metadata_registry.jsonl`
   - Ensure all required fields are populated

4. **Quality Check**
   - Verify page count ≥ 10
   - Confirm policy/evaluation focus
   - Validate metadata completeness
   - Set quality_checked = true only if all criteria met

5. **Commodity Top News**
   - Supplement with Climate/SDG-relevant "Commodity Top News" content
   - Scrape archive: https://www.bgr.bund.de/EN/Themen/Rohstoffe/CommodityTopNews/commodity_top_news_node_en.html

## File Naming Conventions

**PDF files:** `bgr_<topic>_<year>_<slug>.pdf`
- Example: `bgr_groundwater_2021_sustainable_mining_africa.pdf`
- Example: `bgr_climate_risk_2023_sea_level_impacts.pdf`

**Metadata files:** `BGR-<series>-YYYY-###.json`
- Example: `BGR-SGD-2021-001.json`
- Example: `BGR-GMB-2020-042.json`

## Progress Tracking

- Total target: ~650 publications
- Use metadata_registry.jsonl to track acquisition progress
- Monitor acquisition by year, topic, and SDG alignment

## Licensing & Attribution

BGR publications are open for citation under German government guidelines.
**Always cite BGR and keep copyright line in any derivatives.**

Confirm public-domain status per: https://www.bgr.bund.de/

## Data Access Issues & Solutions

⚠️ **IMPORTANT:** The main BGR website (bgr.bund.de) blocks automated scraping with 403 Forbidden errors.

**Solution:** Use legitimate, authorized access methods instead:
- ✅ **CSW Catalog Service** for metadata harvesting
- ✅ **WMS/WFS Services** for geospatial data
- ✅ **BGR Geoportal** for interactive search and download
- ✅ **GEO-LEOe-docs Repository** for open-access publications

📘 **See [BGR_DATA_ACCESS_INVESTIGATION.md](./BGR_DATA_ACCESS_INVESTIGATION.md)** for comprehensive investigation report

🚀 **See [QUICK_ACCESS_GUIDE.md](./QUICK_ACCESS_GUIDE.md)** for quick reference to endpoints and commands

## References

- BGR Publication Repository: https://www.bgr.bund.de/EN/Themen/Publikationen/publikationen_node_en.html
- BGR Geoportal: https://geoportal.bgr.de/
- CSW Catalog Service: https://geoportal.bgr.de/smartfindersdi-csw/api
- GEO-LEOe-docs (Open Access): https://e-docs.geo-leo.de/
- DERA Publications: https://www.deutsche-rohstoffagentur.de/
- Commodity Top News Archive: https://www.bgr.bund.de/EN/Themen/Rohstoffe/CommodityTopNews/commodity_top_news_node_en.html
