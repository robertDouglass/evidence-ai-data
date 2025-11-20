# Prompt 07 – NOAA NCEI Climate Publications & Datasets

**Objective**: Harvest NOAA NCEI flagship datasets/publications relevant to climate monitoring.

**Work Items**
1. Use https://www.ncei.noaa.gov/access/search to target:
   - Global Historical Climatology Network (Daily, Monthly, Yearly)
   - Integrated Surface Dataset (ISD)
   - Global Summary of the Year/Month (GSOM/GSOY)
   - Storm Events Database documentation
   - Local Climatological Data publications.
2. For each dataset/publication:
   - Download the latest documentation PDF and at least one representative data file (e.g., NetCDF, CSV).
   - Store under `data/datasets/noaa/<dataset_name>/`.
3. Update the manifest:
   - `source_id = noaa/<dataset>/<artifact>`
   - `document_type = dataset` or `report`
   - `split = documentation | sample_data`
   - Include access URLs and license text (NOAA public domain).
4. Respect file sizes; for massive archives, download subsets (e.g., 1-year sample) and note in `notes`.
5. Verify data integrity (e.g., decompress, check row counts) before committing.

**Deliverable**
- NOAA dataset directories with documentation/data plus manifest metadata for downstream ingestion.
