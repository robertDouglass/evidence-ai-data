#!/usr/bin/env python3
"""
Download C3S Climate Indicators from Copernicus CDS.

These include temperature and precipitation anomalies, which are
pre-computed climate change indicators.

Requires:
- cdsapi package: pip install cdsapi
- CDS API key configured in ~/.cdsapirc
"""

import cdsapi
import os
from pathlib import Path

# Output directories
BASE_DIR = Path(__file__).parent.parent.parent / "data/datasets/copernicus"
INDICATORS_DIR = BASE_DIR / "climate_indicators"
TEMP_ANOMALY_DIR = BASE_DIR / "temperature_anomalies"
PRECIP_ANOMALY_DIR = BASE_DIR / "precipitation_anomalies"

for d in [INDICATORS_DIR, TEMP_ANOMALY_DIR, PRECIP_ANOMALY_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def download_surface_temperature_anomaly():
    """Download global surface temperature anomaly indicator."""

    c = cdsapi.Client()

    output_file = TEMP_ANOMALY_DIR / "surface_temperature_anomaly_global.nc"

    # C3S Global Temperature Indicator
    c.retrieve(
        'ecv-for-climate-change',
        {
            'variable': 'surface_air_temperature',
            'product_type': 'anomaly',
            'time_aggregation': 'monthly_mean',
            'year': [str(y) for y in range(1979, 2024)],
            'month': [f'{m:02d}' for m in range(1, 13)],
            'origin': 'era5',
            'format': 'zip',  # Contains NetCDF
        },
        str(output_file.with_suffix('.zip'))
    )

    print(f"Downloaded: {output_file.with_suffix('.zip')}")
    return output_file


def download_precipitation_anomaly():
    """Download global precipitation anomaly indicator."""

    c = cdsapi.Client()

    output_file = PRECIP_ANOMALY_DIR / "precipitation_anomaly_global.nc"

    c.retrieve(
        'ecv-for-climate-change',
        {
            'variable': 'precipitation',
            'product_type': 'anomaly',
            'time_aggregation': 'monthly_mean',
            'year': [str(y) for y in range(1979, 2024)],
            'month': [f'{m:02d}' for m in range(1, 13)],
            'origin': 'era5',
            'format': 'zip',
        },
        str(output_file.with_suffix('.zip'))
    )

    print(f"Downloaded: {output_file.with_suffix('.zip')}")
    return output_file


def download_sea_ice_extent():
    """Download sea ice extent indicator."""

    c = cdsapi.Client()

    output_file = INDICATORS_DIR / "sea_ice_extent.nc"

    c.retrieve(
        'ecv-for-climate-change',
        {
            'variable': 'sea_ice',
            'product_type': 'monthly_mean',
            'time_aggregation': 'monthly_mean',
            'year': [str(y) for y in range(1979, 2024)],
            'month': [f'{m:02d}' for m in range(1, 13)],
            'origin': 'c3s',
            'format': 'zip',
        },
        str(output_file.with_suffix('.zip'))
    )

    print(f"Downloaded: {output_file.with_suffix('.zip')}")
    return output_file


if __name__ == "__main__":
    print("C3S Climate Indicators Download Script")
    print("=" * 50)
    print("\nNote: Requires CDS API credentials in ~/.cdsapirc")
    print("Get your API key from: https://cds.climate.copernicus.eu/api-how-to\n")

    # Uncomment to run downloads:
    # download_surface_temperature_anomaly()
    # download_precipitation_anomaly()
    # download_sea_ice_extent()

    print("To download data, uncomment the function calls above.")
    print(f"Files will be saved to: {BASE_DIR}")
