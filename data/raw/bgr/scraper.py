#!/usr/bin/env python3
"""
BGR (Bundesanstalt für Geowissenschaften und Rohstoffe) Document Scraper
Scrapes German Federal Institute for Geosciences and Natural Resources publications
"""

import os
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from io import BytesIO

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BGRScraper:
    """Scrapes BGR publications and metadata"""

    # BGR base URLs
    BGR_BASE = "https://www.bgr.bund.de"
    COMMODITY_NEWS_BASE = f"{BGR_BASE}/SharedDocs/GT_Produkte/Commodity_Top_News"
    GROUNDWATER_BASE = f"{BGR_BASE}/EN/Themen/Wasser"
    MINING_BASE = f"{BGR_BASE}/EN/Themen/Min_rohstoffe"

    # Document topic mappings
    TOPICS = {
        'groundwater': {
            'name': 'Groundwater',
            'sdg_tags': ['SDG 6', 'SDG 13'],
            'urls': [
                f"{BGR_BASE}/EN/Infothek/Publikationen/publikationen_node.html",
            ],
            'keywords': ['groundwater', 'wasser', 'water', 'aquifer', 'hydro']
        },
        'mining': {
            'name': 'Mining & Commodities',
            'sdg_tags': ['SDG 12', 'SDG 13'],
            'urls': [
                f"{BGR_BASE}/SharedDocs/GT_Produkte/Commodity_Top_News/CTN_genTab_DE.html",
            ],
            'keywords': ['mining', 'bergbau', 'commodity', 'rohstoff', 'mineral']
        },
        'climate': {
            'name': 'Climate Risk',
            'sdg_tags': ['SDG 13'],
            'urls': [
                f"{BGR_BASE}/EN/Themen/Wasser/Produkte",
            ],
            'keywords': ['climate', 'klimawandel', 'change', 'risk', 'CO2']
        },
    }

    def __init__(self, output_dir: str = "/home/user/evidence-ai/data/raw/bgr"):
        """Initialize scraper with output directory"""
        self.output_dir = Path(output_dir)
        self.documents_dir = self.output_dir / "documents"
        self.metadata_path = self.output_dir / "metadata" / "bgr_metadata.jsonl"
        self.logs_dir = self.output_dir / "logs"

        # Create directories if needed
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Evidence AI - Academic Research Bot) Document Collector'
        })

        # Track downloaded documents
        self.downloaded_docs: Dict = {}
        self.metadata_cache: List[Dict] = []
        self.load_metadata_cache()

    def load_metadata_cache(self):
        """Load existing metadata cache"""
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            self.metadata_cache.append(json.loads(line))
                logger.info(f"Loaded {len(self.metadata_cache)} existing metadata records")
            except Exception as e:
                logger.warning(f"Could not load metadata cache: {e}")

    def check_robots_txt(self):
        """Check if scraping is allowed"""
        try:
            response = self.session.get(f"{self.BGR_BASE}/robots.txt", timeout=5)
            logger.info(f"robots.txt status: {response.status_code}")
            if response.status_code == 200:
                logger.debug(f"robots.txt content:\n{response.text[:500]}")
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt: {e}")

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        try:
            time.sleep(2)  # Rate limiting - 2 seconds between requests
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_pdf_links(self, soup: BeautifulSoup, base_url: str,
                         topic: str) -> List[Dict]:
        """Extract PDF links from a page"""
        pdf_links = []

        # Find all links ending in .pdf
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Skip non-PDF links
            if not href.endswith('.pdf') and '?__blob=publicationFile' not in href:
                continue

            # Construct full URL
            full_url = urljoin(base_url, href)

            # Extract title from link text or attribute
            title = link.get_text(strip=True) or link.get('title', '')

            if not title:
                # Try to extract from URL
                title = urlparse(href).path.split('/')[-1].replace('.pdf', '').replace('_', ' ')

            pdf_info = {
                'url': full_url,
                'title': title[:200],  # Limit title length
                'topic': topic,
                'extracted_at': datetime.now().isoformat(),
            }

            pdf_links.append(pdf_info)

        logger.info(f"Found {len(pdf_links)} PDF links on {base_url}")
        return pdf_links

    def download_pdf(self, pdf_info: Dict) -> Optional[str]:
        """Download a PDF and return the local path"""
        url = pdf_info['url']
        topic = pdf_info['topic']
        title = pdf_info['title']

        # Create filename
        sanitized_title = re.sub(r'[^\w\-.]', '_', title[:50])
        filename = f"{sanitized_title}.pdf"

        # Determine topic directory with year
        year = datetime.now().year
        doc_dir = self.documents_dir / topic / str(year)
        doc_dir.mkdir(parents=True, exist_ok=True)

        filepath = doc_dir / filename

        # Skip if already downloaded
        if filepath.exists():
            logger.info(f"Already downloaded: {filepath}")
            return str(filepath)

        try:
            time.sleep(2)  # Rate limiting
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # Verify it's a PDF
            if response.headers.get('content-type', '').startswith('application/pdf'):
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                file_size = filepath.stat().st_size
                logger.info(f"Downloaded: {filename} ({file_size} bytes)")

                return str(filepath)
            else:
                logger.warning(f"Not a PDF (content-type: {response.headers.get('content-type')}): {url}")
                return None

        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None

    def extract_pdf_metadata(self, filepath: str) -> Dict:
        """Extract metadata from a PDF file"""
        metadata = {
            'file_path': filepath,
            'file_size': 0,
            'page_count': 0,
            'title': '',
            'author': '',
            'creation_date': '',
        }

        try:
            path = Path(filepath)
            if not path.exists():
                return metadata

            metadata['file_size'] = path.stat().st_size

            # Extract PDF metadata
            with open(filepath, 'rb') as f:
                try:
                    reader = PdfReader(f)
                    metadata['page_count'] = len(reader.pages)

                    if reader.metadata:
                        metadata['title'] = reader.metadata.get('/Title', '')
                        metadata['author'] = reader.metadata.get('/Author', '')
                        metadata['creation_date'] = str(reader.metadata.get('/CreationDate', ''))
                except Exception as e:
                    logger.warning(f"Could not read PDF metadata: {e}")

        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")

        return metadata

    def create_metadata_record(self, pdf_info: Dict, filepath: Optional[str]) -> Optional[Dict]:
        """Create a metadata record for a document"""
        if not filepath:
            return None

        pdf_metadata = self.extract_pdf_metadata(filepath)

        # Check for duplicates
        file_hash = self.compute_file_hash(filepath)

        for existing in self.metadata_cache:
            if existing.get('file_hash') == file_hash:
                logger.info(f"Duplicate detected: {filepath}")
                return None

        record = {
            'document_id': hashlib.md5(pdf_info['url'].encode()).hexdigest()[:12],
            'title': pdf_info.get('title', ''),
            'url': pdf_info['url'],
            'topic': pdf_info['topic'],
            'file_path': filepath,
            'file_size': pdf_metadata['file_size'],
            'page_count': pdf_metadata['page_count'],
            'language': 'en',  # Default, could be detected
            'document_type': 'report',  # Could be inferred from content
            'sdg_tags': self.TOPICS.get(pdf_info['topic'], {}).get('sdg_tags', []),
            'region': 'Germany',
            'downloaded_at': datetime.now().isoformat(),
            'file_hash': file_hash,
        }

        return record

    def compute_file_hash(self, filepath: str) -> str:
        """Compute SHA256 hash of a file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash: {e}")
            return ""

    def save_metadata(self, records: List[Dict]):
        """Save metadata records to JSONL file"""
        try:
            with open(self.metadata_path, 'a') as f:
                for record in records:
                    f.write(json.dumps(record) + '\n')
            logger.info(f"Saved {len(records)} metadata records")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def scrape_topic(self, topic: str, max_documents: int = 50) -> int:
        """Scrape documents for a specific topic"""
        logger.info(f"Starting scrape for topic: {topic}")

        if topic not in self.TOPICS:
            logger.error(f"Unknown topic: {topic}")
            return 0

        topic_info = self.TOPICS[topic]
        pdf_links = []
        new_metadata = []

        # Fetch PDFs from configured URLs
        for url in topic_info['urls']:
            logger.info(f"Fetching from: {url}")
            soup = self.fetch_page(url)
            if soup:
                links = self.extract_pdf_links(soup, url, topic)
                pdf_links.extend(links)

        # Limit to max_documents
        pdf_links = pdf_links[:max_documents]

        # Download PDFs and extract metadata
        downloaded_count = 0
        for i, pdf_info in enumerate(pdf_links, 1):
            logger.info(f"Processing {i}/{len(pdf_links)}: {pdf_info['title']}")

            filepath = self.download_pdf(pdf_info)
            if filepath:
                metadata_record = self.create_metadata_record(pdf_info, filepath)
                if metadata_record:
                    new_metadata.append(metadata_record)
                    self.metadata_cache.append(metadata_record)
                    downloaded_count += 1

        # Save metadata
        if new_metadata:
            self.save_metadata(new_metadata)

        logger.info(f"Completed scrape for {topic}: {downloaded_count} documents downloaded")
        return downloaded_count

    def scrape_all_topics(self, max_per_topic: int = 50) -> int:
        """Scrape all configured topics"""
        logger.info(f"Starting full scrape (max {max_per_topic} per topic)")

        total_downloaded = 0
        for topic in self.TOPICS.keys():
            count = self.scrape_topic(topic, max_per_topic)
            total_downloaded += count

        return total_downloaded

    def generate_status_report(self) -> Dict:
        """Generate a status report of scraping progress"""
        # Count documents by topic
        topic_counts = {}
        total_size = 0
        missing_sdg = 0
        missing_pages = 0

        for record in self.metadata_cache:
            topic = record.get('topic', 'unknown')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

            total_size += record.get('file_size', 0)

            if not record.get('sdg_tags'):
                missing_sdg += 1
            if record.get('page_count', 0) == 0:
                missing_pages += 1

        total_docs = len(self.metadata_cache)
        missing_pct = ((missing_sdg + missing_pages) / max(total_docs, 1)) * 100

        status = {
            'total_documents': total_docs,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'documents_by_topic': topic_counts,
            'topics_represented': len([t for t in topic_counts.values() if t > 0]),
            'missing_sdg_tags': missing_sdg,
            'missing_page_counts': missing_pages,
            'incomplete_percentage': round(missing_pct, 2),
            'generated_at': datetime.now().isoformat(),
        }

        return status


def main():
    """Main entry point"""
    import sys

    scraper = BGRScraper()

    # Check robots.txt
    scraper.check_robots_txt()

    # Default: pilot run (50 docs total)
    max_docs = 50
    if len(sys.argv) > 1:
        try:
            max_docs = int(sys.argv[1])
        except ValueError:
            pass

    logger.info(f"Starting BGR scraper with max {max_docs} documents per topic")

    # Scrape all topics
    total = scraper.scrape_all_topics(max_per_topic=max_docs)

    # Generate status report
    status = scraper.generate_status_report()

    logger.info("=" * 60)
    logger.info("SCRAPING STATUS REPORT")
    logger.info("=" * 60)
    logger.info(json.dumps(status, indent=2))
    logger.info("=" * 60)

    return total


if __name__ == '__main__':
    main()
