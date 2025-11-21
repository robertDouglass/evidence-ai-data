# Unified Ingestion Schema (Document + Page)

Reference for implementing manifests and page exports that feed MinIO → Vespa → OpenSearch.

## Document-Level (metadata_schema.yaml v2)
- Required: `doc_id`, `source`, `title`, `publication_year`, `document_type`, `language`, `local_path`, `file_hash_sha256`
- Core fields: `subtitle`, `original_url`, `file_size_bytes`, `mime_type`, `downloaded_at`, `publication_date`, `timeframe_start`, `timeframe_end`
- Geography: `countries` (ISO2 or names), `regions` (SSA/MENA/APAC/EUR/LAC/NA/Global/Multi), `admin1`
- Taxonomy: `thematic_area` (controlled list), `sector_tags`, `sdg_tags` (SDG1–SDG17), `keywords`
- Language: `language` (ISO 639-1), `alt_languages`
- Org/people: `organisation`, `implementing_partners`, `authors`
- Quality/safety: `license`, `text_extracted`, `extraction_quality`, `pii_flag`, `restricted`, `exclude_from_search`, `quality_checked`
- Counts: `page_count`, `word_count`, `image_count`
- Summaries: `executive_summary`, `abstract`, `notes`
- Relations: `related_ids`, `bilingual_of`
- Processing: `processed_date`, `version`, `pipeline_run_id`

### Controlled Vocabularies
- `document_type`: evaluation | policy_brief | technical_report | research_paper | annual_report | assessment | impact_report | concept_note | synthesis | publication | other
- `thematic_area`: Climate & Energy Resilience | Sustainable Infrastructure & Finance | Governance, Peace & Justice | Natural Resources & Biodiversity | Human Development & Social Protection | Quality Infrastructure & Standards | Other
- `regions`: SSA | MENA | APAC | EUR | LAC | NA | Global | Multi
- `language`: en | de | fr | es | pt | ar | zh | other
- `sdg_tags`: SDG1 .. SDG17 (strings)
- `extraction_quality`: excellent | good | fair | poor | unknown

## Page-Level (for Vespa/OpenSearch)
- ids: `page_id={doc_id}_{page_num:04d}`, `doc_id`, `page_num`
- content: `page_text`, `text_snippet`, optional `chunk_id`, `chunk_index` (if grouping ≤5 pages)
- media: `s3_image_url`, `s3_markdown_url`, `s3_pdf_url`, optional `ocr_confidence`
- embeddings:
  - Vespa: `colpali_embedding` tensor<float>(d_token[1031], dim[128]) (full)
  - OpenSearch: `text_embedding` (384-d MiniLM), `colpali_mean` (128-d)
- filters copied from document: `source`, `organisation`, `document_type`, `regions`, `countries`, `thematic_area`, `sector_tags`, `sdg_tags`, `language`, `publication_year`, `restricted`, `exclude_from_search`, `license`
- audit: `indexed_at`, `file_hash_sha256`

## Mapping Expectations
- Paths: `local_path` must be relative under `data/raw/<source>/documents/...`
- Hash/size: compute from the stored binary before upload to MinIO.
- Regions/countries: normalize to controlled lists; default to `Global` if empty and clearly global.
- SDG tags: use `["SDG13"]` style strings; no integers.
- Restricted handling: set `restricted=true` (and `exclude_from_search=true` if needed) for stubs, corrupted files, or PII.

## Minimal Manifest Record Example
```json
{
  "doc_id": "WB-CLIM-D34442285",
  "source": "World Bank",
  "title": "Loan Agreement for Climate Resilience",
  "publication_year": 2026,
  "document_type": "agreement",
  "language": "en",
  "local_path": "documents/climate/WB-CLIM-D34442285.pdf",
  "file_hash_sha256": "…",
  "file_size_bytes": 985123,
  "mime_type": "application/pdf",
  "original_url": "http://documents.worldbank.org/…",
  "regions": ["Global"],
  "countries": [],
  "sdg_tags": ["SDG13"],
  "thematic_area": "Climate & Energy Resilience",
  "license": "CC-BY-3.0-IGO",
  "page_count": 42,
  "text_extracted": false,
  "restricted": false,
  "processed_date": "2025-11-22T00:00:00Z",
  "version": "2.0",
  "pipeline_run_id": "ingest-test-001"
}
```
