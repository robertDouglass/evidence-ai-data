#!/usr/bin/env python3
"""
BGR Publication Acquisition Script Template

This script provides a template for automated acquisition of BGR publications.
Use with caution: respect robots.txt and add appropriate delays between requests.

Requirements:
    pip install requests beautifulsoup4 python-dateutil
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://www.bgr.bund.de"
REPOSITORY_URL = f"{BASE_URL}/EN/Themen/Publikationen/publikationen_node_en.html"
COMMODITY_NEWS_URL = f"{BASE_URL}/EN/Themen/Rohstoffe/CommodityTopNews/commodity_top_news_node_en.html"

# Output directories
SCRIPT_DIR = Path(__file__).parent
PDF_DIR = SCRIPT_DIR / "pdfs"
METADATA_DIR = SCRIPT_DIR / "metadata"
RAW_PAGES_DIR = SCRIPT_DIR / "raw_pages"
REGISTRY_FILE = SCRIPT_DIR / "metadata_registry.jsonl"

# Ensure directories exist
PDF_DIR.mkdir(exist_ok=True)
METADATA_DIR.mkdir(exist_ok=True)
RAW_PAGES_DIR.mkdir(exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Session with headers to appear as legitimate browser
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Rate limiting: delay between requests (in seconds)
REQUEST_DELAY = 2.0


class BGRPublicationAcquisitor:
    """Handles acquisition of BGR publications"""

    def __init__(self):
        self.publications = []
        self.metadata_registry = self._load_registry()

    def _load_registry(self) -> Dict:
        """Load existing metadata registry"""
        registry = {}
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        entry = json.loads(line)
                        registry[entry.get('doc_id')] = entry
        return registry

    def _save_registry(self):
        """Save metadata registry"""
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            f.write('# JSONL format: one JSON object per line\n')
            for entry in self.metadata_registry.values():
                f.write(json.dumps(entry) + '\n')

    def fetch_publication_list(self, page: int = 1) -> Optional[BeautifulSoup]:
        """
        Fetch a page from the BGR publication repository

        Args:
            page: Page number to fetch (starting from 1)

        Returns:
            BeautifulSoup object or None if request failed
        """
        try:
            # Note: Adjust URL pattern based on actual BGR website structure
            url = f"{REPOSITORY_URL}?page={page}"
            logger.info(f"Fetching: {url}")

            response = session.get(url, timeout=10)
            response.raise_for_status()

            # Save raw page for reference
            raw_file = RAW_PAGES_DIR / f"publications_page_{page}.html"
            with open(raw_file, 'w', encoding='utf-8') as f:
                f.write(response.text)

            time.sleep(REQUEST_DELAY)  # Rate limiting
            return BeautifulSoup(response.text, 'html.parser')

        except requests.RequestException as e:
            logger.error(f"Error fetching page {page}: {e}")
            return None

    def extract_publication_metadata(self, publication_element) -> Optional[Dict]:
        """
        Extract metadata from a publication element on the list page

        Args:
            publication_element: BeautifulSoup element representing one publication

        Returns:
            Dictionary with publication metadata or None if parsing failed
        """
        try:
            # This is a template - adjust selectors based on actual BGR HTML structure
            metadata = {
                'title': publication_element.find('h3').text.strip() if publication_element.find('h3') else '',
                'url': publication_element.find('a')['href'] if publication_element.find('a') else '',
                'year': 2024,  # TODO: extract from page
                'language': 'en',  # TODO: detect from page
                'document_type': 'report',  # TODO: extract from page
                'pages': 0,  # TODO: extract from detail page
                'topic': 'other',  # TODO: infer from content
                'sdg_tags': [],  # TODO: detect from content
            }
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return None

    def fetch_publication_detail(self, publication_url: str) -> Optional[Dict]:
        """
        Fetch detail page for a single publication and extract full metadata

        Args:
            publication_url: URL to the publication detail page

        Returns:
            Dictionary with complete publication metadata
        """
        try:
            full_url = urljoin(BASE_URL, publication_url)
            logger.info(f"Fetching detail: {full_url}")

            response = session.get(full_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract detailed metadata - adjust selectors as needed
            metadata = {
                'title': soup.find('h1').text.strip() if soup.find('h1') else 'Unknown',
                'authors': [],  # TODO: extract authors
                'year': 2024,  # TODO: extract year
                'language': 'en',  # TODO: detect language
                'abstract': '',  # TODO: extract abstract
                'keywords': [],  # TODO: extract keywords
                'isbn': '',  # TODO: extract ISBN
                'series': '',  # TODO: extract series
                'issue_number': '',  # TODO: extract issue
                'pages': 0,  # TODO: extract page count
                'url': full_url,
                'pdf_url': '',  # TODO: find PDF download URL
                'topic': 'other',  # TODO: classify topic
                'document_type': 'report',  # TODO: identify type
                'region': '',  # TODO: extract region
                'sdg_tags': [],  # TODO: identify SDGs
            }

            time.sleep(REQUEST_DELAY)
            return metadata

        except Exception as e:
            logger.error(f"Error fetching detail page: {e}")
            return None

    def download_pdf(self, pdf_url: str, filename: str) -> bool:
        """
        Download PDF file

        Args:
            pdf_url: URL to PDF file
            filename: Filename to save as (without path)

        Returns:
            True if download successful, False otherwise
        """
        try:
            logger.info(f"Downloading PDF: {pdf_url}")
            response = session.get(pdf_url, timeout=30, stream=True)
            response.raise_for_status()

            filepath = PDF_DIR / filename
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Saved: {filepath}")
            time.sleep(REQUEST_DELAY)
            return True

        except Exception as e:
            logger.error(f"Error downloading PDF {pdf_url}: {e}")
            return False

    def save_metadata(self, metadata: Dict) -> bool:
        """
        Save publication metadata to JSON file and registry

        Args:
            metadata: Publication metadata dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Generate doc_id if not present
            if 'doc_id' not in metadata:
                # Format: BGR-<series>-YYYY-###
                year = metadata.get('year', 2024)
                series = metadata.get('series', 'PUB')[:3].upper()
                num = len([k for k in self.metadata_registry.keys()
                          if k.startswith(f"BGR-{series}-{year}")]) + 1
                metadata['doc_id'] = f"BGR-{series}-{year}-{num:03d}"

            # Save individual metadata file
            metadata_file = METADATA_DIR / f"{metadata['doc_id']}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # Add to registry
            registry_entry = {
                'doc_id': metadata['doc_id'],
                'title': metadata.get('title', 'Unknown'),
                'year': metadata.get('year', 0),
                'topic': metadata.get('topic', 'other'),
                'status': 'acquired',
                'download_date': datetime.now().isoformat()
            }
            self.metadata_registry[metadata['doc_id']] = registry_entry
            self._save_registry()

            logger.info(f"Saved metadata for {metadata['doc_id']}")
            return True

        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return False

    def validate_metadata(self, metadata: Dict) -> bool:
        """
        Validate metadata against schema

        Args:
            metadata: Publication metadata to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['title', 'year', 'topic', 'pages', 'url']

        # Check required fields
        if not all(field in metadata for field in required_fields):
            logger.warning(f"Missing required fields in: {metadata.get('title', 'Unknown')}")
            return False

        # Check page count
        if metadata['pages'] < 10:
            logger.warning(f"Document too short ({metadata['pages']} pages): {metadata.get('title', 'Unknown')}")
            return False

        # Check year range
        if not (2013 <= metadata['year'] <= 2024):
            logger.warning(f"Year out of range ({metadata['year']}): {metadata.get('title', 'Unknown')}")
            return False

        metadata['quality_checked'] = True
        return True

    def run_acquisition(self, max_pages: int = 5):
        """
        Main acquisition loop

        Args:
            max_pages: Maximum number of pages to process
        """
        logger.info("Starting BGR publication acquisition")
        logger.info(f"Target: {max_pages} pages")

        for page in range(1, max_pages + 1):
            logger.info(f"Processing page {page}/{max_pages}")

            soup = self.fetch_publication_list(page)
            if not soup:
                logger.warning(f"Failed to fetch page {page}, stopping")
                break

            # Find all publication items on page
            # Adjust selector based on actual BGR HTML structure
            publications = soup.find_all('div', class_='publication-item')

            if not publications:
                logger.info(f"No publications found on page {page}")
                break

            logger.info(f"Found {len(publications)} publications on page {page}")

            for pub in publications:
                # Extract basic info from list page
                basic_metadata = self.extract_publication_metadata(pub)
                if not basic_metadata:
                    continue

                # Fetch detail page for full metadata
                detail_metadata = self.fetch_publication_detail(basic_metadata['url'])
                if not detail_metadata:
                    continue

                # Validate metadata
                if not self.validate_metadata(detail_metadata):
                    continue

                # Download PDF if available
                if detail_metadata.get('pdf_url'):
                    pdf_filename = detail_metadata.get('pdf_filename',
                                                      f"bgr_{detail_metadata.get('year')}_unnamed.pdf")
                    if not self.download_pdf(detail_metadata['pdf_url'], pdf_filename):
                        logger.warning(f"Failed to download PDF for {detail_metadata.get('title')}")
                        continue
                    detail_metadata['pdf_filename'] = pdf_filename
                    detail_metadata['download_date'] = datetime.now().isoformat()

                # Save metadata
                if self.save_metadata(detail_metadata):
                    logger.info(f"Successfully acquired: {detail_metadata['title']}")

        logger.info("Acquisition complete")
        logger.info(f"Total publications acquired: {len(self.metadata_registry)}")


if __name__ == '__main__':
    acquisitor = BGRPublicationAcquisitor()

    # Start acquisition
    # Adjust max_pages parameter as needed
    acquisitor.run_acquisition(max_pages=5)
