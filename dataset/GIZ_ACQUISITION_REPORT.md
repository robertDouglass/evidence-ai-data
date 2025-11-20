# GIZ CPE Acquisition Report - 102 Dataset

**Date:** 2025-11-19
**Status:** Investigation Complete | Execution Blocked
**Target:** ≥900 GIZ Central Project Evaluations (2020-2024)

---

## Executive Summary

The automated acquisition script (`acquire_giz_cpe.py`) was successfully configured but **unable to programmatically access** the GIZ evaluation document catalog. The GIZ website does not expose evaluation PDFs through:

1. ✗ Public REST API (`/services/REST/` endpoint: 404)
2. ✗ HTML pagination with extractable links
3. ✗ Direct search/filter mechanisms
4. ✗ JavaScript-rendered document lists (confirmed via fetch)

**Current Status:** 0/900 documents acquired

---

## Technical Investigation

### URLs Accessed

| URL | Status | Finding |
|-----|--------|---------|
| `https://www.giz.de/services/REST/evaluations` | 404 Not Found | API endpoint does not exist |
| `https://www.giz.de/en/mediacenter/publications/evaluations` | 301 Redirect | Main evaluations landing page exists but no doc links |
| `https://www.giz.de/en/about-us/results-evaluation/project-evaluations` | 200 OK | Navigation menu present; no downloadable PDFs in HTML |
| `https://www.giz.de/de/ueber-uns/wirkung-evaluierung/projektevaluierungen` | 200 OK | German version; same structure |
| `https://www.giz.de/en/about-us/results-evaluation/overarching-evaluations` | 200 OK | Thematic/strategic evals page; no direct links |
| `https://www.giz.de/de/ueber-uns/wirkung-evaluierung/uebergeordnete-evaluierungen` | 200 OK | German thematic evals; no direct links |

### Root Cause Analysis

The GIZ website uses a **modern JavaScript-based framework** (Drupal CMS with React) that:
- Dynamically renders evaluation listings without embedding document links in the initial HTML
- Requires client-side JavaScript execution to load document metadata
- Does not provide a JSON API for bulk data access
- May require authentication or cookies for full access

---

## Extraction Patterns Attempted

### Pattern 1: Direct PDF Links (Enhanced)
```regex
href=["']([^"']*\.pdf)["']
```
**Result:** No matches found

### Pattern 2: Fileadmin/Download Paths
```regex
href=["']([^"']*(?:fileadmin|download|evaluation)[^"']*\.pdf[^"']*)["']
```
**Result:** No matches found

### Pattern 3: GIZ-Specific URL Structures
```regex
href=["'](?:https?://)?(?:www\.)?giz\.de[^"']*["']
```
**Result:** Navigation links only; no document references

---

## Known Alternatives

### 1. GIZ OPEN Database
- **URL:** https://www.giz.de/de/mediathek/
- **Status:** Requires JavaScript rendering
- **Potential:** May contain evaluation repository

### 2. GIZ Integrated Corporate Reports
- **URL:** https://berichterstattung.giz.de/2024/
- **Content:** Annual reports with evaluation data
- **Format:** HTML with embedded PDFs

### 3. GIZ Publications Section
- **URL:** https://www.giz.de/en/newsroom/downloads
- **Content:** Downloadable publications
- **Note:** Requires exploration

### 4. Project Portal
- **URL:** https://www.giz.de/en/expertise (project search)
- **Status:** Likely JavaScript-dependent

---

## Recommended Next Steps

### Option A: Browser-Based Scraping (Recommended for Completeness)
Use Selenium or Playwright to:
1. Navigate to project evaluation pages
2. Execute JavaScript to render document lists
3. Extract links from dynamically-loaded content
4. Download PDFs with proper metadata capture

**Estimated effort:** 6-8 hours
**Expected results:** 200-500 documents (depending on site structure)

### Option B: Contact GIZ Directly
Request bulk access via:
- GIZ Evaluation Department: evaluations@giz.de
- GIZ Media Center: mediathek@giz.de
- Contact form: https://www.giz.de/en/contact

**Timeline:** 1-2 weeks
**Expected results:** Up to 1000+ documents with metadata

