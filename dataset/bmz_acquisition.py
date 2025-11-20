#!/usr/bin/env python3
"""
BMZ Evaluation Reports & Country Concepts Acquisition Script
Captures ~1,200 BMZ-issued evaluation reports, strategy papers, and country concepts (2015-2025)
relevant to SDGs 1, 5, 7, 13, 16.

Usage:
    python bmz_acquisition.py [--limit N] [--dry-run] [--mock-data]
    python bmz_acquisition.py --mock-data --verbose  # Test with mock data

Real environment requirements:
- requests, beautifulsoup4 for web crawling
- Optional: pdf2image, pytesseract for OCR processing
- Valid network access to BMZ website (https://www.bmz.de)
"""

import os
import sys
import json
import re
import time
import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from urllib.parse import urljoin, urlparse
import hashlib

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print("Error: Required packages not installed. Install with:")
    print("pip install requests beautifulsoup4")
    sys.exit(1)

# Optional packages for PDF processing
try:
    import pdf2image
    HAS_PDF_PROCESSING = True
except ImportError:
    HAS_PDF_PROCESSING = False
    logger_msg = "pdf2image not available; OCR features disabled"

# Configuration
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "data" / "raw" / "bmz"
DOCUMENTS_DIR = DATA_DIR / "documents"
METADATA_DIR = DATA_DIR / "metadata"
LOGS_DIR = DATA_DIR / "logs"
METADATA_FILE = METADATA_DIR / "bmz_metadata.jsonl"
SUMMARY_CSV = METADATA_DIR / "bmz_summary.csv"
STATUS_MD = METADATA_DIR / "README_bmz_status.md"

# Create directories
for directory in [DOCUMENTS_DIR, METADATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configure logging to both file and console
log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOGS_DIR / f"bmz_crawl_{log_timestamp}.log"

# File handler
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# BMZ URLs
BMZ_EVALUATION_PORTAL = "https://www.bmz.de/de/ministerium/evaluierung/berichte"
BMZ_COUNTRIES = "https://www.bmz.de/de/laender"
BMZ_SDG = "https://www.bmz.de/de/presse/infothek/sdg"

# SDG Mapping
SDG_KEYWORDS = {
    1: ["armut", "poverty", "ärmste", "einkommensarm"],
    5: ["geschlechter", "gender", "frauen", "women", "gleichstellung"],
    7: ["energie", "energy", "erneuerbar", "renewable"],
    13: ["klima", "climate", "kohlenstoff", "carbon", "erwärmung"],
    16: ["governance", "friedensförderung", "frieden", "peace", "rechtsstaatlichkeit", "justice"],
}

# Request headers to mimic browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
}

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF = [2, 4, 8]  # seconds


@dataclass
class BMZDocument:
    """Represents a BMZ document with metadata."""
    doc_id: str
    title: str
    url: str
    publication_year: int
    document_type: str  # 'evaluation', 'strategy', 'policy_brief'
    focus_country_region: Optional[str] = None
    sdg_tags: List[int] = field(default_factory=list)
    language: str = "de"
    issuing_unit: Optional[str] = None
    local_path: Optional[str] = None
    file_hash: Optional[str] = None
    page_count: Optional[int] = None
    retrieved_date: str = None
    pii_flag: bool = False
    pii_details: Optional[str] = None

    def __post_init__(self):
        if not self.sdg_tags:
            self.sdg_tags = []
        if self.retrieved_date is None:
            self.retrieved_date = datetime.now().isoformat()


