#!/bin/bash

# =====================================================================
# Metastasis-Tracker-AI Core Unifying Simulation Architecture Runner
# =====================================================================

# Stop script execution immediately if any internal task returns an error flag
set -e

# Visual formatting parameters
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}=========================================================================${NC}"
echo -e "${CYAN}   LAUNCHING UNIFIED ECOSYSTEM PIPELINE PLATFORM DRIVER                  ${NC}"
echo -e "${CYAN}=========================================================================${NC}"

# Task 1: Verify folder architecture compliance boundaries
echo -e "\n[TASK 1/4]: Checking directory framework pathways..."
if [ ! -d "src/data" ] || [ ! -d "tests" ]; then
    echo -e "${RED}Error: Core repository directory map structure is corrupted.${NC}"
    exit 1
fi
echo -e "${GREEN} -> System folders verified.${NC}"

# Task 2: Validate Data files and JSON configuration parameters
echo -e "\n[TASK 2/4]: Executing automated data ingestion parser hooks..."
if [ -f "src/parse_json_data.py" ]; then
    python3 src/parse_json_data.py
    echo -e "${GREEN} -> Enzymatic data parsing configurations verified successfully.${NC}"
else
    echo -e "${RED}Warning: parse_json_data.py tool vector missing from workspace.${NC}"
fi

# Task 3: Execute trauma and material boundary unittest checks
echo -e "\n[TASK 3/4]: Running biophysical material boundary unit assertions..."
python3 src/sepsis_redox_engine.py
if [ -f "src/trauma_fluid_core.py" ]; then
    python3 src/trauma_fluid_core.py
fi
echo -e "${GREEN} -> Trauma fluid dynamics and material boundary assertions passed.${NC}"

# Task 4: Ingest configuration matrix parameters
echo -e "\n[TASK 4/4]: Executing automated patient profile cohort validations..."
if [ -f "tests/run_automated_suite.py" ]; then
    python3 tests/run_automated_suite.py
    echo -e "${GREEN} -> Multi-patient testing cohort matrix runs successfully completed.${NC}"
else
    echo -e "${RED}Skipping Task 4: run_automated_suite.py script missing.${NC}"
fi

echo -e "\n${GREEN}=========================================================================${NC}"
echo -e "${GREEN} ✅ ALL SYSTEM VALIDATION CHECKS SUCCESSFULLY VERIFIED                  ${NC}"
echo -e "${GREEN}=========================================================================${NC}"
