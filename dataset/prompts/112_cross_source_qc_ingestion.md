# 112 – Cross-Source QA, Deduplication & Benchmark Prep

**Goal:** As documents start flowing (targets 101–111), ensure harmonized metadata, deduplicate overlaps, and prep benchmark queries for RAG evaluation.

## Tasks
1. **Schema harmonization**: define a shared metadata schema (`data/raw/metadata_schema.yaml`) covering common fields (`doc_id`, `source`, `document_type`, `language`, `publication_year`, `sdg_tags`, `country_region`, `pii_flag`, `file_path`, `license`). Update per-source pipelines to conform.
2. **Deduping service**: build a script that scans `data/raw/*/documents` to detect duplicates via SHA256 + fuzzy title matching. Write results to `data/raw/shared/logs/dedup_report.json` and mark duplicates in metadata.
3. **Benchmark dataset tracker**: create `data/raw/shared/benchmark_counts.csv` summarizing counts per source/SDG/topic, refreshed daily.
4. **PII escalation**: provide a queue file (`data/raw/shared/pii_review.csv`) listing doc_ids flagged for manual redaction.
5. **Benchmark prompts**: document at least 10 ready-to-run RAG benchmark questions (aligned with `dataset_strategy.md`) in `data/raw/shared/benchmark_questions.md`, referencing actual collected doc_ids to prove coverage.

## Success Indicators
- Metadata schema published + referenced by ≥3 source teams
- Dedup report identifies overlaps (e.g., BMZ vs GIZ vs UNDP republished docs)
- Benchmark question file references doc_ids that already exist locally
