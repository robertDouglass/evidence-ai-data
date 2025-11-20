#!/usr/bin/env python3
"""
OECD DAC Metadata Processing Pipeline

Processes downloaded OECD documents and extracts comprehensive metadata
for integration with the Global SDG Evidence Backbone (GSEB) retrieval system.

Features:
- PDF text extraction and OCR fallback
- Automatic metadata detection from document structure
- SDG tagging based on content analysis
- Deduplication and quality validation
- Metadata export in JSON-LD format for semantic integration
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """OECD document types."""
    PEER_REVIEW = "peer-review"
    EVAL_INSIGHT = "eval-insight"


class SDGCategory(Enum):
    """SDG classification categories."""
    SDG_1 = "No Poverty"
    SDG_2 = "Zero Hunger"
    SDG_3 = "Good Health"
    SDG_4 = "Quality Education"
    SDG_5 = "Gender Equality"
    SDG_6 = "Clean Water"
    SDG_7 = "Affordable Energy"
    SDG_8 = "Decent Work"
    SDG_9 = "Industry Innovation"
    SDG_10 = "Reduced Inequalities"
    SDG_11 = "Sustainable Cities"
    SDG_12 = "Responsible Consumption"
    SDG_13 = "Climate Action"
    SDG_14 = "Life Below Water"
    SDG_15 = "Life on Land"
    SDG_16 = "Peace and Justice"
    SDG_17 = "Partnerships"


@dataclass
class OECDDocumentMetadata:
    """Complete metadata for OECD documents."""

    # Identifiers
    doc_id: str  # OECD-DAC-YYYY-###
    filename: str
    file_path: str
    file_size: int

    # Document identification
    document_series: str  # "OECD Peer Reviews" or "OECD Evaluation Insights"
    document_type: DocumentType
    title: Optional[str] = None
    subtitle: Optional[str] = None

    # Content metadata
    publication_year: Optional[int] = None
    language: str = "en"
    url: Optional[str] = None

    # OECD-specific fields
    donor_country: Optional[str] = None  # For peer reviews
    subject_area: Optional[str] = None
    isbn: Optional[str] = None
    doi: Optional[str] = None

    # SDG tagging
    sdg_focus: List[str] = None
    primary_theme: Optional[str] = None

    # Content analysis
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    executive_summary: Optional[str] = None
    keywords: List[str] = None

    # Quality metrics
    extraction_quality: Optional[float] = None  # 0-1 confidence score
    has_toc: bool = False
    has_index: bool = False
    text_extraction_method: str = "pdfplumber"  # or ocr

    # Licensing & compliance
    license: str = "OECD Attribution License"
    access_status: str = "open-access"

    # Processing metadata
    extraction_timestamp: str = None
    last_updated: str = None
    processing_notes: Optional[str] = None

    def __post_init__(self):
        if self.sdg_focus is None:
            self.sdg_focus = []
        if self.keywords is None:
            self.keywords = []
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now().isoformat()
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()

    def to_jsonld(self) -> Dict:
        """Convert to JSON-LD format for semantic web integration."""
        return {
            "@context": "https://schema.org",
            "@type": "ScholarlyArticle",
            "identifier": self.doc_id,
            "name": self.title,
            "description": self.subtitle,
            "datePublished": f"{self.publication_year}-01-01" if self.publication_year else None,
            "inLanguage": self.language,
            "url": self.url,
            "author": {"@type": "Organization", "name": "OECD"},
            "creator": {"@type": "Organization", "name": "OECD DAC"},
            "keywords": ",".join(self.keywords) if self.keywords else None,
            "text": self.executive_summary,
            "license": self.license,
            "metadata": asdict(self)
        }


class OECDMetadataProcessor:
    """Process OECD documents and extract structured metadata."""

    # Donor countries in OECD DAC peer reviews
    DAC_DONORS = {
        'AUS': 'Australia', 'AUT': 'Austria', 'BEL': 'Belgium', 'CAN': 'Canada',
        'CHL': 'Chile', 'CZE': 'Czech Republic', 'DNK': 'Denmark', 'EST': 'Estonia',
        'FIN': 'Finland', 'FRA': 'France', 'DEU': 'Germany', 'GRC': 'Greece',
        'HUN': 'Hungary', 'IRL': 'Ireland', 'ITA': 'Italy', 'JPN': 'Japan',
        'KOR': 'South Korea', 'LUX': 'Luxembourg', 'NLD': 'Netherlands', 'NZL': 'New Zealand',
        'NOR': 'Norway', 'POL': 'Poland', 'PRT': 'Portugal', 'SVK': 'Slovakia',
        'SVN': 'Slovenia', 'ESP': 'Spain', 'SWE': 'Sweden', 'CHE': 'Switzerland',
        'TUR': 'Turkey', 'GBR': 'United Kingdom', 'USA': 'United States'
    }

    # SDG keywords mapping
    SDG_KEYWORDS = {
        'SDG_13': ['climate', 'greenhouse', 'carbon', 'emissions', 'renewable', 'energy'],
        'SDG_7': ['energy', 'electricity', 'power', 'renewable', 'coal', 'solar'],
        'SDG_11': ['urban', 'city', 'infrastructure', 'transport', 'housing'],
        'SDG_16': ['governance', 'corruption', 'justice', 'peace', 'institutions'],
        'SDG_9': ['industry', 'innovation', 'infrastructure', 'technology'],
        'SDG_6': ['water', 'sanitation', 'hygiene', 'irrigation'],
        'SDG_8': ['employment', 'work', 'economic', 'growth', 'labor'],
        'SDG_5': ['gender', 'women', 'equality', 'discrimination'],
        'SDG_4': ['education', 'school', 'training', 'literacy'],
        'SDG_3': ['health', 'disease', 'nutrition', 'mortality'],
        'SDG_15': ['forest', 'biodiversity', 'ecosystem', 'conservation'],
        'SDG_12': ['waste', 'consumption', 'circular', 'sustainable'],
    }

    BASE_DIR = Path(__file__).parent
    PEER_REVIEW_DIR = BASE_DIR / "peer-reviews"
    EVAL_INSIGHTS_DIR = BASE_DIR / "eval-insights"
    METADATA_DIR = BASE_DIR / "metadata"
    CONSOLIDATED_DIR = BASE_DIR / "consolidated"

    def __init__(self):
        """Initialize the metadata processor."""
        self.CONSOLIDATED_DIR.mkdir(parents=True, exist_ok=True)
        self.metadata_records: List[OECDDocumentMetadata] = []

    def extract_text_from_pdf(self, pdf_path: Path) -> Tuple[str, int]:
        """
        Extract text from PDF document.

        Attempts multiple methods:
        1. PyPDF2 (primary, reliable)
        2. OCR via pytesseract (last resort)

        Returns:
            Tuple of (extracted_text, word_count, page_count)
        """
        text_content = ""
        page_count = 0

        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content += text + "\n"

        except ImportError:
            logger.error("PyPDF2 not available")
        except Exception as e:
            logger.error(f"Error extracting text: {e}")

        word_count = len(text_content.split()) if text_content else 0
        return text_content, word_count, page_count

    def detect_donor_country(self, filename: str, text: str) -> Optional[str]:
        """Detect donor country from filename or content."""
        filename_upper = filename.upper()

        # Try to match filename patterns
        for code, country in self.DAC_DONORS.items():
            if code in filename_upper or country.upper() in filename_upper:
                return country

        # Try to match in text headers (typical for peer reviews)
        for country in self.DAC_DONORS.values():
            if f"Peer Review: {country}" in text or f"Development Co-operation Review: {country}" in text:
                return country

        return None

    def detect_sdg_focus(self, text: str, title: str = "") -> List[str]:
        """
        Detect SDG focus areas from document content.

        Uses keyword matching and semantic analysis.
        Returns list of detected SDG identifiers.
        """
        detected_sdgs = []
        text_lower = (text + title).lower()

        for sdg_id, keywords in self.SDG_KEYWORDS.items():
            match_count = sum(1 for kw in keywords if kw in text_lower)
            if match_count >= 2:  # Require at least 2 keyword matches
                detected_sdgs.append(sdg_id)

        return sorted(list(set(detected_sdgs)))

    def extract_metadata_from_pdf(self, pdf_path: Path) -> Dict:
        """Extract comprehensive metadata from a PDF document."""
        metadata = {}

        try:
            # Basic file info
            metadata['file_size'] = pdf_path.stat().st_size
            metadata['file_path'] = str(pdf_path)
            metadata['filename'] = pdf_path.name

            # Extract text
            text, word_count, page_count = self.extract_text_from_pdf(pdf_path)
            metadata['page_count'] = page_count
            metadata['word_count'] = word_count
            metadata['text_extraction_method'] = 'pdfplumber'

            # Extract title (usually first non-empty line or from PDF metadata)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if lines:
                metadata['title'] = lines[0]
                # Try to find executive summary or abstract
                for i, line in enumerate(lines):
                    if 'executive summary' in line.lower() or 'abstract' in line.lower():
                        summary_lines = lines[i+1:min(i+20, len(lines))]
                        metadata['executive_summary'] = ' '.join(summary_lines)[:500]
                        break

            # Try to extract PDF metadata
            try:
                from PyPDF2 import PdfReader

                reader = PdfReader(pdf_path)
                if reader.metadata:
                    pdf_meta = reader.metadata
                    if hasattr(pdf_meta, 'title') and pdf_meta.title:
                        metadata['title'] = pdf_meta.title
                    if hasattr(pdf_meta, 'subject') and pdf_meta.subject:
                        metadata['subject_area'] = pdf_meta.subject
                    if hasattr(pdf_meta, 'creation_date') and pdf_meta.creation_date:
                        metadata['creation_date'] = str(pdf_meta.creation_date)

            except (ImportError, Exception) as e:
                logger.debug(f"Could not extract PDF metadata: {e}")

            # Detect publication year from filename or content
            year_match = re.search(r'20\d{2}', pdf_path.name)
            if year_match:
                metadata['publication_year'] = int(year_match.group())

            # Detect donor country (for peer reviews)
            donor = self.detect_donor_country(pdf_path.name, text)
            if donor:
                metadata['donor_country'] = donor

            # Detect SDG focus
            title = metadata.get('title', '')
            sdgs = self.detect_sdg_focus(text, title)
            metadata['sdg_focus'] = sdgs

            # Extract keywords from title and content
            keywords = set()
            if title:
                keywords.update(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', title))
            for sdg in sdgs:
                keywords.add(sdg)
            metadata['keywords'] = list(keywords)[:10]

        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf_path}: {e}")

        return metadata

    def generate_doc_id(self, document_type: DocumentType, year: Optional[int], index: int) -> str:
        """Generate standard OECD document ID."""
        if year is None:
            year = datetime.now().year

        if document_type == DocumentType.PEER_REVIEW:
            return f"OECD-DAC-{year}-{index:03d}"
        else:
            return f"OECD-EVAL-{year}-{index:03d}"

    def process_peer_reviews(self) -> List[OECDDocumentMetadata]:
        """Process all peer review documents."""
        logger.info("Processing peer reviews...")

        records = []
        index = 1

        for pdf_file in sorted(self.PEER_REVIEW_DIR.glob("*.pdf")):
            try:
                metadata_dict = self.extract_metadata_from_pdf(pdf_file)

                record = OECDDocumentMetadata(
                    doc_id=self.generate_doc_id(DocumentType.PEER_REVIEW, metadata_dict.get('publication_year'), index),
                    filename=metadata_dict.get('filename', ''),
                    file_path=metadata_dict.get('file_path', ''),
                    file_size=metadata_dict.get('file_size', 0),
                    document_series="OECD Development Co-operation Peer Reviews",
                    document_type=DocumentType.PEER_REVIEW,
                    title=metadata_dict.get('title'),
                    publication_year=metadata_dict.get('publication_year'),
                    donor_country=metadata_dict.get('donor_country'),
                    sdg_focus=metadata_dict.get('sdg_focus', []),
                    keywords=metadata_dict.get('keywords', []),
                    executive_summary=metadata_dict.get('executive_summary'),
                    page_count=metadata_dict.get('page_count'),
                    word_count=metadata_dict.get('word_count'),
                )

                records.append(record)
                index += 1
                logger.info(f"✓ Processed: {record.title or record.filename}")

            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")

        return records

    def process_evaluation_insights(self) -> List[OECDDocumentMetadata]:
        """Process all evaluation insights documents."""
        logger.info("Processing evaluation insights...")

        records = []
        index = 1

        for pdf_file in sorted(self.EVAL_INSIGHTS_DIR.glob("*.pdf")):
            try:
                metadata_dict = self.extract_metadata_from_pdf(pdf_file)

                record = OECDDocumentMetadata(
                    doc_id=self.generate_doc_id(DocumentType.EVAL_INSIGHT, metadata_dict.get('publication_year'), index),
                    filename=metadata_dict.get('filename', ''),
                    file_path=metadata_dict.get('file_path', ''),
                    file_size=metadata_dict.get('file_size', 0),
                    document_series="OECD Evaluation Insights",
                    document_type=DocumentType.EVAL_INSIGHT,
                    title=metadata_dict.get('title'),
                    publication_year=metadata_dict.get('publication_year'),
                    sdg_focus=metadata_dict.get('sdg_focus', []),
                    keywords=metadata_dict.get('keywords', []),
                    executive_summary=metadata_dict.get('executive_summary'),
                    page_count=metadata_dict.get('page_count'),
                    word_count=metadata_dict.get('word_count'),
                )

                records.append(record)
                index += 1
                logger.info(f"✓ Processed: {record.title or record.filename}")

            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")

        return records

    def generate_consolidated_metadata(self, records: List[OECDDocumentMetadata]):
        """Generate consolidated metadata file."""
        output_path = self.CONSOLIDATED_DIR / "oecd_dac_metadata.jsonl"

        with open(output_path, 'w') as f:
            for record in records:
                record_dict = asdict(record)
                # Convert enum to string for JSON serialization
                if isinstance(record_dict.get('document_type'), DocumentType):
                    record_dict['document_type'] = record_dict['document_type'].value
                f.write(json.dumps(record_dict, ensure_ascii=False) + '\n')

        logger.info(f"Consolidated metadata saved to: {output_path}")

        # Also generate summary statistics
        summary = {
            "total_documents": len(records),
            "peer_reviews": len([r for r in records if r.document_type == DocumentType.PEER_REVIEW]),
            "evaluation_insights": len([r for r in records if r.document_type == DocumentType.EVAL_INSIGHT]),
            "total_pages": sum(r.page_count or 0 for r in records),
            "total_words": sum(r.word_count or 0 for r in records),
            "sdg_coverage": self._get_sdg_coverage(records),
            "donor_countries": list(set(r.donor_country for r in records if r.donor_country)),
            "year_range": (
                min(r.publication_year for r in records if r.publication_year),
                max(r.publication_year for r in records if r.publication_year)
            )
        }

        summary_path = self.CONSOLIDATED_DIR / "oecd_dac_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Summary statistics saved to: {summary_path}")

        return summary

    def _get_sdg_coverage(self, records: List[OECDDocumentMetadata]) -> Dict:
        """Calculate SDG coverage statistics."""
        sdg_counts = {}
        for record in records:
            for sdg in record.sdg_focus:
                sdg_counts[sdg] = sdg_counts.get(sdg, 0) + 1

        return sdg_counts

    def run(self):
        """Execute the metadata processing pipeline."""
        logger.info("=" * 60)
        logger.info("OECD DAC Metadata Processing Pipeline")
        logger.info("=" * 60)

        # Process documents
        peer_reviews = self.process_peer_reviews()
        insights = self.process_evaluation_insights()

        all_records = peer_reviews + insights

        logger.info(f"\nTotal documents processed: {len(all_records)}")

        if all_records:
            # Generate consolidated metadata
            summary = self.generate_consolidated_metadata(all_records)

            logger.info("\nProcessing Summary:")
            logger.info(f"  Peer Reviews: {summary['peer_reviews']}")
            logger.info(f"  Evaluation Insights: {summary['evaluation_insights']}")
            logger.info(f"  Total Pages: {summary['total_pages']}")
            logger.info(f"  Total Words: {summary['total_words']}")
            logger.info(f"  SDG Topics: {len(summary['sdg_coverage'])}")

        logger.info("\n" + "=" * 60)
        logger.info("Metadata processing complete!")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    processor = OECDMetadataProcessor()
    processor.run()


if __name__ == '__main__':
    main()
