# 105 – PTB Quality Infrastructure (QI) Corpus Build

**Goal:** Use the PTB QI tooling to ingest ≥300 PTB/QI4SD publications (metrology, standards, accreditation, conformity) into `data/raw/ptb/` with clean metadata.

## Actions
1. **Scrape PTB publications table** and QI4SD resource library (authenticated) for 2014-2024 entries; queue only PTB-authored outputs.
2. **Download PDFs** into `data/raw/ptb/documents/<qi_component>/<year>/` (component ∈ {metrology, standards, accreditation, conformity_assessment}).
3. **Metadata export** via CLI to `data/raw/ptb/metadata/ptb_qi_metadata.jsonl` + `ptb_qi_manifest.json` capturing geography, SDGs, license.
4. **QA report**: run `ptb_qi_cli.py quality-check` and store the JSON + textual summary in `data/raw/ptb/logs/`.
5. **GDPR check**: flag any documents with explicit person names/emails.

## Completion Criteria
- ≥300 unique PDFs downloaded and listed
- Manifest includes component + geography for every doc
- Report notes any ISO/IEC items skipped for licensing reasons
