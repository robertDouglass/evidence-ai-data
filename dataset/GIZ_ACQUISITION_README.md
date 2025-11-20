# GIZ Central Project Evaluations (CPE) Acquisition

## Overview

This acquisition system gathers GIZ evaluation documents (2020-2024) covering key SDGs: 3, 4, 6, 13, 16.

**Goal:** Acquire ~1,000 GIZ CPE documents with comprehensive metadata

**Sources:**
- GIZ Evaluation Reports: https://www.giz.de/en/mediacenter/publications/evaluations
- GIZ OPEN Repository: https://www.giz.de/de/mediathek/
- Sector synthesis PDFs from GIZ Evaluation Unit pages

**Licensing:** GIZ publishes evaluations under permissive terms for non-commercial reuse. Retain attribution and publication date.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_giz_acquisition.txt
```

### 2. Run the Acquisition

```bash
python acquire_giz_cpe.py
```

This will:
- Scrape the GIZ evaluation database
- Download PDFs for 2020-2024
- Extract and validate metadata
- Store documents in `data/giz/cpe/<year>/`
- Generate metadata JSON files in `data/giz/metadata/`
- Create a registry file `giz_cpe_registry.json`

## Directory Structure

```
dataset/
├── data/
│   └── giz/
│       ├── cpe/
│       │   ├── 2020/
│       │   ├── 2021/
│       │   ├── 2022/
│       │   ├── 2023/
│       │   └── 2024/
│       ├── metadata/
│       │   └── GIZ-CPE-YYYY-###.json  (one per document)
│       └── giz_cpe_registry.json  (master index)
├── acquire_giz_cpe.py  (main script)
├── requirements_giz_acquisition.txt
└── GIZ_ACQUISITION_README.md  (this file)
```

## Output Formats

### PDF Files

Normalized naming convention:
```
giz_cpe_<year>_<doc_id>.pdf

Example: giz_cpe_2023_001.pdf
```

### Metadata JSON

Each PDF has an associated metadata file:

```json
{
  "doc_id": "GIZ-CPE-2023-001",
  "project_title": "Health Sector Evaluation 2023",
  "commissioning_unit": "GIZ",
  "partner_country": "Ethiopia",
  "thematic_cluster": "health",
  "sdg_tags": ["SDG-3", "SDG-4"],
  "pages": 150,
  "publication_date": "2023-05-15",
  "url": "https://www.giz.de/...",
  "source": "GIZ Evaluations Database",
  "license": "GIZ Attribution - Non-commercial Reuse",
  "file_path": "/path/to/giz_cpe_2023_001.pdf",
  "file_hash": "sha256_hash_here",
  "extraction_date": "2024-11-19T10:30:00",
  "validation": {
    "valid": true,
    "file_size": 2048576,
    "pages": 150
  }
}
```

### Registry File

Master index (`giz_cpe_registry.json`):

```json
[
  {
    "doc_id": "GIZ-CPE-2024-001",
    "project_title": "...",
    "publication_date": "2024-01-15",
    "sdg_tags": ["SDG-3"],
    "file_path": "data/giz/cpe/2024/giz_cpe_2024_001.pdf",
    ...
  },
  ...
]
```

## Configuration

Edit the `CONFIG` dict in `acquire_giz_cpe.py`:

```python
CONFIG = {
    'base_url': 'https://www.giz.de/en/mediacenter/publications/evaluations',
    'start_year': 2020,      # Change to adjust year range
    'end_year': 2024,        # Current year
    'min_pages': 20,         # CPE standard (avoid news articles)
    'output_dir': Path(...), # Base output directory
    'target_sdgs': ['3', '4', '6', '13', '16'],  # Focus areas
    'request_timeout': 30,
    'retry_attempts': 3
}
```

## Metadata Fields

### Core Fields
- `doc_id`: Unique identifier (GIZ-CPE-YYYY-###)
- `project_title`: Full project/evaluation title
- `commissioning_unit`: Organization that commissioned the evaluation
- `partner_country`: Target country or region

### Classification
- `thematic_cluster`: Sector classification (climate, governance, health, etc.)
- `sdg_tags`: List of SDG identifiers (SDG-3, SDG-4, etc.)

### Document Info
- `pages`: Page count (validated: >20 pages)
- `publication_date`: ISO format date
- `url`: Original source URL

### Quality & Tracking
- `source`: "GIZ Evaluations Database"
- `license`: "GIZ Attribution - Non-commercial Reuse"
- `file_path`: Local storage path
- `file_hash`: SHA256 for deduplication
- `validation`: Quality check results

## Acquisition Workflow

1. **Scraping** (via API or HTML pagination)
   - Attempts REST API first
   - Falls back to HTML scraping with pagination
   - Filters by year range (2020-2024)

2. **Downloading**
   - Fetches PDFs with retry logic
   - Validates HTTP responses
   - Rate-limits requests (1-2 second delays)

3. **Metadata Extraction**
   - Generates unique doc_id
   - Infers sector from title
   - Extracts SDG tags
   - Computes file hash (SHA256)

4. **Quality Validation**
   - Validates file size (>50KB)
   - Checks page count (>20 pages for CPE standard)
   - Detects scanned vs. text PDFs

5. **Storage**
   - Organizes by year (`cpe/<year>/`)
   - Saves metadata alongside PDFs
   - Creates master registry

## Advanced Features

### Robust HTTP Handling
- Automatic retry with exponential backoff
- Handles 429, 5xx status codes
- Configurable timeouts

### Deduplication
- SHA256 file hashing
- Can identify duplicate documents
- Preserves bilingual variants

### Logging
- Detailed info/debug output
- Error tracking
- Processing statistics

## Troubleshooting

### No documents found
- Check GIZ website connectivity
- Verify URL format in CONFIG
- Try accessing manually: https://www.giz.de/en/mediacenter/publications/evaluations

### Download failures
- Check internet connectivity
- Increase `request_timeout` if server is slow
- Review `consecutive_empty` logic in pagination

### Metadata extraction issues
- Review title parsing regex patterns
- Adjust SDG keyword matching for specific contexts
- Check partner country extraction logic

## Integration with Evidence AI

This acquisition fits into the broader evidence-ai dataset strategy:

1. **Phase 1**: Acquire GIZ CPE documents (this module)
2. **Phase 2**: Vector embedding & retrieval (via colpali/RAGFlow)
3. **Phase 3**: Evidence synthesis & report generation

The metadata JSON files are designed for compatibility with:
- Document retrieval systems (RAGFlow, Colpali)
- Evidence mapping workflows
- Citation & attribution tracking

## Future Enhancements

- [ ] OCR for scanned documents (2015-2020 era)
- [ ] Bilingual metadata extraction (German/English)
- [ ] Automatic sector classification via NLP
- [ ] Citation network analysis
- [ ] Interactive dashboard for document browser
- [ ] Incremental updates (only new documents)
- [ ] Parallel download processing

## References

- [GIZ Evaluation Function](https://www.giz.de/en/worldwide/36984.html)
- [GIZ Evaluation Reports](https://www.giz.de/en/mediacenter/publications/evaluations)
- [GIZ OPEN Repository](https://www.giz.de/de/mediathek/)
- [GIZ Evaluation Thematic Approaches](https://www.giz.de/en/worldwide/35476.html)

## Contact & Support

For issues or enhancements, refer to the evidence-ai project documentation and issue tracker.
