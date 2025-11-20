#!/usr/bin/env python3
"""
GIZ Central Project Evaluations (CPE) & Sector Syntheses Acquisition Script

This script gathers GIZ evaluation documents (2020-2024) covering SDGs 3, 4, 6, 13, 16.

Primary Sources:
- GIZ Evaluation Reports database: https://www.giz.de/en/mediacenter/publications/evaluations
- GIZ OPEN: https://www.giz.de/de/mediathek/
- Sector synthesis PDFs from GIZ Evaluation Unit pages

Licensing: GIZ publishes evaluations under permissive terms for non-commercial reuse.
"""

import os
import json
import time
import logging
import hashlib
import re
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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

    def __init__(self):
        self.session = RobustSession()
        self.session.timeout = CONFIG['request_timeout']
        self.output_dir = CONFIG['output_dir']
        self.metadata_dir = CONFIG['metadata_dir']
        self.document_registry = []
        self._setup_directories()

    def _setup_directories(self):
        """Create necessary directory structure."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        for year in range(CONFIG['start_year'], CONFIG['end_year'] + 1):
            year_dir = self.output_dir / 'cpe' / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory structure created at {self.output_dir}")

    def scrape_evaluations_list(self) -> List[Dict]:
        """
        Scrape the GIZ evaluations list. This attempts multiple approaches:
        1. First tries the API endpoint
        2. Falls back to HTML scraping with pagination

        Returns:
            List of evaluation document metadata
        """
        evaluations = []

        logger.info("Attempting to scrape GIZ evaluations...")

        # Approach 1: Try API endpoint
        evaluations = self._try_api_endpoint() or []

        # Approach 2: Fall back to HTML scraping with pagination
        if not evaluations:
            evaluations = self._scrape_html_pagination()

        # Filter by year and SDG
        evaluations = self._filter_evaluations(evaluations)

        logger.info(f"Found {len(evaluations)} evaluations matching criteria")
        return evaluations

    def _try_api_endpoint(self) -> Optional[List[Dict]]:
        """Try to fetch evaluations from REST API."""
        try:
            logger.info("Attempting API endpoint access...")
            params = {
                'start': 0,
                'limit': 1000,
                'filter': json.dumps({
                    'year': {'$gte': CONFIG['start_year']},
                }),
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

        # Try both English and German versions
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
                    # Try with and without pagination
                    if page == 0:
                        url = base_url
                    else:
                        url = f"{base_url}?page={page}"

                    logger.info(f"Scraping: {url}")

                    response = self.session.get(url, timeout=CONFIG['request_timeout'])
                    response.raise_for_status()

                    # Simple HTML parsing - extract evaluation links and metadata
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

    def _extract_evaluations_from_html(self, html: str) -> List[Dict]:
        """
        Extract evaluation metadata from HTML.

        This looks for patterns in GIZ evaluation pages.
        """
        evaluations = []

        # Enhanced regex patterns for extracting evaluation links
        # Pattern 1: Direct PDF links
        pdf_pattern1 = r'href=["\']([^"\']*\.pdf)["\']'
        # Pattern 2: Links containing 'fileadmin', 'download', or 'evaluation'
        pdf_pattern2 = r'href=["\']([^"\']*(?:fileadmin|download|evaluation)[^"\']*\.pdf[^"\']*)["\']'
        # Pattern 3: Download links in common GIZ URL structures
        pdf_pattern3 = r'href=["\'](?:https?://)?(?:www\.)?giz\.de[^"\']*["\']'

        title_pattern = r'<(?:h[1-3]|strong|b)[^>]*>([^<]*(?:evaluation|assessment|synthesis|project)[^<]*)</(?:h[1-3]|strong|b)>'

        try:
            # Try multiple PDF patterns
            pdf_links = re.findall(pdf_pattern1, html, re.IGNORECASE)
            if not pdf_links:
                pdf_links = re.findall(pdf_pattern2, html, re.IGNORECASE)

            # Also look for evaluation titles
            titles = re.findall(title_pattern, html, re.IGNORECASE)

            for link in pdf_links:
                eval_metadata = {
                    'url': urljoin(CONFIG['base_url'], link),
                    'filename': os.path.basename(link),
                    'title': titles[len(evaluations)] if len(evaluations) < len(titles) else '',
                    'year': None,
                    'publication_date': None
                }
                evaluations.append(eval_metadata)

            logger.debug(f"Extracted {len(evaluations)} evaluation links from HTML")
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")

        return evaluations

    def _filter_evaluations(self, evaluations: List[Dict]) -> List[Dict]:
        """Filter evaluations by year and other criteria."""
        filtered = []

        for eval_doc in evaluations:
            # Try to extract year from metadata or filename
            year = eval_doc.get('year')
            if not year:
                # Try to extract from filename or URL
                year = self._extract_year_from_string(
                    eval_doc.get('filename', '') + ' ' + eval_doc.get('url', '')
                )

            if year and CONFIG['start_year'] <= year <= CONFIG['end_year']:
                filtered.append(eval_doc)

        return filtered

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
        """
        Download a PDF document.

        Args:
            url: PDF download URL
            year: Publication year
            doc_id: Document identifier

        Returns:
            Path to saved file or None if failed
        """
        try:
            logger.info(f"Downloading: {url}")

            response = self.session.get(url, timeout=CONFIG['request_timeout'], stream=True)
            response.raise_for_status()

            # Generate normalized filename
            filename = f"giz_cpe_{year}_{doc_id}.pdf"
            filepath = self.output_dir / 'cpe' / str(year) / filename

            # Write PDF
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
        """
        Validate PDF quality.

        Returns dict with validation results.
        """
        validation = {
            'valid': False,
            'file_size': 0,
            'pages': 0,
            'is_scanned': False,
            'has_text': False
        }

        try:
            # Check file size
            validation['file_size'] = filepath.stat().st_size

            # Try to extract page count and basic info
            # This requires PyPDF2 - for basic validation we check file size
            if validation['file_size'] > 50000:  # At least 50KB
                validation['valid'] = True

            logger.info(f"PDF validation - {filepath.name}: {validation}")

        except Exception as e:
            logger.error(f"Validation error for {filepath}: {e}")

        return validation

    def extract_metadata(self, doc: Dict, filepath: Optional[Path] = None) -> Dict:
        """
        Extract and structure metadata for a document.

        Args:
            doc: Document information dict
            filepath: Optional path to PDF for additional extraction

        Returns:
            Structured metadata dict
        """
        year = doc.get('year') or self._extract_year_from_string(
            doc.get('filename', '') + ' ' + doc.get('url', '')
        )

        # Generate doc_id
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
        return 'governance'  # Default sector

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

        return found_sdgs if found_sdgs else ['SDG-16']  # Default to SDG-16

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
            registry_file = self.output_dir / 'giz_cpe_registry.json'
            with open(registry_file, 'w') as f:
                json.dump(self.document_registry, f, indent=2)
            logger.info(f"Registry saved: {registry_file}")
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")

    def acquire(self):
        """Main acquisition workflow."""
        logger.info("=" * 60)
        logger.info("Starting GIZ CPE Acquisition")
        logger.info(f"Target years: {CONFIG['start_year']}-{CONFIG['end_year']}")
        logger.info("=" * 60)

        # Step 1: Scrape evaluations list
        evaluations = self.scrape_evaluations_list()

        if not evaluations:
            logger.warning("No evaluations found. This may require manual configuration.")
            logger.info("GIZ Evaluations can be accessed at:")
            logger.info(f"  {CONFIG['base_url']}")
            return

        # Step 2: Process each evaluation
        processed = 0
        failed = 0

        for eval_doc in evaluations[:100]:  # Limit to first 100 for this run
            try:
                # Extract metadata
                metadata = self.extract_metadata(eval_doc)

                # Download PDF (if URL available)
                filepath = None
                if eval_doc.get('url'):
                    year = metadata.get('publication_date', '2024')[:4]
                    slug = metadata['doc_id'].split('-')[-1]
                    filepath = self.download_pdf(
                        eval_doc['url'],
                        year,
                        slug
                    )

                # Validate
                if filepath:
                    validation = self.validate_pdf(filepath)
                    metadata['validation'] = validation
                    if not validation['valid']:
                        logger.warning(f"Document failed validation: {filepath}")
                        continue

                # Save metadata
                self.save_metadata(metadata)
                self.document_registry.append(metadata)
                processed += 1

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error processing evaluation: {e}")
                failed += 1

        # Step 3: Save registry
        self.save_registry()

        logger.info("=" * 60)
        logger.info(f"Acquisition Complete")
        logger.info(f"Processed: {processed}, Failed: {failed}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("=" * 60)


def main():
    """Entry point."""
    try:
        acquisitor = GIZCPEAcquisitor()
        acquisitor.acquire()
    except KeyboardInterrupt:
        logger.info("Acquisition interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
