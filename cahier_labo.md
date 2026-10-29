# Cahier de laboratoire : Synténie des décapodes

*Septembre 2026*

---

## Dimanche 13 septembre : choix des génomes

Les génomes ont été choisis selon plusieurs critères qui, dans l'ordre d'importance, sont les suivants :

1. Tous les génomes ont des *chromosome level assembly* ;
2. Tous les génomes de décapodes ont des scores BUSCO GC d'au moins 90 %, pour avoir une bonne complétude ;
3. Les génomes avec les meilleurs contig N50 ont été choisis de manière à garder une bonne contiguïté ;
4. Les génomes ont été choisis de manière à garder une diversité phylogénétique au sein des décapodes.

---

## Étapes et tâches réalisées

| Tâche | Qui |
|---|---|
| Création de l'environnement conda : 1er essai (semaine du 14/09/26, je ne sais plus quel jour) | Tsiambaka |
| Installation de bioconda, BUSCO | Jade |
| Analyse BUSCO | Aurélio |
| `git init`, `git push` | Tsiambaka |
| Droits et permissions | Jade / Aurélio |
| Ajout des génomes | Jade |
| Ajout de l'isopode GenBank | Tsiambaka |
| Création du cahier de labo | Tsiambaka |

---

## Journal de bord

### Dimanche 20 septembre

**Aurélio** · 2 h

- Modification du README
- Mise en place du `.gitignore` 

```bash
#Enlever Dossier et Fichier non nécessaire ou trop gros:
*.zip
.gff
.fna
envs/
genomes/
precomputed_crustacea_odb12
*.zip
*.tar.gz
busco_downloads/
busco_metaeuk/
busco_miniprot/
```

- Copie du repository
- Mise en place de `git pull` / `git push`

### Lundi 21 septembre

**Aurélio** · 1 h

- Modification du `.gitignore`
- Nouvel environnement pour BUSCO
- Lancement de l'analyse BUSCO
- screen -r -> pour lancer le script sur une fenêtre en fond

**Tsiambaka** · 1 h

J'ai juste téléchargé le fichier GenBank de *Jaera* :

```bash
(/data/projet2/conda/env_busco) randaoharison@ptu:/data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data$ ls
GCA_965208005.1
```

Commande :

```bash
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/965/208/005/GCA_965208005.1_qmJaePrae1.hap1.1/GCA_965208005.1_qmJaePrae1.hap1.1_genomic.fna.gz
```

**Tsiambaka** · 1 h

**Lancement de l'analyse BUSCO sur Jaera**

Commandes : d'abord, pour dézipper le génome :

```bash
gunzip -k /data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data/GCA_965208005.1/GCA_965208005.1_qmJaePrae1.hap1.1_genomic.fna.gz
```

puis, pour lancer l'analyse BUSCO (~ 1 h) :

```bash
FNA=$(find /data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data/GCA_965208005.1 -name "*_genomic.fna")
echo "$FNA"
```

### Vendredi 25 septembre

**Aurélio** · 2 h

- J'ai essayé de faire marcher BUSCO : problème de serveur saturé par le script (8 cœurs → 4 cœurs).
- Modification du script et relance de BUSCO.

### Dimanche 27 septembre

**Aurélio** · 1 h

- Problème avec certains génomes qui saturent le serveur.
- Création d'un fichier log où j'ai affiché tout ce que BUSCO m'a renvoyé : log_analyse_busco_metaeuk.txt

**Tsiambaka** · 30 min

- Lancement de BUSCO sur l'isopode *Jaera*, avec 3 cœurs sur le serveur.


### Lundi 28 septembre

**Aurélio** · 45 min

- Vérification des analyses BUSCO.
- Modification du fichier log pour ajouter les dernières infos sur l'analyse BUSCO.
- Essai de comprendre le problème d'analyse BUSCO.

### Mardi 29 septembre

**Aurélio** · 20 min

- Vérification de la fin de l'analyse BUSCO.
- Modification du script pour relancer sur ceux qui ne sont pas passés.
- Mise à jour du fichier log.

---

## Récupérer les fichiers depuis le cluster

À exécuter **en dehors de ssh** :

```bash
scp vitale@ptu.bigest-icube.fr:/data/projet2/Syntenie_des_decapodes/log_analyse_busco.md .
```

---

## Script d'analyse BUSCO

<!-- script à coller ici -->

## Mardi 06 octobre 

**Aurélio** · 1h

- Installation de panda et plotly dans l'environnement pour script diagramme de sankey
- Adaptation d'un code pré existant de mon stage de M1
- Lancer le script et analyser premier résultat sur metaeuk en attendant run de miniprot
- Réorganisation de certains fichier et dossier


