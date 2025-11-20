#!/usr/bin/env python3
"""
Data Catalog Intake Script
Ingests climate datasets from Data.gov and OSTI APIs.
"""

import os
import json
import csv
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import time

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATASETS_DIR = DATA_DIR / "datasets" / "data_gov"
REPORTS_DIR = DATA_DIR / "reports" / "osti"
MANIFEST_PATH = BASE_DIR / "metadata" / "manifest.csv"

# Batch limits
MAX_DATA_GOV = 50
MAX_OSTI = 50

def sha256_file(filepath):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def download_file(url, dest_path, timeout=60):
    """Download a file from URL to destination path."""
    try:
        response = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)
        response.raise_for_status()

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False

def query_data_gov():
    """Query Data.gov API for climate change datasets."""
    print("\n=== Querying Data.gov API ===")

    url = "https://catalog.data.gov/api/3/action/package_search"
    params = {
        "q": "climate change",
        "fq": "metadata_modified:[2025-01-01T00:00:00Z TO *]",  # Filter for 2025 data
        "rows": 200,
        "sort": "metadata_modified desc"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            print("Data.gov API returned unsuccessful response")
            return []

        results = data.get("result", {}).get("results", [])
        print(f"Found {len(results)} total datasets")

        # Filter for datasets with downloadable resources
        filtered = []
        for pkg in results:
            resources = pkg.get("resources", [])
            for res in resources:
                fmt = res.get("format", "").upper()
                if fmt in ["CSV", "NETCDF", "PDF", "JSON", "XML"]:
                    filtered.append({
                        "package_name": pkg.get("name", "unknown"),
                        "title": pkg.get("title", "Unknown Title"),
                        "resource_url": res.get("url"),
                        "resource_format": fmt,
                        "license": pkg.get("license_title", "Unknown"),
                        "notes": pkg.get("notes", "")[:200] if pkg.get("notes") else ""
                    })
                    break  # Only take first downloadable resource per package

        print(f"Filtered to {len(filtered)} datasets with downloadable resources")
        return filtered[:MAX_DATA_GOV]

    except Exception as e:
        print(f"Error querying Data.gov: {e}")
        return []

def query_osti():
    """Query OSTI API for DOE-funded climate reports."""
    print("\n=== Querying OSTI API ===")

    all_records = []

    # Use OSTI.gov biblio API (documented endpoint)
    for page in range(1, 3):  # Get 2 pages
        url = "https://www.osti.gov/api/v1/records"
        headers = {"Accept": "application/json"}
        params = {
            "research_org": "DOE",  # Filter to DOE funded
            "subject": "climate",
            "rows": 50,
            "page": page
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            records = response.json()

            for rec in records:
                osti_id = rec.get("osti_id")
                if osti_id:
                    # OSTI PDFs follow predictable URL pattern
                    pdf_url = f"https://www.osti.gov/servlets/purl/{osti_id}"

                    all_records.append({
                        "osti_id": osti_id,
                        "title": rec.get("title", "Unknown Title"),
                        "doi": rec.get("doi", ""),
                        "pdf_url": pdf_url,
                        "authors": ", ".join(rec.get("authors", [])[:3]) if rec.get("authors") else "",
                        "publication_date": rec.get("publication_date", ""),
                        "contract_number": rec.get("doe_contract_number", "")
                    })

            print(f"Page {page}: Found {len(records)} records")
            time.sleep(1)  # Be nice to API

        except Exception as e:
            print(f"Error querying OSTI page {page}: {e}")
            break

    print(f"Total OSTI records: {len(all_records)}")
    return all_records[:MAX_OSTI]

def load_existing_manifest():
    """Load existing manifest entries."""
    existing = set()
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row.get("source_id", ""))
    return existing

def append_to_manifest(entries):
    """Append new entries to manifest."""
    if not entries:
        return

    fieldnames = [
        "source_id", "title", "document_type", "split", "items_count",
        "file_path", "file_size_bytes", "sha256", "download_url", "license", "notes"
    ]

    # Check if file exists and has content
    file_exists = MANIFEST_PATH.exists() and MANIFEST_PATH.stat().st_size > 0

    with open(MANIFEST_PATH, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for entry in entries:
            writer.writerow(entry)

    print(f"Added {len(entries)} entries to manifest")

def main():
    """Main intake process."""
    print("=" * 60)
    print("Data Catalog Intake - Data.gov & OSTI")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    existing = load_existing_manifest()
    new_entries = []

    # Process Data.gov datasets
    data_gov_datasets = query_data_gov()
    downloaded_data_gov = 0

    for dataset in data_gov_datasets:
        pkg_name = dataset["package_name"]
        source_id = f"data_gov/{pkg_name}"

        if source_id in existing:
            print(f"  Skipping {pkg_name} (already in manifest)")
            continue

        # Determine file extension
        fmt = dataset["resource_format"].lower()
        ext_map = {"csv": ".csv", "netcdf": ".nc", "pdf": ".pdf", "json": ".json", "xml": ".xml"}
        ext = ext_map.get(fmt, ".dat")

        # Download
        dest_dir = DATASETS_DIR / pkg_name
        dest_path = dest_dir / f"data{ext}"

        print(f"Downloading: {pkg_name}")
        if download_file(dataset["resource_url"], dest_path):
            file_size = dest_path.stat().st_size
            file_hash = sha256_file(dest_path)

            new_entries.append({
                "source_id": source_id,
                "title": dataset["title"][:200],
                "document_type": "dataset",
                "split": "resource",
                "items_count": 1,
                "file_path": str(dest_path.relative_to(BASE_DIR)),
                "file_size_bytes": file_size,
                "sha256": file_hash,
                "download_url": dataset["resource_url"],
                "license": dataset["license"],
                "notes": dataset["notes"][:150] if dataset["notes"] else f"Data.gov {fmt} resource"
            })
            downloaded_data_gov += 1

            if downloaded_data_gov >= 25:  # Limit per batch
                break

        time.sleep(0.5)  # Rate limiting

    print(f"\nDownloaded {downloaded_data_gov} Data.gov datasets")

    # Process OSTI reports
    osti_records = query_osti()
    downloaded_osti = 0

    for record in osti_records:
        osti_id = record["osti_id"]
        source_id = f"osti/{osti_id}"

        if source_id in existing:
            print(f"  Skipping OSTI {osti_id} (already in manifest)")
            continue

        dest_path = REPORTS_DIR / f"{osti_id}.pdf"

        print(f"Downloading OSTI: {osti_id}")
        if download_file(record["pdf_url"], dest_path):
            file_size = dest_path.stat().st_size
            file_hash = sha256_file(dest_path)

            notes = f"DOE Report"
            if record["doi"]:
                notes += f", DOI: {record['doi']}"
            if record["contract_number"]:
                notes += f", Contract: {record['contract_number']}"

            new_entries.append({
                "source_id": source_id,
                "title": record["title"][:200],
                "document_type": "report",
                "split": "fulltext",
                "items_count": 1,
                "file_path": str(dest_path.relative_to(BASE_DIR)),
                "file_size_bytes": file_size,
                "sha256": file_hash,
                "download_url": record["pdf_url"],
                "license": "U.S. Government Work",
                "notes": notes[:150]
            })
            downloaded_osti += 1

            if downloaded_osti >= 25:  # Limit per batch
                break

        time.sleep(0.5)  # Rate limiting

    print(f"\nDownloaded {downloaded_osti} OSTI reports")

    # Update manifest
    append_to_manifest(new_entries)

    # Summary
    print("\n" + "=" * 60)
    print("INTAKE SUMMARY")
    print("=" * 60)
    print(f"Data.gov datasets downloaded: {downloaded_data_gov}")
    print(f"OSTI reports downloaded: {downloaded_osti}")
    print(f"Total new manifest entries: {len(new_entries)}")
    print(f"Completed: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
