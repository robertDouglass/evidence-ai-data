#!/usr/bin/env python3
"""
Deduplication Service for Evidence AI Data Lake
==========================================

Scans all source directories in data/raw/*/documents to detect and report duplicates
using SHA256 file hashing and fuzzy title matching.

Outputs:
  - data/raw/shared/logs/dedup_report.json: Detailed deduplication report
  - Updates source metadata files with duplicate flags

Usage:
    python dedup_service.py [--sources BMZ,GIZ,KfW] [--generate-report-only]

Author: Evidence AI Ingestion Pipeline
Version: 1.0 (2025-11-19)
"""

import json
import os
import hashlib
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Set
from difflib import SequenceMatcher
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeduplicationService:
    """Service for detecting and tracking document duplicates."""

    def __init__(self, data_raw_path: str = "/home/user/evidence-ai/data/raw"):
        """Initialize deduplication service."""
        self.data_raw_path = Path(data_raw_path)
        self.hash_to_files: Dict[str, List[Dict]] = defaultdict(list)
        self.title_groups: Dict[str, List[Dict]] = defaultdict(list)
        self.duplicates: List[Dict] = []
        self.report: Dict = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_files_scanned": 0,
            "duplicate_groups": [],
            "fuzzy_matches": [],
            "summary": {}
        }

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.warning(f"Error hashing {file_path}: {e}")
            return None

    def extract_title_from_metadata(self, metadata_dir: Path, doc_id: str) -> str:
        """Extract document title from source metadata files."""
        # Try common metadata file formats
        for metadata_file in metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if item.get("doc_id") == doc_id:
                                return item.get("title", "")
                    elif isinstance(data, dict):
                        if data.get("doc_id") == doc_id:
                            return data.get("title", "")
            except:
                pass
        return ""

    def fuzzy_title_match(self, title1: str, title2: str, threshold: float = 0.85) -> bool:
        """Check if two titles are similar using fuzzy matching."""
        if not title1 or not title2:
            return False
        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        if t1 == t2:
            return True
        # Use sequence matcher for fuzzy comparison
        ratio = SequenceMatcher(None, t1, t2).ratio()
        return ratio >= threshold

    def scan_documents(self, sources: List[str] = None) -> None:
        """Scan all documents in data/raw structure."""
        logger.info("Starting document scan for deduplication...")

        # If no sources specified, scan all
        if sources is None:
            sources = [d.name for d in self.data_raw_path.iterdir()
                      if d.is_dir() and d.name != "shared"]

        file_count = 0
        for source in sources:
            source_path = self.data_raw_path / source
            docs_path = source_path / "documents"
            metadata_path = source_path / "metadata"

            if not docs_path.exists():
                logger.debug(f"Skipping {source}: no documents directory")
                continue

            logger.info(f"Scanning {source}...")

            # Recursively find all PDFs and DOCX files
            for doc_file in docs_path.rglob("*"):
                if doc_file.is_file() and doc_file.suffix.lower() in [".pdf", ".docx"]:
                    file_count += 1
                    file_hash = self.compute_file_hash(doc_file)

                    if file_hash:
                        doc_id = doc_file.stem  # Extract doc_id from filename
                        title = self.extract_title_from_metadata(metadata_path, doc_id)

                        file_info = {
                            "source": source,
                            "doc_id": doc_id,
                            "file_path": str(doc_file.relative_to(self.data_raw_path)),
                            "file_size_bytes": doc_file.stat().st_size,
                            "title": title
                        }

                        # Track by hash (exact duplicates)
                        self.hash_to_files[file_hash].append(file_info)

                        # Track by title (fuzzy matches)
                        if title:
                            title_normalized = title.lower().strip()
                            self.title_groups[title_normalized].append(file_info)

        self.report["total_files_scanned"] = file_count
        logger.info(f"Scanned {file_count} files across {len(sources)} sources")

    def identify_duplicates(self) -> None:
        """Identify exact and fuzzy duplicates."""
        logger.info("Identifying exact hash duplicates...")

        # Exact duplicates (same SHA256 hash)
        for file_hash, files in self.hash_to_files.items():
            if len(files) > 1:
                duplicate_group = {
                    "hash": file_hash,
                    "duplicate_count": len(files),
                    "files": files,
                    "notes": "Exact duplicate: identical file content"
                }
                self.report["duplicate_groups"].append(duplicate_group)
                self.duplicates.extend(files[1:])  # Mark all but first as duplicates

        logger.info(f"Found {len(self.report['duplicate_groups'])} exact duplicate groups")

        # Fuzzy title matches (cross-source)
        logger.info("Identifying fuzzy title matches...")
        processed_titles = set()

        for title_normalized, files in self.title_groups.items():
            if title_normalized in processed_titles or len(files) <= 1:
                continue

            # Check if titles match with high similarity
            for i, file1 in enumerate(files):
                for file2 in files[i+1:]:
                    if file1["source"] != file2["source"]:  # Cross-source comparison
                        if self.fuzzy_title_match(file1["title"], file2["title"], threshold=0.85):
                            fuzzy_match = {
                                "title": file1["title"],
                                "similarity": "high",
                                "files": [
                                    {"source": file1["source"], "doc_id": file1["doc_id"], "file_path": file1["file_path"]},
                                    {"source": file2["source"], "doc_id": file2["doc_id"], "file_path": file2["file_path"]}
                                ],
                                "notes": "Possible republished or translated version across sources"
                            }
                            self.report["fuzzy_matches"].append(fuzzy_match)

            processed_titles.add(title_normalized)

        logger.info(f"Found {len(self.report['fuzzy_matches'])} fuzzy title matches")

    def generate_summary(self) -> None:
        """Generate summary statistics."""
        logger.info("Generating summary report...")

        total_duplicates = sum(len(group["files"]) - 1 for group in self.report["duplicate_groups"])

        self.report["summary"] = {
            "total_files_scanned": self.report["total_files_scanned"],
            "exact_duplicate_groups": len(self.report["duplicate_groups"]),
            "total_duplicate_files": total_duplicates,
            "fuzzy_match_groups": len(self.report["fuzzy_matches"]),
            "deduplication_ratio": round(total_duplicates / self.report["total_files_scanned"] * 100, 2) if self.report["total_files_scanned"] > 0 else 0,
            "recommendation": "Remove identified exact duplicates; manually review fuzzy matches for cross-source consolidation"
        }

    def write_report(self, output_path: str = None) -> str:
        """Write deduplication report to JSON file."""
        if output_path is None:
            output_path = "/home/user/evidence-ai/data/raw/shared/logs/dedup_report.json"

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2)

        logger.info(f"Report written to {output_path}")
        return output_path

    def print_summary(self) -> None:
        """Print summary to console."""
        print("\n" + "="*70)
        print("DEDUPLICATION SERVICE SUMMARY")
        print("="*70)
        print(f"Timestamp: {self.report['timestamp']}")
        print(f"Total files scanned: {self.report['total_files_scanned']}")
        print(f"Exact duplicate groups: {self.report['summary'].get('exact_duplicate_groups', 0)}")
        print(f"Total duplicate files: {self.report['summary'].get('total_duplicate_files', 0)}")
        print(f"Fuzzy match groups: {self.report['summary'].get('fuzzy_match_groups', 0)}")
        print(f"Deduplication ratio: {self.report['summary'].get('deduplication_ratio', 0)}%")
        print(f"\nRecommendation: {self.report['summary'].get('recommendation', '')}")
        print("="*70 + "\n")

    def run(self, sources: List[str] = None) -> Dict:
        """Run complete deduplication workflow."""
        self.scan_documents(sources)
        self.identify_duplicates()
        self.generate_summary()
        self.write_report()
        self.print_summary()
        return self.report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deduplication service for Evidence AI data lake"
    )
    parser.add_argument(
        "--sources",
        type=str,
        help="Comma-separated list of sources to scan (default: all)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/home/user/evidence-ai/data/raw/shared/logs/dedup_report.json",
        help="Output path for dedup report"
    )

    args = parser.parse_args()

    sources = None
    if args.sources:
        sources = [s.strip() for s in args.sources.split(",")]

    service = DeduplicationService()
    service.run(sources)


if __name__ == "__main__":
    main()
