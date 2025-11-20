# EvidenceAI Data Lake & Acquisition Pipelines

Reference repo for building the Global SDG Evidence Backbone (GSEB): data lake layout, scraping prompts, and acquisition scripts that pull open evidence from German development agencies, multilateral partners, and climate data providers.

## Repository Guide
- `data/` – canonical landing zone; see `data/README.md` for the required `data/raw/<source>/{documents,metadata,logs}` structure used by all crawlers.
- `dataset/` – acquisition modules, prompts, and metadata for BMZ, GIZ, KfW, BGR, OECD DAC, UN SDG, and other sources; includes the overall `dataset_strategy.md` and per-source READMEs.
- `climate_change_dataset/` – climate and geospatial downloads (Copernicus CDS, USGS, huggingface datasets) plus helper scripts under `scripts/`.
- `worldbank/` – downloaded World Bank climate project documents and `metadata.jsonl` describing each file.

## Typical Data Flow
1) Pick a source prompt in `dataset/prompts/` (Phase 2 tasks 101–112) or the per-module READMEs (e.g., `dataset/BMZ_ACQUISITION_README.md`, `dataset/kfw/README.md`, `dataset/modules/oecd/README.md`).
2) Run the acquisition script, writing binaries to `data/raw/<source>/documents/` and metadata to `data/raw/<source>/metadata/` (or module-specific JSONL files).
3) Store crawl logs/QA reports under `data/raw/<source>/logs/`.

## Setup
- Python 3.10+ recommended; create a virtualenv.
- Install dependencies per module, e.g.:
  - `pip install -r dataset/requirements_giz_acquisition.txt`
  - `pip install cdsapi xarray netCDF4` (for Copernicus scripts)
- Large binaries in `data/raw/**` are tracked with Git LFS; run `git lfs install` before adding documents.

## Running Common Jobs
- BMZ evaluations / strategies: `python dataset/bmz_acquisition.py --limit 50 --verbose`
- GIZ central project evaluations: `python dataset/acquire_giz_cpe_enhanced.py --limit 50`
- KfW evaluations: `python dataset/kfw/acquisition_script.py --config dataset/kfw/config.json`
- OECD DAC peer reviews & Evaluation Insights: `python dataset/modules/oecd/acquisition_oecd_dac.py --limit 10`
- Copernicus climate data (ERA5, indicators): `python climate_change_dataset/scripts/cds/download_era5_monthly.py`

## Data Handling & QA
- Keep to the `data/raw/<source>/` layout so downstream ingestion and deduplication work.
- Verify licensing/attribution notes in the per-source READMEs; many sources are CC BY or CC BY IGO.
- Sanitize for PII when needed (evaluations may include staff names).
- Use module validation tools where provided (e.g., `dataset/modules/oecd/validation_and_testing.py`).

## Useful References
- High-level goals and volume targets: `dataset/dataset_strategy.md`
- Acquisition prompts and Git LFS notes: `dataset/prompts/README.md`
- Climate data coverage: `climate_change_dataset/data/datasets/copernicus/README.md`
