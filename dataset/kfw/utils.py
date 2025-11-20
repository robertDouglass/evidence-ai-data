#!/usr/bin/env python3
"""
Utility functions for KfW evaluation acquisition and processing
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class MetadataManager:
    """Manages metadata extraction and validation"""

    def __init__(self, metadata_file: Path):
        """Initialize metadata manager"""
        self.metadata_file = metadata_file
        self.records = []
        self.load()

    def load(self):
        """Load existing metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            self.records.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse metadata line: {e}")

    def add_record(self, record: Dict) -> bool:
        """Add a metadata record"""
        try:
            # Validate required fields
            required_fields = ['doc_id', 'url', 'publication_year']
            if not all(field in record for field in required_fields):
                logger.error(f"Missing required fields in record: {record}")
                return False

            self.records.append(record)
            return True
        except Exception as e:
            logger.error(f"Error adding record: {e}")
            return False

    def save(self):
        """Save metadata to JSONL file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                for record in self.records:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            logger.info(f"Saved {len(self.records)} metadata records")
            return True
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return False

    def get_by_doc_id(self, doc_id: str) -> Optional[Dict]:
        """Retrieve record by document ID"""
        for record in self.records:
            if record.get('doc_id') == doc_id:
                return record
        return None

    def get_by_year(self, year: int) -> List[Dict]:
        """Retrieve all records for a given year"""
        return [r for r in self.records if r.get('publication_year') == year]

    def get_by_sector(self, sector: str) -> List[Dict]:
        """Retrieve all records for a given sector"""
        sector_lower = sector.lower()
        return [r for r in self.records if sector_lower in r.get('sector', '').lower()]

    def get_by_region(self, region: str) -> List[Dict]:
        """Retrieve all records for a given region"""
        region_lower = region.lower()
        return [r for r in self.records if region_lower in r.get('region', '').lower()]

    def get_by_sdg(self, sdg: str) -> List[Dict]:
        """Retrieve all records tagged with a specific SDG"""
        return [r for r in self.records if sdg in r.get('sdg_tags', [])]

    def get_statistics(self) -> Dict:
        """Generate statistics about the dataset"""
        stats = {
            'total_records': len(self.records),
            'years': sorted(set(r.get('publication_year') for r in self.records if 'publication_year' in r)),
            'sectors': sorted(set(r.get('sector') for r in self.records if 'sector' in r)),
            'regions': sorted(set(r.get('region') for r in self.records if 'region' in r)),
            'languages': sorted(set(r.get('language') for r in self.records if 'language' in r)),
            'total_size_bytes': sum(r.get('file_size_bytes', 0) for r in self.records),
        }

        # SDG coverage
        all_sdgs = set()
        for record in self.records:
            all_sdgs.update(record.get('sdg_tags', []))
        stats['sdg_coverage'] = sorted(list(all_sdgs))

        # Regional breakdown
        regional_breakdown = {}
        for record in self.records:
            region = record.get('region', 'Unknown')
            regional_breakdown[region] = regional_breakdown.get(region, 0) + 1
        stats['regional_breakdown'] = regional_breakdown

        # Sector breakdown
        sector_breakdown = {}
        for record in self.records:
            sector = record.get('sector', 'Unknown')
            sector_breakdown[sector] = sector_breakdown.get(sector, 0) + 1
        stats['sector_breakdown'] = sector_breakdown

        return stats


class FileValidator:
    """Validates downloaded files"""

    def __init__(self, min_size_bytes: int = 5000):
        """Initialize file validator"""
        self.min_size_bytes = min_size_bytes

    def validate_pdf(self, file_path: Path) -> Tuple[bool, str]:
        """Validate PDF file"""
        try:
            if not file_path.exists():
                return False, "File does not exist"

            file_size = file_path.stat().st_size
            if file_size < self.min_size_bytes:
                return False, f"File too small ({file_size} bytes)"

            # Check PDF signature
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return False, "Invalid PDF header"

            return True, "Valid PDF"

        except Exception as e:
            return False, f"Validation error: {e}"

    def calculate_checksum(self, file_path: Path) -> Optional[str]:
        """Calculate SHA256 checksum of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return None


