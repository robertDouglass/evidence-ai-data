# KfW Development Bank Financial Cooperation Evaluations Acquisition

## Overview

This directory contains the automated acquisition workflow for downloading and processing ~900 KfW (Kreditanstalt für Wiederaufbau) Development Bank project evaluations and thematic reports from 2013-2024, with emphasis on SDGs 7 (Affordable and Clean Energy), 8 (Decent Work and Economic Growth), 9 (Industry, Innovation and Infrastructure), 11 (Sustainable Cities and Communities), and 13 (Climate Action).

## Directory Structure

```
kfw/
├── evaluations/           # Project evaluations organized by year (2013-2024)
│   ├── 2013/
│   ├── 2014/
│   └── ...
├── annual-report/         # KfW annual evaluation reports
├── acquisition_script.py   # Main acquisition automation script
├── config.json            # Configuration parameters
└── README.md             # This file
```

## Data Sources

**Primary Sources:**
- KfW Evaluation Unit publications: https://www.kfw-entwicklungsbank.de/International-financing/KfW-Development-Bank/About-us/Evaluation/Results/
- KfW annual evaluation reports (PDF series)
- Sector/topic brochures (renewable energy, transport, MSME finance)

**Licensing:**
- Copyright: © KfW
- License: Non-commercial reuse allowed with attribution
- Requirements: Include attribution and leave copyright notice intact

## Acquisition Process

### Step 1: Enumeration
The script enumerates evaluation results pages from the KfW Evaluation Unit. Each page contains ~20 entries with `data-filename` attributes pointing to PDF documents.

### Step 2: Document Retrieval
Documents are retrieved using two methods:
1. **JSON API**: Query `EvaluationReportDownloadServlet?docId=` endpoints when available
2. **Direct Downloads**: Use direct PDF links via `/blob/` or `/DownloadCenter/` URLs as fallback

### Step 3: Language Handling
Captures both German (`de`) and English (`en`) versions when available, labeled separately.

### Step 4: Storage
- Evaluations: `evaluations/<year>/<doc_id>_<language>.pdf`
- Annual reports: `annual-report/<doc_id>_<language>.pdf`

### Step 5: Metadata Extraction
Summary tables are parsed using `tabula` or similar tools to extract:
- Success ratings
- Investment volumes
- Regional breakdowns
- Sectoral classifications

## Metadata Schema

Each downloaded document has associated metadata:

| Field | Type | Notes |
|-------|------|-------|
| `doc_id` | String | Format: `KFW-EVAL-YYYY-###` |
| `project_name` | String | Title from landing page |
| `region` | String | Africa, Asia, Latin America, Global |
| `financing_volume_eur` | Number | EUR millions |
| `sector` | String | energy, transport, finance, health, water, agriculture, infrastructure, etc. |
| `kfw_product` | String | loan, grant, blended finance, technical assistance |
| `publication_year` | Integer | 2013-2024 |
| `sdg_tags` | Array | Mapped based on sector [7, 8, 9, 11, 13] |
| `language` | String | de or en |
| `url` | String | Source URL |
| `file_path` | String | Local storage path |
| `file_size_bytes` | Integer | Document size |
| `download_timestamp` | String | ISO 8601 timestamp |

## Quality Checks

The acquisition process includes the following validation steps:

1. **File Size**: Prioritizes PDFs >15 pages (~50 KB minimum); skips 2-page fact sheets unless they contain evaluation findings
2. **Metadata Validation**: Cross-checks with evaluation summary tables on HTML pages
3. **PII Detection**: Spot-checks for personally identifiable information (KfW rarely publishes names beyond institutional partners)
4. **Coverage**: Ensures SDG coverage across priority areas (7, 8, 9, 11, 13)
5. **Completeness**: Verifies successful download of ~900 documents

## Running the Acquisition

### Prerequisites

```bash
pip install requests beautifulsoup4 tabula-py
```

### Execution

```bash
python /home/user/evidence-ai/dataset/kfw/acquisition_script.py
```

