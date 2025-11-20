# Prompt 11 – Copernicus Climate Data Store (CDS) Extraction

**Objective**: Acquire key Copernicus CDS datasets (ERA5 reanalysis subsets, climate indicators, and Toolbox workflows) for offline use.

**Actions**
1. Log into https://cds.climate.copernicus.eu and identify priority datasets:
   - ERA5 monthly averaged data on single levels (global subset).
   - Climate Data Store indicators (Essential Climate Variables).
   - C3S climate indicators (temperature, precipitation anomalies).
2. Use the CDS API (`cdsapi`) to script downloads of manageable spatiotemporal subsets (e.g., 1980–present, global 1° grid).
3. Save NetCDF files under `data/datasets/copernicus/<dataset_name>/`.
4. Document each dataset in `metadata/manifest.csv` with:
   - `source_id = copernicus/<dataset>/<subset>`
   - `document_type = dataset`
   - `split = netcdf`
   - `license = Copernicus Data Policy`
   - `notes = describe spatial/temporal coverage + variables`.
5. Keep API scripts in `scripts/cds/` so others can reproduce.
6. Verify integrity by loading a sample (e.g., using `xarray`) and logging variable stats in the notes or a sidecar README.

**Deliverable**
- Curated ERA5/C3S datasets stored locally with reproducible scripts + manifest metadata.
