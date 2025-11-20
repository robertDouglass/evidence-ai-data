# 108 – UNDP Evaluation Resource Centre (Live API Pull)

**Goal:** Replace the mock/demo ingestion with a real ERC API pipeline that harvests ≥500 evaluations + management responses across all BMZ priority regions into `data/raw/undp/`.

## Must-Do Items
1. **API integration**: Use the official ERC endpoints (`https://erc.undp.org/api/documents`) with pagination (`page`, `per_page`) and filters (`type=evaluation`, `from=2013`, `to=2024`). Coordinate with UNDP ERC support to obtain an API key/session token (anonymous access is blocked), and keep requests under 200 per page to avoid rate limiting.
2. **Download PDFs**: store under `data/raw/undp/documents/<region>/<year>/<doc_id>.pdf`; include management responses when available.
3. **Metadata**: produce `data/raw/undp/metadata/undp_erc_metadata.jsonl` and CSV containing doc_id, evaluation_type, SDG tags, region, page_count, implementing partners.
4. **Logging**: replace the demo log with real execution logs in `data/raw/undp/logs/` (`undp_erc_crawl.log`, `undp_erc_stats.json`).
5. **Verification**: provide `data/raw/undp/logs/undp_execution_summary.md` summarizing totals, failure URLs, and any licensing anomalies.

## Acceptance Criteria
- ≥500 documents downloaded this pass
- Metadata fields `country`, `sdg_tags`, `publication_year` filled for ≥95%
- Demonstrated handling of timeouts + retries
