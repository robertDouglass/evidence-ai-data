# BGR Publication Acquisition Guide

## Access Issues & Solutions

The BGR website has protection against automated scraping. This guide provides both manual and semi-automated approaches.

## Manual Acquisition Process

### Step 1: Access the BGR Repository
1. Visit: https://www.bgr.bund.de/EN/Themen/Publikationen/publikationen_node_en.html
2. Click on "Publikationen" (Publications) in the top menu
3. You'll see a searchable list with filters

### Step 2: Apply Filters
Look for filter options to narrow down results:
- **Type:** Select "Reports" (Berichte)
- **Topic:** Select "International Cooperation" (Internationale Zusammenarbeit)
- **Year Range:** 2013-2024
- **Language:** English (English) or German (Deutsch)

### Step 3: Navigate Through Results
- The repository uses pagination (`?q=&page=1`, `?q=&page=2`, etc.)
- Each page typically shows 10-20 results
- Total available: 1,000+ publication entries
- Manually iterate through pages or use the search box

### Step 4: For Each Publication
1. **Click the publication title** to open detail page
2. **Capture metadata:**
   - Title
   - Authors
   - Year
   - Language
   - Abstract/Description
   - ISBN (if available)
   - Keywords
   - Series/Issue number

3. **Download the PDF:**
   - Look for "Download" or PDF icon
   - The PDF URL typically follows pattern: `...?__blob=publicationFile`
   - Save with naming: `bgr_<topic>_<year>_<slug>.pdf`

4. **Create metadata file:**
   - Save as `metadata/BGR-<series>-YYYY-###.json`
   - Follow the schema in `metadata_schema.json`
   - Update `metadata_registry.jsonl` with entry

### Step 5: Quality Check
Before adding to registry, verify:
- ✓ PDF successfully downloaded
- ✓ Page count ≥ 10
- ✓ Document is policy/evaluation focused (not raw dataset)
- ✓ All required metadata fields populated
- ✓ Set `quality_checked: true`

### Step 6: Supplement with Commodity Top News
1. Visit: https://www.bgr.bund.de/EN/Themen/Rohstoffe/CommodityTopNews/commodity_top_news_node_en.html
2. Browse the archive for climate/SDG-relevant content
3. Apply same acquisition process for matching publications

## Programmatic Approach (Python)

If you want to automate with Python, see `acquisition_script_template.py` in this directory. This requires:
- Respecting robots.txt
- Adding delays between requests
- Being prepared to handle anti-scraping measures

## Recommended Workflow

For ~650 publications, recommended approach:
1. **Days 1-3:** Manual search and filtering to understand repository structure
2. **Days 4-10:** Batch download key publications by topic (groundwater, mining, climate risk)
3. **Days 11-15:** Process Commodity Top News supplementary materials
4. **Days 16+:** Fill gaps with targeted searches

## Topics to Prioritize

Focus acquisition on these topics (supporting relevant SDGs):

### SDG 6 (Clean Water & Sanitation)
- Groundwater management reports
- Water security assessments
- Hydrogeology studies
- Transboundary water cooperation

### SDG 12 (Responsible Consumption & Production)
- Sustainable mining practices
- Mining governance frameworks
- Circular economy in extractive industries
- Mineral resource assessment

### SDG 13 (Climate Action)
- Climate risk to mining operations
- Geoscience data for climate adaptation
- Geological hazards and resilience
- Climate change impact assessments

### SDG 15 (Life on Land)
- Land degradation from mining
- Biodiversity impact assessments
- Soil and land restoration
- Ecosystem service valuation

## Expected Metadata Example

Once you acquire a publication, create a metadata file like:

```json
{
  "doc_id": "BGR-GMB-2021-015",
  "title": "Sustainable Mining and Climate Resilience in West Africa",
  "authors": ["Schmidt, H.", "Mueller, K.", "Weber, J."],
  "year": 2021,
  "language": "en",
  "topic": "mining_governance",
  "region": "West Africa",
  "document_type": "report",
  "pages": 156,
  "isbn": "978-3-942315-42-1",
  "series": "German Technical Cooperation Reports",
  "issue_number": "GMB-2021-015",
  "abstract": "This comprehensive report examines sustainable mining practices...",
  "keywords": ["mining", "climate", "sustainability", "west africa", "sdg"],
  "sdg_tags": ["SDG_12", "SDG_13"],
  "url": "https://www.bgr.bund.de/EN/Themen/Publikationen/...",
  "pdf_url": "https://www.bgr.bund.de/...?__blob=publicationFile",
  "pdf_filename": "bgr_mining_governance_2021_west_africa_sustainability.pdf",
  "download_date": "2024-11-19T14:30:00Z",
  "related_ids": [],
  "quality_checked": true,
  "notes": "High quality evaluation report with policy recommendations"
}
```

Then add one-line entry to `metadata_registry.jsonl`:
```
{"doc_id": "BGR-GMB-2021-015", "title": "Sustainable Mining and Climate Resilience in West Africa", "year": 2021, "topic": "mining_governance", "status": "acquired"}
```

## Next Steps

1. Visit the BGR repository using the links above
2. Start with 5-10 publications to establish the workflow
3. As you acquire publications:
   - Save PDFs to `pdfs/` directory
   - Save metadata JSON to `metadata/` directory
   - Update `metadata_registry.jsonl`
4. Report progress and share findings

Good luck with the acquisition!
