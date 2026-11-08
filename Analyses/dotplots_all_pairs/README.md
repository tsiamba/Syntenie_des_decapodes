# Dot plots de synténie BUSCO

## Description

Le script `dotplot_all_pairs.py` compare les 11 génomes deux à deux à partir
des BUSCO complets à copie unique issus de `crustacea_odb12`.

Il réalise les 55 comparaisons possibles et produit un dot plot pour chaque paire.
Chaque point représente un BUSCO commun entre deux génomes. La position du point
correspond à sa position dans chacun des deux génomes.

Le script calcule également un score de conservation de l'ordre des BUSCO, compris
approximativement entre 0 et 1. Un score élevé indique une organisation plus
régulière des marqueurs, tandis qu'un score faible indique une organisation plus
dispersée.

## Exécution

```bash
conda activate /data/projet2/conda/env_dotplot

python /data/projet2/Syntenie_des_decapodes/scripts/dotplot_all_pairs_V2.py \
    --input-dir \
    /data/projet2/Syntenie_des_decapodes/Analyses/Syngraph/busco_input \
    --out-dir \
    /data/projet2/Syntenie_des_decapodes/Analyses/dotplots_all_pairs_V2 \
    --min-chrom-size 10 \
    --min-shared 5

