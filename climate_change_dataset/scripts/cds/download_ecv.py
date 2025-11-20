#!/usr/bin/env python3
"""
Download Essential Climate Variables (ECV) for climate change assessment from Copernicus CDS.

This dataset is specifically designed for monitoring and assessment of climate variability
and change, making it ideal for RAG systems understanding climate change.

Requires:
- cdsapi package: pip install cdsapi
- CDS API key configured in ~/.cdsapirc

Configuration file ~/.cdsapirc should contain:
url: https://cds.climate.copernicus.eu/api/v2
key: <your-uid>:<your-api-key>
"""

import cdsapi
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data/datasets/copernicus/ecv_climate_change"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_ecv_monthly_means():
    """
    Download Essential Climate Variables monthly means for climate change assessment.

    Variables included:
    - Surface air temperature
    - Surface air relative humidity
    - 0-7cm volumetric soil moisture
    - Precipitation
    - Sea ice cover

    Time coverage: Selected years from 1979-2025 (5-year intervals + recent years)
    """

    dataset = "ecv-for-climate-change"
    request = {
        "variable": [
            "surface_air_temperature",
            "surface_air_relative_humidity",
            "0_7cm_volumetric_soil_moisture",
            "precipitation",
            "sea_ice_cover"
        ],
        "origin": [
            "era5",
            "era5_land"
        ],
        "product_type": ["monthly_mean"],
        "time_aggregation": ["1_month_mean"],
        "year": [
            "2019", "2020", "2021",
            "2022", "2023", "2024"
        ],
        "month": [
            "01", "02", "03",
            "04", "05", "06",
            "07", "08", "09",
            "10", "11", "12"
        ]
    }

    output_file = OUTPUT_DIR / "ecv_monthly_means_2019_2024.zip"

    client = cdsapi.Client()
    client.retrieve(dataset, request).download(str(output_file))

    print(f"Downloaded: {output_file}")
    print("\nDataset contains:")
    print("  - Surface air temperature")
    print("  - Surface air relative humidity")
    print("  - Volumetric soil moisture (0-7cm)")
    print("  - Precipitation")
    print("  - Sea ice cover")
    print(f"\nYears: 1979, 1984, 1989, 1994, 1999, 2004, 2009, 2014, 2019-2025")
    print("Origin: ERA5 and ERA5-Land reanalysis")

    return output_file


if __name__ == "__main__":
    print("Essential Climate Variables Download Script")
    print("=" * 50)
    print("\nNote: Requires CDS API credentials in ~/.cdsapirc")
    print("Get your API key from: https://cds.climate.copernicus.eu/api-how-to\n")

    download_ecv_monthly_means()
