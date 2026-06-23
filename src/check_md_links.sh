#!/bin/bash

# =====================================================================
# Continuous Integration Markdown Documentation Broken Link Checker
# =====================================================================

set -e

# Visual text formatting parameters
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

DOCS_DIR="docs"
broken_links_count=0

echo -e "${CYAN}=========================================================================${NC}"
echo -e "${CYAN}   LAUNCHING ANATOMICAL SUITE DOCUMENTATION LINK INTEGRITY CHECKER      ${NC}"
echo -e "${CYAN}=========================================================================${NC}"

if [ ! -d "$DOCS_DIR" ]; then
    echo -e "${RED}Error: Target documentation repository directory '$DOCS_DIR' is missing.${NC}"
    exit 1
fi

# Locate all markdown files inside the target path
md_files=$(find "$DOCS_DIR" -type f -name "*.md")

for file in $md_files; do
    echo -e "[*] Scanning document frames: $file"
    
    # Extract links matching standard markdown regex patterns [text](link)
    # Exclude external web protocols (http/https) to focus purely on relative repository file targets
    links=$(grep -oP '\[.*?\]\(\s*\K[^)]+' "$file" | grep -v '^http' || true)
    
    current_file_dir=$(dirname "$file")
    
    while read -r link; do
        [ -z "$link" ] && continue
        
        # Strip trailing anchors/sections (#heading) from link comparisons
        clean_link=$(echo "$link" | cut -d'#' -f1)
        [ -z "$clean_link" ] && continue
        
        # Build path resolution vector relative to current file workspace context
        if [[ "$clean_link" == /* ]]; then
            resolved_path=".${clean_link}" # Treats root path as repository root
        else
            resolved_path="${current_file_dir}/${clean_link}"
        fi
        
        # Check target physical presence on disk
        if [ ! -e "$resolved_path" ]; then
            echo -e "  ${RED}├──> BROKEN RELATIVE LINK DETECTED: '$link' (Resolved: $resolved_path)${NC}"
            broken_links_count=$((broken_links_count + 1))
        fi
    done <<< "$links"
done

echo -e "${CYAN}-------------------------------------------------------------------------${NC}"
if [ "$broken_links_count" -gt 0 ]; then
    echo -e "${RED}❌ INTEGRITY CHECKS FAILED: Found $broken_links_count broken linkages inside docs/ files.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ INTEGRITY CHECKS PASSED: 100% of internal documentation links verified.${NC}"
    exit 0
fi
