#!/bin/bash
# Build PDF from markdown files with Mermaid diagram support
# Usage: ./scripts/build-pdf.sh [lab-number|all]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_DIR/build"
OUTPUT_DIR="$PROJECT_DIR/output"

# Ensure npm global bin is in PATH
export PATH=~/.npm-global/bin:$PATH

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Create directories
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

# Function to convert emojis to text alternatives for PDF compatibility
convert_emojis() {
    local content="$1"
    # Common emojis used in the labs -> text alternatives
    echo "$content" | sed \
        -e 's/🔍/[SEARCH]/g' \
        -e 's/⏱/[TIME]/g' \
        -e 's/✓/[OK]/g' \
        -e 's/✗/[X]/g' \
        -e 's/⚠/[!]/g' \
        -e 's/💰/[$]/g' \
        -e 's/✅/[DONE]/g' \
        -e 's/❌/[FAIL]/g' \
        -e 's/📁/[FOLDER]/g' \
        -e 's/💻/[PC]/g' \
        -e 's/☁️/[CLOUD]/g' \
        -e 's/⚙️/[GEAR]/g' \
        -e 's/🚀/[LAUNCH]/g' \
        -e 's/📦/[PKG]/g' \
        -e 's/📡/[API]/g' \
        -e 's/👤/[USER]/g' \
        -e 's/↔️/[<->]/g' \
        -e 's/🖥️/[SERVER]/g' \
        -e 's/🔧/[TOOL]/g' \
        -e 's/📊/[CHART]/g' \
        -e 's/🎯/[TARGET]/g' \
        -e 's/💡/[TIP]/g' \
        -e 's/⭐/[*]/g' \
        -e 's/🏆/[WIN]/g' \
        -e 's/📝/[NOTE]/g' \
        -e 's/🔒/[LOCK]/g' \
        -e 's/🔑/[KEY]/g'
}