class BMZCrawler:
    """Crawls BMZ portal for evaluation reports and country concepts."""

    def __init__(self, dry_run: bool = False, limit: int = None, use_mock_data: bool = False):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.dry_run = dry_run
        self.limit = limit
        self.use_mock_data = use_mock_data
        self.documents: List[BMZDocument] = []
        self.doc_counter = 0
        self.failed_urls: List[Tuple[str, str]] = []
        self.processed_urls: Set[str] = set()
        self.file_hashes: Set[str] = set()  # For deduplication

    def generate_mock_data(self) -> List[BMZDocument]:
        """Generate mock BMZ documents for testing."""
        mock_docs = [
            BMZDocument(
                doc_id="BMZ-2023-0001",
                title="Evaluation of Climate Adaptation in East Africa",
                url="https://www.bmz.de/mock/evaluation_climate_ea_2023.pdf",
                publication_year=2023,
                document_type="evaluation",
                focus_country_region="East Africa",
                sdg_tags=[13, 7],
                language="en",
                issuing_unit="BMZ Division for Climate and Energy"
            ),
            BMZDocument(
                doc_id="BMZ-2023-0002",
                title="Länderstrategie Kenya 2023-2028",
                url="https://www.bmz.de/mock/strategy_kenya_2023.pdf",
                publication_year=2023,
                document_type="strategy",
                focus_country_region="Kenya",
                sdg_tags=[1, 5, 7, 13, 16],
                language="de",
                issuing_unit="BMZ Country Programs"
            ),
            BMZDocument(
                doc_id="BMZ-2023-0003",
                title="Policy Brief: Geschlechtergerechte Energiewende",
                url="https://www.bmz.de/mock/policy_gender_energy_2023.pdf",
                publication_year=2023,
                document_type="policy_brief",
                sdg_tags=[5, 7],
                language="de",
                issuing_unit="BMZ SDG Policy Office"
            ),
            BMZDocument(
                doc_id="BMZ-2022-0001",
                title="Impact Evaluation: Governance Programs in Sahel",
                url="https://www.bmz.de/mock/eval_governance_sahel_2022.pdf",
                publication_year=2022,
                document_type="evaluation",
                focus_country_region="Sahel",
                sdg_tags=[16, 5],
                language="en",
                issuing_unit="BMZ Governance Division"
            ),
            BMZDocument(
                doc_id="BMZ-2022-0002",
                title="Midterm Review: Urban Development Program Ghana",
                url="https://www.bmz.de/mock/review_urban_ghana_2022.pdf",
                publication_year=2022,
                document_type="evaluation",
                focus_country_region="Ghana",
                sdg_tags=[1, 7, 16],
                language="en",
                issuing_unit="BMZ Infrastructure Division"
            ),
            BMZDocument(
                doc_id="BMZ-2022-0003",
                title="Länderstrategie Äthiopien 2022-2027",
                url="https://www.bmz.de/mock/strategy_ethiopia_2022.pdf",
                publication_year=2022,
                document_type="strategy",
                focus_country_region="Ethiopia",
                sdg_tags=[1, 5, 7, 13, 16],
                language="de",
                issuing_unit="BMZ Country Programs"
            ),
            BMZDocument(
                doc_id="BMZ-2021-0001",
                title="Synthesis Report: Renewable Energy in Sub-Saharan Africa",
                url="https://www.bmz.de/mock/synthesis_renewables_ssa_2021.pdf",
                publication_year=2021,
                document_type="evaluation",
                sdg_tags=[7, 13],
                language="en",
                issuing_unit="BMZ Energy Division"
            ),
            BMZDocument(
                doc_id="BMZ-2021-0002",
                title="Länderstrategie Mosambik 2021-2025",
                url="https://www.bmz.de/mock/strategy_mozambique_2021.pdf",
                publication_year=2021,
                document_type="strategy",
                focus_country_region="Mozambique",
                sdg_tags=[1, 5, 7, 13, 16],
                language="de",
                issuing_unit="BMZ Country Programs"
            ),
        ]

        # Truncate to limit if specified
        if self.limit:
            mock_docs = mock_docs[:self.limit]

        self.documents = mock_docs
        return mock_docs

    def fetch_url(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch URL with retry logic and 429 rate limit handling."""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=timeout)

                # Handle rate limiting (429)
                if response.status_code == 429:
                    wait_time = RETRY_BACKOFF[attempt] if attempt < len(RETRY_BACKOFF) else 16
                    logger.warning(f"Rate limited (429). Waiting {wait_time}s before retry {attempt + 1}/{MAX_RETRIES}")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_BACKOFF[attempt]
                    logger.warning(f"Retry {attempt + 1}/{MAX_RETRIES} for {url} after {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {MAX_RETRIES} attempts: {e}")
                    self.failed_urls.append((url, str(e)))
                    # Persist HTML snapshot for failed page if available
                    self._save_failed_snapshot(url, str(e))
                    return None

        return None

    def _save_failed_snapshot(self, url: str, error: str):
        """Save snapshot of failed URL for debugging."""
        try:
            snapshot_dir = LOGS_DIR / "failed_snapshots"
            snapshot_dir.mkdir(parents=True, exist_ok=True)

            # Create filename from URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            snapshot_file = snapshot_dir / f"failed_{url_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            with open(snapshot_file, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write(f"Error: {error}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")

            logger.debug(f"Saved failed snapshot to {snapshot_file}")
        except Exception as e:
            logger.warning(f"Could not save failed snapshot: {e}")

    def extract_pdf_links(self, html: str, base_url: str) -> List[str]:
        """Extract PDF/DOCX links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        # Look for resource blob links and PDF links
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Filter for PDFs and DOCXs, including /resource/blob/ patterns
            if any(pattern in href for pattern in ['/resource/blob/', '.pdf', '.docx']):
                full_url = urljoin(base_url, href)
                if full_url not in links:
                    links.append(full_url)

        return links

    def extract_year_from_html(self, html: str) -> Optional[int]:
        """Extract year from HTML content."""
        year_pattern = r'(20[0-2]\d)'
        matches = re.findall(year_pattern, html)
        if matches:
            # Return the most common year (likely publication year)
            return int(max(set(matches), key=matches.count))
        return None

    def tag_sdg_keywords(self, text: str) -> List[int]:
        """Tag SDGs based on keyword matching."""
        text_lower = text.lower()
        sdgs = []

        for sdg_num, keywords in SDG_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if sdg_num not in sdgs:
                        sdgs.append(sdg_num)
                    break

        return sorted(sdgs)

    def detect_pii(self, text: str, title: str = "") -> Tuple[bool, Optional[str]]:
        """Detect PII (names, emails) in text."""
        combined_text = f"{text} {title}".lower()
        pii_matches = []

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, combined_text)
        if emails:
            pii_matches.append(f"emails({len(emails)})")

        # Common name patterns (simplified)
        name_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
            r'\b(Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.) [A-Z][a-z]+\b',  # Title + Last
        ]

        for pattern in name_patterns:
            names = re.findall(pattern, text)
            if names:
                pii_matches.append(f"names({len(names)})")
                break

        if pii_matches:
            return True, ", ".join(pii_matches)
        return False, None

    def slugify_filename(self, title: str) -> str:
        """Convert title to filesystem-safe slug."""
        slug = title.lower()
        slug = re.sub(r'[äöüß]', lambda m: {
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'
        }[m.group()], slug)
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug[:100]

    def crawl_evaluation_portal(self) -> List[BMZDocument]:
        """Crawl the BMZ evaluation portal with pagination support."""
        logger.info(f"Crawling BMZ Evaluation Portal: {BMZ_EVALUATION_PORTAL}")

        page = 1
        max_pages = 50  # Safety limit
        found_in_page = True

        while found_in_page and page <= max_pages:
            if self.limit and self.doc_counter >= self.limit:
                break

            # Try paginated URL
            paginated_url = f"{BMZ_EVALUATION_PORTAL}?page={page}"
            logger.info(f"Fetching evaluation portal page {page}")

            html = self.fetch_url(paginated_url)
            if not html:
                if page == 1:
                    # Try without pagination
                    html = self.fetch_url(BMZ_EVALUATION_PORTAL)
                    if not html:
                        return []
                else:
                    break

            # Extract links from portal
            pdf_links = self.extract_pdf_links(html, BMZ_EVALUATION_PORTAL)
            found_in_page = len(pdf_links) > 0

            if not found_in_page and page > 1:
                logger.info(f"No more documents found after page {page - 1}")
                break

            year = self.extract_year_from_html(html)
            sdgs = self.tag_sdg_keywords(html)

            if page == 1:
                logger.info(f"Found {len(pdf_links)} PDF links in evaluation portal page 1")

            # Process each PDF link
            for link in pdf_links:
                if self.limit and self.doc_counter >= self.limit:
                    break

                if link in self.processed_urls:
                    continue

                self.processed_urls.add(link)
                self.doc_counter += 1

                # Extract title from URL or link text
                parsed_url = urlparse(link)
                title = os.path.basename(parsed_url.path).replace('.pdf', '').replace('.docx', '')
                title = title.replace('-', ' ').replace('_', ' ')

                # Detect PII in title
                pii_flag, pii_details = self.detect_pii("", title)

                doc = BMZDocument(
                    doc_id=f"BMZ-{year or 2024}-{self.doc_counter:04d}",
                    title=title,
                    url=link,
                    publication_year=year or 2024,
                    document_type="evaluation",
                    sdg_tags=sdgs,
                    language="de",
                    issuing_unit="BMZ",
                    pii_flag=pii_flag,
                    pii_details=pii_details
                )

                self.documents.append(doc)
                logger.info(f"[{self.doc_counter}] Found: {doc.title}")

            page += 1

        return self.documents

    def crawl_country_strategies(self) -> List[BMZDocument]:
        """Crawl country strategy pages with pagination support."""
        logger.info(f"Crawling BMZ Country Strategies: {BMZ_COUNTRIES}")

        page = 1
        max_pages = 50  # Safety limit
        found_in_page = True

        while found_in_page and page <= max_pages:
            if self.limit and self.doc_counter >= self.limit:
                break

            # Try paginated URL
            if page == 1:
                paginated_url = BMZ_COUNTRIES
            else:
                paginated_url = f"{BMZ_COUNTRIES}?page={page}"

            logger.info(f"Fetching country strategies page {page}")
            html = self.fetch_url(paginated_url)
            if not html:
                if page > 1:
                    break
                return []

            soup = BeautifulSoup(html, 'html.parser')

            # Find all country links
            country_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/de/laender/' in href and not href.endswith('/laender'):
                    country_links.append(urljoin(BMZ_COUNTRIES, href))

            found_in_page = len(country_links) > 0

            if page == 1:
                logger.info(f"Found {len(country_links)} country pages on page 1")

            # Process each country page
            for country_url in country_links:
                if self.limit and self.doc_counter >= self.limit:
                    break

                if country_url in self.processed_urls:
                    continue

                self.processed_urls.add(country_url)

                country_html = self.fetch_url(country_url)
                if not country_html:
                    continue

                # Extract country name from URL
                country_slug = country_url.split('/laender/')[-1].rstrip('/')

                # Look for strategy PDF
                pdf_links = self.extract_pdf_links(country_html, country_url)

                for pdf_link in pdf_links:
                    if self.limit and self.doc_counter >= self.limit:
                        break

                    if pdf_link in self.processed_urls:
                        continue

                    if 'strateg' in pdf_link.lower() or 'concept' in pdf_link.lower():
                        self.processed_urls.add(pdf_link)
                        self.doc_counter += 1

                        # Detect PII
                        pii_flag, pii_details = self.detect_pii(country_html, country_slug)

                        doc = BMZDocument(
                            doc_id=f"BMZ-{datetime.now().year}-{self.doc_counter:04d}",
                            title=f"Country Strategy: {country_slug}",
                            url=pdf_link,
                            publication_year=self.extract_year_from_html(country_html) or 2024,
                            document_type="strategy",
                            focus_country_region=country_slug,
                            sdg_tags=[1, 5, 7, 13, 16],  # Default SDGs for strategies
                            language="de",
                            issuing_unit="BMZ",
                            pii_flag=pii_flag,
                            pii_details=pii_details
                        )

                        self.documents.append(doc)
                        logger.info(f"[{self.doc_counter}] Found: {doc.title}")

            page += 1

        return self.documents

    def crawl_sdg_papers(self) -> List[BMZDocument]:
        """Crawl SDG-specific policy papers with pagination support."""
        logger.info(f"Crawling BMZ SDG Papers: {BMZ_SDG}")

        page = 1
        max_pages = 50  # Safety limit
        found_in_page = True

        while found_in_page and page <= max_pages:
            if self.limit and self.doc_counter >= self.limit:
                break

            # Try paginated URL
            if page == 1:
                paginated_url = BMZ_SDG
            else:
                paginated_url = f"{BMZ_SDG}?page={page}"

            logger.info(f"Fetching SDG papers page {page}")
            html = self.fetch_url(paginated_url)
            if not html:
                if page > 1:
                    break
                return []

            # Extract PDF links
            pdf_links = self.extract_pdf_links(html, BMZ_SDG)
            found_in_page = len(pdf_links) > 0

            if page == 1:
                logger.info(f"Found {len(pdf_links)} SDG paper links on page 1")

            for link in pdf_links:
                if self.limit and self.doc_counter >= self.limit:
                    break

                if link in self.processed_urls:
                    continue

                self.processed_urls.add(link)
                self.doc_counter += 1

                parsed_url = urlparse(link)
                title = os.path.basename(parsed_url.path).replace('.pdf', '').replace('.docx', '')
                title = title.replace('-', ' ').replace('_', ' ')

                # Detect PII
                pii_flag, pii_details = self.detect_pii(html, title)

                doc = BMZDocument(
                    doc_id=f"BMZ-{datetime.now().year}-{self.doc_counter:04d}",
                    title=title,
                    url=link,
                    publication_year=self.extract_year_from_html(html) or 2024,
                    document_type="policy_brief",
                    sdg_tags=self.tag_sdg_keywords(title),
                    language="de",
                    issuing_unit="BMZ",
                    pii_flag=pii_flag,
                    pii_details=pii_details
                )

                self.documents.append(doc)
                logger.info(f"[{self.doc_counter}] Found: {doc.title}")

            page += 1

        return self.documents

    def save_metadata(self):
        """Save document metadata to JSONL and CSV files."""
        logger.info(f"Saving metadata to {METADATA_FILE}")

        # Save JSONL
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            for doc in self.documents:
                json.dump(asdict(doc), f, ensure_ascii=False)
                f.write('\n')

        logger.info(f"Saved {len(self.documents)} documents to JSONL")

        # Save CSV summary
        self.save_summary_csv()

    def save_summary_csv(self):
        """Save document summary to CSV file."""
        logger.info(f"Saving summary CSV to {SUMMARY_CSV}")

        try:
            with open(SUMMARY_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'doc_id', 'title', 'url', 'publication_year', 'document_type',
                    'focus_country_region', 'sdg_tags', 'language', 'issuing_unit',
                    'pii_flag', 'pii_details', 'local_path', 'file_hash'
                ])

                for doc in self.documents:
                    writer.writerow([
                        doc.doc_id,
                        doc.title,
                        doc.url,
                        doc.publication_year,
                        doc.document_type,
                        doc.focus_country_region or '',
                        ';'.join(map(str, doc.sdg_tags)) if doc.sdg_tags else '',
                        doc.language,
                        doc.issuing_unit or '',
                        'YES' if doc.pii_flag else 'NO',
                        doc.pii_details or '',
                        doc.local_path or '',
                        doc.file_hash or ''
                    ])

            logger.info(f"Saved summary CSV with {len(self.documents)} records")
        except Exception as e:
            logger.error(f"Failed to save summary CSV: {e}")

    def save_status_report(self):
        """Generate and save status report."""
        logger.info(f"Generating status report: {STATUS_MD}")

        # Compute statistics
        total_docs = len(self.documents)
        by_type = {}
        by_year = {}
        by_country = {}
        sdg_coverage = {}
        pii_count = 0
        year_populated = 0
        country_populated = 0
        sdg_populated = 0

        for doc in self.documents:
            # Type breakdown
            by_type[doc.document_type] = by_type.get(doc.document_type, 0) + 1

            # Year breakdown
            if doc.publication_year:
                by_year[doc.publication_year] = by_year.get(doc.publication_year, 0) + 1
                year_populated += 1

            # Country breakdown
            if doc.focus_country_region:
                by_country[doc.focus_country_region] = by_country.get(doc.focus_country_region, 0) + 1
                country_populated += 1

            # SDG coverage
            if doc.sdg_tags:
                sdg_populated += 1
                for sdg in doc.sdg_tags:
                    sdg_coverage[sdg] = sdg_coverage.get(sdg, 0) + 1

            # PII flag
            if doc.pii_flag:
                pii_count += 1

        # Generate markdown report
        report = f"""# BMZ Acquisition Status Report
Generated: {datetime.now().isoformat()}

## Summary Statistics
- **Total Documents**: {total_docs}
- **Failed URLs**: {len(self.failed_urls)}
- **Documents with PII Flags**: {pii_count}

## Data Quality Metrics
"""

        if total_docs > 0:
            report += f"""- **Publication Year Populated**: {year_populated}/{total_docs} ({100*year_populated/total_docs:.1f}%)
- **Country/Region Populated**: {country_populated}/{total_docs} ({100*country_populated/total_docs:.1f}%)
- **SDG Tags Populated**: {sdg_populated}/{total_docs} ({100*sdg_populated/total_docs:.1f}%)
"""
        else:
            report += "- No documents found in this crawl\n"

        report += """
## Document Types Breakdown
"""

        for doc_type in sorted(by_type.keys()):
            count = by_type[doc_type]
            report += f"- {doc_type}: {count}\n"

        report += "\n## Year Distribution\n"
        for year in sorted(by_year.keys()):
            count = by_year[year]
            report += f"- {year}: {count}\n"

        report += "\n## SDG Coverage\n"
        for sdg in sorted(sdg_coverage.keys()):
            count = sdg_coverage[sdg]
            report += f"- SDG {sdg}: {count} documents\n"

        report += "\n## Top Countries/Regions\n"
        top_countries = sorted(by_country.items(), key=lambda x: x[1], reverse=True)[:10]
        for country, count in top_countries:
            report += f"- {country}: {count}\n"

        if self.failed_urls:
            report += "\n## Failed URLs (Sample)\n"
            for url, error in self.failed_urls[:10]:
                report += f"- {url}: {error}\n"

        report += "\n## Storage Information\n"
        report += f"- Metadata File: {METADATA_FILE}\n"
        report += f"- Summary CSV: {SUMMARY_CSV}\n"
        report += f"- Log File: {log_file}\n"
        report += f"- Documents Directory: {DOCUMENTS_DIR}\n"

        # Write report
        try:
            with open(STATUS_MD, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Status report saved to {STATUS_MD}")
        except Exception as e:
            logger.error(f"Failed to save status report: {e}")

    def run(self):
        """Run the complete crawling pipeline."""
        logger.info("="*60)
        logger.info("BMZ ACQUISITION PIPELINE STARTING")
        logger.info("="*60)
        logger.info(f"Mode: {'MOCK DATA' if self.use_mock_data else 'LIVE CRAWLING'}")
        logger.info(f"Dry run: {self.dry_run}")
        if self.limit:
            logger.info(f"Document limit: {self.limit}")
        logger.info(f"Log file: {log_file}")

        try:
            # Create data directories
            for directory in [DOCUMENTS_DIR, METADATA_DIR, LOGS_DIR]:
                directory.mkdir(parents=True, exist_ok=True)

            if self.use_mock_data:
                # Use mock data for testing
                self.generate_mock_data()
                logger.info(f"Generated {len(self.documents)} mock documents")
            else:
                # Run crawling stages
                logger.info("\n--- Starting Evaluation Portal Crawl ---")
                self.crawl_evaluation_portal()
                logger.info(f"Evaluation Portal: {len(self.documents)} documents")

                logger.info("\n--- Starting Country Strategies Crawl ---")
                self.crawl_country_strategies()
                logger.info(f"After Country Strategies: {len(self.documents)} documents")

                logger.info("\n--- Starting SDG Papers Crawl ---")
                self.crawl_sdg_papers()
                logger.info(f"After SDG Papers: {len(self.documents)} documents")

            # Save metadata and reports
            if not self.dry_run:
                logger.info("\n--- Saving Metadata and Reports ---")
                self.save_metadata()
                self.save_status_report()

            # Print summary
            self.print_summary()

            logger.info("="*60)
            logger.info("BMZ ACQUISITION PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*60)

        except Exception as e:
            logger.error(f"Crawling failed: {e}", exc_info=True)
            logger.error("="*60)
            sys.exit(1)

    def print_summary(self):
        """Print crawling summary."""
        logger.info("\n" + "="*60)
        logger.info("BMZ ACQUISITION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total documents found: {len(self.documents)}")
        logger.info(f"Failed URLs: {len(self.failed_urls)}")

        # PII detection summary
        pii_count = sum(1 for doc in self.documents if doc.pii_flag)
        logger.info(f"Documents flagged for PII: {pii_count}")

        # Document type breakdown
        types = {}
        for doc in self.documents:
            types[doc.document_type] = types.get(doc.document_type, 0) + 1

        logger.info("\nDocument types:")
        for doc_type, count in sorted(types.items()):
            logger.info(f"  - {doc_type}: {count}")

        # SDG coverage
        sdg_counts = {}
        for doc in self.documents:
            for sdg in doc.sdg_tags:
                sdg_counts[sdg] = sdg_counts.get(sdg, 0) + 1

        logger.info("\nSDG coverage:")
        for sdg in sorted(sdg_counts.keys()):
            logger.info(f"  - SDG {sdg}: {sdg_counts[sdg]} docs")

        # Year distribution
        years = {}
        for doc in self.documents:
            years[doc.publication_year] = years.get(doc.publication_year, 0) + 1

        logger.info("\nYear distribution:")
        for year in sorted(years.keys()):
            logger.info(f"  - {year}: {years[year]} docs")

        # Data quality metrics
        total = len(self.documents)
        if total > 0:
            year_populated = sum(1 for doc in self.documents if doc.publication_year)
            country_populated = sum(1 for doc in self.documents if doc.focus_country_region)
            sdg_populated = sum(1 for doc in self.documents if doc.sdg_tags)

            logger.info(f"\nData Quality:")
            logger.info(f"  - Publication year populated: {year_populated}/{total} ({100*year_populated/total:.1f}%)")
            logger.info(f"  - Country/region populated: {country_populated}/{total} ({100*country_populated/total:.1f}%)")
            logger.info(f"  - SDG tags populated: {sdg_populated}/{total} ({100*sdg_populated/total:.1f}%)")

        if self.failed_urls:
            logger.info(f"\nFailed URLs (showing {min(5, len(self.failed_urls))}):")
            for url, error in self.failed_urls[:5]:
                logger.info(f"  - {url[:80]}...: {error}")
            if len(self.failed_urls) > 5:
                logger.info(f"  ... and {len(self.failed_urls) - 5} more")

        logger.info(f"\nOutput files:")
        logger.info(f"  - Metadata: {METADATA_FILE}")
        logger.info(f"  - Summary CSV: {SUMMARY_CSV}")
        logger.info(f"  - Status Report: {STATUS_MD}")
        logger.info(f"  - Log: {log_file}")

        logger.info("="*60 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='BMZ Evaluation Reports & Country Concepts Acquisition'
    )
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of documents to crawl')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without saving files')
    parser.add_argument('--mock-data', action='store_true',
                       help='Use mock data for testing (no live crawling)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    crawler = BMZCrawler(dry_run=args.dry_run, limit=args.limit, use_mock_data=args.mock_data)
    crawler.run()


if __name__ == '__main__':
    main()
