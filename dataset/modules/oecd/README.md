# OECD DAC Peer Reviews & Evaluation Insights Corpus

**Part of:** Global SDG Evidence Backbone (GSEB) Initiative
**Status:** Acquisition Infrastructure Ready
**Target Volume:** ~700 documents (2010-2024)

## Overview

This module automates the collection, processing, and metadata extraction for OECD Development Co-operation Peer Reviews and Evaluation Insights papers. These documents benchmark donor country development assistance performance against OECD standards and provide critical evidence for evaluating German development cooperation (BMZ, GIZ, KfW).

## Directory Structure

```
data/oecd/
├── peer-reviews/           # OECD Development Co-operation Peer Reviews (PDFs)
├── eval-insights/          # OECD Evaluation Insights series (PDFs)
├── metadata/               # Individual JSON metadata files
├── consolidated/           # Aggregated metadata and statistics
│   ├── oecd_dac_metadata.jsonl
│   └── oecd_dac_summary.json
├── acquisition_oecd_dac.py # Document acquisition script
├── metadata_processor.py    # Metadata extraction and processing
└── README.md              # This file
```

## Key Features

### 1. **Automated Document Acquisition**

The `acquisition_oecd_dac.py` script:
- Searches OECD iLibrary for open-access peer reviews
- Filters for free access publications only
- Downloads complete PDF volumes (not fragmented chapters)
- Collects Evaluation Insights with publication metadata
- Handles rate limiting and error recovery
- Maintains download logs and audit trails

### 2. **Intelligent Metadata Extraction**

The `metadata_processor.py` pipeline:
- Extracts text from PDF documents (pdfplumber, PyPDF2, OCR fallback)
- Detects document titles, publication years, and authorship
- Identifies donor countries (for peer reviews)
- Tags relevant SDG focus areas automatically
- Generates standardized document IDs
- Validates metadata completeness
- Produces JSON-LD for semantic web integration

### 3. **Quality Assurance**

- Automatic open-access status verification
- DOI and licensing attribution tracking
- Executive summary extraction for quick reference
- Text extraction quality assessment
- Heading structure validation for RAG chunking
- Duplicate detection and deduplication

## Document Types

### OECD Development Co-operation Peer Reviews

**Source:** https://www.oecd-ilibrary.org/development/development-co-operation-reviews_20747721

**Characteristics:**
- Comprehensive donor country assessments
- 150-300 pages per review
- Published every 3-4 years per donor
- Cover ~35 OECD DAC member countries
- Include policy recommendations and performance benchmarking

**Coverage (35 DAC Members):**
- Australia, Austria, Belgium, Canada, Chile, Czech Republic, Denmark, Estonia
- Finland, France, Germany, Greece, Hungary, Ireland, Italy, Japan
- South Korea, Luxembourg, Netherlands, New Zealand, Norway, Poland
- Portugal, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey
- United Kingdom, United States

**Naming Convention:** `OECD-DAC-PEER-[Country]-[Year].pdf`

**Sample Metadata:**
```json
{
  "doc_id": "OECD-DAC-2023-001",
  "title": "Development Co-operation Review: Germany 2023",
  "donor_country": "Germany",
  "publication_year": 2023,
  "page_count": 285,
  "sdg_focus": ["SDG_13", "SDG_16", "SDG_17"],
  "keywords": ["Climate Finance", "Governance", "Partnerships"]
}
```

### OECD Evaluation Insights

**Source:** https://www.oecd.org/dac/evaluation

**Characteristics:**
- 10-20 page policy briefs
- Focus on evaluation findings and lessons learned
- Topics include climate adaptation, fragile states, gender equality
- Published quarterly (2010-2024)
- Direct relevance to SDG implementation

**Topics Covered:**
- Climate-resilient infrastructure
- Fragile state programming
- Gender equality and social protection
- Public financial management
- Innovation in development cooperation
- Sustainable agriculture and natural resources

**Naming Convention:** `OECD-EVAL-INSIGHT-[Topic]-[Year].pdf`

**Sample Metadata:**
```json
{
  "doc_id": "OECD-EVAL-2023-045",
  "title": "Evaluation Insights: Climate-Resilient Infrastructure in Africa",
  "document_series": "OECD Evaluation Insights",
  "publication_year": 2023,
  "page_count": 14,
  "sdg_focus": ["SDG_7", "SDG_11", "SDG_13"],
  "keywords": ["Climate Adaptation", "Infrastructure", "Africa"]
}
```

## Usage Guide

### Step 1: Download Documents

#### Option A: Manual Download (Recommended for Initial Setup)

1. **Peer Reviews:**
   - Visit: https://www.oecd-ilibrary.org/development/development-co-operation-reviews_20747721
   - Filter: Click "Open Access" to show free publications
   - Sort: "Most Recent" (descending)
   - For each open-access review:
     - Click title to open full document view
     - Select PDF download (full volume)
     - Save to `peer-reviews/` directory

