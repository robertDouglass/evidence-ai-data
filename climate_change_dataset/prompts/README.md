# Climate Evidence Harvest Prompts

Each prompt in this folder is a self-contained set of instructions for another agent (or human teammate) to ingest a specific slice of high-value climate science/government material. The structure enables parallel execution: assign one prompt per agent, merge their downloaded files under `data/reports/` (or the referenced directory), and append metadata rows to `metadata/manifest.csv`.

**Common requirements**

- Store PDFs or datasets inside the provided `data/...` path, using descriptive filenames (e.g., `IPCC_AR6_WGI_CH01_...pdf`).
- Do not overwrite existing files; check `metadata/manifest.csv` before downloading.
- Capture provenance (source URL, publication title, year, issuing body, license/terms).
- Update `metadata/manifest.csv` with SHA256 hashes, byte sizes, and citation notes immediately after downloading.
- If a prompt spans many documents, commit partial progress frequently to keep diffs manageable.

Assign as many prompts as needed simultaneously to accelerate the build-out toward (and beyond) the 1,000-document target. Additional prompts can be added following the same pattern if new repositories are identified.
