#!/usr/bin/env python3
"""
World Bank & GFDRR Climate Adaptation Evidence Harvester

Harvests ~1,200 open World Bank/GFDRR reports on climate adaptation,
resilience, and disaster risk management (2010-2024).

Licensing: World Bank (CC BY 3.0 IGO), GFDRR (CC BY 3.0 IGO)
"""

import os
import json
import csv
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import quote
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorldBankHarvester:
    """Harvest World Bank climate adaptation documents."""

    # World Bank API endpoints
    WB_API_BASE = "https://search.worldbank.org/api/v2/wds"
    WB_DOCS_BASE = "https://documents.worldbank.org/curated/en"

    # Configuration
    BATCH_SIZE = 500  # API rows per query
    MAX_RETRIES = 4
    RETRY_DELAY = 2  # seconds, exponential backoff
    TIMEOUT = 30

    def __init__(self, output_base_dir: str = None):
        """Initialize harvester with output directory."""
        if output_base_dir is None:
            output_base_dir = "/home/user/evidence-ai/worldbank/climate"

        self.output_base = Path(output_base_dir)
        self.output_base.mkdir(parents=True, exist_ok=True)

        # Create subdirectories by doc type
        self.doc_type_dirs = {
            "Implementation Completion Report": self.output_base / "icr",
            "Impact Evaluation": self.output_base / "impact_evaluation",
            "Policy Research Working Paper": self.output_base / "policy_paper",
            "Other": self.output_base / "other"
        }
        for d in self.doc_type_dirs.values():
            d.mkdir(parents=True, exist_ok=True)

        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=self.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Metadata log
        self.metadata_log = self.output_base / "metadata.jsonl"
        self.download_log = self.output_base / "download_log.csv"

    def query_api(self, offset: int = 0, rows: int = None) -> Optional[Dict]:
        """Query World Bank WDS API for climate change documents."""
        if rows is None:
            rows = self.BATCH_SIZE

        params = {
            "format": "json",
            "fl": "id,docdt,docty,title,repnb,subTitle,theme,geoRegion",
            "fct": "doctype_exact:Implementation Completion Report;topic_exact:Climate Change",
            "rows": rows,
            "os": offset
        }

        try:
            logger.info(f"Querying API: offset={offset}, rows={rows}")
            response = self.session.get(
                self.WB_API_BASE,
                params=params,
                timeout=self.TIMEOUT,
                verify=False  # Handle SSL certificate issues
            )
            response.raise_for_status()
            data = response.json()

            logger.info(f"Retrieved {len(data.get('documents', {}))} documents")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"API query failed: {e}")
            return None

    def extract_metadata(self, doc_id: str, doc_data: Dict) -> Dict:
        """Extract standardized metadata from document."""
        doc_type = doc_data.get("docty", "Other")

        # Parse publication year from docdt
        docdt = doc_data.get("docdt", "")
        pub_year = docdt[:4] if docdt else None

        # Extract region from geoRegion if available
        geo_region = doc_data.get("geoRegion", [])
        if isinstance(geo_region, dict):
            geo_region = list(geo_region.keys())
        elif not isinstance(geo_region, list):
            geo_region = [str(geo_region)] if geo_region else []

        # Extract themes
        theme = doc_data.get("theme", "")
        themes = [t.strip() for t in theme.split(",") if t.strip()]

        # SDG tagging based on themes
        sdg_tags = self._extract_sdg_tags(themes)

        metadata = {
            "doc_id": f"WB-CLIM-{doc_data.get('repnb', doc_id)}",
            "document_type": doc_type,
            "title": doc_data.get("title", ""),
            "subtitle": doc_data.get("subTitle", ""),
            "country": [],  # Would need additional lookup
            "region": geo_region,
            "themes": themes,
            "sdg_tags": sdg_tags,
            "publication_year": pub_year,
            "url": doc_data.get("url", ""),
            "pdfurl": doc_data.get("pdfurl", ""),
            "license": "CC BY 3.0 IGO",
            "harvested_date": datetime.now().isoformat(),
            "wb_docid": doc_id,
            "repnb": doc_data.get("repnb", "")
        }

        return metadata

    def _extract_sdg_tags(self, themes: List[str]) -> List[int]:
        """Extract SDG numbers from themes."""
        sdg_mapping = {
            "Climate change": [13],
            "Adaptation": [13],
            "Mitigation": [13],
            "Resilience": [1, 13],
            "Disaster": [1, 11, 13],
            "Water": [6, 13],
            "Agriculture": [2, 13],
            "Energy": [7, 13],
            "Infrastructure": [9, 11],
            "Urban": [11, 13],
            "Coastal": [14],
        }

        sdg_set = set()
        for theme in themes:
            for keyword, sdgs in sdg_mapping.items():
                if keyword.lower() in theme.lower():
                    sdg_set.update(sdgs)

        return sorted(list(sdg_set))

    def download_document(self, metadata: Dict, max_size: int = 500_000_000) -> bool:
        """Download document PDF."""
        pdfurl = metadata.get("pdfurl", "")
        if not pdfurl:
            logger.warning(f"No PDF URL for {metadata.get('doc_id')}")
            return False

        doc_type = metadata.get("document_type", "Other")
        output_dir = self.doc_type_dirs.get(doc_type, self.doc_type_dirs["Other"])

        # Construct filename: WB-CLIM-<repnb>.pdf
        filename = f"{metadata.get('doc_id')}.pdf"
        filepath = output_dir / filename

        if filepath.exists():
            logger.info(f"Already downloaded: {filename}")
            return True

        try:
            logger.info(f"Downloading: {filename}")
            response = self.session.get(
                pdfurl,
                timeout=self.TIMEOUT,
                stream=True,
                verify=False,
                allow_redirects=True
            )
            response.raise_for_status()

            # Validate file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > max_size:
                logger.warning(f"File too large ({content_length} bytes): {filename}")
                return False

            # Download in chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = filepath.stat().st_size
            if file_size == 0:
                logger.warning(f"Downloaded file is empty: {filename}")
                filepath.unlink()
                return False

            logger.info(f"Downloaded ({file_size} bytes): {filename}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed for {filename}: {e}")
            if filepath.exists():
                filepath.unlink()
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading {filename}: {e}")
            if filepath.exists():
                filepath.unlink()
            return False

    def save_metadata(self, metadata: Dict):
        """Save metadata to JSONL file."""
        try:
            with open(self.metadata_log, 'a') as f:
                f.write(json.dumps(metadata) + '\n')
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def log_download_result(self, doc_id: str, success: bool, file_size: int = 0):
        """Log download result to CSV."""
        try:
            file_exists = self.download_log.exists()
            with open(self.download_log, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['timestamp', 'doc_id', 'success', 'file_size'])
                writer.writerow([datetime.now().isoformat(), doc_id, success, file_size])
        except Exception as e:
            logger.error(f"Failed to log download: {e}")

    def harvest(self, max_documents: int = None, start_offset: int = 0):
        """Main harvest loop."""
        logger.info("=" * 60)
        logger.info("World Bank Climate Adaptation Harvester")
        logger.info(f"Output directory: {self.output_base}")
        logger.info("=" * 60)

        total_docs = 0
        total_downloads = 0
        offset = start_offset

        try:
            while True:
                # Query API
                api_data = self.query_api(offset=offset)
                if not api_data:
                    logger.warning("API query failed, stopping harvest")
                    break

                documents = api_data.get('documents', {})
                if not documents:
                    logger.info("No more documents from API")
                    break

                total_api_count = api_data.get('total', 0)
                logger.info(f"Total available in API: {total_api_count}")

                # Process each document
                for doc_id, doc_data in documents.items():
                    # Extract metadata
                    metadata = self.extract_metadata(doc_id, doc_data)

                    # Download document
                    success = self.download_document(metadata)

                    # Log results
                    self.save_metadata(metadata)
                    if success:
                        filepath = self._get_filepath(metadata)
                        file_size = filepath.stat().st_size if filepath.exists() else 0
                        self.log_download_result(metadata.get('doc_id'), True, file_size)
                        total_downloads += 1
                    else:
                        self.log_download_result(metadata.get('doc_id'), False, 0)

                    total_docs += 1

                    # Check if we've reached max documents
                    if max_documents and total_docs >= max_documents:
                        logger.info(f"Reached max documents limit: {max_documents}")
                        break

                if max_documents and total_docs >= max_documents:
                    break

                # Move to next batch
                offset += self.BATCH_SIZE

                # Polite delay between API calls
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Harvest interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error during harvest: {e}", exc_info=True)
        finally:
            logger.info("=" * 60)
            logger.info(f"Harvest complete:")
            logger.info(f"  Total documents processed: {total_docs}")
            logger.info(f"  Total documents downloaded: {total_downloads}")
            logger.info(f"  Metadata log: {self.metadata_log}")
            logger.info(f"  Download log: {self.download_log}")
            logger.info("=" * 60)

    def _get_filepath(self, metadata: Dict) -> Path:
        """Get the filepath for a document based on its metadata."""
        doc_type = metadata.get("document_type", "Other")
        output_dir = self.doc_type_dirs.get(doc_type, self.doc_type_dirs["Other"])
        filename = f"{metadata.get('doc_id')}.pdf"
        return output_dir / filename


def main():
    """Run the harvester."""
    import argparse

    parser = argparse.ArgumentParser(
        description="World Bank Climate Adaptation Evidence Harvester"
    )
    parser.add_argument(
        "--max-documents",
        type=int,
        default=None,
        help="Maximum number of documents to harvest (default: all)"
    )
    parser.add_argument(
        "--start-offset",
        type=int,
        default=0,
        help="Starting offset for API queries (default: 0)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/home/user/evidence-ai/worldbank/climate",
        help="Output directory for downloaded documents"
    )

    args = parser.parse_args()

    harvester = WorldBankHarvester(output_base_dir=args.output_dir)
    harvester.harvest(
        max_documents=args.max_documents,
        start_offset=args.start_offset
    )


if __name__ == "__main__":
    main()
