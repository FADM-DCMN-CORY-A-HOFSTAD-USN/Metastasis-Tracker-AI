# Real-Time FHIR Schema Validation & CSV Flattening Specifications

## 1. Overview
This continuous integration specification details the automated parsing, JSON schema validation, and tabular CSV compilation tasks that process streaming interoperability records during patient evaluation loops.

---

## 2. Inoperability Log Directory Blueprint

Live execution tracking loops discard flat monolithic logs, writing timestamped, independent JSON transaction objects down inside the protected data trees:
*   **Target Log Registry Directory**: `src/data/fhir/logs/`
*   **Filename Architecture Scheme**: `payload_[PATIENT_ID]_[YYYYMMDD_HHMMSS_mmm].json`

Each file passes through an automated `jsonschema` validation gate comparing fields against official structural constraints before writing sectors to the storage arrays.

---

## 3. Tool Utility Console Command Bindings

Automate database compilation and schema checks via short console execution shortcuts:

### A. Dynamic Real-Time CSV Flattening
To parse the directory files and flatten them into a structured spreadsheet sheet format, run the conversion shell command wrapper:
```bash
make compile-csv
```
This generates a clean tabular layout (`src/data/fhir/hemostasis_summary.csv`) containing clear columns tracking:
```csv
TIMESTAMP,PATIENT_ID,PLATELET_COUNT,HEPARIN_INHIBITION
2026-06-23T21:50:00Z,pat-04,240000.0,0.85
```