# Function to extract and render Mermaid diagrams
process_mermaid() {
    local input_file="$1"
    local output_file="$2"
    local temp_dir="$3"
    local diagram_count=0

    log_info "Processing Mermaid diagrams in $(basename "$input_file")..."

    # Read file and process mermaid blocks
    local in_mermaid=false
    local mermaid_content=""
    local output_content=""

    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ "$line" =~ ^\`\`\`mermaid ]]; then
            in_mermaid=true
            mermaid_content=""
        elif [[ "$line" =~ ^\`\`\` ]] && $in_mermaid; then
            in_mermaid=false
            diagram_count=$((diagram_count + 1))
            local diagram_file="$temp_dir/diagram_${diagram_count}.mmd"
            local png_file="$temp_dir/diagram_${diagram_count}.png"

            # Write mermaid content to file
            echo "$mermaid_content" > "$diagram_file"

            # Render to PNG (better PDF compatibility than SVG)
            if mmdc -i "$diagram_file" -o "$png_file" -b transparent -s 2 2>/dev/null; then
                # Replace mermaid block with image reference
                output_content+=$'\n'"![Diagram $diagram_count]($png_file){ width=90% }"$'\n\n'
            else
                log_warn "Failed to render diagram $diagram_count, keeping as code block"
                output_content+=$'\n```\n'"$mermaid_content"$'\n```\n'
            fi
        elif $in_mermaid; then
            mermaid_content+="$line"$'\n'
        else
            output_content+="$line"$'\n'
        fi
    done < "$input_file"

    # Convert emojis to text alternatives
    convert_emojis "$output_content" > "$output_file"
    log_info "Processed $diagram_count Mermaid diagrams"
}

# Function to build a single lab PDF
build_lab() {
    local lab_dir="$1"
    local lab_name=$(basename "$lab_dir")
    local lab_file="$lab_dir/LAB.md"

    if [[ ! -f "$lab_file" ]]; then
        log_warn "No LAB.md found in $lab_name, skipping..."
        return
    fi

    log_info "Building PDF for $lab_name..."

    # Create temp directory for this lab
    local temp_dir="$BUILD_DIR/$lab_name"
    mkdir -p "$temp_dir"

    # Process mermaid diagrams
    local processed_file="$temp_dir/processed.md"
    process_mermaid "$lab_file" "$processed_file" "$temp_dir"

    # Build PDF with Pandoc using lualatex
    local output_file="$OUTPUT_DIR/${lab_name}.pdf"

    pandoc "$processed_file" \
        --pdf-engine=lualatex \
        --variable geometry:margin=1in \
        --variable fontsize=11pt \
        --variable documentclass=article \
        --variable colorlinks=true \
        --variable linkcolor=blue \
        --variable urlcolor=blue \
        --highlight-style=tango \
        --toc \
        --toc-depth=2 \
        --standalone \
        -o "$output_file" 2>&1 | grep -v "Missing character" || true

    if [[ -f "$output_file" ]]; then
        log_info "Created: $output_file"
    else
        log_error "Failed to build $lab_name"
        return 1
    fi
}

# Function to build combined PDF of all labs
build_all() {
    log_info "Building combined PDF of all labs..."

    local temp_dir="$BUILD_DIR/combined"
    mkdir -p "$temp_dir"

    local combined_file="$temp_dir/combined.md"
    > "$combined_file"

    # Add title page
    cat >> "$combined_file" << 'EOF'
---
title: "AWS Machine Learning Associate Exam Prep"
subtitle: "Complete Lab Guide"
author: "ML Labs Collection"
date: \today
geometry: margin=1in
fontsize: 11pt
documentclass: report
colorlinks: true
linkcolor: blue
urlcolor: blue
toc: true
toc-depth: 2
---

\newpage

EOF

    # Process each lab
    for lab_dir in "$PROJECT_DIR"/[0-9][0-9]-*/; do
        if [[ -d "$lab_dir" ]]; then
            local lab_name=$(basename "$lab_dir")
            local lab_file="$lab_dir/LAB.md"

            if [[ -f "$lab_file" ]]; then
                log_info "Adding $lab_name to combined document..."

                local lab_temp_dir="$temp_dir/$lab_name"
                mkdir -p "$lab_temp_dir"

                local processed_file="$lab_temp_dir/processed.md"
                process_mermaid "$lab_file" "$processed_file" "$lab_temp_dir"

                # Add chapter header and content
                echo -e "\n# ${lab_name}\n" >> "$combined_file"
                # Remove any YAML frontmatter from individual files
                sed '/^---$/,/^---$/d' "$processed_file" >> "$combined_file"
                echo -e "\n\\\\newpage\n" >> "$combined_file"
            fi
        fi
    done

    # Build combined PDF
    local output_file="$OUTPUT_DIR/aws-ml-labs-complete.pdf"

    pandoc "$combined_file" \
        --pdf-engine=lualatex \
        --highlight-style=tango \
        --standalone \
        -o "$output_file" 2>&1 | grep -v "Missing character" || true

    if [[ -f "$output_file" ]]; then
        log_info "Created combined PDF: $output_file"
    else
        log_error "Failed to build combined PDF"
        return 1
    fi
}

# Main
case "${1:-all}" in
    all)
        build_all
        ;;
    combined)
        build_all
        ;;
    clean)
        log_info "Cleaning build directories..."
        rm -rf "$BUILD_DIR" "$OUTPUT_DIR"
        log_info "Done"
        ;;
    [0-9][0-9])
        # Build specific lab by number
        lab_dir=$(find "$PROJECT_DIR" -maxdepth 1 -type d -name "${1}-*" | head -1)
        if [[ -n "$lab_dir" ]]; then
            build_lab "$lab_dir"
        else
            log_error "Lab $1 not found"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 [all|combined|clean|NN]"
        echo "  all/combined - Build combined PDF of all labs"
        echo "  clean        - Remove build artifacts"
        echo "  NN           - Build specific lab (e.g., 01, 02)"
        exit 1
        ;;
esac
