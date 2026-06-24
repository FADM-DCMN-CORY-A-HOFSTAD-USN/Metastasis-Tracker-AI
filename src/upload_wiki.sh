#!/bin/bash

# =====================================================================
# Automated Repository Wiki Documentation Ingestion Loop Wrapper
# =====================================================================

set -e

# Visual formatting parameters
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

CHART_ASSET="docs/pulmonary_trends.png"
WBC_WIKI_DIR="tests/wiki_clone"
# GitHub references wiki repositories by adding '.wiki.git' to the base URI
WI_URL="https://github.com"

echo -e "${CYAN}[*] Starting automated wiki documentation synchronization deployment...${NC}"

# Step 1: Confirm source plot asset presence
if [ ! -f "$CHART_ASSET" ]; then
    echo -e "${RED}Error: Source chart target (${CHART_ASSET}) is missing. Aborting upload.${NC}"
    exit 1
fi

# Clean historical scratch paths safely
rm -rf "$WBC_WIKI_DIR"

# Step 2: Clone the secure remote wiki repository branch tree
echo -e "[+] Fetching remote documentation wiki tree sectors..."
git clone "$WI_URL" "$WBC_WIKI_DIR" --quiet

# Step 3: Copy chart assets and inject Markdown references into Home.md
echo -e "[+] Injecting synchronized chart images into local wiki sectors..."
cp "$CHART_ASSET" "$WBC_WIKI_DIR/"

HOME_MD="$WBC_WIKI_DIR/Home.md"
if [ -f "$HOME_MD" ]; then
    # Add image reference only if not already present
    if ! grep -q "pulmonary_trends.png" "$HOME_MD"; then
        echo -e "\n## Real-Time Pulmonary Simulation Metrics\n![Pulmonary Metrics](pulmonary_trends.png)" >> "$HOME_MD"
    fi
fi

# Step 4: Commit and push changes back to the upstream wiki tree
cd "$WBC_WIKI_DIR"
git config user.name "Anatomy Engine Automation Builder"
git config user.email "ci-engine@bmed.mil"

git add .
if ! git diff-index --quiet HEAD --; then
    git commit -m "Automated Pipeline Update: Synchronized diagnostic telemetry charts [Skip CI]" --quiet
    echo -e "[+] Pushing updated layout schemas back to GitHub Wiki server..."
    git push origin main --quiet
    echo -e "${GREEN} ✅ WIKI REPOSITORY CHANNELS SYNCHRONIZED SUCCESSFULLY ${NC}"
else
    echo -e "${CYAN}[*] Zero changes detected inside structural assets. Wiki up to date.${NC}"
fi

# Clean up transient workspace tracks
cd - > /dev/null
rm -rf "$WBC_WIKI_DIR"
