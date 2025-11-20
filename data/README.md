# Data Lake Structure

All raw corpora collected for EvidenceAI must be stored under `data/raw/<source>/` using the following canonical layout:

```
data/
  raw/
    <source>/
      documents/   # PDFs, DOCX, HTML snapshots grouped by year/topic
      metadata/    # JSONL/CSV/YAML metadata extracted per document
      logs/        # Acquisition logs, QA reports, crawl manifests
```

## Current Sources
- `bmz`
- `giz`
- `kfw`
- `deval`
- `ptb`
- `bgr`
- `iki`
- `un_sdg`
- `undp`
- `oecd`
- `worldbank` (use for World Bank + GFDRR climate/adaptation evidence)

Each directory already contains placeholder `.gitkeep` files so that agents can start writing outputs immediately. When moving legacy assets into the new tree, place primary documents under `documents/` and keep derived metadata/QA artifacts in the corresponding subdirectories.
