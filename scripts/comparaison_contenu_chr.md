# Comparaison du contenu chromosomique avec le score de Jaccard

Le script `comparaison_contenu_chr.py` mesure la similarité du contenu en BUSCO entre deux génomes. Il utilise les fichiers `_liens.tsv` et `_sequences.tsv` produits par `sankey_syntenie.py`. Python 3 suffit pour l’exécuter.

## Générer les cartes

Depuis le dossier du projet sur le cluster, lance les commandes suivantes.

```bash
cd /data/projet2/Syntenie_des_decapodes

# Paire proche : Macrobrachium nipponense et Macrobrachium rosenbergii
python3 scripts/comparaison_contenu_chr.py --pair proches

# Paire éloignée : Jaera praehirsuta et Scylla paramamosain
python3 scripts/comparaison_contenu_chr.py --pair eloignes
```

Par défaut, le script lit les tableaux du Sankey dans `Analyses/Diagramme_Sankey/` et écrit les résultats dans `Analyses/Diagramme_Sankey/Contenu_chromosomes/`.

| Fichier | Contenu |
|---|---|
| `*_carte_jaccard.html` | Carte interactive à ouvrir dans un navigateur |
| `*_matrice_jaccard.tsv` | Matrice des scores de Jaccard |
| `*_contenu_chromosomes.tsv` | Détail de chaque comparaison, avec les effectifs BUSCO et la fraction partagée de chaque côté |

Les fichiers commencent par `macrobrachium_` pour la paire proche et `jaera_scylla_` pour la paire éloignée.

## Lire la carte

Télécharge le fichier HTML et ouvre-le dans un navigateur. **Clique sur une case** pour afficher les deux séquences comparées, le score de Jaccard, le nombre de BUSCO partagés et les effectifs retenus de chaque côté.

Le score correspond au **nombre de BUSCO partagés divisé par le nombre total de BUSCO distincts présents dans les deux ensembles**. Un score de **0** indique qu’aucun marqueur retenu n’est partagé. Un score de **1** indique que les deux ensembles de marqueurs retenus sont identiques. Les cases les plus foncées correspondent aux scores les plus élevés.

Chez les deux *Macrobrachium*, par exemple, le chromosome 21 de *M. nipponense* et le chromosome 5 de *M. rosenbergii* partagent leurs 45 BUSCO retenus, ce qui donne un score de 1. La case est éloignée de la diagonale parce que les chromosomes sont triés selon leur numéro dans chaque assemblage.

## Comparer la carte et le dotplot

La carte de Jaccard résume le **contenu partagé** pour chaque couple de séquences. Le dotplot montre **la position et l’ordre** des BUSCO à l’intérieur de ce couple. Pour interpréter les deux figures ensemble, repère une case foncée sur la carte, puis examine le bloc correspondant dans le dotplot.

Le filtre appliqué dépend de la paire :

- **Paire proche** — seuls les BUSCO situés sur des chromosomes dans les deux génomes sont retenus.
- **Paire éloignée** — les séquences `OZ…` de *Jaera* gardent leur identifiant d’origine. Du côté de *Scylla*, seuls les BUSCO situés sur des chromosomes sont retenus.
