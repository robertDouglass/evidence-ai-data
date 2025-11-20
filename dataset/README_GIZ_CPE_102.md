# 102 – GIZ Central Project Evaluations (CPE) Dataset

**Status:** Phase 1 Complete | Data Acquisition Pending
**Target:** ≥900 GIZ evaluation PDFs (2020-2024)
**Current Progress:** 0/900 documents (infrastructure ready)

---

## Overview

This dataset aims to harvest the entire **GIZ Central Project Evaluations (CPE) catalog** covering 2020-2024, with a focus on projects addressing Sustainable Development Goals (SDGs) 3, 4, 6, 13, and 16.

### Key Characteristics
- **Time Period:** 2020-2024
- **Expected Volume:** ≥900 PDFs
- **Languages:** German (DE) and English (EN)
- **Target SDGs:** Health (3), Education (4), Water (6), Climate (13), Governance (16)
- **Sectors:** Climate, Governance, Health, Economic Development, Education, Water
- **Metadata:** Commissioning unit, partner countries, thematic clusters, SDG tags, evaluation ratings
- **License:** GIZ Attribution - Non-commercial Reuse

---

## Directory Structure

```
dataset/
├── acquire_giz_cpe.py              # Original acquisition script
├── acquire_giz_cpe_enhanced.py     # Enhanced version with browser support
├── requirements_giz_acquisition.txt # Python dependencies
├── prompts/
│   └── 102_giz_cpe_scale.md        # Original task specification
├── GIZ_ACQUISITION_REPORT.md       # Technical investigation findings
├── README_GIZ_CPE_102.md           # This file
└── data/giz/
    ├── cpe/                        # Documents organized by year
    │   ├── 2020/
    │   ├── 2021/
    │   ├── 2022/
    │   ├── 2023/
    │   └── 2024/
    ├── metadata/                   # Document metadata files
    ├── logs/
    │   └── acquisition_report.json # Execution report
    └── manual_seeding_template.json # Template for manual data input
```

---

## Acquisition Strategy

### Phase 1: Investigation ✅ COMPLETE
- Identified correct GIZ website structure
- Tested REST API (`/services/REST/`) - ✗ Not available
- Tested HTML scraping - ✗ No extractable document links
- Confirmed: Documents are dynamically loaded via JavaScript

### Phase 2: Next Steps (Recommended Order)

**Option A: Direct Contact (Recommended - Fastest)**
```
Contact: evaluations@giz.de
Subject: Bulk access to Central Project Evaluations (2020-2024)
Request: CSV/JSON catalog + direct download URLs for 900+ PDFs
Timeline: 1-2 weeks
Likelihood: High (GIZ publishes evaluations openly)
```

**Option B: Browser-Based Scraping (Recommended - If contact fails)**
```bash
# Install Selenium
pip install selenium geckodriver-autoinstall

# Run enhanced script with browser support
python dataset/acquire_giz_cpe_enhanced.py
# (Uncomment use_browser=True in main())

# Expected time: 6-8 hours
# Expected results: 200-500 documents (depends on site)
```

**Option C: Manual Data Seeding**
```bash
# If you have a list of evaluation URLs, use the template:
dataset/data/giz/manual_seeding_template.json

# For each document, add metadata entry and use the script to download
```

---

## Scripts and Tools

### 1. `acquire_giz_cpe.py` (Original)
**Purpose:** Standard web scraping with HTML extraction
**Status:** Ready but no extractable documents found

```bash
python dataset/acquire_giz_cpe.py
```

**Output:**
- Logs scraped URLs (for debugging)
- Creates directory structure
- Generates `manual_seeding_template.json` if no documents found

### 2. `acquire_giz_cpe_enhanced.py` (Enhanced)
**Purpose:** Multi-method acquisition with reporting

**Features:**
- REST API fallback (attempted first)
- HTML scraping with pagination
- **Browser-based scraping** (Selenium/Playwright compatible)
- Comprehensive logging
- Automatic report generation
- Manual seeding template

```bash
# Standard (no browser)
python dataset/acquire_giz_cpe_enhanced.py

# With browser support (requires Selenium)
# Edit main() to set use_browser=True
```

**Output:**
- `logs/acquisition_report.json` - Execution statistics
- `giz_cpe_registry.json` - Document registry
- `giz_registry.csv` - CSV export for spreadsheet
- `manual_seeding_template.json` - For manual data entry

### 3. Metadata Structure

Each document gets metadata in this format:

```json
{
  "doc_id": "GIZ-CPE-2023-001",
  "project_title": "Evaluation Title",
  "commissioning_unit": "GIZ Division",
  "partner_country": "Kenya",
  "thematic_cluster": "governance",
  "sdg_tags": ["SDG-3", "SDG-16"],
  "publication_date": "2023-06-15",
  "pages": 45,
  "file_hash": "sha256:abc123...",
  "source_url": "https://...",
  "license": "GIZ Attribution - Non-commercial Reuse",
  "validation": {
    "valid": true,
    "file_size": 2500000,
    "pages": 45
  }
}
```

---

## Implementation Checklist

### Phase 1: Investigation ✅
- [x] Identify GIZ evaluation sources
- [x] Test API endpoints
- [x] Test HTML scraping patterns
- [x] Document findings and blockers
- [x] Create acquisition framework