### Output Files

After execution, the following files are generated:

- **metadata.jsonl**: Line-delimited JSON with all document metadata
- **metadata.csv**: CSV spreadsheet of metadata (for easy viewing in Excel)
- **quality_report.json**: Summary statistics and quality metrics
- **evaluations/**: Organized PDF files by year and language

## Configuration

Edit `config.json` to customize:
- Target year range
- Priority SDGs and sectors
- Quality thresholds (minimum PDF size, pages)
- Retry policy (timeouts, backoff times)
- Output paths

## SDG Mapping

Automatic SDG tags are assigned based on document sector:

| Sector | SDGs |
|--------|------|
| Energy | 7, 13 |
| Renewable Energy | 7, 9, 13 |
| Transport | 9, 11, 13 |
| Finance/MSME | 8, 9 |
| Climate | 13 |
| Water | 6, 13 |
| Health | 3 |
| Education | 4 |
| Agriculture | 2, 12, 13 |
| Infrastructure | 9, 11 |

## Error Handling

The acquisition script implements robust error handling:

- **Network Retries**: Up to 4 attempts with exponential backoff (2s, 4s, 8s, 16s)
- **Timeout Protection**: 30-second timeout per request
- **Rate Limiting**: 0.5s delay between requests to avoid server overload
- **Partial Success**: Failed downloads are logged; acquisition continues

## Monitoring

Monitor acquisition progress in the logs:

```
2024-11-19 14:30:00 - INFO - Starting KfW Evaluation Acquisition
2024-11-19 14:30:05 - INFO - Enumerating evaluation results pages...
2024-11-19 14:30:10 - INFO - Downloaded KFW-EVAL-2023-001 (245.3 KB)
...
2024-11-19 15:45:00 - INFO - Acquisition complete: 850 downloaded, 50 failed
```

## Dataset Statistics

Expected outcomes (~900 documents):

- **Total Documents**: ~900 project evaluations + annual reports
- **Time Period**: 2013-2024 (12 years)
- **Languages**: Bilingual (German + English)
- **Storage Size**: ~2-3 GB (estimated)
- **SDG Coverage**: All priority SDGs represented
- **Regional Distribution**: Africa, Asia, Latin America, Global

## Legal and Ethical Considerations

1. **Attribution**: Always cite KfW as the source
2. **Copyright**: Respect © KfW copyright notice
3. **PII**: No personally identifiable information should be extracted beyond institutional partners
4. **Non-Commercial**: Reuse is limited to non-commercial applications
5. **Fact-Checking**: Validate data before use in analyses

## Troubleshooting

**SSL/TLS Errors**
- Update certificates: `pip install --upgrade certifi`
- May require VPN if accessing from restricted networks

**404 Errors**
- Website structure may have changed; verify current KfW evaluation URL
- Check if pages are behind authentication

**Slow Downloads**
- Increase rate limit delay in config.json if server throttles
- Use parallel downloads (with caution)

## Future Enhancements

- [ ] Parallel downloads using `asyncio` or `multiprocessing`
- [ ] OCR for scanned PDFs
- [ ] Full-text extraction and indexing
- [ ] Automated relationship extraction (projects, countries, sectors)
- [ ] Dashboard visualization of dataset

## References

- KfW Development Bank: https://www.kfw-entwicklungsbank.de
- Evaluation Unit: https://www.kfw-entwicklungsbank.de/International-financing/KfW-Development-Bank/About-us/Evaluation/
- SDG Framework: https://sdgs.un.org

## Notes

This acquisition represents a significant research dataset of development finance evaluations. The documents contain rich information on:
- Project outcomes and impact
- Investment patterns by region and sector
- Climate finance commitments
- Sustainable development alignment
- Lessons learned from implemented projects

The structured metadata allows for analysis of:
- SDG alignment trends
- Regional development priorities
- Sector effectiveness
- Portfolio composition over time

---

**Status**: Acquisition framework complete. Ready for deployment.
**Last Updated**: 2025-11-19
