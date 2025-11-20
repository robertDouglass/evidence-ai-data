# Acquisition Sprint Prompts (Phase 2)

These prompts reset the acquisition effort with an emphasis on **real document collection** (no mock data) and aligned storage under `data/raw/<source>/`. Each brief references the key blockers identified in the initial review (pagination gaps, promotional PDFs, mock APIs) and provides concrete next steps so agents can immediately ingest thousands of SDG-relevant documents for BMZ, GIZ, KfW, DEval, PTB, BGR, IKI, UNDP, UN SDG, OECD, and World Bank/GFDRR sources.

## Git LFS Requirement
Large binary artefacts (PDF, DOCX, ZIP, etc.) inside `data/raw/` **must** be tracked using Git LFS. Inside your web-dev container run:

```bash
sudo apt-get update && sudo apt-get install -y git-lfs   # Debian/Ubuntu images
git lfs install                                          # run once per container
```

`.gitattributes` already covers `data/raw/**`. Before committing, run `git lfs status` to confirm new binaries are queued for LFS and extend the attributes file if you introduce additional binary types.

**Numbering scheme:**
- `101–103`: German core agencies (BMZ, GIZ, KfW)
- `104–106`: Specialized German institutes (DEval, PTB, BGR)
- `107–111`: Global comparators (IKI, UNDP, UN SDG, OECD, World Bank/GFDRR)
- `112`: Cross-source QA & ingestion alignment

Follow the directory guidance in `data/README.md` and cite any deviations in your execution report.
