#!/usr/bin/env python3
"""
Verify downloaded Copernicus CDS data using xarray.

This script loads NetCDF files and logs variable statistics
to verify data integrity.

Requires:
- xarray: pip install xarray
- netCDF4: pip install netCDF4
"""

import os
from pathlib import Path

try:
    import xarray as xr
    import numpy as np
    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False
    print("Warning: xarray not installed. Install with: pip install xarray netCDF4")

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data/datasets/copernicus"


def verify_netcdf(filepath):
    """Load and verify a NetCDF file, printing statistics."""

    if not HAS_XARRAY:
        print("Cannot verify: xarray not installed")
        return None

    filepath = Path(filepath)
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return None

    print(f"\nVerifying: {filepath.name}")
    print("-" * 50)

    ds = xr.open_dataset(filepath)

    # Print dimensions
    print(f"Dimensions: {dict(ds.dims)}")

    # Print coordinates
    print(f"Coordinates: {list(ds.coords)}")

    # Print variables and their stats
    print("\nVariables:")
    for var_name in ds.data_vars:
        var = ds[var_name]
        print(f"\n  {var_name}:")
        print(f"    Shape: {var.shape}")
        print(f"    Dtype: {var.dtype}")

        # Calculate statistics
        values = var.values
        if np.issubdtype(values.dtype, np.number):
            valid = ~np.isnan(values)
            if valid.any():
                print(f"    Min: {np.nanmin(values):.4f}")
                print(f"    Max: {np.nanmax(values):.4f}")
                print(f"    Mean: {np.nanmean(values):.4f}")
                print(f"    Std: {np.nanstd(values):.4f}")
                print(f"    NaN count: {(~valid).sum()}")

        # Print attributes
        if var.attrs:
            units = var.attrs.get('units', 'N/A')
            long_name = var.attrs.get('long_name', 'N/A')
            print(f"    Units: {units}")
            print(f"    Long name: {long_name}")

    # Time range if available
    if 'time' in ds.coords:
        times = ds['time'].values
        print(f"\nTime range: {times[0]} to {times[-1]}")
        print(f"Time steps: {len(times)}")

    ds.close()
    return True


def verify_all_data():
    """Verify all NetCDF files in the Copernicus data directory."""

    print("Copernicus CDS Data Verification")
    print("=" * 50)

    nc_files = list(DATA_DIR.rglob("*.nc"))

    if not nc_files:
        print(f"\nNo NetCDF files found in {DATA_DIR}")
        print("Run the download scripts first to acquire data.")
        return

    print(f"\nFound {len(nc_files)} NetCDF file(s)")

    for nc_file in nc_files:
        verify_netcdf(nc_file)

    print("\n" + "=" * 50)
    print("Verification complete")


if __name__ == "__main__":
    verify_all_data()
