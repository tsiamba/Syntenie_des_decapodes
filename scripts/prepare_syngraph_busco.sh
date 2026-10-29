#!/usr/bin/env bash
set -euo pipefail

BUSCO_ROOT="${1:?Usage: $0 dossier_BUSCO dossier_sortie}"
OUTDIR="${2:?Usage: $0 dossier_BUSCO dossier_sortie}"

LINEAGE="crustacea_odb12"

mkdir -p "$OUTDIR"

found=0

while IFS= read -r full_table
do
    # Exemple de répertoire parent :
    # BUSCO_GCF_015104395.2_ASM1510439v2_genomic.fna
    run_dir=$(dirname "$full_table")
    result_dir=$(dirname "$run_dir")
    result_name=$(basename "$result_dir")

    # Retirer les préfixes utilisés dans tes noms de résultats
    taxon="$result_name"
    taxon="${taxon#BUSCO_}"
    taxon="${taxon#resultats_busco_}"

    # Retirer le suffixe correspondant au fichier d'entrée
    taxon="${taxon%_genomic.fna}"

    output="$OUTDIR/${taxon}.tsv"

    echo "Traitement : $taxon"
    echo "  Entrée : $full_table"
    echo "  Sortie : $output"

    awk -F '\t' '
        BEGIN {
            OFS = "\t"
        }

        # Ignorer les commentaires et l’en-tête BUSCO
        /^#/ {
            next
        }

        # BUSCO full_table.tsv :
        # $1 = Busco_id
        # $2 = Status
        # $3 = Sequence
        # $4 = Gene_Start
        # $5 = Gene_End
        #
        # On conserve uniquement les BUSCO complets.
        NF >= 5 && $2 == "Complete" {
            print $1, $3, $4, $5
        }
    ' "$full_table" > "$output"

    n=$(wc -l < "$output")

    if [[ "$n" -eq 0 ]]; then
        echo "  ATTENTION : aucun BUSCO complet trouvé"
        rm -f "$output"
    else
        echo "  BUSCO conservés : $n"
        found=$((found + 1))
    fi

done < <(
    find "$BUSCO_ROOT" \
        -type f \
        -path "*/run_${LINEAGE}/full_table.tsv" \
        -print
)

if [[ "$found" -eq 0 ]]; then
    echo "Erreur : aucun full_table.tsv exploitable trouvé." >&2
    exit 1
fi

echo
echo "Conversion terminée."
echo "Fichiers Syngraph créés dans : $OUTDIR"
echo "Nombre de taxons : $found"
