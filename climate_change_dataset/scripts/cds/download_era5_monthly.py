#!/usr/bin/env python3
"""
Download ERA5 monthly averaged data on single levels from Copernicus CDS.

Requires:
- cdsapi package: pip install cdsapi
- CDS API key configured in ~/.cdsapirc

Configuration file ~/.cdsapirc should contain:
url: https://cds.climate.copernicus.eu/api/v2
key: <your-uid>:<your-api-key>
"""

import cdsapi
import os
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data/datasets/copernicus/era5_monthly"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def download_era5_monthly_temperature():
    """Download ERA5 monthly mean 2m temperature (1980-present, global 1 degree)."""

    c = cdsapi.Client()

    output_file = OUTPUT_DIR / "era5_monthly_2m_temperature_1980_2023.nc"

    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': '2m_temperature',
            'year': [str(y) for y in range(1980, 2024)],
            'month': [f'{m:02d}' for m in range(1, 13)],
            'time': '00:00',
            'area': [90, -180, -90, 180],  # Global
            'grid': [1.0, 1.0],  # 1 degree resolution
            'format': 'netcdf',
        },
        str(output_file)
    )

    print(f"Downloaded: {output_file}")
    return output_file


def download_era5_monthly_precipitation():
    """Download ERA5 monthly mean total precipitation (1980-present, global 1 degree)."""

    c = cdsapi.Client()

    output_file = OUTPUT_DIR / "era5_monthly_total_precipitation_1980_2023.nc"

    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': 'total_precipitation',
            'year': [str(y) for y in range(1980, 2024)],
            'month': [f'{m:02d}' for m in range(1, 13)],
            'time': '00:00',
            'area': [90, -180, -90, 180],
            'grid': [1.0, 1.0],
            'format': 'netcdf',
        },
        str(output_file)
    )

    print(f"Downloaded: {output_file}")
    return output_file


def download_era5_monthly_sea_level_pressure():
    """Download ERA5 monthly mean sea level pressure (1980-present, global 1 degree)."""

    c = cdsapi.Client()

    output_file = OUTPUT_DIR / "era5_monthly_msl_1980_2023.nc"

    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': 'mean_sea_level_pressure',
            'year': [str(y) for y in range(1980, 2024)],
            'month': [f'{m:02d}' for m in range(1, 13)],
            'time': '00:00',
            'area': [90, -180, -90, 180],
            'grid': [1.0, 1.0],
            'format': 'netcdf',
        },
        str(output_file)
    )

    print(f"Downloaded: {output_file}")
    return output_file


if __name__ == "__main__":
    print("ERA5 Monthly Data Download Script")
    print("=" * 50)
    print("\nNote: Requires CDS API credentials in ~/.cdsapirc")
    print("Get your API key from: https://cds.climate.copernicus.eu/api-how-to\n")

    # Uncomment to run downloads:
    # download_era5_monthly_temperature()
    # download_era5_monthly_precipitation()
    # download_era5_monthly_sea_level_pressure()

    print("To download data, uncomment the function calls above.")
    print(f"Files will be saved to: {OUTPUT_DIR}")
