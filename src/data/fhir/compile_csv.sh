#!/bin/bash

# =====================================================================
# Automated FHIR Log Flattener and Tabular CSV Assembler
# =====================================================================

set -e

# Visual text variables
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

CSV_TARGET="src/data/fhir/hemostasis_summary.csv"

echo -e "${CYAN}[*] Initializing individual JSON log parsing loops...${NC}"

# Execute python compilation method block wrapper directly
python3 -c "from src.data.fhir.fhir_pipeline import FHIRPipelineAutomationEngine; e=FHIRPipelineAutomationEngine(); e.compile_logs_to_tabular_csv('$CSV_TARGET')"

echo -e "${GREEN}=========================================================================${NC}"
echo -e "${GREEN} ✅ SPREADSHEET COMPILATION COMPLETE: Tabular CSV matrix updated.     ${NC}"
echo -e "${GREEN} Target Spreadsheet Asset: ${CSV_TARGET}                             ${NC}"
echo -e "${GREEN}=========================================================================${NC}"
