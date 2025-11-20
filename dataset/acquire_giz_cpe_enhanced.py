#!/usr/bin/env python3
"""
GIZ CPE Acquisition Script - Enhanced Version with Browser Support

This script includes:
1. REST API fallback (attempted first)
2. HTML scraping with pagination
3. Browser-based scraping with JavaScript support (optional)
4. Manual data seeding framework
5. Comprehensive logging and quality reporting
"""

import os
import json
import time
import logging
import hashlib
import re
import csv
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Try to import optional dependencies for enhanced scraping
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available - browser-based scraping disabled")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('giz_acquisition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'base_url': 'https://www.giz.de/en/mediacenter/publications/evaluations',
    'api_endpoint': 'https://www.giz.de/services/REST/',
    'start_year': 2020,
    'end_year': 2024,
    'min_pages': 20,
    'output_dir': Path(__file__).parent / 'data' / 'giz',
    'metadata_dir': Path(__file__).parent / 'data' / 'giz' / 'metadata',
    'user_agent': 'Mozilla/5.0 (Linux; U; Linux) Gecko/20100101 Firefox/110.0',
    'target_sdgs': ['3', '4', '6', '13', '16'],
    'giz_sectors': ['climate', 'governance', 'health', 'economic_development', 'education', 'water'],
    'request_timeout': 30,
    'retry_attempts': 3
}


