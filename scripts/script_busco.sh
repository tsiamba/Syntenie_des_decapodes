#!/bin/bash

# 1. Activation de l'environnement Conda (nécessaire dans un script bash)
eval "$(conda shell.bash hook)"
conda activate env_busco

# 2. Liste de vos génomes (les 10 décapodes)
ACCESSIONS=(
    "GCF_015104395.2"
    "GCF_042767895.1"
    "GCF_024679095.1"
    "GCF_040412425.1"
    "GCF_040958095.1"
    "GCF_035594125.1"
    "GCF_017591435.1"
    "GCF_038502225.1"
    "GCF_019202785.1"
    "GCF_036320965.1"
)

# 3. Paramètres globaux
BASE_DIR="/data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data"
LINEAGE="arthropoda_odb10"
# PASSAGE A 4 COEURS POUR SAUVER LA RAM
THREADS=4

# 4. Boucle sur chaque génome
for ACC in "${ACCESSIONS[@]}"; do
    echo "--------------------------------------------------------"
    echo "Démarrage de BUSCO pour : $ACC"

    # Recherche du fichier génomique .fna exact
    FNA_FILE=$(find "$BASE_DIR/$ACC" -name "${ACC}*_genomic.fna" | head -n 1)

    if [ -z "$FNA_FILE" ]; then
        echo "ERREUR : Fichier FASTA introuvable pour $ACC"
        continue
    fi

    # Votre modification pour remonter d'un dossier
    OUT_DIR="../resultats_busco_${ACC}"

    # Vérification : si le dossier de résultats existe déjà, on saute
    if [ -d "$OUT_DIR" ]; then
        echo "Le dossier $OUT_DIR existe déjà, passage au génome suivant..."
        continue
    fi

    # AJOUT DE --metaeuk POUR CONTOURNER miniprot ET SÉPARATION DU echo
    busco -i "$FNA_FILE" -o "$OUT_DIR" -m genome -l "$LINEAGE" -c "$THREADS" --metaeuk
    
    echo "Terminé pour : $ACC"
done

echo "Toutes les analyses sont terminées !"