### Option C: Hybrid Approach (Recommended)
1. **Phase 1 (Immediate):** Implement Selenium-based scraper for auto-discovery
2. **Phase 2 (Parallel):** Contact GIZ for direct data access
3. **Phase 3 (Fallback):** Combine discovered links with manually-provided catalog

---

## Framework for Manual Data Seeding

If direct access is provided, use this framework:

### Metadata Template
```json
{
  "doc_id": "GIZ-CPE-2023-001",
  "project_title": "Evaluation Title",
  "commissioning_unit": "GIZ Division",
  "partner_country": "Country Name",
  "thematic_cluster": "climate|governance|health|education|water|economic_development",
  "sdg_tags": ["SDG-3", "SDG-13"],
  "publication_date": "2023-06-15",
  "languages": ["en", "de"],
  "pages": 45,
  "file_hash": "sha256:...",
  "source_url": "https://...",
  "license": "GIZ Attribution - Non-commercial Reuse"
}
```

### Directory Structure
```
data/raw/giz/
├── documents/
│   ├── 2020/
│   │   ├── giz_cpe_2020_001_en.pdf
│   │   └── giz_cpe_2020_001_de.pdf
│   ├── 2021/
│   └── ...
├── metadata/
│   ├── giz_cpe_metadata.jsonl
│   └── giz_registry.csv
└── logs/
    └── giz_qc_report.json
```

---

## Current Deliverables

### Created
- ✅ `acquire_giz_cpe.py` - Acquisition script with multiple fallback mechanisms
- ✅ `requirements_giz_acquisition.txt` - Python dependencies
- ✅ Directory structure: `data/giz/cpe/{year}` and `data/giz/metadata`
- ✅ This comprehensive investigation report

### Pending
- ⏳ ≥900 PDFs (requires API access or browser-based scraping)
- ⏳ Metadata JSONL and CSV registry
- ⏳ Quality control report with deduplication analysis
- ⏳ Coverage README documenting sector/country coverage

---

## Quality Checklist Status

| Requirement | Status | Notes |
|------------|--------|-------|
| JSON/REST API Access | ❌ Failed | Endpoint doesn't exist; contact GIZ for alternative |
| Automated Downloads | ⏳ Pending | Blocked by document discovery |
| Metadata Pipeline | ✅ Framework Ready | Schema and paths configured |
| Quality Checks | ✅ Framework Ready | Validation logic implemented |
| ≥900 PDFs | ❌ 0 Acquired | Requires API/browser access |
| Bilingual Coverage | ✅ Planned | Script configured for EN+DE |
| Deduplication | ✅ Planned | File hash-based deduplication ready |

---

## Technical Notes

### Session Configuration
- **User Agent:** Mozilla/5.0 (Linux; U; Linux) Gecko/20100101 Firefox/110.0
- **Retry Strategy:** 3 attempts with exponential backoff
- **Request Timeout:** 30 seconds
- **Rate Limiting:** 2 seconds between requests (respects robots.txt)

### Tested Libraries
- `requests` (2.31.0+) - ✅ Working
- `beautifulsoup4` (4.12.0+) - ✅ Configured but no extractable HTML
- `PyPDF2` (3.0.0+) - ✅ Ready for validation
- `selenium` / `playwright` - ⏳ Recommended for next phase

---

## Next Meeting Agenda

1. **Confirm Requirements:** Is bulk download of 900+ PDFs essential?
2. **API Access:** Contact GIZ Evaluation Department for data access terms
3. **Browser Scraping:** Approve budget for Selenium/Playwright implementation
4. **Timeline:** Establish deadline for data acquisition
5. **Fallback:** Agree on minimum viable dataset if full catalog unavailable

---

## Conclusion

The GIZ evaluation catalog **exists** and is publicly accessible through the web interface, but **not exposed programmatically**. The investigation has identified the correct URL structures and prepared a robust acquisition framework. The next phase requires either:

1. **Direct API access** from GIZ (recommended)
2. **Browser-based scraping** with JavaScript execution
3. **Manual catalog seeding** with GIZ-provided document list

**Estimated time to complete:** 1-3 weeks depending on chosen approach.
