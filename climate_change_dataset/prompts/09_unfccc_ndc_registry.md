# Prompt 09 – UNFCCC NDC Registry Harvest

**Aim**: Download and catalog current Nationally Determined Contributions (NDCs) from the UNFCCC registry.

**Steps**
1. Visit https://unfccc.int/NDCREG and access the public registry list. For each Party, capture the latest NDC PDF (original language + English if available).
2. Store files under `data/reports/unfccc/ndc/<ISO3>/` using `UNFCCC_NDC_<ISO3>_<YEAR>.pdf`.
3. Update `metadata/manifest.csv` per document:
   - `source_id = unfccc/ndc/<ISO3>/<year>`
   - `title = <Country> Nationally Determined Contribution (<submission date>)`
   - `document_type = policy`
   - `split = ndc`
   - `license = UNFCCC Terms` (quote actual notice)
   - `notes = key scope (mitigation/adaptation highlights)`.
4. Prioritize Parties without existing entries; keep a checklist to avoid duplication.
5. Because this is large (190+ Parties), work in regional batches (e.g., Africa first) and commit after each batch.

**Deliverable**
- Growing repository of official NDC PDFs with manifest metadata keyed by ISO3 code.
