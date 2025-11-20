#!/usr/bin/env python3
"""
Download USGS climate science publications from the Publications Warehouse API.
"""

import json
import os
import re
import hashlib
import time
import csv
from pathlib import Path
import requests

BASE_URL = "https://pubs.usgs.gov/pubs-services/publication"
DATA_DIR = Path(__file__).parent.parent / "data" / "reports" / "usgs"
METADATA_DIR = Path(__file__).parent.parent / "metadata"
MANIFEST_PATH = METADATA_DIR / "manifest.csv"

# Search terms to cover different climate topics
# Use USGS Numbered Series which have reliable PDF downloads
SEARCH_TOPICS = [
    ("climate", 25),
    ("sea level", 10),
    ("wildfire", 8),
    ("drought", 8),
    ("glacier", 8),
    ("groundwater temperature", 6),
    ("coastal erosion", 5),
    ("ecosystem change", 5),
]

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:60]

def get_file_hash(filepath):
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def fetch_publications(query, page_size=25):
    """Fetch publications from USGS API."""
    params = {
        'q': query,
        'pageSize': page_size,
        'subtypeName': 'USGS Numbered Series',  # These have PDFs
        'mimeType': 'json'
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json().get('records', [])
    except Exception as e:
        print(f"Error fetching publications for '{query}': {e}")
        return []

def find_pdf_link(pub):
    """Extract PDF download URL from publication record."""
    links = pub.get('links', [])

    # First pass: look for explicit PDF links
    for link in links:
        link_type = link.get('type', {})
        if isinstance(link_type, dict):
            type_text = link_type.get('text', '')
        else:
            type_text = str(link_type)

        url = link.get('url', '')
        if 'pdf' in type_text.lower() or url.endswith('.pdf'):
            return url

    # Second pass: look for Index Page or Document links on pubs.usgs.gov
    for link in links:
        url = link.get('url', '')
        if 'pubs.usgs.gov' in url and not url.endswith('.pdf'):
            link_type = link.get('type', {})
            type_text = link_type.get('text', '') if isinstance(link_type, dict) else ''
            if 'Index Page' in type_text or 'Document' in type_text:
                # Try to construct PDF URL from index page
                pub_id = pub.get('indexId')
                if pub_id:
                    pdf_url = f"https://pubs.usgs.gov/publication/{pub_id}/pdf"
                    try:
                        resp = requests.head(pdf_url, timeout=10, allow_redirects=True)
                        if resp.status_code == 200:
                            return pdf_url
                    except:
                        pass

    # Try standard USGS PDF URL pattern
    pub_id = pub.get('indexId')
    if pub_id:
        pdf_url = f"https://pubs.usgs.gov/publication/{pub_id}/pdf"
        try:
            resp = requests.head(pdf_url, timeout=10, allow_redirects=True)
            if resp.status_code == 200:
                return pdf_url
        except:
            pass

    return None

def download_pdf(url, filepath):
    """Download PDF file with retry logic."""
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=60, stream=True)
            resp.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                print(f"Failed to download {url}: {e}")
    return False

def load_existing_hashes():
    """Load existing file hashes from manifest to avoid duplicates."""
    hashes = set()
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('sha256'):
                    hashes.add(row['sha256'])
    return hashes

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    existing_hashes = load_existing_hashes()
    downloaded = []
    seen_ids = set()

    print("Fetching USGS climate publications...")

    for query, count in SEARCH_TOPICS:
        print(f"\nSearching for: {query} (target: {count})")
        pubs = fetch_publications(query, page_size=count * 3)

        topic_count = 0
        for pub in pubs:
            if topic_count >= count:
                break

            pub_id = pub.get('indexId')
            if not pub_id or pub_id in seen_ids:
                continue

            title = pub.get('title', 'Unknown')
            pdf_url = find_pdf_link(pub)

            if not pdf_url:
                continue

            # Create slug and directory
            slug = slugify(title)
            pub_dir = DATA_DIR / slug
            pub_dir.mkdir(exist_ok=True)

            pdf_path = pub_dir / f"{slug}.pdf"

            print(f"  Downloading: {title[:60]}...")

            if download_pdf(pdf_url, pdf_path):
                file_hash = get_file_hash(pdf_path)

                # Check for duplicates
                if file_hash in existing_hashes:
                    print(f"    Skipping duplicate: {title[:40]}")
                    pdf_path.unlink()
                    if not any(pub_dir.iterdir()):
                        pub_dir.rmdir()
                    continue

                existing_hashes.add(file_hash)
                seen_ids.add(pub_id)

                # Extract metadata
                abstract = pub.get('docAbstract', '')
                if abstract:
                    # Strip HTML tags
                    abstract = re.sub(r'<[^>]+>', '', abstract)[:300]

                authors = []
                for contrib in pub.get('contributors', {}).get('authors', []):
                    name = contrib.get('text', '')
                    if name:
                        authors.append(name)

                doi = pub.get('doi', '')
                year = pub.get('publicationYear', '')

                # Save sidecar JSON
                metadata = {
                    'pub_id': pub_id,
                    'title': title,
                    'authors': authors,
                    'doi': doi,
                    'year': year,
                    'abstract': abstract,
                    'download_url': pdf_url,
                    'publication_type': pub.get('publicationType', {}).get('text', ''),
                    'series': pub.get('seriesTitle', {}).get('text', '') if isinstance(pub.get('seriesTitle'), dict) else ''
                }

                json_path = pub_dir / f"{slug}_metadata.json"
                with open(json_path, 'w') as f:
                    json.dump(metadata, f, indent=2)

                # Prepare manifest entry
                file_size = pdf_path.stat().st_size
                rel_path = pdf_path.relative_to(Path(__file__).parent.parent)

                downloaded.append({
                    'source_id': f"usgs/{slug}",
                    'title': title,
                    'document_type': 'report',
                    'split': 'main',
                    'items_count': 1,
                    'file_path': str(rel_path),
                    'file_size_bytes': file_size,
                    'sha256': file_hash,
                    'download_url': pdf_url,
                    'license': 'USGS Public Domain',
                    'notes': abstract[:200] if abstract else f"USGS publication {pub_id}"
                })

                topic_count += 1

            time.sleep(0.5)  # Rate limiting

    print(f"\n\nDownloaded {len(downloaded)} publications")

    # Append to manifest
    if downloaded:
        fieldnames = ['source_id', 'title', 'document_type', 'split', 'items_count',
                      'file_path', 'file_size_bytes', 'sha256', 'download_url', 'license', 'notes']

        with open(MANIFEST_PATH, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for entry in downloaded:
                writer.writerow(entry)

        print(f"Added {len(downloaded)} entries to manifest")

    return len(downloaded)

if __name__ == '__main__':
    main()
