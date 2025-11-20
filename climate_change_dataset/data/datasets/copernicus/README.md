# Copernicus Climate Data Store (CDS) Data

This directory contains climate data downloaded from the Copernicus Climate Data Store.

## Directory Structure

```
copernicus/
  era5_monthly/           # ERA5 monthly reanalysis data
  climate_indicators/     # General climate indicators (sea ice, etc.)
  temperature_anomalies/  # Temperature anomaly datasets
  precipitation_anomalies/# Precipitation anomaly datasets
```

## Prerequisites

1. **CDS API Key**: Register at https://cds.climate.copernicus.eu and get your API key
2. **Configuration**: Create `~/.cdsapirc` with:
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: <your-uid>:<your-api-key>
   ```
3. **Dependencies**:
   ```bash
   pip install cdsapi xarray netCDF4
   ```

## Download Scripts

Scripts are in `scripts/cds/`:

- `download_era5_monthly.py` - ERA5 monthly reanalysis (temperature, precipitation, pressure)
- `download_climate_indicators.py` - C3S climate indicators (anomalies, sea ice)
- `verify_data.py` - Verify downloaded NetCDF files using xarray

## Usage

```bash
cd scripts/cds/

# Edit scripts to uncomment desired downloads
python download_era5_monthly.py
python download_climate_indicators.py

# Verify downloaded data
python verify_data.py
```

## Data Coverage

- **Temporal**: 1979/1980 to 2023
- **Spatial**: Global, 1-degree resolution
- **Frequency**: Monthly means

## Datasets

| Dataset | Variables | Coverage | Size Est. |
|---------|-----------|----------|-----------|
| ERA5 2m Temperature | t2m | 1980-2023, Global 1deg | ~500 MB |
| ERA5 Total Precipitation | tp | 1980-2023, Global 1deg | ~500 MB |
| ERA5 Sea Level Pressure | msl | 1980-2023, Global 1deg | ~500 MB |
| C3S Temperature Anomaly | temp_anomaly | 1979-2023 | ~200 MB |
| C3S Precipitation Anomaly | precip_anomaly | 1979-2023 | ~200 MB |
| C3S Sea Ice Extent | sie | 1979-2023 | ~100 MB |

## License

All data subject to Copernicus Data Policy:
https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf

## References

- ERA5: https://doi.org/10.24381/cds.adbb2d47
- Climate Indicators: https://doi.org/10.24381/cds.4311f3f4
