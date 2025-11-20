# OECD DAC Peer Reviews Acquisition - Quick Start Guide

**Status:** ✓ Infrastructure Ready
**Target:** ~700 documents (2010-2024)
**Part of:** Global SDG Evidence Backbone (GSEB)

## 5-Minute Setup

This module provides everything needed to acquire, process, and manage OECD DAC peer reviews and evaluation insights.

### Step 1: Understand the Structure

```
data/oecd/
├── peer-reviews/         # Store OECD peer review PDFs here
├── eval-insights/        # Store evaluation insights PDFs here
├── metadata/             # Individual document metadata (auto-generated)
├── consolidated/         # Aggregated metadata (auto-generated)
├── acquisition_oecd_dac.py      # Document download script
├── metadata_processor.py         # Metadata extraction pipeline
├── validation_and_testing.py     # Testing and validation utilities
└── README.md            # Full technical documentation
```

### Step 2: Download Documents

**Option A: Manual Download (Recommended - 20 minutes)**

1. Open: https://www.oecd-ilibrary.org/development/development-co-operation-reviews_20747721

2. Filter by:
   - Select "Open Access" (checkbox on left)
   - Sort by "Most Recent"

3. For each peer review:
   - Click title
   - Click "PDF" download button
   - Save to `peer-reviews/` directory

4. Open: https://www.oecd.org/dac/evaluation

5. Find "Evaluation Insights" section, download PDFs to `eval-insights/`

**Option B: Scripted Download (When Available)**

```bash
python3 acquisition_oecd_dac.py
```

### Step 3: Process & Extract Metadata

```bash
python3 metadata_processor.py
```

Output:
- `metadata/*.json` - Individual document metadata
- `consolidated/oecd_dac_metadata.jsonl` - All documents in JSONL format
- `consolidated/oecd_dac_summary.json` - Aggregate statistics

### Step 4: Validate

```bash
python3 validation_and_testing.py
```

Checks:
- ✓ Directory structure
- ✓ PDF integrity
- ✓ Metadata completeness
- ✓ Document-metadata alignment
- ✓ SDG tagging

## Expected Results

After acquiring and processing all documents:

```json
{
  "total_documents": 135,
  "peer_reviews": 35,
  "evaluation_insights": 100,
  "total_pages": 4250,
  "total_words": 850000,
  "sdg_coverage": {
    "SDG_13": 92,
    "SDG_16": 78,
    "SDG_7": 65,
    "SDG_11": 52,
    ...
  }
}
```

## Troubleshooting

### Q: Where do I get the PDFs?

**A:** Download from OECD's free public sources:
- Peer Reviews: https://www.oecd-ilibrary.org/development/development-co-operation-reviews_20747721
- Insights: https://www.oecd.org/dac/evaluation

All open-access materials are free to download.

### Q: How long does it take?

**A:** Breakdown:
- Download (manual): 20 minutes
- Processing: 5-10 minutes
- Total: ~30 minutes for 100+ documents

### Q: Do I need special software?

**A:** Install Python dependencies:
```bash
pip install requests beautifulsoup4 pdfplumber PyPDF2 pandas
```

Optional (for OCR on scanned docs):
```bash
pip install pytesseract
apt-get install tesseract-ocr  # Linux
brew install tesseract         # macOS
```

### Q: What if PDF extraction fails?

**A:** The system uses multiple extraction methods:
1. **pdfplumber** (preferred, fastest)
2. **PyPDF2** (fallback)
3. **Tesseract OCR** (for scanned documents)

If one fails, the next automatically tries.

### Q: Can I process partial downloads?

**A:** Yes! The system processes whatever documents you've downloaded:
- 10 documents? Process and get metrics for 10
- 50 documents? Process 50 and scale up
- No waiting for all 135 documents

## Integration with Global SDG Evidence Backbone

This OECD corpus integrates with the larger GSEB project:

```
GSEB (10,000+ documents across 12 sources)
├── German Core (4,700 docs)
│   ├── BMZ Evaluations
│   ├── GIZ CPEs
│   ├── KfW Financial Cooperation
│   └── DEval Studies
├── Specialized (1,150 docs)
│   ├── PTB Quality Infrastructure
│   └── BGR Geoscience
└── Climate & SDG Globals (4,150 docs)
    ├── OECD DAC ← YOU ARE HERE
    ├── UN SDG Monitoring
    ├── World Bank ICRs
    ├── UNDP Evaluations
    └── IKI Climate Projects
```

## Sample Questions This Enables

Once the corpus is complete, EvidenceAI can answer:

1. _"Compare German peer review critiques (OECD DAC) with DEval recommendations on climate finance effectiveness."_

2. _"What OECD Evaluation Insights on gender equality align with GIZ CPE findings in Sahel countries?"_

3. _"Extract SDG13 implementation lessons from OECD peer reviews of climate-leading donors (Denmark, Germany, Sweden)."_

4. _"Summarize OECD DAC findings on ODA concentration and compare with KfW portfolio analysis."_

## File Naming Convention

### Peer Reviews
`OECD-DAC-PEER-[Country]-[Year].pdf`

Examples:
- `OECD-DAC-PEER-Germany-2023.pdf`
- `OECD-DAC-PEER-Australia-2021.pdf`
- `OECD-DAC-PEER-Denmark-2022.pdf`

### Evaluation Insights
`OECD-EVAL-INSIGHT-[Topic]-[Year].pdf`

Examples:
- `OECD-EVAL-INSIGHT-Climate-Adaptation-2023.pdf`
- `OECD-EVAL-INSIGHT-Fragile-States-2022.pdf`
- `OECD-EVAL-INSIGHT-Gender-Equality-2021.pdf`

## Next Steps

1. **Start downloading** documents from OECD sources
2. **Save to appropriate folder** (peer-reviews/ or eval-insights/)
3. **Run metadata processor** when ready
4. **Validate results** with validation suite
5. **Integrate with GSEB** (see main README)

## Support

- **Full Documentation:** See `README.md` in this directory
- **Technical Questions:** Check `README.md` Troubleshooting section
- **Project Overview:** See `../../README.md`
- **GSEB Strategy:** See `../../dataset/dataset_strategy.md`

---

**Time to Start:** 5 minutes
**Expected First Run:** 30 minutes (download + process)
**Ready to proceed?** Start downloading from OECD iLibrary!
