#!/usr/bin/env bash
# busco_batch.sh — BUSCO (miniprot) on every GC* genome in a given directory.
# Usage: busco_batch.sh [-l LINEAGE] [-o OUTDIR] GENOME_DIR
# Vesion 2 with less cores to avoid RAM shortage + -f option to force rewrite failed genomes (as a naive premature trial, to be changed in later versions)
set -euo pipefail

LINEAGE="crustacea_odb12.2"
OUTDIR="$PWD"

while getopts "l:o:" opt; do
    case "$opt" in
        l) LINEAGE="$OPTARG" ;;
        o) OUTDIR="$OPTARG" ;;
        *) echo "Usage: $0 [-l LINEAGE] [-o OUTDIR] GENOME_DIR" >&2; exit 1 ;;
    esac
done
shift $((OPTIND - 1))

GENOME_DIR="${1:?Usage: $0 [-l LINEAGE] [-o OUTDIR] GENOME_DIR}"

OUT_BASE="${OUTDIR}/busco_output"
mkdir -p "$OUT_BASE"


# One genome at a time, full core count each — avoids
# stacking concurrent jobs' memory footprints on limited RAM.

for dir in "$GENOME_DIR"/GC*; do
    acc=$(basename "$dir")
    fna=$(find "$dir" -name "*_genomic.fna" | head -n1)
    [[ -z "$fna" ]] && { echo "WARN: no FASTA for $acc, skipping" >&2; continue; }

    echo "=== $acc $(date '+%F %T') ==="
    busco -f -i "$fna" -o "resultats_busco_${acc}" --out_path "$OUT_BASE" \
          -m genome -l "$LINEAGE" -c 1 --miniprot
done

echo "Done. Results in $OUT_BASE/"
