#!/usr/bin/env bash
set -euo pipefail

# Default: use all available CPU cores
NUM_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

# Parse command line options
while getopts ":c:h" opt; do
  case ${opt} in
    c)
      NUM_CORES="$OPTARG"
      ;;
    h)
      echo "Usage: $0 [-c num_cores] <path/to/files/*.tsv> ..."
      echo "  -c : Limit the number of parallel processing cores (default: max available)"
      exit 0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 [-c num_cores] <path/to/files/*.tsv> ..."
    exit 1
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SUMMARY_FILE="filtering_summary_${TIMESTAMP}.txt"

echo "=== Syngraph Chromosome Filtering Summary (${TIMESTAMP}) ===" > "$SUMMARY_FILE"
echo -e "Filename\tBefore_Lines\tAfter_Lines" >> "$SUMMARY_FILE"
echo "--------------------------------------------------" >> "$SUMMARY_FILE"

OUT_DIR=""

# Export variables and function for xargs parallel execution
export OUT_DIR
process_file() {
    local filepath="$1"
    
    if [ ! -f "$filepath" ]; then
        echo "Skipping (not a file): $filepath"
        return
    fi

    if [[ "$filepath" != *.tsv ]]; then
        echo "Skipping (non-TSV): $filepath"
        return
    fi

    local in_dir
    in_dir=$(dirname "$filepath")
    local out_dir="${in_dir}/../filtered_busco_chromosomes"
    mkdir -p "$out_dir"

    local filename
    filename=$(basename "$filepath")
    local out_name="${filename%.tsv}_chromosome_only.tsv"
    local out_path="$out_dir/$out_name"

    local before_count
    before_count=$(wc -l < "$filepath")

    # Filter: check column 2 for NC or OZ accessions
    awk -F'\t' '{ if ($2 ~ /NC|OZ/) print $0 }' "$filepath" > "$out_path"

    local after_count
    after_count=$(wc -l < "$out_path")

    echo "Processed: $filename | Kept: $after_count / $before_count lines"
    echo -e "$filename\t$before_count\t$after_count"
}
export -f process_file

# Process files in parallel using xargs based on the user-specified core limit
printf '%s\n' "$@" | xargs -P "$NUM_CORES" -I {} bash -c 'process_file "$@"' _ {} >> "$SUMMARY_FILE"

echo "--------------------------------------------------"
echo "Done! Filtered files saved to sister directory."
echo "Run summary saved to: $SUMMARY_FILE"