**Jade** · 1 h

- Bibliographie sur BUSCO et choix des paramètres de l'analyse
- Choix retenus :
  - prédicteur de gènes : **miniprot** (plus rapide que metaeuk et prédicteur par défaut de BUSCO)
  - jeu de données : **odb12.2** (plus récent et mieux curé qu'odb10)
  - lignée : **crustacea** (plus précise qu'arthropoda, permet une évaluation plus informative)
  - cœurs : tous 

Commande pour vérifier les lignées disponibles

```bash
busco --list-datasets
```

## Mercredi 7 octobre

**Jade** · 30 mins

- Création de `script_busco_miniprot.sh` avec nano (v1 : tous les cœurs via `nproc`, `--miniprot`, `crustacea_odb12.2`)
- Premiers runs sur les génomes

Commande BUSCO utilisée par le script

```bash
busco -i [génome.fna] -o [nom_sortie] --out_path [dossier] -m genome -l crustacea_odb12.2 -c $(nproc) --miniprot

```
Commande pour run le script:
```bash
./script_busco_miniprot.sh -o <out_dir/> <genomes>
```


## Jeudi 8 octobre

**Jade** · 1h10 (en total)

- Nouveaux runs : plusieurs échecs (voir section ci-dessous)
- Création de `script_busco_miniprot_2.sh` (v2) : moins de cœurs pour éviter la pénurie de RAM, option `-f` pour forcer la réécriture des génomes échoués (essai naïf, à revoir dans les versions suivantes), `set -euo pipefail`
- Nombre de cœurs dans la v2 : 8 au départ, puis 4, puis 1 : échecs persistants
- Contact avec le professeur
- Observation : les dossiers de sortie de la v2 portent le nom complet du fichier FASTA (`resultats_busco_<accession>_<nom_assemblage>_genomic.fna`), alors que ceux de la v1 portent l'accession seule

Utilisation de la v2

```bash
./scripts/script_busco_miniprot_2.sh -o busco_miniprot/busco_output/ genomes/ncbi_dataset/data/[accession]/
```

### Problèmes rencontrés : échec de BUSCO (code -9)

- Erreur `-9` (SIGKILL) à l'étape `miniprot_index`, avec 8 puis 4 puis avec 1 cœur
- Une des génomes concernés : `GCF_036320965.1` (2,65 Gb, 1451 contigs)
- Fichier d'erreur de miniprot vide
- Hypothèse (non confirmée) : mémoire insuffisante sur le serveur (16 Go, sans swap)
- Vérifications faites :
  - aucune trace de OOM dans `dmesg` (non concluant)
  - mémoire : 15 Gi au total, environ 13 Gi libres au moment du test, pas de swap
  - `ulimit -a` : tout en `unlimited`
  - cgroup v2, `MemoryMax=infinity` pour la session utilisateur

Commandes de diagnostic

```bash
free -h
ulimit -a
cat /proc/self/cgroup
systemctl show "user-$(id -u).slice" -p MemoryMax
```



### Vendredi 09 Octobre
**Tsiambaka** · 1h
Extraction des fichiers de génomes les plus lourds fait par le prof de /data/data_tutor/precomputed_busco.tar.gz vers:
mkdir -p /data/projet2/Syntenie_des_decapodes/precomputed_crustacea_odb12
tar -xvf /data/data_tutor/precomputed_busco.tar.gz \
    -C /data/projet2/Syntenie_des_decapodes/precomputed_crustacea_odb12 \
    --wildcards "*/full_table.tsv" "*/short_summary*" "*/log/*"

=> Récupération des fichiers short_summary.txt pour lancer le diagramme de Sankey et le dot plot

---

## Samedi 10 octobre

**Aurélio** · 45 min

- Modification du .gitignore pour inclure les fichiers trop gros (output busco)
- Mise à jour du cahier de labo
- Modification de l'arborésence

Commande pour vérifier la taille des dossiers/sous dossiers

```bash
du -h --max-depth=1 dossier/
```

Commande pour voir l'arborésence des dossiers

```bash
tree -d
```

**Jade** · 30 mins total

- Modification de la v2 : 8 cœurs (échec sur les petits génomes), puis **4 cœurs** (succès sur les petits génomes)
- Changement de jeu de données : `crustacea_odb12.2` → `crustacea_odb12`, pour correspondre à celui utilisé par M Nevers
- Recalcul des génomes de taille gérable sur notre serveur [GCA_965208005.1; GCF_017591435.1; GCF_019202785.1; GCF_024679095.1]

Commande pour vérifier quels runs ont abouti (présence d'un `short_summary` = succès)

```bash
ls precomputed_crustacea_odb12/precomputed/BUSCO/busco_output/*
```


## Dimanche 11 Octobre
**Tsiambaka** · 1h20  min

- L'analyse busco avec Miniprot pour ce génome ici : resultats_busco_GCF_036320965.1_ASM3632096v1_genomic.fna
 a été killed, je pense à cause de problèmes de ressources. 
- Je vais relancer cette analyse toute seule.
- Commande : 
Pour voir le job en cours : screen -S resultats_busco_GCF_036320965.1_ASM3632096v1_genomic_notkilled.fna
Lancer le busco : busco -f -i /data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data/GCF_036320965.1/*_genomic.fna -o resultats_busco_GCF_036320965.1_ASM3632096v1_genomic_notkilled.fna -m genome -l crustacea_odb12 -c 3 --miniprot
- Je vais rajouter dans le dossier scripts, un nouveau script qui servira pour réaliser le dotplot de la conservation de gènes entre les différents génomes. Ceci ne sera qu'un script qui servira de test pour le moment. Nom du fichier :/data/projet2/Syntenie_des_decapodes/scripts/dotplot.py

**Jade** · 15 mins total

- Suite du rerun des génomes restants (en cours) [GCF_035594125.1; GCF_042767895.1]
- GCF_036320965.1 échoue toujours (3 essais).

## Difficultés rencontrées et adaptations du travail

Septembre - Octobre
Tsiambaka, Aurélio, Jade

### Saturation de la mémoire lors des analyses BUSCO

Les analyses BUSCO de certains génomes ont saturé la mémoire vive (RAM) du serveur, empêchant leur achèvement. Une partie des problèmes et des messages associés est conservée dans les fichiers suivants, à la racine du projet :

- `git_status.txt` ;
- `busco_693521.log` ;
- `busco_771368.log` ;
- `log_analyse_busco_metaeuk.txt`:

Nous avons essayé le pipeline MetaEuk dans l’objectif de réduire l’utilisation de RAM. Cet essai n’a pas résolu le problème pour les génomes concernés.

En attendant de disposer des résultats des analyses avec Miniprot, nous avons développé et adapté les scripts de traitement et de visualisation aux sorties MetaEuk disponibles. Cela nous a permis d’avancer sur les étapes en aval malgré les difficultés de calcul. Les adaptations nécessaires aux sorties Miniprot doivent être décrites dans les sessions correspondantes.

Les accessions des génomes concernés, commandes de lancement, versions des programmes, paramètres de ressources, messages d’erreur et état final de chaque analyse.

### Changements de base de référence BUSCO

Les premières analyses avec MetaEuk ont été lancées avec `arthropoda_odb10`. Elles ont ensuite été relancées avec `crustacea_odb12.2`.

Certains génomes ne pouvant pas être analysés jusqu’au bout avec les ressources disponibles, nous avons récupéré des résultats précalculés par l’enseignant avec `crustacea_odb12`. Pour travailler avec une base de référence commune, une nouvelle relance de nos analyses avec `crustacea_odb12` est donc nécessaire. Son état d’avancement doit être indiqué pour chaque génome.

Les résultats précalculés ont été extraits le **9 octobre 2026 par Tsiambaka** depuis :

`/data/data_tutor/precomputed_busco.tar.gz`

vers :

`/data/projet2/Syntenie_des_decapodes/precomputed_crustacea_odb12/`

Les résultats des différentes bases doivent rester identifiés séparément. Pour chaque figure, nous devons préciser les fichiers utilisés, le pipeline et la base de référence correspondante.

### Difficultés de synchronisation avec GitHub

Lors d’une tentative de `git push` vers GitHub, nous avons rencontré un problème lié à des fichiers d’environnement précédemment suivis par Git. Ces fichiers avaient été supprimés à la suite d’une mauvaise installation, et leur suppression a compliqué la synchronisation du dépôt.

Cette description devra être complétée avec le message d’erreur exact et l’état du dépôt consigné dans `git_status.txt`, afin de préciser la cause technique du blocage.

**Aurélio, Vendredi 09 Octobre** :  personne ayant effectué la tentative, fichiers concernés, commandes exécutées pour corriger le problème et confirmation de la réussite du `push`.

### Conséquences sur la progression du projet

Les difficultés de mémoire ont conduit à avancer sur les scripts à partir des sorties disponibles, puis à récupérer des résultats précalculés pour certains génomes. Le changement de base de référence impose maintenant d’harmoniser les analyses retenues avant de produire les comparaisons finales.

Les sessions suivantes devront relier chaque relance ou correction à ses commandes, à ses logs et aux résultats effectivement utilisés.



## Mercredi 28 Octobre 2026
**Tsiambaka** ~2h
- Création de fichier env_busco.yml pour la version des environnement et des outils. Mais scipy 1.15.3, a été installé avec pip et non avec conda.
- Commandes: 
mkdir -p envs
conda env export --no-builds > envs/env_busco.yml
Afin d'exporter le fichier .yml 
- J'ai modifié le .gitignore en précisant: 
!envs/
!envs/*.yml

afin de faire une exception et pouvoir push le fichier.yml


## Jeudi 29 Octobre 2026
**Tsiambaka** ~ 2h

Environnement logiciel utilisé

Les analyses BUSCO ont été réalisées sur le serveur `ptu`, dans
l'environnement Conda `env_busco`, situé à l'emplacement suivant :

```text
/data/projet2/conda/env_busco
```

Cet environnement était actif au moment des analyses. Cela a été vérifié
avec la commande :

```bash
conda env list
```

La sortie obtenue était :

```text
# conda environments:
#
# * -> active
# + -> frozen
env_busco            *   /data/projet2/conda/env_busco
base                     /opt/conda
```

L'astérisque indique que l'environnement `env_busco` était actif.  
L'environnement `base`, situé dans `/opt/conda`, était installé sur le
serveur mais n'a pas été utilisé pour les analyses BUSCO.

Les principaux logiciels et versions utilisés étaient :

| Logiciel ou bibliothèque | Version | Source d'installation |
|---|---:|---|
| BUSCO | 6.1.0 | Bioconda |
| Miniprot | 0.18 | Bioconda |
| HMMER | 3.4 | Bioconda |
| Python | 3.10 | Conda |
| NumPy | 2.2.6 | Conda |
| Pandas | 2.3.3 | Conda |
| Matplotlib | 3.10.9 | Conda |
| Plotly | 6.9.0 | Conda |
| SciPy | 1.15.3 | pip |

La liste des paquets a été obtenue avec :

```bash
conda list
```

Les informations principales de l'environnement étaient :

```text
busco                          6.1.0
hmmer                          3.4
miniprot                       0.18
matplotlib-base                3.10.9
numpy                          2.2.6
pandas                         2.3.3
plotly                         6.9.0
scipy                          1.15.3
```

Les analyses finales ont été réalisées avec BUSCO en mode `genome`, en
utilisant Miniprot pour rechercher les gènes BUSCO dans les séquences
génomiques. Le jeu de données BUSCO utilisé était `crustacea_odb12`,
adapté à l'étude des génomes de crustacés.

Les commandes utilisées pour vérifier l'environnement et les versions
étaient :

```bash
conda activate env_busco
conda env list
conda list
busco --version
miniprot --version
python --version
busco --list-datasets
```

L'environnement a été exporté afin de conserver les versions des outils
utilisés et de permettre la recréation d'un environnement similaire :

```bash
mkdir -p envs
conda env export --no-builds > envs/env_busco.yml
```

Le fichier `envs/env_busco.yml` contient la description de l'environnement
Conda. Il faut toutefois noter que SciPy 1.15.3 a été installé avec
`pip` et non avec Conda. Cette installation a donc été vérifiée séparément
avec :

```bash
python -m pip show scipy
``` 

## Choix du jeu de données BUSCO

Les premières analyses ont été réalisées avec le jeu de données
`arthropoda_odb10`. Ces résultats ont servi à évaluer une première fois
la complétude des génomes, mais ils ne constituent pas les résultats
finaux utilisés pour les comparaisons entre génomes.

Les analyses finales ont été harmonisées avec le jeu de données
`crustacea_odb12`, plus adapté au groupe étudié. Les génomes utilisés
pour les comparaisons finales ont été analysés avec le même jeu de
données afin que les pourcentages BUSCO soient comparables.

Nous avons ensuite poursuivi les analyses busco sur un nouveau jeu de données, `crustacea_odb12.2`.
Les résultats finaux retenus sont les dossiers contenant notamment :

- `short_summary.txt` ;
- `short_summary.json` ;
- `full_table.tsv` ;
- `missing_busco_list.tsv` ;
- les sorties de Miniprot ;
- les journaux d'exécution dans le dossier `logs/`.

Les anciennes analyses réalisées avec `arthropoda_odb10` sont conservées.

## Outils:
#  Orthofinder (Tsiambaka)
- Commande:  conda create \
    --prefix /data/projet2/conda/env_orthofinder \
    python=3.12 \
    -y

# MCScanX
- Commande: conda create \
    --prefix /data/projet2/conda/env_mcscanx \
    -c conda-forge \
    -c bioconda \
    mcscanx \
    openjdk \
    -y