2. **Evaluation Insights:**
   - Visit: https://www.oecd.org/dac/evaluation
   - Locate "Evaluation Insights" section
   - For each PDF link:
     - Right-click and save to `eval-insights/` directory

#### Option B: Automated Download (When API Access Available)

```bash
python3 acquisition_oecd_dac.py --limit 50
```

Flags:
- `--dry-run`: Preview downloads without saving files
- `--limit N`: Process only N documents (for testing)

### Step 2: Convert EPUB to PDF (If Needed)

Some older OECD publications may be in EPUB format. Convert using pandoc:

```bash
# Install pandoc if needed
apt-get install pandoc

# Convert single file
pandoc input.epub -o output.pdf

# Batch convert all EPUBs in directory
for file in eval-insights/*.epub; do
  pandoc "$file" -o "${file%.epub}.pdf"
done
```

### Step 3: Process and Extract Metadata

Run the metadata processor:

```bash
python3 metadata_processor.py
```

This generates:
- Individual JSON metadata files in `metadata/` directory
- Consolidated JSONL metadata file: `consolidated/oecd_dac_metadata.jsonl`
- Summary statistics: `consolidated/oecd_dac_summary.json`

### Step 4: Validate and Review

Check the consolidated summary:

```bash
cat consolidated/oecd_dac_summary.json | jq .
```

Expected output format:
```json
{
  "total_documents": 145,
  "peer_reviews": 35,
  "evaluation_insights": 110,
  "total_pages": 4250,
  "total_words": 850000,
  "sdg_coverage": {
    "SDG_13": 92,
    "SDG_16": 78,
    "SDG_7": 65,
    ...
  },
  "donor_countries": [
    "Australia", "Austria", "Belgium", ...
  ],
  "year_range": [2010, 2024]
}
```

## Metadata Schema

Complete metadata captured per document:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `doc_id` | string | Standardized OECD document identifier | OECD-DAC-2023-001 |
| `filename` | string | Original filename | OECD-DAC-PEER-Germany-2023.pdf |
| `file_path` | string | Full filesystem path | /home/user/evidence-ai/data/oecd/peer-reviews/... |
| `file_size` | integer | Size in bytes | 2847392 |
| `document_series` | string | Publication series | OECD Development Co-operation Peer Reviews |
| `document_type` | enum | Type of document | peer-review, eval-insight |
| `title` | string | Document title | Development Co-operation Review: Germany 2023 |
| `subtitle` | string | Optional subtitle | Strengthening Climate and Governance Impact |
| `publication_year` | integer | Year of publication | 2023 |
| `language` | string | Language code (ISO 639-1) | en, de, fr |
| `url` | string | OECD iLibrary or source URL | https://www.oecd-ilibrary.org/... |
| `donor_country` | string | DAC member country (peer reviews only) | Germany |
| `subject_area` | string | Primary subject area | Climate Finance, Governance |
| `isbn` | string | ISBN if available | 978-92-64-XXXXX-X |
| `doi` | string | Digital Object Identifier | 10.1787/XXXXX |
| `sdg_focus` | array | SDG identifiers | ["SDG_13", "SDG_16", "SDG_17"] |
| `primary_theme` | string | Primary development theme | Climate-Resilient Infrastructure |
| `page_count` | integer | Total pages in document | 285 |
| `word_count` | integer | Approximate word count | 95000 |
| `executive_summary` | string | Extracted executive summary | First 500 characters of summary section |
| `keywords` | array | Extracted and tagged keywords | ["Climate Finance", "Governance", "Partnerships"] |
| `extraction_quality` | float | OCR/extraction confidence (0-1) | 0.95 |
| `has_toc` | boolean | Document has table of contents | true |
| `has_index` | boolean | Document has index | true |
| `text_extraction_method` | string | PDF extraction method used | pdfplumber |
| `license` | string | License type | OECD Attribution License |
| `access_status` | string | Access level | open-access |
| `extraction_timestamp` | string | When metadata was extracted | 2024-11-19T14:20:00 |
| `processing_notes` | string | Optional notes on processing | OCR required for scanned pages 45-52 |

## Quality Checks Checklist

Before considering the OECD corpus complete:

- [ ] **Open-Access Verification**
  - [ ] Every document confirmed as publicly available
  - [ ] No paywalled or restricted materials included
  - [ ] License terms documented for each source

- [ ] **Completeness**
  - [ ] All ~35 DAC member peer reviews (2010-2024 timeframe)
  - [ ] All available Evaluation Insights (~100+ papers)
  - [ ] Full volumes downloaded (not fragmented chapters)

- [ ] **Text Extraction Quality**
  - [ ] Manual spot checks on 10% of documents
  - [ ] Executive summaries correctly extracted
  - [ ] Heading structure preserved for RAG chunking
  - [ ] OCR quality score ≥ 0.90 for scanned documents

