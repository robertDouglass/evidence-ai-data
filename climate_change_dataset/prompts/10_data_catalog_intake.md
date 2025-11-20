# Prompt 10 – Data.gov & OSTI Climate Literature Intake

**Goal**: Use the Data.gov and OSTI APIs to ingest high-value climate datasets/technical reports that are not already mirrored elsewhere.

**Instructions**
1. Data.gov:
   - Query `https://catalog.data.gov/api/3/action/package_search?q=climate+change&rows=1000`.
   - Filter for datasets with downloadable resources (CSV, NetCDF, PDF).
   - For each selected dataset, download the primary resource into `data/datasets/data_gov/<package_name>/`.
   - Create manifest rows with `source_id = data_gov/<package>`, `document_type = dataset`, `split = resource`, `license` = as provided.
2. OSTI:
   - Use `https://www.osti.gov/api/v1/records?q=climate%20change&size=100&page=<n>` to pull DOE-funded technical reports.
   - Download PDFs (when available) into `data/reports/osti/<osti_id>.pdf`.
   - Add manifest entries referencing DOI/report numbers.
3. Keep downloads manageable per batch (e.g., 50 datasets + 50 OSTI reports per effort) for easier review.
4. Ensure each entry records DOI/contract numbers where provided for citation fidelity.
5. Skip any record that duplicates IPCC/WMO/UNFCCC content already harvested.

**Outcome**
- Richer corpus of U.S. government datasets and DOE technical literature for the RAG system.