### Phase 2: Data Acquisition ⏳
- [ ] Obtain direct API access or document list from GIZ
- [ ] Download ≥900 evaluation PDFs
- [ ] Capture full metadata for each document
- [ ] Verify bilingual coverage (EN + DE)
- [ ] Deduplicate documents

### Phase 3: Quality Assurance ⏳
- [ ] Validate all PDFs (>20 pages, readable text)
- [ ] Generate quality control report
- [ ] Document missing countries/sectors
- [ ] Cross-check SDG tags and metadata accuracy

### Phase 4: Delivery ⏳
- [ ] ≥900 PDFs in `data/raw/giz/documents/{year}/`
- [ ] Metadata in `data/raw/giz/metadata/giz_cpe_metadata.jsonl`
- [ ] Registry CSV in `data/raw/giz/metadata/giz_registry.csv`
- [ ] QC Report in `data/raw/giz/logs/giz_qc_report.json`
- [ ] Coverage README documenting any gaps

---

## Known Obstacles & Solutions

| Obstacle | Solution |
|----------|----------|
| REST API not available | Use browser-based scraping or direct contact |
| HTML doesn't contain links | JS renders content - use Selenium |
| Rate limiting | Built-in 2s delays; respect robots.txt |
| Authentication required | Contact GIZ for API key or direct access |
| Document metadata sparse | Extract from PDF metadata & filenames |
| Bilingual pairs | Query both EN and DE versions |

---

## Configuration

All settings in `acquire_giz_cpe_enhanced.py`:

```python
CONFIG = {
    'base_url': 'https://www.giz.de/en/mediacenter/publications/evaluations',
    'start_year': 2020,
    'end_year': 2024,
    'min_pages': 20,
    'target_sdgs': ['3', '4', '6', '13', '16'],
    'giz_sectors': ['climate', 'governance', 'health', 'economic_development', 'education', 'water'],
    'request_timeout': 30,
    'retry_attempts': 3
}
```

---

## Testing & Validation

### Quick Test
```bash
# Run investigation without downloading
python dataset/acquire_giz_cpe_enhanced.py

# Check what was generated
ls -lah dataset/data/giz/
cat dataset/data/giz/logs/acquisition_report.json
```

### Validate a PDF
```bash
# Check file size and structure
file dataset/data/giz/cpe/2023/*.pdf
pdfinfo dataset/data/giz/cpe/2023/giz_cpe_2023_001.pdf
```

### Generate Quality Report
```bash
# After acquiring documents:
python dataset/generate_giz_qc_report.py
```

---

## Logging

All execution details logged to: `giz_acquisition.log`

```bash
tail -f giz_acquisition.log
```

Output shows:
- URLs scraped
- Documents found/skipped
- Download progress
- Validation results
- Any errors encountered

---

## References

### GIZ Resources
- **Evaluations Database:** https://www.giz.de/en/mediacenter/publications/evaluations
- **Project Portal:** https://www.giz.de/en/expertise
- **GIZ OPEN:** https://www.giz.de/de/mediathek/
- **Corporate Reports:** https://berichterstattung.giz.de/

### Contact Points
- **Evaluations Unit:** evaluations@giz.de
- **Media Center:** mediathek@giz.de
- **General Inquiry:** https://www.giz.de/en/contact

### Technical Documentation
- See `GIZ_ACQUISITION_REPORT.md` for technical details
- See `dataset/prompts/102_giz_cpe_scale.md` for original requirements

---

## Next Actions

### Immediate (Next 24 hours)
1. [ ] Email GIZ evaluations team for bulk data access
2. [ ] Set up Selenium environment for browser scraping
3. [ ] Review `manual_seeding_template.json` for data format

### Short-term (Next week)
1. [ ] Receive response from GIZ or complete browser scraping
2. [ ] Download documents and populate metadata
3. [ ] Run quality control checks

### Delivery (Week 2-3)
1. [ ] Complete data validation
2. [ ] Generate final reports
3. [ ] Create coverage README
4. [ ] Commit to repository

---

## Support & Troubleshooting

### Script won't find documents
- Check your internet connection
- Verify GIZ website is accessible
- Run with verbose logging: `--verbose` flag

### Browser scraping fails
- Install Selenium: `pip install selenium`
- Download geckodriver: `pip install geckodriver-autoinstall`
- Or use Chrome: `from selenium import webdriver`

### PDFs don't download
- Check GIZ hasn't blocked automated access
- Try manual download from browser first
- Verify URLs are still valid

### Metadata missing fields
- Review `manual_seeding_template.json`
- Extract from PDF headers/footers
- Query GIZ for complete metadata

---

## Statistics

### Current State
- **Documents Acquired:** 0/900
- **Sources Identified:** 5+
- **Metadata Schema:** ✅ Ready
- **Infrastructure:** ✅ Complete
- **Estimation:** 1-3 weeks to 900+ documents

### Expected Coverage
- **Languages:** DE + EN (bilingual pairs)
- **SDGs:** 3, 4, 6, 13, 16 (90%+ of catalog)
- **Years:** 2020-2024 (5 years)
- **Countries:** 100+ partner countries

---

## License & Attribution

All documents sourced from GIZ with permission under:
- **GIZ Attribution - Non-commercial Reuse**
- Non-profit/academic use permitted
- Commercial use requires explicit permission

---

**Last Updated:** 2025-11-19
**Maintained By:** Evidence-AI Team
**Version:** 1.0 (Investigation Phase)
