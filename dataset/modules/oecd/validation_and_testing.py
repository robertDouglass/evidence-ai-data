#!/usr/bin/env python3
"""
OECD DAC Acquisition Validation & Testing Suite

Provides testing and validation utilities for the OECD DAC corpus acquisition pipeline.
Includes document download verification, metadata quality checks, and integration tests.

Usage:
    python3 validation_and_testing.py [--test-mode] [--generate-samples]
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationSuite:
    """Comprehensive validation suite for OECD DAC corpus."""

    BASE_DIR = Path(__file__).parent
    PEER_REVIEW_DIR = BASE_DIR / "peer-reviews"
    EVAL_INSIGHTS_DIR = BASE_DIR / "eval-insights"
    METADATA_DIR = BASE_DIR / "metadata"
    CONSOLIDATED_DIR = BASE_DIR / "consolidated"

    # Expected document counts (approximate for target)
    EXPECTED_PEER_REVIEWS = 35  # One per DAC member
    EXPECTED_EVAL_INSIGHTS = 100  # Historical and recent
    EXPECTED_TOTAL_DOCUMENTS = 135

    # Quality thresholds
    MIN_PAGE_COUNT = 5
    MIN_WORD_COUNT = 1000
    MIN_TITLE_LENGTH = 20
    MIN_EXTRACTION_QUALITY = 0.85

    def __init__(self):
        """Initialize validation suite."""
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "warnings": [],
            "errors": [],
            "document_checks": [],
            "metadata_checks": []
        }

    def test_directory_structure(self) -> bool:
        """Verify required directory structure exists."""
        logger.info("Testing directory structure...")

        required_dirs = [
            self.PEER_REVIEW_DIR,
            self.EVAL_INSIGHTS_DIR,
            self.METADATA_DIR,
            self.CONSOLIDATED_DIR
        ]

        all_exist = True
        for d in required_dirs:
            if d.exists() and d.is_dir():
                logger.info(f"✓ {d.name}/ exists")
            else:
                logger.error(f"✗ {d.name}/ missing or not a directory")
                self.validation_results["errors"].append(f"Missing directory: {d}")
                all_exist = False

        if all_exist:
            self.validation_results["tests_passed"] += 1
        else:
            self.validation_results["tests_failed"] += 1

        return all_exist

    def test_pdf_integrity(self, pdf_path: Path) -> bool:
        """Test if PDF file is readable and valid."""
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                page_count = len(reader.pages)
                return page_count > 0

        except Exception as e:
            logger.warning(f"PDF integrity check failed: {pdf_path.name} - {e}")
            return False

    def check_document_structure(self, pdf_path: Path) -> Dict:
        """Check document structure (page count, text extraction, etc.)."""
        result = {
            "filename": pdf_path.name,
            "file_size": pdf_path.stat().st_size,
            "checks": {}
        }

        try:
            import PyPDF2

            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                page_count = len(reader.pages)
                result["page_count"] = page_count
                result["checks"]["has_pages"] = page_count >= self.MIN_PAGE_COUNT

                # Try text extraction
                text_found = 0
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_found += len(text.split())

                result["word_count"] = text_found
                result["checks"]["has_text"] = text_found >= self.MIN_WORD_COUNT

                # Check for metadata
                if reader.metadata:
                    result["has_metadata"] = True
                    result["checks"]["has_metadata"] = True
                else:
                    result["checks"]["has_metadata"] = False

        except Exception as e:
            result["error"] = str(e)
            for check in ["has_pages", "has_text", "has_metadata"]:
                result["checks"][check] = False

        return result

    def validate_metadata_file(self, json_path: Path) -> Tuple[bool, Dict]:
        """Validate metadata JSON file against schema."""
        required_fields = [
            "doc_id", "filename", "file_path", "file_size",
            "document_series", "publication_year", "language", "license"
        ]

        try:
            with open(json_path, 'r') as f:
                metadata = json.load(f)

            issues = []

            # Check required fields
            for field in required_fields:
                if field not in metadata or not metadata[field]:
                    issues.append(f"Missing required field: {field}")

            # Check field types
            if metadata.get("publication_year") and not isinstance(metadata["publication_year"], int):
                issues.append("publication_year should be integer")

            if isinstance(metadata.get("sdg_focus"), str):
                issues.append("sdg_focus should be array, not string")

            # Check data quality
            if metadata.get("title") and len(metadata["title"]) < self.MIN_TITLE_LENGTH:
                issues.append(f"Title too short (<{self.MIN_TITLE_LENGTH} chars)")

            if metadata.get("word_count", 0) < self.MIN_WORD_COUNT:
                issues.append(f"Word count below minimum ({self.MIN_WORD_COUNT})")

            is_valid = len(issues) == 0
            return is_valid, {
                "filename": json_path.name,
                "valid": is_valid,
                "issues": issues,
                "metadata": metadata
            }

        except json.JSONDecodeError as e:
            return False, {
                "filename": json_path.name,
                "valid": False,
                "issues": [f"Invalid JSON: {e}"]
            }
        except Exception as e:
            return False, {
                "filename": json_path.name,
                "valid": False,
                "issues": [f"Error reading file: {e}"]
            }

    def validate_consolidated_metadata(self) -> Tuple[bool, Dict]:
        """Validate consolidated metadata file."""
        consolidated_path = self.CONSOLIDATED_DIR / "oecd_dac_metadata.jsonl"

        logger.info("Validating consolidated metadata...")

        if not consolidated_path.exists():
            logger.warning("No consolidated metadata file found")
            return False, {"error": "File not found"}

        try:
            records = []
            with open(consolidated_path, 'r') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))

            logger.info(f"  Total records: {len(records)}")

            # Check for duplicates
            doc_ids = [r.get("doc_id") for r in records]
            duplicate_ids = [id for id in doc_ids if doc_ids.count(id) > 1]

            checks = {
                "total_records": len(records),
                "unique_records": len(set(doc_ids)),
                "duplicate_ids": duplicate_ids,
                "peer_reviews": len([r for r in records if "PEER" in r.get("doc_id", "")]),
                "eval_insights": len([r for r in records if "EVAL" in r.get("doc_id", "")]),
                "year_range": [
                    min([r.get("publication_year") for r in records if r.get("publication_year")]),
                    max([r.get("publication_year") for r in records if r.get("publication_year")])
                ] if records else None,
                "languages": list(set([r.get("language", "unknown") for r in records])),
                "sdg_coverage": {}
            }

            # Calculate SDG coverage
            for record in records:
                for sdg in record.get("sdg_focus", []):
                    checks["sdg_coverage"][sdg] = checks["sdg_coverage"].get(sdg, 0) + 1

            is_valid = len(duplicate_ids) == 0 and len(records) > 0

            return is_valid, checks

        except Exception as e:
            logger.error(f"Error validating consolidated metadata: {e}")
            return False, {"error": str(e)}

    def run_full_validation(self) -> Dict:
        """Execute full validation suite."""
        logger.info("=" * 60)
        logger.info("OECD DAC Acquisition Validation Suite")
        logger.info("=" * 60)

        # Test 1: Directory structure
        logger.info("\n[Test 1/5] Directory Structure")
        self.test_directory_structure()

        # Test 2: Document files
        logger.info("\n[Test 2/5] Document Files")
        self._test_document_files()

        # Test 3: Individual metadata files
        logger.info("\n[Test 3/5] Individual Metadata Files")
        self._test_individual_metadata()

        # Test 4: Consolidated metadata
        logger.info("\n[Test 4/5] Consolidated Metadata")
        is_valid, consolidated_check = self.validate_consolidated_metadata()
        if is_valid:
            self.validation_results["tests_passed"] += 1
            logger.info("✓ Consolidated metadata valid")
        else:
            self.validation_results["tests_failed"] += 1
            logger.warning("✗ Consolidated metadata has issues")

        self.validation_results["consolidated_metadata"] = consolidated_check

        # Test 5: Integration checks
        logger.info("\n[Test 5/5] Integration Checks")
        self._test_integration()

        # Summary
        self._print_summary()

        return self.validation_results

    def _test_document_files(self):
        """Test document files in peer-reviews and eval-insights."""
        pdf_files = list(self.PEER_REVIEW_DIR.glob("*.pdf")) + \
                   list(self.EVAL_INSIGHTS_DIR.glob("*.pdf"))

        logger.info(f"  Found {len(pdf_files)} PDF documents")

        if not pdf_files:
            logger.warning("  ✗ No PDF documents found")
            self.validation_results["warnings"].append("No PDF documents found")
            return

        structural_issues = 0
        for pdf_file in pdf_files[:5]:  # Check first 5 as sample
            check_result = self.check_document_structure(pdf_file)
            is_readable = check_result["checks"].get("has_text", False)

            if is_readable:
                logger.info(f"  ✓ {pdf_file.name}: {check_result.get('page_count', '?')} pages, "
                           f"{check_result.get('word_count', '?')} words")
            else:
                logger.warning(f"  ✗ {pdf_file.name}: extraction issues")
                structural_issues += 1

            self.validation_results["document_checks"].append(check_result)

        if structural_issues == 0:
            self.validation_results["tests_passed"] += 1
        else:
            self.validation_results["tests_failed"] += 1

    def _test_individual_metadata(self):
        """Test individual metadata JSON files."""
        json_files = list(self.METADATA_DIR.glob("*.json"))

        logger.info(f"  Found {len(json_files)} metadata files")

        if not json_files:
            logger.warning("  ✗ No metadata files found")
            return

        valid_count = 0
        for json_file in json_files[:5]:  # Check first 5 as sample
            is_valid, check_result = self.validate_metadata_file(json_file)

            if is_valid:
                logger.info(f"  ✓ {json_file.name}: valid")
                valid_count += 1
            else:
                logger.warning(f"  ✗ {json_file.name}: {', '.join(check_result['issues'][:2])}")

            self.validation_results["metadata_checks"].append(check_result)

        if valid_count == len(json_files[:5]):
            self.validation_results["tests_passed"] += 1
        else:
            self.validation_results["tests_failed"] += 1

    def _test_integration(self):
        """Test integration between documents and metadata."""
        logger.info("  Checking document-metadata alignment...")

        pdf_files = set([f.stem for f in self.PEER_REVIEW_DIR.glob("*.pdf")] +
                       [f.stem for f in self.EVAL_INSIGHTS_DIR.glob("*.pdf")])

        json_files = set([f.stem for f in self.METADATA_DIR.glob("*.json")])

        missing_metadata = pdf_files - json_files
        orphaned_metadata = json_files - pdf_files

        if missing_metadata:
            logger.warning(f"  ✗ {len(missing_metadata)} documents missing metadata files")
            self.validation_results["warnings"].append(
                f"Missing metadata for {len(missing_metadata)} documents"
            )

        if orphaned_metadata:
            logger.warning(f"  ✗ {len(orphaned_metadata)} orphaned metadata files")
            self.validation_results["warnings"].append(
                f"{len(orphaned_metadata)} metadata files without corresponding documents"
            )

        if not missing_metadata and not orphaned_metadata:
            logger.info("  ✓ Document-metadata alignment verified")
            self.validation_results["tests_passed"] += 1
        else:
            self.validation_results["tests_failed"] += 1

    def _print_summary(self):
        """Print validation summary."""
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)

        passed = self.validation_results["tests_passed"]
        failed = self.validation_results["tests_failed"]
        total = passed + failed

        logger.info(f"\nTests Passed: {passed}/{total}")
        logger.info(f"Tests Failed: {failed}/{total}")

        if self.validation_results["warnings"]:
            logger.info(f"\nWarnings ({len(self.validation_results['warnings'])}):")
            for warning in self.validation_results["warnings"]:
                logger.warning(f"  • {warning}")

        if self.validation_results["errors"]:
            logger.info(f"\nErrors ({len(self.validation_results['errors'])}):")
            for error in self.validation_results["errors"]:
                logger.error(f"  • {error}")

        if failed == 0:
            logger.info("\n✓ All validation tests passed!")
        else:
            logger.info(f"\n✗ {failed} validation test(s) failed")

        logger.info("=" * 60)

    def save_validation_report(self) -> Path:
        """Save validation results to JSON report."""
        report_path = self.BASE_DIR / "VALIDATION_REPORT.json"

        # Remove unprintable objects for JSON serialization
        results = self.validation_results.copy()
        results["timestamp"] = str(results["timestamp"])

        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"\nValidation report saved to: {report_path}")
        return report_path


def generate_sample_metadata():
    """Generate sample metadata file for testing."""
    base_dir = Path(__file__).parent
    sample_metadata = {
        "doc_id": "OECD-DAC-2023-001",
        "filename": "OECD-DAC-PEER-Germany-2023.pdf",
        "file_path": str(base_dir / "peer-reviews" / "OECD-DAC-PEER-Germany-2023.pdf"),
        "file_size": 2847392,
        "document_series": "OECD Development Co-operation Peer Reviews",
        "document_type": "peer-review",
        "title": "Development Co-operation Review: Germany 2023",
        "subtitle": "Strengthening Climate and Governance Impact",
        "publication_year": 2023,
        "language": "en",
        "url": "https://www.oecd-ilibrary.org/development/development-co-operation-review-germany-2023_...",
        "donor_country": "Germany",
        "subject_area": "Development Cooperation",
        "isbn": "978-92-64-XXXXX-X",
        "doi": "10.1787/XXXXX",
        "sdg_focus": ["SDG_13", "SDG_16", "SDG_17"],
        "primary_theme": "Climate Finance and Governance",
        "page_count": 285,
        "word_count": 95000,
        "executive_summary": "This peer review of Germany's development cooperation examines...",
        "keywords": ["Climate Finance", "Governance", "Partnerships", "SDG Implementation"],
        "extraction_quality": 0.95,
        "has_toc": True,
        "has_index": True,
        "text_extraction_method": "pdfplumber",
        "license": "OECD Attribution License",
        "access_status": "open-access",
        "extraction_timestamp": datetime.now().isoformat(),
        "processing_notes": "Sample metadata for validation testing"
    }

    return sample_metadata


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="OECD DAC Acquisition Validation & Testing Suite"
    )
    parser.add_argument(
        '--generate-samples',
        action='store_true',
        help='Generate sample metadata for testing'
    )

    args = parser.parse_args()

    if args.generate_samples:
        logger.info("Generating sample metadata...")
        sample = generate_sample_metadata()
        print("\nSample Metadata:")
        print(json.dumps(sample, indent=2))
        return

    # Run validation suite
    suite = ValidationSuite()
    results = suite.run_full_validation()
    suite.save_validation_report()


if __name__ == '__main__':
    main()