class DocumentOrganizer:
    """Organizes downloaded documents into directory structure"""

    def __init__(self, base_dir: Path):
        """Initialize organizer"""
        self.base_dir = base_dir

    def organize_by_year(self, file_path: Path, year: int) -> Path:
        """Organize document by year"""
        year_dir = self.base_dir / "evaluations" / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        return year_dir / file_path.name

    def organize_by_sector(self, file_path: Path, sector: str) -> Path:
        """Organize document by sector"""
        sector_dir = self.base_dir / "by-sector" / sector
        sector_dir.mkdir(parents=True, exist_ok=True)
        return sector_dir / file_path.name

    def organize_by_region(self, file_path: Path, region: str) -> Path:
        """Organize document by region"""
        region_dir = self.base_dir / "by-region" / region
        region_dir.mkdir(parents=True, exist_ok=True)
        return region_dir / file_path.name

    def organize_annual_reports(self, file_path: Path, year: int) -> Path:
        """Organize annual report"""
        report_dir = self.base_dir / "annual-report" / str(year)
        report_dir.mkdir(parents=True, exist_ok=True)
        return report_dir / file_path.name


class DataQualityReporter:
    """Generates data quality reports"""

    def __init__(self, output_dir: Path):
        """Initialize reporter"""
        self.output_dir = output_dir
        self.report = {}

    def check_coverage(self, metadata_manager: MetadataManager) -> Dict:
        """Check dataset coverage"""
        stats = metadata_manager.get_statistics()

        coverage = {
            'total_documents': stats['total_records'],
            'years_covered': len(stats['years']),
            'year_range': f"{min(stats['years']) if stats['years'] else 'N/A'} - {max(stats['years']) if stats['years'] else 'N/A'}",
            'sectors_covered': len(stats['sectors']),
            'regions_covered': len(stats['regions']),
            'languages_covered': stats['languages'],
            'target_sdgs_found': len(set(stats['sdg_coverage']).intersection({'7', '8', '9', '11', '13'})),
            'storage_size_gb': stats['total_size_bytes'] / (1024**3),
        }

        return coverage

    def check_completeness(self, metadata_manager: MetadataManager) -> Dict:
        """Check dataset completeness"""
        missing_fields = {
            'missing_project_name': 0,
            'missing_region': 0,
            'missing_sector': 0,
            'missing_sdg_tags': 0,
            'missing_financing_volume': 0,
        }

        for record in metadata_manager.records:
            if not record.get('project_name'):
                missing_fields['missing_project_name'] += 1
            if not record.get('region'):
                missing_fields['missing_region'] += 1
            if not record.get('sector'):
                missing_fields['missing_sector'] += 1
            if not record.get('sdg_tags'):
                missing_fields['missing_sdg_tags'] += 1
            if not record.get('financing_volume_eur'):
                missing_fields['missing_financing_volume'] += 1

        total = len(metadata_manager.records)
        completeness = {
            'total_records': total,
            'missing_fields': missing_fields,
            'completeness_percentage': {
                k: 100 * (total - v) / total if total > 0 else 0
                for k, v in missing_fields.items()
            }
        }

        return completeness

    def generate_report(self, metadata_manager: MetadataManager) -> Dict:
        """Generate comprehensive quality report"""
        self.report = {
            'generated_at': datetime.now().isoformat(),
            'coverage': self.check_coverage(metadata_manager),
            'completeness': self.check_completeness(metadata_manager),
            'statistics': metadata_manager.get_statistics(),
        }

        # Save report
        report_file = self.output_dir / "quality_report_detailed.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)

        logger.info(f"Quality report saved to {report_file}")
        return self.report

    def print_summary(self):
        """Print quality report summary"""
        if not self.report:
            logger.warning("No report generated yet")
            return

        coverage = self.report.get('coverage', {})
        print("\n" + "="*60)
        print("KfW EVALUATION DATASET - QUALITY REPORT")
        print("="*60)
        print(f"\nCoverage:")
        print(f"  Total Documents: {coverage.get('total_documents', 0)}")
        print(f"  Year Range: {coverage.get('year_range', 'N/A')}")
        print(f"  Sectors: {coverage.get('sectors_covered', 0)}")
        print(f"  Regions: {coverage.get('regions_covered', 0)}")
        print(f"  Languages: {', '.join(coverage.get('languages_covered', []))}")
        print(f"  Storage Size: {coverage.get('storage_size_gb', 0):.2f} GB")
        print(f"  Target SDGs Found: {coverage.get('target_sdgs_found', 0)}/5")
        print("="*60 + "\n")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize metadata manager
    metadata_file = Path("/home/user/evidence-ai/dataset/kfw/metadata.jsonl")
    mm = MetadataManager(metadata_file)

    # Print statistics
    if mm.records:
        stats = mm.get_statistics()
        print(json.dumps(stats, indent=2))
    else:
        print("No metadata records found. Run acquisition_script.py first.")
