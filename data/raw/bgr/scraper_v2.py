#!/usr/bin/env python3
"""
BGR (Bundesanstalt für Geowissenschaften und Rohstoffe) Data Acquisition
Uses legitimate APIs: CSW Catalog Service, OGC Web Services, and GEO-LEOe-docs Repository
"""

import os
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import re
from xml.etree import ElementTree as ET

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BGRDataAcquisition:
    """Acquires BGR publications and data using authorized APIs"""

    # BGR APIs and Services
    CSW_ENDPOINT = "https://geoportal.bgr.de/smartfindersdi-csw/api"
    GEOPORTAL_BASE = "https://geoportal.bgr.de"
    GEO_LEO_DOCS = "https://e-docs.geo-leo.de"
    DERA_BASE = "https://www.deutsche-rohstoffagentur.de"

    # OGC Web Services
    WMS_SERVICES = {
        'groundwater_occurrences': 'https://services.bgr.de/wms/grundwasser/ergw1000/',
        'groundwater_recharge': 'https://services.bgr.de/wms/grundwasser/gwn1000/',
        'surface_geology': 'https://services.bgr.de/wms/geologie/BGR_EN_Surface_Geology/',
        'geology_map_250k': 'https://services.bgr.de/wms/inspire_ge/guek250/',
        'geology_map_1m': 'https://services.bgr.de/wms/inspire_ge/gk1000/',
        'mineral_resources': 'https://services.bgr.de/wms/rohstoffe/bsk1000/',
    }

    # Topic configurations
    TOPICS = {
        'groundwater': {
            'name': 'Groundwater',
            'sdg_tags': ['SDG 6', 'SDG 13'],
            'keywords': ['groundwater', 'wasser', 'water', 'aquifer', 'hydro'],
            'services': ['groundwater_occurrences', 'groundwater_recharge']
        },
        'mining': {
            'name': 'Mining & Commodities',
            'sdg_tags': ['SDG 12', 'SDG 13'],
            'keywords': ['mining', 'bergbau', 'commodity', 'rohstoff', 'mineral'],
            'services': ['mineral_resources']
        },
        'geology': {
            'name': 'Geology',
            'sdg_tags': ['SDG 13', 'SDG 15'],
            'keywords': ['geology', 'geologie', 'rocks', 'mineral'],
            'services': ['surface_geology', 'geology_map_250k']
        },
    }

    def __init__(self, output_dir: str = "/home/user/evidence-ai/data/raw/bgr"):
        """Initialize with output directory"""
        self.output_dir = Path(output_dir)
        self.documents_dir = self.output_dir / "documents"
        self.metadata_path = self.output_dir / "metadata" / "bgr_metadata.jsonl"
        self.logs_dir = self.output_dir / "logs"

        # Create directories
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

        # Professional user agent
        self.session.headers.update({
            'User-Agent': 'Evidence-AI Research Bot (Data Acquisition) +https://github.com/robertDouglass/evidence-ai'
        })

        self.metadata_cache: List[Dict] = []
        self.load_metadata_cache()

    def load_metadata_cache(self):
        """Load existing metadata"""
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            self.metadata_cache.append(json.loads(line))
                logger.info(f"Loaded {len(self.metadata_cache)} existing metadata records")
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")

    def search_csw_catalog(self, keywords: List[str], max_results: int = 50) -> List[Dict]:
        """Search BGR CSW catalog for records"""
        results = []

        for keyword in keywords:
            try:
                # CSW GetRecords request
                params = {
                    'request': 'GetRecords',
                    'service': 'CSW',
                    'version': '2.0.1',
                    'resultType': 'results',
                    'typeNames': 'csw:Record',
                    'outputSchema': 'http://www.opengis.net/cat/csw/cswiso',
                    'startPosition': 1,
                    'maxRecords': max_results,
                    'ElementSetName': 'full',
                }

                # Add search filter
                params['CQL_TEXT'] = f'title like "%{keyword}%" OR abstract like "%{keyword}%"'

                time.sleep(1)  # Rate limit
                response = self.session.get(
                    self.CSW_ENDPOINT,
                    params=params,
                    timeout=10
                )
                response.raise_for_status()

                # Parse CSW response
                records = self._parse_csw_response(response.text)
                results.extend(records)
                logger.info(f"Found {len(records)} CSW records for keyword: {keyword}")

            except Exception as e:
                logger.error(f"CSW search failed for '{keyword}': {e}")

        return results

    def _parse_csw_response(self, xml_text: str) -> List[Dict]:
        """Parse CSW GetRecords response"""
        records = []

        try:
            root = ET.fromstring(xml_text)

            # Handle CSW namespace
            ns = {
                'csw': 'http://www.opengis.net/cat/csw/2.0.1',
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'dct': 'http://purl.org/dc/terms/',
                'dc': 'http://purl.org/dc/elements/1.1/'
            }

            # Extract records
            for record in root.findall('.//csw:SummaryRecord', ns) or root.findall('.//rdf:Description', ns):
                title = record.findtext('dc:title', ns) or record.findtext('dct:title', ns) or ''
                description = record.findtext('dct:abstract', ns) or record.findtext('dc:description', ns) or ''
                identifier = record.findtext('dc:identifier', ns) or ''
                issued = record.findtext('dct:issued', ns) or ''

                if title or identifier:
                    records.append({
                        'title': title,
                        'description': description,
                        'identifier': identifier,
                        'issued': issued,
                        'source': 'CSW',
                        'url': identifier if identifier.startswith('http') else '',
                    })

        except Exception as e:
            logger.warning(f"Could not parse CSW response: {e}")

        return records

    def search_geo_leo_docs(self, keywords: List[str], max_results: int = 50) -> List[Dict]:
        """Search GEO-LEOe-docs repository for BGR publications"""
        results = []

        for keyword in keywords:
            try:
                # OAI-PMH ListRecords with search
                params = {
                    'verb': 'ListRecords',
                    'metadataPrefix': 'oai_dc',
                    'from': '2015-01-01',
                    'set': 'openair',
                }

                time.sleep(1)  # Rate limit
                response = self.session.get(
                    f"{self.GEO_LEO_DOCS}/oai/",
                    params=params,
                    timeout=10
                )
                response.raise_for_status()

                # Parse OAI response
                records = self._parse_oai_response(response.text, keyword)
                results.extend(records[:max_results])
                logger.info(f"Found {len(records)} GEO-LEOe-docs records for: {keyword}")

            except Exception as e:
                logger.error(f"GEO-LEOe-docs search failed for '{keyword}': {e}")

        return results

    def _parse_oai_response(self, xml_text: str, keyword: str = '') -> List[Dict]:
        """Parse OAI-PMH response"""
        records = []

        try:
            root = ET.fromstring(xml_text)

            ns = {
                'oai': 'http://www.openarchives.org/OAI/2.0/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'dct': 'http://purl.org/dc/terms/'
            }

            for record in root.findall('.//oai:record', ns):
                metadata = record.find('.//oai:metadata/oai_dc:dc', ns) or \
                          record.find('.//oai:metadata/dc:dc', ns)

                if metadata is None:
                    continue

                title = metadata.findtext('dc:title', ns) or ''
                description = metadata.findtext('dc:description', ns) or ''
                identifier = metadata.findtext('dc:identifier', ns) or ''
                creator = metadata.findtext('dc:creator', ns) or ''
                date = metadata.findtext('dc:date', ns) or ''

                # Filter by keyword if not found in title/description
                full_text = f"{title} {description} {creator}".lower()
                if keyword.lower() in full_text or not keyword:
                    records.append({
                        'title': title,
                        'description': description,
                        'identifier': identifier,
                        'creator': creator,
                        'date': date,
                        'source': 'GEO-LEOe-docs',
                        'url': identifier if identifier.startswith('http') else '',
                    })

        except Exception as e:
            logger.warning(f"Could not parse OAI response: {e}")

        return records

    def query_geoportal(self, topic: str, max_results: int = 50) -> List[Dict]:
        """Query BGR Geoportal for topic-specific resources"""
        results = []

        try:
            # Geoportal advanced search
            search_url = f"{self.GEOPORTAL_BASE}/mapapps/resources/apps/geoportal/index.html"

            topic_config = self.TOPICS.get(topic, {})
            keywords = topic_config.get('keywords', [])

            # Combine CSW and GEO-LEOe-docs results
            results.extend(self.search_csw_catalog(keywords, max_results))
            results.extend(self.search_geo_leo_docs(keywords, max_results))

            logger.info(f"Found {len(results)} total results for topic: {topic}")

        except Exception as e:
            logger.error(f"Geoportal query failed: {e}")

        return results

    def create_metadata_record(self, doc_info: Dict, topic: str) -> Dict:
        """Create a metadata record from API result"""
        record = {
            'document_id': hashlib.md5(f"{doc_info.get('identifier', '')}{doc_info.get('title', '')}".encode()).hexdigest()[:12],
            'title': doc_info.get('title', '')[:200],
            'url': doc_info.get('url', '') or doc_info.get('identifier', ''),
            'description': doc_info.get('description', '')[:500],
            'topic': topic,
            'source': doc_info.get('source', 'unknown'),
            'author': doc_info.get('creator', '') or doc_info.get('author', ''),
            'published_date': doc_info.get('date', '') or doc_info.get('issued', ''),
            'language': 'en',
            'document_type': 'report',
            'sdg_tags': self.TOPICS.get(topic, {}).get('sdg_tags', []),
            'region': 'Germany',
            'acquired_at': datetime.now().isoformat(),
        }

        return record

    def acquire_topic_documents(self, topic: str, max_documents: int = 50) -> int:
        """Acquire documents for a specific topic"""
        logger.info(f"Acquiring documents for topic: {topic}")

        if topic not in self.TOPICS:
            logger.error(f"Unknown topic: {topic}")
            return 0

        # Query available sources
        documents = self.query_geoportal(topic, max_documents)

        # Create metadata records
        new_metadata = []
        for doc_info in documents:
            # Check for duplicates
            doc_id = doc_info.get('identifier', '') + doc_info.get('title', '')
            if any(m['document_id'] == hashlib.md5(doc_id.encode()).hexdigest()[:12] for m in self.metadata_cache):
                continue

            metadata_record = self.create_metadata_record(doc_info, topic)
            new_metadata.append(metadata_record)
            self.metadata_cache.append(metadata_record)

        # Save metadata
        if new_metadata:
            self.save_metadata(new_metadata)
            logger.info(f"Acquired {len(new_metadata)} documents for {topic}")

        return len(new_metadata)

    def save_metadata(self, records: List[Dict]):
        """Save metadata records to JSONL"""
        try:
            with open(self.metadata_path, 'a') as f:
                for record in records:
                    f.write(json.dumps(record) + '\n')
            logger.info(f"Saved {len(records)} metadata records")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def acquire_all_topics(self, max_per_topic: int = 50) -> int:
        """Acquire documents for all topics"""
        logger.info(f"Starting data acquisition (max {max_per_topic} per topic)")

        total_acquired = 0
        for topic in self.TOPICS.keys():
            count = self.acquire_topic_documents(topic, max_per_topic)
            total_acquired += count

        return total_acquired

    def generate_status_report(self) -> Dict:
        """Generate acquisition status report"""
        topic_counts = {}
        sources = {}

        for record in self.metadata_cache:
            topic = record.get('topic', 'unknown')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

            source = record.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1

        total_docs = len(self.metadata_cache)

        status = {
            'total_documents_acquired': total_docs,
            'documents_by_topic': topic_counts,
            'topics_represented': len([t for t in topic_counts.values() if t > 0]),
            'documents_by_source': sources,
            'generated_at': datetime.now().isoformat(),
        }

        return status


def main():
    """Main entry point"""
    import sys

    acquisition = BGRDataAcquisition()

    # Default: 50 documents per topic
    max_docs = 50
    if len(sys.argv) > 1:
        try:
            max_docs = int(sys.argv[1])
        except ValueError:
            pass

    logger.info(f"Starting BGR data acquisition (max {max_docs} per topic)")
    logger.info("Using legitimate APIs: CSW Catalog, OAI-PMH, OGC Web Services")

    # Acquire documents
    total = acquisition.acquire_all_topics(max_docs)

    # Generate status report
    status = acquisition.generate_status_report()

    logger.info("=" * 70)
    logger.info("BGR DATA ACQUISITION STATUS REPORT")
    logger.info("=" * 70)
    logger.info(json.dumps(status, indent=2))
    logger.info("=" * 70)

    return total


if __name__ == '__main__':
    main()
