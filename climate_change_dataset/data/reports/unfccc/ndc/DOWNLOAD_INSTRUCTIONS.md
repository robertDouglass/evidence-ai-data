# UNFCCC NDC Registry - Manual Download Instructions

The UNFCCC website uses Incapsula bot protection that blocks automated downloads.
These files must be downloaded manually via browser.

## African Countries NDCs (First Batch)

### 2025 NDCs (NDC 3.0)

| Country | ISO3 | URL | Filename |
|---------|------|-----|----------|
| Kenya | KEN | https://unfccc.int/sites/default/files/2025-05/KENYAS%20SECOND%20NATIONALLY%20DETERMINED%20CONTRIBUTION%202031_2035.pdf | UNFCCC_NDC_KEN_2025.pdf |
| Nigeria | NGA | https://unfccc.int/sites/default/files/2025-09/Nigeria%20NDC%203.0%20-%20Transimission%20Version%202.pdf | UNFCCC_NDC_NGA_2025.pdf |
| Ethiopia | ETH | https://unfccc.int/sites/default/files/2025-09/Ethiopia%20NDC%203.0%20Final.pdf | UNFCCC_NDC_ETH_2025.pdf |
| Rwanda | RWA | https://unfccc.int/sites/default/files/2025-11/Rwanda%20NDC3.0.pdf | UNFCCC_NDC_RWA_2025.pdf |
| Somalia | SOM | https://unfccc.int/sites/default/files/2025-06/Somalia%20NDC%203.0_Submitted_to_UNFCCC_Final.pdf | UNFCCC_NDC_SOM_2025.pdf |
| Liberia | LBR | https://unfccc.int/sites/default/files/2025-09/Liberias_2035_NDC_3.0_Final.pdf | UNFCCC_NDC_LBR_2025.pdf |
| Mauritius | MUS | https://unfccc.int/sites/default/files/2025-09/NDC%203.0%20%20Mauritius.pdf | UNFCCC_NDC_MUS_2025.pdf |
| Seychelles | SYC | https://unfccc.int/sites/default/files/2025-09/ICTU%20Update%202025%20for%20Seychelles%20new%20NDC%203.0.pdf | UNFCCC_NDC_SYC_2025.pdf |

### Updated NDCs (2021-2022)

| Country | ISO3 | URL | Filename |
|---------|------|-----|----------|
| South Africa | ZAF | https://unfccc.int/sites/default/files/NDC/2022-06/South%20Africa%20updated%20first%20NDC%20September%202021.pdf | UNFCCC_NDC_ZAF_2021.pdf |
| Egypt | EGY | https://unfccc.int/sites/default/files/NDC/2022-07/Egypt%20Updated%20NDC.pdf.pdf | UNFCCC_NDC_EGY_2022.pdf |
| Ghana | GHA | https://unfccc.int/sites/default/files/NDC/2022-06/Ghana's%20Updated%20Nationally%20Determined%20Contribution%20to%20the%20UNFCCC_2021.pdf | UNFCCC_NDC_GHA_2021.pdf |
| Tanzania | TZA | https://unfccc.int/sites/default/files/NDC/2022-06/The%20United%20Republic%20of%20Tanzania%20First%20NDC.pdf | UNFCCC_NDC_TZA_2016.pdf |
| Morocco | MAR | https://unfccc.int/sites/default/files/NDC/2022-06/Morocco%20First%20NDC-English.pdf | UNFCCC_NDC_MAR_2016.pdf |
| Rwanda (prev) | RWA | https://unfccc.int/sites/default/files/NDC/2022-06/Rwanda_Updated_NDC_May_2020.pdf | UNFCCC_NDC_RWA_2020.pdf |

## Download Instructions

1. Open each URL in a web browser
2. Save the PDF to the corresponding `data/reports/unfccc/ndc/<ISO3>/` directory
3. Use the filename specified in the table above
4. After downloading, run the file hash script to update manifest.csv

## Directory Structure

```
data/reports/unfccc/ndc/
├── KEN/
│   └── UNFCCC_NDC_KEN_2025.pdf
├── ZAF/
│   └── UNFCCC_NDC_ZAF_2021.pdf
├── NGA/
│   └── UNFCCC_NDC_NGA_2025.pdf
...
```

## Manifest Entry Format

After downloading, add entries to `metadata/manifest.csv`:
- source_id: unfccc/ndc/<ISO3>/<year>
- document_type: policy
- split: ndc
- license: UNFCCC Terms of Use
