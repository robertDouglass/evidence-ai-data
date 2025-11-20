#!/usr/bin/env python3
"""
Batch operations for KfW evaluation dataset processing

Provides utilities for:
- Bulk metadata updates
- Duplicate detection
- Data export in various formats
- Validation and cleanup
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
import csv

logger = logging.getLogger(__name__)


class BatchMetadataProcessor:
    """Process metadata in batches"""

    def __init__(self, metadata_file: Path):
        """Initialize batch processor"""
        self.metadata_file = metadata_file
        self.records = []
        self.load()

    def load(self):
        """Load metadata from JSONL file"""
        if not self.metadata_file.exists():
            logger.warning(f"Metadata file not found: {self.metadata_file}")
            return

        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        self.records.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing line {line_num}: {e}")

        logger.info(f"Loaded {len(self.records)} records")

    def detect_duplicates(self) -> Dict[str, List[Dict]]:
        """Detect duplicate records"""
        duplicates = {}

        # Check for duplicate URLs
        url_map = {}
        for record in self.records:
            url = record.get('url')
            if url:
                if url not in url_map:
                    url_map[url] = []
                url_map[url].append(record)

        for url, records in url_map.items():
            if len(records) > 1:
                duplicates[url] = records

        logger.info(f"Found {len(duplicates)} duplicate URLs")
        return duplicates

    def remove_duplicates(self) -> int:
        """Remove duplicate records, keeping first occurrence"""
        seen_urls = set()
        unique_records = []
        removed_count = 0

        for record in self.records:
            url = record.get('url')
            if url not in seen_urls:
                unique_records.append(record)
                seen_urls.add(url)
            else:
                removed_count += 1
                logger.debug(f"Removing duplicate: {url}")

        self.records = unique_records
        logger.info(f"Removed {removed_count} duplicate records")
        return removed_count

    def update_field(self, field: str, value: any, filter_field: str = None, filter_value: any = None):
        """Update a field across records"""
        updated_count = 0

        for record in self.records:
            if filter_field and filter_value:
                if record.get(filter_field) != filter_value:
                    continue

            record[field] = value
            updated_count += 1

        logger.info(f"Updated {updated_count} records")
        return updated_count

    def batch_add_sdg_tags(self, sector_sdg_mapping: Dict[str, List[str]]):
        """Add SDG tags based on sector"""
        updated_count = 0

        for record in self.records:
            if 'sdg_tags' in record and record['sdg_tags']:
                continue  # Skip if already has tags

            sector = record.get('sector', '').lower()
            tags = set()

            for key, sdgs in sector_sdg_mapping.items():
                if key in sector:
                    tags.update(sdgs)

            if tags:
                record['sdg_tags'] = sorted(list(tags))
                updated_count += 1

        logger.info(f"Added SDG tags to {updated_count} records")
        return updated_count

    def validate_metadata(self) -> Dict[str, List[str]]:
        """Validate metadata quality"""
        issues = {
            'missing_doc_id': [],
            'missing_project_name': [],
            'missing_url': [],
            'missing_sdg_tags': [],
            'invalid_year': [],
        }

        for record in self.records:
            doc_id = record.get('doc_id')

            if not doc_id:
                issues['missing_doc_id'].append(record.get('url', 'Unknown'))

            if not record.get('project_name'):
                issues['missing_project_name'].append(doc_id or 'Unknown')

            if not record.get('url'):
                issues['missing_url'].append(doc_id or 'Unknown')

            if not record.get('sdg_tags'):
                issues['missing_sdg_tags'].append(doc_id or 'Unknown')

            year = record.get('publication_year')
            if year and (year < 2013 or year > 2024):
                issues['invalid_year'].append(f"{doc_id}: {year}")

        # Log summary
        for issue_type, records in issues.items():
            if records:
                logger.warning(f"{issue_type}: {len(records)} records")

        return issues

    def export_to_csv(self, output_file: Path):
        """Export records to CSV"""
        if not self.records:
            logger.warning("No records to export")
            return

        try:
            fieldnames = list(self.records[0].keys())
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.records)

            logger.info(f"Exported {len(self.records)} records to {output_file}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")

    def export_to_json(self, output_file: Path):
        """Export records to JSON"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)

            logger.info(f"Exported {len(self.records)} records to {output_file}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")

    def save(self):
        """Save processed records back to JSONL"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                for record in self.records:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')

            logger.info(f"Saved {len(self.records)} records")
        except Exception as e:
            logger.error(f"Error saving records: {e}")


class DatasetSummaryGenerator:
    """Generate summary statistics about the dataset"""

    def __init__(self, metadata_file: Path):
        """Initialize summary generator"""
        self.metadata_file = metadata_file
        self.records = []
        self.load()

    def load(self):
        """Load metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            self.records.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

    def generate_summary(self) -> Dict:
        """Generate dataset summary"""
        summary = {
            'dataset_overview': {
                'total_documents': len(self.records),
                'date_generated': Path(self.metadata_file).stat().st_mtime,
            },
            'year_distribution': self._year_distribution(),
            'sector_distribution': self._sector_distribution(),
            'regional_distribution': self._region_distribution(),
            'sdg_coverage': self._sdg_coverage(),
            'language_distribution': self._language_distribution(),
            'financing_summary': self._financing_summary(),
        }

        return summary

    def _year_distribution(self) -> Dict:
        """Get distribution by year"""
        distribution = {}
        for record in self.records:
            year = record.get('publication_year')
            if year:
                distribution[year] = distribution.get(year, 0) + 1

        return dict(sorted(distribution.items()))

    def _sector_distribution(self) -> Dict:
        """Get distribution by sector"""
        distribution = {}
        for record in self.records:
            sector = record.get('sector', 'Unknown')
            distribution[sector] = distribution.get(sector, 0) + 1

        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))

    def _region_distribution(self) -> Dict:
        """Get distribution by region"""
        distribution = {}
        for record in self.records:
            region = record.get('region', 'Unknown')
            distribution[region] = distribution.get(region, 0) + 1

        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))

    def _sdg_coverage(self) -> Dict:
        """Get SDG coverage"""
        coverage = {}
        for record in self.records:
            sdgs = record.get('sdg_tags', [])
            for sdg in sdgs:
                coverage[sdg] = coverage.get(sdg, 0) + 1

        # Sort by SDG number
        return dict(sorted(coverage.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0))

    def _language_distribution(self) -> Dict:
        """Get distribution by language"""
        distribution = {}
        for record in self.records:
            language = record.get('language', 'Unknown')
            distribution[language] = distribution.get(language, 0) + 1

        return dict(sorted(distribution.items()))

    def _financing_summary(self) -> Dict:
        """Get financing statistics"""
        volumes = [r.get('financing_volume_eur', 0) for r in self.records if r.get('financing_volume_eur')]

        if not volumes:
            return {
                'documents_with_volume': 0,
                'total_volume_eur': 0,
                'average_volume_eur': 0,
                'min_volume_eur': 0,
                'max_volume_eur': 0,
            }

        volumes.sort()
        return {
            'documents_with_volume': len(volumes),
            'total_volume_eur': sum(volumes),
            'average_volume_eur': sum(volumes) / len(volumes),
            'median_volume_eur': volumes[len(volumes) // 2],
            'min_volume_eur': volumes[0],
            'max_volume_eur': volumes[-1],
        }

    def save_summary(self, output_file: Path):
        """Save summary to file"""
        summary = self.generate_summary()
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            logger.info(f"Summary saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving summary: {e}")

    def print_summary(self):
        """Print summary to console"""
        summary = self.generate_summary()
        print("\n" + "="*70)
        print("KFW EVALUATION DATASET SUMMARY")
        print("="*70)

        overview = summary['dataset_overview']
        print(f"\nDataset Overview:")
        print(f"  Total Documents: {overview['total_documents']}")

        if summary['year_distribution']:
            years = summary['year_distribution']
            print(f"\nYear Distribution:")
            for year in sorted(years.keys()):
                print(f"  {year}: {years[year]} documents")

        if summary['sector_distribution']:
            print(f"\nTop Sectors:")
            for i, (sector, count) in enumerate(list(summary['sector_distribution'].items())[:10], 1):
                print(f"  {i}. {sector}: {count} documents")

        if summary['regional_distribution']:
            print(f"\nRegional Distribution:")
            for region, count in summary['regional_distribution'].items():
                print(f"  {region}: {count} documents")

        if summary['sdg_coverage']:
            print(f"\nSDG Coverage:")
            for sdg, count in summary['sdg_coverage'].items():
                print(f"  SDG {sdg}: {count} documents")

        if summary['financing_summary'].get('total_volume_eur'):
            fin = summary['financing_summary']
            print(f"\nFinancing Summary:")
            print(f"  Total Volume: €{fin['total_volume_eur']:,.0f}M")
            print(f"  Average Volume: €{fin['average_volume_eur']:,.0f}M")
            print(f"  Range: €{fin['min_volume_eur']:,.0f}M - €{fin['max_volume_eur']:,.0f}M")

        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    metadata_file = Path("/home/user/evidence-ai/dataset/kfw/metadata.jsonl")

    # Process metadata
    processor = BatchMetadataProcessor(metadata_file)
    processor.remove_duplicates()
    processor.save()

    # Generate summary
    summarizer = DatasetSummaryGenerator(metadata_file)
    summarizer.print_summary()
    summarizer.save_summary(metadata_file.parent / "dataset_summary.json")
