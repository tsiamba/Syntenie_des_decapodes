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

**Lancement de l'analyse BUSCO sur *Jaera*** (Tsiambaka)

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

**Tsiambaka**

- Lancement de BUSCO sur l'isopode *Jaera*, avec 3 cœurs sur le serveur.
- L'analyse a duré 24190 secondes.

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

### Vendredi 09 Octobre
Extraction des fichiers de génomes les plus lourds fait par le prof de /data/data_tutor/precomputed_busco.tar.gz (Tsiambaka) vers:
mkdir -p /data/projet2/Syntenie_des_decapodes/precomputed_crustacea_odb12
tar -xvf /data/data_tutor/precomputed_busco.tar.gz \
    -C /data/projet2/Syntenie_des_decapodes/precomputed_crustacea_odb12 \
    --wildcards "*/full_table.tsv" "*/short_summary*" "*/log/*"

=> Récupération des fichiers short_summary.txt pour lancer le diagramme de Sankey et le dot plot

---

## Samedi 11 octobre

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

**À compléter :** accessions des génomes concernés, commandes de lancement, versions des programmes, paramètres de ressources, messages d’erreur et état final de chaque analyse.

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

**À compléter :** date, personne ayant effectué la tentative, fichiers concernés, commandes exécutées pour corriger le problème et confirmation de la réussite du `push`.

### Conséquences sur la progression du projet

Les difficultés de mémoire ont conduit à avancer sur les scripts à partir des sorties disponibles, puis à récupérer des résultats précalculés pour certains génomes. Le changement de base de référence impose maintenant d’harmoniser les analyses retenues avant de produire les comparaisons finales.

Les sessions suivantes devront relier chaque relance ou correction à ses commandes, à ses logs et aux résultats effectivement utilisés.
