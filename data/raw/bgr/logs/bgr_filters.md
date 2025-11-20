# BGR Filters & Pagination Documentation

**Date:** 2025-11-19
**Organization:** Bundesanstalt für Geowissenschaften und Rohstoffe (German Federal Institute for Geosciences and Natural Resources)

## Main URLs

| Resource | URL |
|----------|-----|
| Main Website | https://www.bgr.bund.de |
| Geoportal | https://geoportal.bgr.de |
| Publications | https://www.bgr.bund.de/EN/Infothek/Publikationen/publikationen_node.html |
| BGR Reports | https://www.bgr.bund.de/EN/Infothek/Publikationen/BGR-Report/bgr-report_node.html |
| Commodity Top News | https://www.bgr.bund.de/SharedDocs/GT_Produkte/Commodity_Top_News/CTN_genTab_DE.html |

## Available Topics/Categories

### 1. Groundwater (Grundwasser)
- **Path:** `/DE/Themen/Grundwasser/` or `/Themen/Wasser/`
- **Key Publications:**
  - Groundwater and Climate Change reports
  - Groundwater situation assessments
  - Groundwater quality studies

### 2. Mining (Bergbau & Rohstoffe)
- **Path:** `/Themen/Min_rohstoffe/Bergbau_Nachhaltigkeit/`
- **Key Topics:**
  - Sustainability in mining
  - Mining regulations and compliance
  - Commodity market analysis
  - Human rights risks in mining

### 3. Climate Risk & Energy
- **Energy Studies:** `/DE/Themen/Energie/` (biennial publication)
- **Climate Focus:** "Groundwater and Climate Change" series
- **Energy Data:** Annual tables available

### 4. Commodity Top News
- **Series:** Monthly/regular publication
- **Categories:** Energie, Wasser, Rohstoffwirtschaft
- **URL Pattern:** `/DE/Gemeinsames/Produkte/Downloads/Commodity_Top_News/[CATEGORY]/[NUMBER]_[TOPIC].pdf`

## Four Main Departments

| Dept | Name | Focus |
|------|------|-------|
| B1 | Raw Materials (Rohstoffe) | Mineral commodities, markets |
| B2 | Groundwater and Soil | Water resources, soil science |
| B3 | Underground Storage | CO2 storage, strategic reserves |
| B4 | Geoscientific Information | Data management, international cooperation |

## Filters & Pagination

### Filter Options (Available in BGR search/Geoportal)
- **Topic/Subject area** - By thematic categories
- **Document type** - Reports, studies, fact sheets, maps
- **Time period/Year** - Publication year filtering
- **Author** - Contributing researchers
- **Keywords** - Free text search
- **Data type** - Geospatial, tabular, etc.
- **Language** - `/DE/` (German) or `/EN/` (English)

### Pagination Structure
- **Method:** Results-based filtering (not traditional page numbers)
- **Geoportal:** Supports advanced search with filtering
- **Direct links:** Topic pages list publications chronologically
- **Search:** Internal magnifying glass icon supports filtered queries

## PDF URL Patterns

### Standard Pattern
```
https://www.bgr.bund.de/[LANG]/[PATH]/[FILENAME].pdf?__blob=publicationFile&v=[VERSION]
```

### Example URLs

**Commodity Top News:**
```
https://www.bgr.bund.de/DE/Gemeinsames/Produkte/Downloads/Commodity_Top_News/Wasser/21_grundwasser.pdf?__blob=publicationFile&v=3
```

**Groundwater Reports:**
```
https://www.bgr.bund.de/EN/Themen/Wasser/Produkte/Downloads/groundwater_climate_change_pdf.pdf?__blob=publicationFile&v=3
```

**Mining Studies:**
```
https://www.bgr.bund.de/DE/Themen/Zusammenarbeit/TechnZusammenarbeit/Downloads/human_rights_risks_in_mining.pdf?__blob=publicationFile&v=2
```

### URL Components
- **Language:** `/DE/` (German) or `/EN/` (English)
- **Common paths:**
  - `/Gemeinsames/Produkte/Downloads/` - Shared products
  - `/Themen/[TOPIC]/` - Topic-specific content
  - `/SharedDocs/` - Shared documents
- **Query parameters:**
  - `?__blob=publicationFile` - **Required** for PDF access
  - `&v=[number]` - Version parameter (optional)

## Document Types Available

- BGR Reports (biennial, 2012-2022 in English)
- Activity Reports (1999-2011)
- Commodity Top News (numbered series)
- Energy Studies (biennial)
- Raw Materials Situation Reports (annual since 1980)
- Fact sheets & studies
- Maps and spatial data
- Policy advice documents
- Technical cooperation reports

## Legal & Scraping Considerations

### Terms of Service
- **Impressum:** `/DE/Service/Impressum/impressum_node.html`
- **Usage Terms:** Available on legal page
- **Privacy Policy:** Datenschutzerklärung linked from impressum

### Robots.txt
- Expected location: `https://www.bgr.bund.de/robots.txt`
- **Note:** Must check before scraping to respect crawl restrictions

### Copyright/Licensing
- BGR publications: Generally **free download** permitted
- Federal government agency (Ministry for Economic Affairs)
- **Action:** Check individual documents for license terms
- Reuse policies may apply to German federal government works

### Scraping Best Practices
1. ✅ Implement 2-5 second delays between requests (government site)
2. ✅ Check and respect `robots.txt` restrictions
3. ✅ Use `User-Agent` identifying your bot
4. ✅ Verify terms of use before mass download
5. ✅ Cache results to avoid duplicate requests
6. ✅ Monitor for rate limiting (429 responses)

## Geoportal Features

- **URL:** `https://geoportal.bgr.de/mapapps/resources/apps/geoportal/index.html?lang=en`
- **Standards:** Supports Web Map Service (WMS), OGC standards
- **Catalog Service:** CSW (Catalog Service for the Web) support likely
- **Features:** Advanced metadata search, spatial filtering, download

## Implementation Strategy

### Phase 1: Pilot (50 PDFs)
1. Start with Commodity Top News (structured, numbered)
2. Scrape Groundwater topic pages (topic-specific listings)
3. Test URL patterns and PDF download validation
4. Capture basic metadata (title, date, URL, file size)

### Phase 2: Scale (200+ PDFs)
1. Expand to Mining/Commodity news section
2. Add Energy Studies and Climate-related reports
3. Collect data across multiple years
4. Implement full metadata extraction

### Phase 3: Metadata & SDG Tagging
1. Parse PDF metadata (title, author, date)
2. Extract page counts
3. Assign SDG tags based on content classification
4. Validate metadata completeness (≤5% missing)

## Tags for Tracking

**Topics to prioritize:**
- `groundwater` - All groundwater-related publications
- `mining` - Mining sustainability and commodities
- `climate-risk` - Climate change and environmental impact
- `commodity-news` - Commodity Top News series
- `energy` - Energy studies and data

**SDG Alignment:**
- SDG 6: Clean Water and Sanitation (groundwater focus)
- SDG 12: Responsible Consumption (mining sustainability)
- SDG 13: Climate Action (climate risk reports)
- SDG 15: Life on Land (soil, environmental impact)