class RobustSession(requests.Session):
    """Session with retry logic for robust HTTP requests."""

    def __init__(self):
        super().__init__()
        retry_strategy = Retry(
            total=CONFIG['retry_attempts'],
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.mount("https://", adapter)
        self.mount("http://", adapter)
        self.headers.update({'User-Agent': CONFIG['user_agent']})


class GIZCPEAcquisitor:
    """Main class for GIZ CPE document acquisition."""

    def __init__(self, use_browser=False):
        self.session = RobustSession()
        self.session.timeout = CONFIG['request_timeout']
        self.output_dir = CONFIG['output_dir']
        self.metadata_dir = CONFIG['metadata_dir']
        self.document_registry = []
        self.use_browser = use_browser and SELENIUM_AVAILABLE
        self.acquisition_stats = {
            'total_found': 0,
            'downloaded': 0,
            'failed': 0,
            'skipped': 0,
            'sources': {}
        }
        self._setup_directories()

    def _setup_directories(self):
        """Create necessary directory structure."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        logs_dir = self.output_dir / 'logs'
        logs_dir.mkdir(parents=True, exist_ok=True)

        for year in range(CONFIG['start_year'], CONFIG['end_year'] + 1):
            year_dir = self.output_dir / 'cpe' / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Directory structure created at {self.output_dir}")

    def acquire(self):
        """Main acquisition workflow."""
        logger.info("=" * 70)
        logger.info("Starting GIZ CPE Acquisition (Enhanced)")
        logger.info(f"Target years: {CONFIG['start_year']}-{CONFIG['end_year']}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("=" * 70)

        evaluations = []

        # Step 1: Try API endpoint
        evaluations = self._try_api_endpoint() or []
        if evaluations:
            self.acquisition_stats['sources']['api'] = len(evaluations)

        # Step 2: Fall back to HTML scraping
        if not evaluations:
            evaluations = self._scrape_html_pagination()
            if evaluations:
                self.acquisition_stats['sources']['html_scrape'] = len(evaluations)

        # Step 3: Try browser-based scraping if configured
        if not evaluations and self.use_browser:
            evaluations = self._scrape_with_browser()
            if evaluations:
                self.acquisition_stats['sources']['browser'] = len(evaluations)

        self.acquisition_stats['total_found'] = len(evaluations)

        if not evaluations:
            logger.warning("No evaluations found through any method")
            logger.info("="*70)
            logger.info("MANUAL DATA SEEDING REQUIRED")
            logger.info("="*70)
            self._generate_data_seeding_template()
            self._generate_report()
            return

        # Process each evaluation
        for eval_doc in evaluations:
            try:
                metadata = self.extract_metadata(eval_doc)

                # Attempt download
                filepath = None
                if eval_doc.get('url'):
                    year = metadata.get('publication_date', '2024')[:4]
                    slug = metadata['doc_id'].split('-')[-1]
                    filepath = self.download_pdf(eval_doc['url'], year, slug)

                # Validate and save
                if filepath:
                    validation = self.validate_pdf(filepath)
                    metadata['validation'] = validation
                    if validation['valid']:
                        self.save_metadata(metadata)
                        self.document_registry.append(metadata)
                        self.acquisition_stats['downloaded'] += 1
                    else:
                        self.acquisition_stats['failed'] += 1
                        logger.warning(f"Document failed validation: {filepath}")
                else:
                    self.acquisition_stats['failed'] += 1

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error processing evaluation: {e}")
                self.acquisition_stats['failed'] += 1

        # Save registry and report
        self.save_registry()
        self._generate_report()

        logger.info("=" * 70)
        logger.info("Acquisition Complete")
        logger.info(f"Summary: {json.dumps(self.acquisition_stats, indent=2)}")
        logger.info("=" * 70)

    def _try_api_endpoint(self) -> Optional[List[Dict]]:
        """Try to fetch evaluations from REST API."""
        try:
            logger.info("Attempting API endpoint access...")
            params = {
                'start': 0,
                'limit': 1000,
                'filter': json.dumps({'year': {'$gte': CONFIG['start_year']}}),
                'sort': {'date': -1}
            }

            response = self.session.get(
                f"{CONFIG['api_endpoint']}evaluations",
                params=params,
                timeout=CONFIG['request_timeout']
            )
            response.raise_for_status()
            data = response.json()

            if data.get('records'):
                logger.info(f"API returned {len(data['records'])} records")
                return data['records']
            return None

        except Exception as e:
            logger.warning(f"API endpoint failed: {e}")
            return None

    def _scrape_html_pagination(self) -> List[Dict]:
        """Scrape evaluation list via HTML pagination."""
        evaluations = []

        base_urls = [
            'https://www.giz.de/en/about-us/results-evaluation/project-evaluations',
            'https://www.giz.de/de/ueber-uns/wirkung-evaluierung/projektevaluierungen',
            'https://www.giz.de/en/about-us/results-evaluation/overarching-evaluations',
            'https://www.giz.de/de/ueber-uns/wirkung-evaluierung/uebergeordnete-evaluierungen',
            CONFIG['base_url']
        ]

        for base_url in base_urls:
            page = 0
            consecutive_empty = 0

            while consecutive_empty < 2:
                try:
                    if page == 0:
                        url = base_url
                    else:
                        url = f"{base_url}?page={page}"

                    logger.info(f"Scraping: {url}")

                    response = self.session.get(url, timeout=CONFIG['request_timeout'])
                    response.raise_for_status()

                    page_evals = self._extract_evaluations_from_html(response.text)

                    if not page_evals:
                        consecutive_empty += 1
                    else:
                        evaluations.extend(page_evals)
                        consecutive_empty = 0

                    page += 1
                    time.sleep(2)  # Rate limiting

                except Exception as e:
                    logger.warning(f"Error scraping {url}: {e}")
                    consecutive_empty += 1
                    break

        return evaluations

    def _scrape_with_browser(self) -> List[Dict]:
        """Scrape evaluation list using Selenium WebDriver."""
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available for browser-based scraping")
            return []

        evaluations = []

        try:
            logger.info("Starting browser-based scraping...")
            driver = webdriver.Chrome()  # Or webdriver.Firefox()

            urls = [
                'https://www.giz.de/en/about-us/results-evaluation/project-evaluations',
                'https://www.giz.de/en/about-us/results-evaluation/overarching-evaluations'
            ]

            for url in urls:
                try:
                    driver.get(url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
                    )

                    # Extract PDF links from rendered page
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute('href')
                        if href and href.endswith('.pdf'):
                            text = link.text or link.get_attribute('title') or 'Unknown'
                            evaluations.append({
                                'url': href,
                                'title': text,
                                'filename': href.split('/')[-1],
                                'year': self._extract_year_from_string(text),
                                'publication_date': None
                            })

                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Error scraping {url} with browser: {e}")

            driver.quit()
            logger.info(f"Browser scraping found {len(evaluations)} documents")

        except Exception as e:
            logger.error(f"Browser scraping failed: {e}")

        return evaluations

    def _extract_evaluations_from_html(self, html: str) -> List[Dict]:
        """Extract evaluation metadata from HTML."""
        evaluations = []

        pdf_pattern1 = r'href=["\']([^"\']*\.pdf)["\']'
        pdf_pattern2 = r'href=["\']([^"\']*(?:fileadmin|download|evaluation)[^"\']*\.pdf[^"\']*)["\']'

        try:
            pdf_links = re.findall(pdf_pattern1, html, re.IGNORECASE)
            if not pdf_links:
                pdf_links = re.findall(pdf_pattern2, html, re.IGNORECASE)

            for link in pdf_links:
                evaluations.append({
                    'url': urljoin(CONFIG['base_url'], link),
                    'filename': os.path.basename(link),
                    'title': '',
                    'year': None,
                    'publication_date': None
                })

            logger.debug(f"Extracted {len(evaluations)} evaluation links from HTML")
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")

        return evaluations

    def _extract_year_from_string(self, text: str) -> Optional[int]:
        """Extract year from text."""
        match = re.search(r'\b(20\d{2})\b', text)
        if match:
            try:
                year = int(match.group(1))
                if CONFIG['start_year'] <= year <= CONFIG['end_year']:
                    return year
            except ValueError:
                pass
        return None

    def download_pdf(self, url: str, year: int, doc_id: str) -> Optional[Path]:
        """Download a PDF document."""
        try:
            logger.info(f"Downloading: {url}")

            response = self.session.get(url, timeout=CONFIG['request_timeout'], stream=True)
            response.raise_for_status()

            filename = f"giz_cpe_{year}_{doc_id}.pdf"
            filepath = self.output_dir / 'cpe' / str(year) / filename

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Downloaded to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None

    def validate_pdf(self, filepath: Path) -> Dict:
        """Validate PDF quality."""
        validation = {
            'valid': False,
            'file_size': 0,
            'pages': 0,
            'is_scanned': False,
            'has_text': False
        }

        try:
            validation['file_size'] = filepath.stat().st_size
            if validation['file_size'] > 50000:  # At least 50KB
                validation['valid'] = True

            logger.info(f"PDF validation - {filepath.name}: {validation}")

        except Exception as e:
            logger.error(f"Validation error for {filepath}: {e}")

        return validation

    def extract_metadata(self, doc: Dict, filepath: Optional[Path] = None) -> Dict:
        """Extract and structure metadata for a document."""
        year = doc.get('year') or self._extract_year_from_string(
            doc.get('filename', '') + ' ' + doc.get('url', '')
        )

        doc_count = len(self.document_registry) + 1
        doc_id = f"GIZ-CPE-{year}-{doc_count:03d}"

        metadata = {
            'doc_id': doc_id,
            'project_title': doc.get('title', 'Unknown'),
            'commissioning_unit': doc.get('commissioning_unit', 'GIZ'),
            'partner_country': doc.get('partner_country', 'Unknown'),
            'thematic_cluster': doc.get('sector') or self._infer_sector(doc.get('title', '')),
            'sdg_tags': self._extract_sdg_tags(doc.get('title', '')),
            'pages': doc.get('pages', 0),
            'publication_date': doc.get('publication_date') or f"{year}-01-01",
            'url': doc.get('url', ''),
            'source': 'GIZ Evaluations Database',
            'license': 'GIZ Attribution - Non-commercial Reuse',
            'file_path': str(filepath) if filepath else None,
            'file_hash': self._compute_file_hash(filepath) if filepath else None,
            'extraction_date': datetime.now().isoformat(),
            'validation': {}
        }

        if filepath:
            metadata['validation'] = self.validate_pdf(filepath)

        return metadata

    def _infer_sector(self, title: str) -> str:
        """Infer sector from document title."""
        title_lower = title.lower()
        for sector in CONFIG['giz_sectors']:
            if sector in title_lower:
                return sector
        return 'governance'

    def _extract_sdg_tags(self, title: str) -> List[str]:
        """Extract SDG tags from title."""
        sdg_keywords = {
            '3': ['health', 'healthcare', 'disease', 'nutrition', 'maternal'],
            '4': ['education', 'learning', 'literacy', 'training', 'vocational'],
            '6': ['water', 'sanitation', 'hygiene', 'wash'],
            '13': ['climate', 'renewable', 'mitigation', 'adaptation', 'emissions'],
            '16': ['governance', 'peace', 'justice', 'rule of law', 'institutions'],
        }

        found_sdgs = []
        title_lower = title.lower()

        for sdg, keywords in sdg_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                found_sdgs.append(f"SDG-{sdg}")

        return found_sdgs if found_sdgs else ['SDG-16']

    def _compute_file_hash(self, filepath: Path) -> Optional[str]:
        """Compute SHA256 hash of file."""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Hash computation failed: {e}")
            return None

    def save_metadata(self, metadata: Dict) -> Path:
        """Save metadata to JSON file."""
        try:
            metadata_file = self.metadata_dir / f"{metadata['doc_id']}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Metadata saved: {metadata_file}")
            return metadata_file
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            return None

    def save_registry(self):
        """Save the complete document registry."""
        try:
            # JSON format
            registry_json = self.output_dir / 'giz_cpe_registry.json'
            with open(registry_json, 'w') as f:
                json.dump(self.document_registry, f, indent=2)
            logger.info(f"JSON Registry saved: {registry_json}")

            # CSV format
            registry_csv = self.output_dir / 'giz_registry.csv'
            if self.document_registry:
                with open(registry_csv, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self.document_registry[0].keys())
                    writer.writeheader()
                    writer.writerows(self.document_registry)
                logger.info(f"CSV Registry saved: {registry_csv}")

        except Exception as e:
            logger.error(f"Failed to save registry: {e}")

    def _generate_data_seeding_template(self):
        """Generate template for manual data seeding."""
        template = {
            "instructions": "Add GIZ evaluation documents here",
            "example": {
                "doc_id": "GIZ-CPE-2023-001",
                "project_title": "Example Project Evaluation",
                "commissioning_unit": "GIZ Division",
                "partner_country": "Kenya",
                "thematic_cluster": "governance",
                "sdg_tags": ["SDG-3", "SDG-16"],
                "publication_date": "2023-06-15",
                "languages": ["en", "de"],
                "pages": 45,
                "url": "https://example.com/document.pdf",
                "license": "GIZ Attribution - Non-commercial Reuse"
            }
        }

        template_file = self.output_dir / 'manual_seeding_template.json'
        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)
        logger.info(f"Data seeding template created: {template_file}")

    def _generate_report(self):
        """Generate acquisition report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "target_years": f"{CONFIG['start_year']}-{CONFIG['end_year']}",
            "statistics": self.acquisition_stats,
            "documents_acquired": len(self.document_registry),
            "output_directory": str(self.output_dir),
            "next_steps": [
                "1. Contact GIZ for direct API access: evaluations@giz.de",
                "2. Implement browser-based scraping using Selenium",
                "3. Use manual_seeding_template.json to add documents",
                "4. Run quality checks with generate_qc_report.py"
            ]
        }

        report_file = self.output_dir / 'logs' / 'acquisition_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Acquisition report saved: {report_file}")


def main():
    """Entry point."""
    try:
        # Standard acquisition (no browser)
        acquisitor = GIZCPEAcquisitor(use_browser=False)
        acquisitor.acquire()

        # Optional: Uncomment to use browser-based scraping
        # acquisitor = GIZCPEAcquisitor(use_browser=True)
        # acquisitor.acquire()

    except KeyboardInterrupt:
        logger.info("Acquisition interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
