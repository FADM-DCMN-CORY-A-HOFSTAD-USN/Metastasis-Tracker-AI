#!/bin/bash

# =====================================================================
# Automated Image Frame-to-GIF Animation Assembly Engine
# =====================================================================

set -e

# Visual formatting parameters
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

FRAME_DIR="docs/animation_frames"
OUTPUT_GIF="docs/spatial_growth_trajectory.gif"
FPS=10

echo -e "${CYAN}[*] Starting automated space-time trajectory compilation...${NC}"

# Step 1: Verify presence of source frame assets
if [ ! -d "$FRAME_DIR" ] || [ -z "$(ls -A $FRAME_DIR/*.png 2>/dev/null)" ]; then
    echo -e "${RED}Error: Source frame folder missing or contains 0 sequential .png assets.${NC}"
    exit 1
fi

# Step 2: Check for system compiler prerequisites (convert utility)
if ! command -v convert &> /dev/null; then
    echo -e "${RED}Prerequisite Error: 'ImageMagick (convert)' utility tool not found on host environment.${NC}"
    echo -e "${CYAN}Please initialize package mapping manually via: sudo apt-get install imagemagick${NC}"
    exit 1
fi

# Step 3: Run the conversion assembly line matching delay math: delay = 100 / FPS
DELAY_TICK=$(( 100 / FPS ))
echo -e "[+] Processing raw image frames at frame rate pacing: ${FPS} FPS (Delay: ${DELAY_TICK}ms)..."

convert -delay ${DELAY_TICK} -loop 0 ${FRAME_DIR}/rotation_frame_*.png ${OUTPUT_GIF}

echo -e "${GREEN}=========================================================================${NC}"
echo -e "${GREEN} ✅ ANIMATED TRAJECTORY PACKAGE COMPILED SUCCESSFULLY                  ${NC}"
echo -e "${GREEN} Output Path Target Asset: ${OUTPUT_GIF}                              ${NC}"
echo -e "${GREEN}=========================================================================${NC}"
