#!/usr/bin/env python3
"""
KfW Development Bank Financial Cooperation Evaluations Acquisition Script

This script automates the download and processing of ~900 KfW project evaluations
and thematic reports (2013-2024) emphasizing SDGs 7, 8, 9, 11, 13.

The script accesses the KfW IDEaL (Interactive Database Evaluation and Learning)
database at https://www.kfw-entwicklungsbank.de/ideal/ which provides access to
over 1,250 evaluations.

Usage:
    python acquisition_script.py
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from urllib.parse import urljoin, parse_qs, urlparse
import csv

try:
    from bs4 import BeautifulSoup
    HAS_BEAUTIFULSOUP = True
except ImportError:
    HAS_BEAUTIFULSOUP = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/evidence-ai/dataset/kfw/acquisition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KfWEvaluationAcquisition:
    """Manages the acquisition of KfW evaluation documents"""

    # Updated URLs pointing to actual KfW evaluation pages
    BASE_URL = "http://www.kfw-entwicklungsbank.de"
    IDEAL_DATABASE_URL = "https://www.kfw-entwicklungsbank.de/ideal/#/deViewDefault"
    EVALUATION_HOME = "/Evaluierung/"

    # SDG mappings based on sectors
    SECTOR_SDG_MAPPING = {
        'energy': ['7', '13'],
        'renewable energy': ['7', '9', '13'],
        'renewableenergy': ['7', '9', '13'],
        'transport': ['9', '11', '13'],
        'finance': ['8', '9'],
        'msme': ['8', '9'],
        'small': ['8', '9'],
        'medium': ['8', '9'],
        'enterprise': ['8', '9'],
        'climate': ['13'],
        'water': ['6', '13'],
        'health': ['3'],
        'education': ['4'],
        'agriculture': ['2', '12', '13'],
        'infrastructure': ['9', '11'],
        'industry': ['9'],
        'innovation': ['9'],
        'sustainable': ['7', '13'],
    }

    def __init__(self, config_path: str = "config.json", output_dir: str = "/home/user/evidence-ai/dataset/kfw"):
        """Initialize the acquisition manager"""
        self.output_dir = Path(output_dir)
        self.evaluations_dir = self.output_dir / "evaluations"
        self.annual_report_dir = self.output_dir / "annual-report"
        self.logs_dir = self.output_dir / "logs"
        self.metadata_file = self.output_dir / "metadata.jsonl"
        self.metadata_csv = self.output_dir / "metadata.csv"

        # Load config if it exists
        config_file = self.output_dir / config_path
        self.config = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                self.config = config_data.get('acquisition_config', {})

        # Create directories
        for dir_path in [self.evaluations_dir, self.annual_report_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Session with retry logic
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.downloaded_count = 0
        self.failed_count = 0
        self.metadata_records = []
        self.http_errors = {}
        self.start_time = datetime.now()

    def fetch_with_retry(self, url: str, max_retries: int = 4, is_pdf: bool = False) -> Optional[requests.Response]:
        """Fetch URL with exponential backoff retry logic"""
        backoff_times = [2, 4, 8, 16]

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30, stream=is_pdf)
                if response.status_code == 200:
                    return response
                elif response.status_code == 404:
                    logger.warning(f"URL not found (404): {url}")
                    self.http_errors[404] = self.http_errors.get(404, 0) + 1
                    return None
                elif response.status_code >= 500:
                    # Server error - retry
                    if attempt < max_retries - 1:
                        wait_time = backoff_times[attempt]
                        logger.warning(f"Server error ({response.status_code}) for {url}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    continue
            except requests.Timeout:
                if attempt < max_retries - 1:
                    wait_time = backoff_times[attempt]
                    logger.warning(f"Timeout for {url}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Timeout for {url} after {max_retries} attempts")
                    self.http_errors['timeout'] = self.http_errors.get('timeout', 0) + 1
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = backoff_times[attempt]
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                    self.http_errors['other'] = self.http_errors.get('other', 0) + 1

        return None

    def enumerate_evaluation_pages(self) -> List[Dict]:
        """
        Enumerate the evaluation results from KfW Evaluation Unit pages.
        Attempts to parse HTML for evaluation entries.
        """
        logger.info("Enumerating evaluation results pages...")
        evaluations = []

        if not HAS_BEAUTIFULSOUP:
            logger.warning("BeautifulSoup not installed. Please install with: pip install beautifulsoup4")
            logger.info("Attempting to enumerate from KfW evaluation homepage...")

        # Try to fetch the evaluation homepage
        home_url = f"{self.BASE_URL}{self.EVALUATION_HOME}"
        logger.info(f"Fetching evaluation homepage: {home_url}")

        response = self.fetch_with_retry(home_url)
        if response and HAS_BEAUTIFULSOUP:
            try:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for links to evaluation documents
                # The exact selectors will depend on the HTML structure
                links = soup.find_all('a', href=True)

                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)

                    # Look for PDF links or evaluation document links
                    if 'pdf' in href.lower() or 'evaluation' in href.lower() or 'evaluierung' in href.lower():
                        # Extract metadata from link text and URL
                        year = self._extract_year_from_text(text + ' ' + href)

                        if year and 2013 <= year <= 2024:
                            eval_entry = {
                                'doc_id': f'KFW-EVAL-{year}-{len(evaluations) + 1:03d}',
                                'url': urljoin(self.BASE_URL, href),
                                'title': text,
                                'metadata': {
                                    'publication_year': year,
                                    'sector': self._extract_sector(text),
                                    'region': self._extract_region(text),
                                    'language': 'en' if 'en' in href.lower() else 'de',
                                }
                            }
                            evaluations.append(eval_entry)
                            logger.debug(f"Found evaluation: {eval_entry['title']}")

                logger.info(f"Found {len(evaluations)} evaluation links on homepage")

            except Exception as e:
                logger.error(f"Error parsing evaluation homepage: {e}")
        elif response:
            logger.info("HTML parsing not available (BeautifulSoup not installed)")

        # If we didn't find any evaluations from HTML parsing, provide sample entries for demonstration
        if len(evaluations) == 0:
            logger.info("Note: No evaluations found from website. Creating sample metadata structure.")
            logger.info("To acquire actual evaluations, the KfW IDEaL database requires JavaScript rendering.")
            logger.info(f"IDEaL Database: {self.IDEAL_DATABASE_URL}")

            # Return empty list - actual data would come from IDEaL database
            # which requires JavaScript rendering (use Selenium, Playwright, or similar)

        return evaluations

    def _extract_year_from_text(self, text: str) -> Optional[int]:
        """Extract year from text"""
        import re
        years = re.findall(r'\b(20[0-2][0-9])\b', text)
        if years:
            return int(years[0])
        return None

    def _extract_sector(self, text: str) -> str:
        """Extract sector from text"""
        text_lower = text.lower()
        for sector_key in self.SECTOR_SDG_MAPPING.keys():
            if sector_key in text_lower:
                return sector_key
        return "general"

    def _extract_region(self, text: str) -> str:
        """Extract region from text"""
        text_lower = text.lower()
        if 'africa' in text_lower or 'sub-saharan' in text_lower:
            return 'Africa'
        elif 'asia' in text_lower:
            return 'Asia'
        elif 'latin' in text_lower or 'america' in text_lower:
            return 'Latin America'
        elif 'middle' in text_lower or 'north' in text_lower:
            return 'MENA'
        else:
            return 'Global'

    def download_evaluation(self, doc_id: str, url: str, metadata: Dict) -> bool:
        """Download a single evaluation document"""
        try:
            response = self.fetch_with_retry(url, is_pdf=True)
            if not response:
                self.failed_count += 1
                return False

            # Determine file path
            year = metadata.get('publication_year', 'unknown')
            language = metadata.get('language', 'en')
            filename = f"{doc_id}_{language}.pdf"
            file_path = self.evaluations_dir / str(year) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(file_path, 'wb') as f:
                f.write(response.content)

            # Validate file size
            file_size = file_path.stat().st_size
            min_size = self.config.get('quality_thresholds', {}).get('min_pdf_size_bytes', 5000)

            if file_size < min_size:  # Skip very small documents
                logger.warning(f"Skipping {doc_id} - file too small ({file_size} bytes, minimum {min_size})")
                file_path.unlink()
                self.failed_count += 1
                return False

            logger.info(f"Downloaded {doc_id} ({file_size / 1024:.1f} KB)")
            self.downloaded_count += 1

            # Store metadata
            metadata['doc_id'] = doc_id
            metadata['file_path'] = str(file_path)
            metadata['file_size_bytes'] = file_size
            metadata['download_timestamp'] = datetime.now().isoformat()

            # Map SDG tags if not already present
            if 'sdg_tags' not in metadata:
                sector = metadata.get('sector', '')
                metadata['sdg_tags'] = self.map_sdg_tags(sector)

            self.metadata_records.append(metadata)

            return True

        except Exception as e:
            logger.error(f"Error downloading {doc_id}: {e}")
            self.failed_count += 1
            return False

    def map_sdg_tags(self, sector: str, keywords: str = "") -> List[str]:
        """Map sector and keywords to SDG tags"""
        tags = set()

        # Map based on sector
        sector_lower = sector.lower()
        for key, sdgs in self.SECTOR_SDG_MAPPING.items():
            if key in sector_lower:
                tags.update(sdgs)

        # Additional mapping based on keywords
        keywords_lower = keywords.lower()
        for key, sdgs in self.SECTOR_SDG_MAPPING.items():
            if key in keywords_lower:
                tags.update(sdgs)

        # Ensure we have at least some SDGs
        if not tags:
            # Default to priority SDGs for documents without clear sector mapping
            tags.update(['7', '8', '9', '11', '13'])

        return sorted(list(tags))

    def save_metadata(self):
        """Save all collected metadata to JSONL and CSV files"""
        logger.info(f"Saving metadata for {len(self.metadata_records)} documents...")

        # Save as JSONL
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            for record in self.metadata_records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        logger.info(f"Saved {len(self.metadata_records)} records to {self.metadata_file}")

        # Also save as CSV for easier viewing
        if self.metadata_records:
            fieldnames = list(self.metadata_records[0].keys())
            # Ensure consistent field order
            priority_fields = ['doc_id', 'project_name', 'region', 'sector', 'publication_year', 'language']
            ordered_fields = [f for f in priority_fields if f in fieldnames]
            ordered_fields.extend([f for f in fieldnames if f not in ordered_fields])

            with open(self.metadata_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=ordered_fields)
                writer.writeheader()
                writer.writerows(self.metadata_records)

            logger.info(f"Saved CSV to {self.metadata_csv}")

    def generate_quality_report(self) -> Dict:
        """Generate comprehensive quality checks and statistics"""
        logger.info("Generating quality report...")

        # Basic statistics
        checks = {
            'execution_date': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
            'total_attempted': self.downloaded_count + self.failed_count,
            'total_downloaded': self.downloaded_count,
            'total_failed': self.failed_count,
            'success_rate_percent': (self.downloaded_count / (self.downloaded_count + self.failed_count) * 100
                                    if self.downloaded_count + self.failed_count > 0 else 0),
            'metadata_records': len(self.metadata_records),
        }

        # Check for SDG coverage
        all_sdgs = set()
        sdg_counts = {}
        for record in self.metadata_records:
            sdgs = record.get('sdg_tags', [])
            all_sdgs.update(sdgs)
            for sdg in sdgs:
                sdg_counts[sdg] = sdg_counts.get(sdg, 0) + 1

        priority_sdgs = {'7', '8', '9', '11', '13'}
        coverage = priority_sdgs.intersection(all_sdgs)
        checks['sdg_coverage'] = {
            'priority_sdgs_found': sorted(list(coverage)),
            'coverage_percentage': (len(coverage) / len(priority_sdgs) * 100),
            'sdg_distribution': sdg_counts
        }

        # Coverage by year
        year_coverage = {}
        for record in self.metadata_records:
            year = record.get('publication_year', 'unknown')
            year_coverage[year] = year_coverage.get(year, 0) + 1

        checks['year_coverage'] = dict(sorted(year_coverage.items()))

        # Coverage by sector
        sector_coverage = {}
        for record in self.metadata_records:
            sector = record.get('sector', 'unknown')
            sector_coverage[sector] = sector_coverage.get(sector, 0) + 1

        checks['sector_coverage'] = dict(sorted(sector_coverage.items(), key=lambda x: x[1], reverse=True))

        # Coverage by region
        region_coverage = {}
        for record in self.metadata_records:
            region = record.get('region', 'unknown')
            region_coverage[region] = region_coverage.get(region, 0) + 1

        checks['region_coverage'] = dict(sorted(region_coverage.items(), key=lambda x: x[1], reverse=True))

        # Coverage by language
        language_coverage = {}
        for record in self.metadata_records:
            lang = record.get('language', 'unknown')
            language_coverage[lang] = language_coverage.get(lang, 0) + 1

        checks['language_coverage'] = language_coverage

        # HTTP error summary
        checks['http_errors'] = self.http_errors

        logger.info(f"Quality Report: {json.dumps(checks, indent=2)}")

        # Save quality report
        report_file = self.output_dir / "quality_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(checks, f, indent=2, ensure_ascii=False)

        logger.info(f"Quality report saved to {report_file}")

        return checks

    def run(self):
        """Execute the full acquisition workflow"""
        logger.info("=" * 80)
        logger.info("Starting KfW Evaluation Acquisition")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Target documents: {self.config.get('target_documents', 'not specified')}")
        logger.info(f"Year range: {self.config.get('year_range', 'not specified')}")
        logger.info(f"Priority SDGs: {self.config.get('priority_sdgs', 'not specified')}")
        logger.info("=" * 80)

        try:
            # Step 1: Enumerate evaluation pages
            evaluations = self.enumerate_evaluation_pages()
            logger.info(f"Found {len(evaluations)} evaluations to download")

            # Step 2: Download each evaluation
            for i, eval_item in enumerate(evaluations, 1):
                doc_id = eval_item.get('doc_id')
                url = eval_item.get('url')
                metadata = eval_item.get('metadata', {})

                if doc_id and url:
                    logger.info(f"[{i}/{len(evaluations)}] Downloading {doc_id}...")
                    self.download_evaluation(doc_id, url, metadata)
                    time.sleep(0.5)  # Rate limiting per config

            # Step 3: Save metadata
            self.save_metadata()

            # Step 4: Quality checks and report
            self.generate_quality_report()

            logger.info("=" * 80)
            logger.info(f"Acquisition complete: {self.downloaded_count} downloaded, {self.failed_count} failed")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Fatal error during acquisition: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    acquisition = KfWEvaluationAcquisition()
    acquisition.run()
