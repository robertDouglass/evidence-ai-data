# Global SDG Evidence Backbone (GSEB) – Demo Corpus Plan

## Vision & Scope
Build a 10,000-document reference corpus that mirrors how BMZ, GIZ, KfW, DEval, PTB, and BGR (plus coordinating ministries BMUV/BMZ) source qualitative evidence for SDG-focused decisions. The corpus should blend German government evaluations with global SDG monitoring sources so that EvidenceAI can answer complex, multi-document questions about climate action, sustainable infrastructure, governance, and quality infrastructure across partner countries.

### Primary Themes
1. **Climate & Energy Resilience (SDGs 7, 11, 13)** – IKI, KfW, World Bank, GFDRR.
2. **Sustainable Infrastructure & Finance (SDGs 8, 9)** – KfW, PTB, OECD DAC.
3. **Governance, Peace & Justice (SDG 16)** – BMZ, GIZ, UNDP, DEval.
4. **Natural Resources & Biodiversity (SDGs 6, 12, 14, 15)** – BGR, IKI, UN SDG.
5. **Human Development & Social Protection (SDGs 1, 2, 3, 4, 5)** – GIZ, DEval, UNDP, BMZ policies.

## Source Coverage
| Agency / Partner | Indicative Sources | Est. Docs | Licensing |
| --- | --- | --- | --- |
| BMZ | Evaluation Portal, Country Concepts, SDG policy briefs | 1,200 | German federal open access |
| GIZ | Central Project Evaluations, thematic syntheses | 1,000 | GIZ reuse permitted |
| KfW | Financial Cooperation evaluations, annual reviews | 900 | © KfW, citation allowed |
| DEval | Evaluations, REAs, policy briefs | 600 | CC BY 4.0 |
| PTB | Quality Infrastructure cooperation docs | 500 | CC BY 4.0 |
| BGR | Georesource governance & geo-risk reports | 650 | German federal open access |
| IKI/BMUV | Project evaluations & impact reports | 800 | CC BY 4.0 |
| UN SDG | GSDR chapters, VNRs | 1,500 | © UN, attribution |
| OECD DAC | Peer reviews, Evaluation Insights | 700 | Open-access OECD titles |
| World Bank/GFDRR | Climate ICRs, adaptation studies | 1,200 | CC BY 3.0 IGO |
| UNDP ERC | Evaluation documents + responses | 1,500 | © UNDP, attribution |
| **Total** |  | **10,550** |  |

## Data Lake Structure
All raw corpora now flow into `data/raw/<source>/` with three mandatory subdirectories:

```
data/raw/<source>/
  documents/   # PDF/DOCX/HTML artefacts grouped by year/topic
  metadata/    # JSONL/CSV/YAML metadata exports
  logs/        # Crawl logs, QA reports, manifests
```

See `data/README.md` for the current source list (`bmz`, `giz`, `kfw`, `deval`, `ptb`, `bgr`, `iki`, `un_sdg`, `undp`, `oecd`, `worldbank`, plus `shared` for cross-cutting QA). Agents must write their outputs to this structure so downstream ingestion, anonymization, and benchmark scripting can operate consistently.

## Benchmark Question Themes
1. **Cross-Agency Climate Finance Impact** – e.g., "Compare lessons on climate-resilient infrastructure from GIZ CPEs in Peru and KfW ICRs in Morocco (2018-2023)."
2. **Quality Infrastructure Outcomes** – "What evidence exists on PTB-supported metrology reforms improving SME competitiveness in ECOWAS states?"
3. **Governance & Rule of Law** – "Summarize BMZ and DEval findings on anti-corruption programming effectiveness in Central America."
4. **Natural Resource Governance** – "How do BGR groundwater studies inform SDG6 monitoring for the Niger Basin?"
5. **Gender & Social Protection** – "Extract SDG5-related recommendations from UNDP and BMZ evaluations in Sahel countries."
6. **Comparative Donor Performance** – "What OECD DAC peer-review critiques align with DEval recommendations on German portfolio management?"
7. **Climate Adaptation Evidence** – "List top lessons from World Bank ICRs and IKI evaluations about nature-based solutions in coastal regions."
8. **Budget Efficiency** – "Using KfW and BMZ evaluations, what cost-effectiveness ratios are reported for off-grid solar programs in East Africa?"
9. **SDG Monitoring** – "Combine UN VNR data and GIZ evaluations to describe progress on SDG16 indicators in fragile states."
10. **Multi-Language Retrieval** – "Provide German-language summaries of DEval REAs on digitalization plus English-language UN SDG insights."

These benchmark questions stress-test multi-document synthesis, multilingual retrieval, SDG tagging, and citation fidelity.

## Licensing & Compliance Notes
- All sources are government or multilateral publications available for public download; most follow CC BY/CC BY IGO. Maintain attribution and preserve copyright statements.
- Screen documents for PII before ingestion; evaluations occasionally mention staff names—use anonymization pipeline flagged in requirements.
- Restrict storage and processing to EU data centers (aligns with Nephele).

## Implementation Order
1. **German Core (BMZ, GIZ, KfW, DEval)** – ensures relevance to six agencies.
2. **Specialized Agencies (PTB, BGR)** – adds niche technical evidence.
3. **Climate & SDG Globals (IKI, UN SDG, World Bank, UNDP, OECD)** – broadens comparative context.
4. **Quality Gates** – deduplication, OCR, metadata enrichment.
5. **Benchmark Question Validation** – run RAG queries per theme, verify citation coverage.

## Phase 2 Sprint Focus
The new prompts in `dataset/prompts/` translate the above plan into concrete actions:
- **101–103**: Execute real crawls for BMZ, GIZ, and KfW (no more mock data) with pagination, SDG tagging, and GDPR flags.
- **104–106**: Backfill DEval archives and populate PTB/BGR corpora with hundreds of technical publications.
- **107–111**: Scale IKI, UNDP ERC, UN SDG, OECD, and World Bank/GFDRR harvesters, each targeting hundreds of documents per run.
- **112**: Harmonize metadata schemas, deduplicate overlaps, and produce benchmark-ready question sets referencing collected doc_ids.

Agents should treat these tasks as the starting point for mass acquisition so the EvidenceAI RAG pilot can demonstrate deep coverage across all six German agencies plus the global SDG ecosystem.

See `./prompts/*.md` for actionable scraping instructions per source.