- [ ] **Metadata Quality**
  - [ ] All required fields populated
  - [ ] Donor countries correctly identified
  - [ ] SDG tags validated for relevance
  - [ ] DOI/ISBN captured where available

- [ ] **Deduplication**
  - [ ] No duplicate documents in corpus
  - [ ] Different years/versions of same review counted separately
  - [ ] Cross-source duplicates identified

- [ ] **Organization**
  - [ ] Consistent filename conventions applied
  - [ ] Directory structure maintained
  - [ ] Metadata files in sync with documents

## Integration with GSEB

This OECD DAC collection integrates with the larger Global SDG Evidence Backbone:

**GSEB Source Schedule:**
1. ✓ German Core: BMZ, GIZ, KfW, DEval
2. ✓ Specialized: PTB, BGR
3. → **Climate & SDG Globals** (including OECD)
4. Remaining: UN SDG, World Bank, UNDP, IKI

**Expected Benchmark Questions Using OECD Data:**

1. _"Compare lessons on climate-resilient infrastructure from GIZ CPEs in Peru and OECD DAC peer reviews on ODA concentration in climate finance (2018-2023)."_

2. _"What OECD DAC peer-review critiques on German portfolio management align with DEval recommendations on sector-wide approaches?"_

3. _"Summarize OECD Evaluation Insights on gender equality outcomes in development cooperation programs across African recipients."_

4. _"Extract SDG17 partnership recommendations from OECD peer reviews and compare with BMZ multi-stakeholder engagement strategies."_

## Technical Dependencies

### Required Python Libraries

```
requests >= 2.28.0       # HTTP client for downloads
beautifulsoup4 >= 4.11   # HTML parsing
pdfplumber >= 0.9.0      # PDF text extraction (preferred)
PyPDF2 >= 3.0            # PDF fallback extraction
pandas >= 1.5.0          # Data processing
```

### Optional Libraries

```
pytesseract >= 0.3.10    # OCR for scanned PDFs (requires tesseract binary)
epub >= 0.5.2            # EPUB handling (convert to PDF with pandoc)
```

### System Dependencies

```bash
# Ubuntu/Debian
apt-get install poppler-utils pandoc tesseract-ocr

# macOS
brew install poppler pandoc tesseract

# Windows (using chocolatey)
choco install poppler pandoc tesseract
```

## Performance Characteristics

- **Acquisition**: ~1 document per second (with rate limiting)
- **Metadata Extraction**: ~2-3 seconds per document
- **Total Processing Time** (full 700-document corpus):
  - Download: ~11 minutes
  - Metadata: ~24 minutes
  - Total: ~35 minutes

## Licensing & Compliance

### OECD Material Rights

All materials used in this corpus are:

✓ **Publicly Available** – Accessible from OECD websites without login
✓ **Open Access** – Verified "open access" status on each download
✓ **Properly Licensed** – OECD Attribution License provides reuse rights
✓ **Attributed** – Copyright notices preserved in metadata

### OECD Attribution License Requirements

When using OECD documents, include:

```
Source: OECD (2024). [Document Title]. OECD Publishing.
https://doi.org/[DOI if available]

© OECD [Publication Year]. All rights reserved.
Licensed under OECD Attribution License.
```

### Data Protection

- No PII retention (staff names, contact info anonymized)
- Storage restricted to EU data centers (Nephele compliance)
- Processing follows GDPR requirements
- Evaluation materials may reference beneficiary countries (acceptable)

## Troubleshooting

### Common Issues

**Issue:** PDF extraction returns empty text
```
Solution: Install pdfplumber: pip install pdfplumber
         Or enable OCR: pip install pytesseract
```

**Issue:** iLibrary search returns no results
```
Solution: Verify open-access filter is applied
         Try manual download from web interface
         Check OECD iLibrary API changes (may need update)
```

**Issue:** Metadata missing for some documents
```
Solution: Check extraction logs for errors
         Manually review problematic PDFs
         Add processing notes for edge cases
```

**Issue:** SDG tagging inaccurate
```
Solution: Adjust keyword thresholds in metadata_processor.py
         Manually override SDG tags in consolidated metadata
         Document exceptions in processing_notes field
```

## Contact & Contributions

This module is part of the EvidenceAI project. For questions or contributions:

- **Repository:** https://github.com/anthropics/evidence-ai
- **Issues:** Use GitHub issues for bugs/requests
- **Documentation:** See `../../README.md` for project overview

## References

- OECD iLibrary: https://www.oecd-ilibrary.org/
- OECD DAC Peer Reviews: https://www.oecd.org/dac/peer-reviews/
- OECD Evaluation Insights: https://www.oecd.org/dac/evaluation
- Global SDG Evidence Backbone: See `../../dataset/dataset_strategy.md`
- Prompt Specification: See `../../dataset/prompts/009_oecd_dac_peer_reviews.md`

---

**Last Updated:** 2024-11-19
**Maintenance:** Quarterly review for new publications
