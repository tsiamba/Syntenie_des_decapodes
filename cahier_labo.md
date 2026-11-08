# Cahier de laboratoire : Synténie des décapodes

*Septembre–octobre 2026 — compléments et synthèse mis à jour le 29 octobre 2026*

Les précisions rétrospectives du 29 octobre complètent les entrées historiques sans attribuer de nouvelles commandes ou de nouvelles exécutions aux journées précédentes. Les anciens chemins sont conservés dans les commandes d'origine ; les emplacements actuels sont indiqués dans les compléments. Les commandes proposées pour la suite sont distinguées de celles dont une sortie a été consultée.

---

## Dimanche 13 septembre : choix des génomes

Les génomes ont été choisis selon plusieurs critères qui, dans l'ordre d'importance, sont les suivants :

1. Tous les génomes ont des *chromosome level assembly* ;
2. Tous les génomes de décapodes ont des scores BUSCO GC d'au moins 90 %, pour avoir une bonne complétude ;
3. Les génomes avec les meilleurs contig N50 ont été choisis de manière à garder une bonne contiguïté ;
4. Les génomes ont été choisis de manière à garder une diversité phylogénétique au sein des décapodes.

---

**Recul au 29 octobre 2026 sur le critère de sélection.** Le seuil de 90 % était un critère initial, et non une propriété vérifiée de tous les résultats finaux. En `crustacea_odb12`, *Penaeus vannamei* et *Cherax quadricarinatus* ont C < 90 %. Si l'on retient le seuil sur les seuls marqueurs complets à copie unique (S), *Macrobrachium nipponense* est également sous 90 %. Le tableau et les conséquences pour les comparaisons figurent dans le bilan critique de fin de cahier.

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

**Précision rétrospective du 29 octobre — exclusions Git.** Dans les règles consignées ci-dessus, `.fna` et `.gff` visent des noms exacts ; les motifs généraux attendus sont `*.fna` et `*.gff`. L'exclusion de `envs/` doit aussi être compatible avec le suivi des fichiers YAML et de `versions.txt`. L'état actuel du `.gitignore` et la publication effective de ces fichiers restent à vérifier ; aucune nouvelle correction ou publication Git n'est attestée par ce complément.

### Lundi 21 septembre

**Aurélio** · 1 h

- Modification du `.gitignore`
- Nouvel environnement pour BUSCO
- Lancement de l'analyse BUSCO
- Utilisation de `screen` pour conserver une session de travail ; `screen -r` permet de se rattacher à une session existante.

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

puis, pour repérer le FASTA avant le lancement de BUSCO (~ 1 h annoncé) :

```bash
FNA=$(find /data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data/GCA_965208005.1 -name "*_genomic.fna")
echo "$FNA"
```

**Précision rétrospective du 29 octobre — environnement et commande.** L'environnement local documenté est `/data/projet2/conda/env_busco`. Les commandes `find` et `echo` ci-dessus localisent le FASTA mais ne lancent pas BUSCO ; la commande complète du lancement de *Jaera* n'est pas consignée dans cette entrée. Les versions exactes de chaque résultat retenu sont établies à partir de ses en-têtes et résumés, et non déduites de l'environnement actuellement installé.

### Vendredi 25 septembre

**Aurélio** · 2 h

- J'ai essayé de faire marcher BUSCO : problème de serveur saturé par le script (8 cœurs → 4 cœurs).
- Modification du script et relance de BUSCO.

**Complément rétrospectif du 29 octobre — problème, fichiers et résultat.** Cette phase concerne les essais BUSCO locaux, dont le lanceur historique est `scripts/script_busco.sh`. Les sorties MetaEuk sont actuellement regroupées sous `Busco/busco_metaeuk/busco_output/` et les diagnostics disponibles dans `log_error_busco/`. La baisse du nombre de cœurs visait à limiter la charge, mais n'a pas permis de terminer tous les gros génomes. Le professeur a ensuite relancé les calculs concernés sur des machines plus puissantes avec succès, confirmant la limitation des ressources de notre cluster. Les commandes individuelles de cette journée ne sont pas conservées dans cette entrée.

### Dimanche 27 septembre

**Aurélio** · 1 h

- Problème avec certains génomes qui saturent le serveur.
- Création d'un fichier log où j'ai affiché tout ce que BUSCO m'a renvoyé : log_analyse_busco_metaeuk.txt

**Tsiambaka** · 30 min

- Lancement de BUSCO sur l'isopode *Jaera*, avec 3 cœurs sur le serveur.


**Complément rétrospectif du 29 octobre — fichier de suivi.** Le journal cité est actuellement situé dans `/data/projet2/Syntenie_des_decapodes/log_error_busco/log_analyse_busco_metaeuk.txt`. Il sert à conserver les messages d'exécution et les essais sur MetaEuk. La commande exacte de lancement de chaque essai doit être retrouvée dans les journaux disponibles ; elle n'est pas reconstituée ici.

### Lundi 28 septembre

**Aurélio** · 45 min

- Vérification des analyses BUSCO.
- Modification du fichier log pour ajouter les dernières infos sur l'analyse BUSCO.
- Essai de comprendre le problème d'analyse BUSCO.

**Complément rétrospectif du 29 octobre — contrôle des analyses.** Les vérifications portent sur les sorties BUSCO et leurs journaux. La commande de consultation utilisée le 28 septembre n'est pas consignée. Le contrôle du 29 octobre est reproductible avec les commandes `find`, `head` et `cat` enregistrées plus loin ; il distingue la présence des fichiers, les scores du résumé et la validation encore à réaliser des tables intégrales.

### Mardi 29 septembre

**Aurélio** · 20 min

- Vérification de la fin de l'analyse BUSCO.
- Modification du script pour relancer sur ceux qui ne sont pas passés.
- Mise à jour du fichier log.

---

**Complément rétrospectif du 29 octobre — relances.** Le script `scripts/script_busco_rerun.sh` est présent dans le projet. Son nom ne suffit pas à déterminer les options réellement employées lors de cette relance : la commande exacte et l'état final doivent être reliés aux journaux du génome concerné. Les anciennes tentatives sont conservées et ne sont pas assimilées automatiquement aux résultats retenus pour les comparaisons finales.

## Récupérer les fichiers depuis le cluster

À exécuter **en dehors de ssh** :

```bash
scp vitale@ptu.bigest-icube.fr:/data/projet2/Syntenie_des_decapodes/log_analyse_busco.md .
```

**Précision du 29 octobre.** Cette commande conserve le chemin historique. L'arborescence actuelle situe ce journal à `/data/projet2/Syntenie_des_decapodes/Busco/busco_metaeuk/busco_output/log_analyse_busco.md` : adapter le chemin source avant un nouveau transfert. Aucun nouveau transfert n'est consigné lors de cette mise à jour.

---

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

**Complément rétrospectif du 29 octobre — premières figures.** Les scripts concernés sont `scripts/sankey_syntenie.py` et, pour les essais de dot plots ultérieurs, `scripts/dotplot.py`. Les premiers Sankey MetaEuk sont rangés dans `Analyses/Diagramme_Sankey/Metaeuk/`, avec les sous-dossiers `busco_chr_organisme/` et `output/`. Ils constituent des résultats exploratoires issus d'`arthropoda_odb10`. Les chemins des scripts doivent être vérifiés après les déplacements. L'identité des chromosomes et la conservation de l'ordre des marqueurs restent à valider avant de tirer des conclusions biologiques de ces figures. Les commandes d'installation de Pandas et Plotly ainsi que la commande exacte du premier tracé ne sont pas consignées dans l'entrée du 6 octobre.

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


**Complément rétrospectif du 29 octobre — ressources du lanceur v1.** Le fichier concerné est `scripts/script_busco_miniprot.sh`. La commande historique utilise `nproc` pour fixer le nombre de cœurs et ne constitue pas une mesure de la mémoire nécessaire. Les ressources doivent être adaptées aux possibilités de la machine ou aux ressources attribuées au calcul ; le gestionnaire de tâches du cluster n'est pas identifié dans ce cahier. La référence `crustacea_odb12.2` correspond à cette série d'essais, distincte de la référence finale retenue, `crustacea_odb12`.

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
- Un des génomes concernés : `GCF_036320965.1` (2,65 Gb). Précision du 29 octobre d'après le résumé : 1 451 scaffolds et 8 059 contigs.
- Fichier d'erreur de miniprot vide
- Diagnostic initial : mémoire insuffisante sur le serveur (16 Go, sans swap). Confirmation ultérieure rapportée le 29 octobre : les programmes ont été relancés par le professeur sur des machines plus puissantes et ont terminé avec succès ; les ressources du cluster local étaient insuffisantes pour ces calculs.
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



**Complément rétrospectif du 29 octobre — commande et traces.** Le lanceur concerné est `scripts/script_busco_miniprot_2.sh`. La commande historique ci-dessus doit être relue avec la version du script réellement utilisée : certains lanceurs ajoutent eux-mêmes `busco_output/` au chemin donné par `-o`. L'option `-f` figurait dans les essais de la v2 et peut remplacer une sortie existante ; cette commande est conservée comme historique, sans nouvelle exécution. Les journaux disponibles sont regroupés sous `log_error_busco/`, `Busco/busco_miniprot/` et `Busco/precomputed_crustacea_odb12/log/`, selon l'essai. Le nom exact du fichier d'erreur vide n'est pas consigné ici et ne doit pas être inventé.

### Vendredi 09 Octobre
**Tsiambaka** · 1h
Extraction des résultats des génomes trop volumineux, recalculés avec succès par le professeur sur des machines plus puissantes. Archive source : `/data/data_tutor/precomputed_busco.tar.gz`.

Commandes historiques d'extraction :

```bash
mkdir -p /data/projet2/Syntenie_des_decapodes/precomputed_crustacea_odb12
tar -xvf /data/data_tutor/precomputed_busco.tar.gz \
    -C /data/projet2/Syntenie_des_decapodes/precomputed_crustacea_odb12 \
    --wildcards "*/full_table.tsv" "*/short_summary*" "*/log/*"
```

**Fichiers récupérés et usage.** Les `short_summary` fournissent les scores, les versions et les paramètres. Les positions destinées aux Sankey et aux dot plots proviennent des `full_table.tsv`. Cette extraction est sélective : l'absence de toutes les sorties intermédiaires de Miniprot ou de tous les journaux n'établit donc pas un échec du calcul du professeur.

**Emplacement actuel, vérifié le 29 octobre :** `/data/projet2/Syntenie_des_decapodes/Busco/precomputed_crustacea_odb12/`. Le déplacement a eu lieu après l'extraction ; l'ancien chemin reste dans les commandes historiques.

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

Commande historique pour repérer les dossiers de sortie. Précision du 29 octobre : la présence d'un résumé est un indice de bilan, à compléter par le contrôle des tables et des journaux disponibles.

```bash
ls precomputed_crustacea_odb12/precomputed/BUSCO/busco_output/*
```


## Dimanche 11 Octobre
**Tsiambaka** · 1h20  min

- L'analyse busco avec Miniprot pour ce génome ici : resultats_busco_GCF_036320965.1_ASM3632096v1_genomic.fna
 a été killed, je pense à cause de problèmes de ressources. 
- Je vais relancer cette analyse toute seule.
- Commande : 
Création d'une session nommée avec `screen -S resultats_busco_GCF_036320965.1_ASM3632096v1_genomic_notkilled.fna` ; `screen -r` sert à se rattacher à une session existante.
Lancer le busco : busco -f -i /data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data/GCF_036320965.1/*_genomic.fna -o resultats_busco_GCF_036320965.1_ASM3632096v1_genomic_notkilled.fna -m genome -l crustacea_odb12 -c 3 --miniprot
- Je vais rajouter dans le dossier scripts, un nouveau script qui servira pour réaliser le dotplot de la conservation de gènes entre les différents génomes. Ceci ne sera qu'un script qui servira de test pour le moment. Nom du fichier :/data/projet2/Syntenie_des_decapodes/scripts/dotplot.py

**Jade** · 15 mins total

- Suite du rerun des génomes restants (en cours) [GCF_035594125.1; GCF_042767895.1]
- GCF_036320965.1 échoue toujours (3 essais).

**Complément rétrospectif du 29 octobre — issue des tentatives.** Les essais locaux répétés de `GCF_036320965.1` n'ont pas permis d'achever ce calcul sur notre cluster. Le résultat retenu provient de la relance réussie du professeur et se trouve actuellement dans `Busco/precomputed_crustacea_odb12/BUSCO/BUSCO_GCF_036320965.1_ASM3632096v1_genomic.fna/`. La commande BUSCO avec `-f` ci-dessus est historique ; aucune nouvelle relance n'a été effectuée lors de l'inventaire du 29 octobre. La présence de `scripts/dotplot.py` atteste un script de test, pas une analyse finale de colinéarité.

## Difficultés rencontrées et adaptations du travail

Septembre–octobre 2026 — Tsiambaka, Aurélio, Jade. Synthèse complétée le 29 octobre.

### Ressources insuffisantes pour certains calculs BUSCO

Les analyses locales de certains génomes volumineux ont été interrompues, notamment avec le code `-9` (SIGKILL) à l'étape `miniprot_index`. La diminution du nombre de cœurs n'a pas permis de terminer tous les calculs. Le professeur a ensuite relancé les programmes sur des machines plus puissantes et les calculs ont réussi. Ce résultat confirme la limitation des ressources du cluster local ; le manque de mémoire a été retenu comme explication des blocages rencontrés.

Les diagnostics consignés comprenaient `free -h`, `ulimit -a`, la lecture de `/proc/self/cgroup` et `systemctl show "user-$(id -u).slice" -p MemoryMax`. Le serveur local disposait d'environ 16 Go de RAM, sans swap. L'absence de message OOM retrouvé dans `dmesg` et le fichier d'erreur Miniprot vide avaient limité le diagnostic initial ; la réussite ultérieure des relances du professeur a permis d'aboutir à la solution opérationnelle.

| Élément | Fichier ou emplacement actuel | Rôle et état documenté |
|---|---|---|
| Lanceur MetaEuk | `scripts/script_busco.sh` | Essais historiques, puis réduction du nombre de cœurs |
| Relances MetaEuk | `scripts/script_busco_rerun.sh` | Options réellement utilisées à retrouver dans les journaux |
| Lanceurs Miniprot | `scripts/script_busco_miniprot.sh` et `scripts/script_busco_miniprot_2.sh` | Essais avec réduction des cœurs ; présence historique de `-f` dans la v2 |
| Diagnostics BUSCO conservés | `log_error_busco/busco_693521.log`, `log_error_busco/busco_771368.log`, `log_error_busco/log_analyse_busco_metaeuk.txt` | Messages disponibles pour documenter les problèmes ; le détail de chaque tentative doit être relié à son accession |
| Sorties des essais locaux | `Busco/busco_metaeuk/busco_output/` et `Busco/busco_miniprot/busco_output/` | Historique, dont certaines tentatives incomplètes |
| Résultats utilisables fournis par le professeur | `Busco/precomputed_crustacea_odb12/BUSCO/BUSCO_GCF_*/` | Cinq résultats retenus pour les gros génomes ; versions vérifiées dans les résumés |
| Journaux extraits de l'archive | `Busco/precomputed_crustacea_odb12/log/` | Journaux disponibles de la série du professeur |

Les cinq génomes dont les résultats retenus viennent du professeur sont `GCF_015104395.2`, `GCF_036320965.1`, `GCF_038502225.1`, `GCF_040412425.1` et `GCF_040958095.1`. Cette solution a permis de poursuivre le projet sans nouveau calcul de ces génomes sur le cluster local.

### Changements de référence et différences de versions

La chronologie retenue est : premiers essais MetaEuk avec `arthropoda_odb10`, essais Miniprot avec `crustacea_odb12.2`, puis sélection finale commune en `crustacea_odb12` pour correspondre aux résultats du professeur. Les sorties en `odb10` et `odb12.2` restent conservées comme historique et ne sont pas mélangées directement aux comparaisons finales.

L'inventaire du 29 octobre retrouve 11 tables en `crustacea_odb12`, toutes associées à la référence datée du 22 mai 2026 et à 1 536 groupes BUSCO. Une relance générale n'est donc plus requise pour obtenir cette référence ; les éventuels recalculs devront répondre à un problème identifié lors des contrôles restants.

Six résultats locaux utilisent BUSCO 6.1.0 et Miniprot 0.18-r281 ; les cinq résultats du professeur utilisent BUSCO 5.8.2 et Miniprot 0.13-r248. La référence est commune, mais les versions logicielles diffèrent : cette information doit accompagner les tableaux, les figures et leur interprétation.

### Organisation, noms de sorties et chemins des scripts

Le dossier `Busco/precomputed_crustacea_odb12/BUSCO/` regroupe désormais les six résultats locaux et les cinq résultats de l'enseignant. Son nom ne signifie donc pas que tous les calculs ont été effectués par l'enseignant. Les préfixes des dossiers ne remplacent pas les informations de provenance inscrites dans les résumés.

Les commandes historiques peuvent encore utiliser les anciens chemins avant regroupement sous `Busco/`. Pour les nouvelles analyses, utiliser les emplacements actuels. Les chemins relatifs de `scripts/sankey_syntenie.py`, `scripts/dotplot.py` et des lanceurs BUSCO restent à vérifier après les déplacements. Le lanceur v2 et son argument `-o` doivent aussi être relus ensemble afin d'éviter un éventuel double niveau `busco_output/`. Aucune correction de ces scripts n'est présentée ici comme déjà effectuée.

Les sorties de consultation obtenues avec `find`, `head` et `cat` sont affichées dans le terminal. Elles ne constituent pas de nouveaux tableaux de positions ou de nouvelles figures.

### Difficultés de synchronisation avec GitHub

Une difficulté de `git push` a été signalée par Aurélio le 9 octobre, dans un contexte de suppression de fichiers d'un ancien environnement précédemment suivis par Git. L'état conservé est dans `log_error_busco/git_status.txt`. Ce fichier concerne le suivi Git et ne constitue pas un diagnostic mémoire.

Le message exact de refus du `push`, la commande de correction et la confirmation de la réussite restent à consigner. Les suppressions de fichiers suivis, à elles seules, ne suffisent pas à établir la cause technique du refus. L'organisation locale actuelle n'est pas encore confirmée comme publiée sur GitHub.

Les règles `.gitignore` consignées en septembre doivent être vérifiées pour les extensions `*.fna` et `*.gff`, les dossiers BUSCO et les exceptions permettant de suivre les descriptions d'environnement. Les YAML et `versions.txt` sont des fichiers de documentation ; les installations Conda et les gros résultats restent sur le cluster.

### Conséquences sur les analyses

Les difficultés de calcul ont conduit à développer les premières visualisations à partir des résultats MetaEuk disponibles, puis à compléter la série finale avec les relances réussies du professeur. Les étapes suivantes reposent sur les 11 tables `crustacea_odb12` sélectionnées, avec contrôle des statuts, des coordonnées et des chromosomes réels. La présence de scripts et de dossiers MCScanX ou OrthoFinder ne démontre pas que ces analyses ont déjà été exécutées.

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

L'environnement `env_busco` apparaît actif dans le relevé ci-dessous. Ce relevé décrit l'installation locale au 29 octobre ; les versions effectivement utilisées pour les résultats retenus sont vérifiées dans leurs en-têtes et résumés. Commande de consultation de la liste des environnements :

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

L'astérisque indique que `env_busco` est actif dans ce relevé. Les consultations récentes de fichiers avec `find`, `head` et `cat` ont été effectuées depuis une invite `(base)` ; elles ne nécessitent pas d'activer BUSCO et ne relancent aucun calcul. Les six analyses locales retenues sont documentées par leurs résumés BUSCO 6.1.0 ; les cinq résultats du professeur proviennent d'une autre installation.

Les principaux logiciels et versions relevés dans l'environnement BUSCO local étaient :

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

### Autres environnements du projet et rôle de chacun

| Environnement | Emplacement | Version principale relevée | Utilisation documentée |
|---|---|---|---|
| `env_busco` | `/data/projet2/conda/env_busco` | BUSCO 6.1.0 ; Miniprot 0.18 | Calculs BUSCO locaux ; Pandas, NumPy, Matplotlib et Plotly disponibles pour le traitement des résultats |
| `env_orthofinder` | `/data/projet2/conda/env_orthofinder` | OrthoFinder 3.2 | Environnement préparé pour l'inférence d'orthologie ; aucune sortie d'analyse OrthoFinder n'a été examinée lors de cet inventaire |
| `env_mcscanx` | `/data/projet2/conda/env_mcscanx` | MCScanX 1.0.0 | Environnement préparé pour l'analyse de colinéarité ; aucune sortie MCScanX n'a été examinée lors de cet inventaire |

Les fichiers de description sont `envs/env_busco.yml`, `envs/env_orthofinder.yml`, `envs/env_mcscanx.yml` et `envs/versions.txt`. Les versions principales ont été relevées dans `versions.txt`. La ligne OrthoFinder contient des codes de couleur du terminal : sa présentation est à nettoyer, sans changement de version. Le script `scripts/export_env.sh` est présent ; son exécution n'est pas attestée par les sorties consultées pour ce complément.

Les commandes de consultation déjà consignées pour BUSCO incluent `conda env list`, `conda list`, `busco --version`, `miniprot --version`, `python --version` et `python -m pip show scipy`. Les YAML décrivent les installations locales ; ils ne décrivent pas automatiquement l'environnement BUSCO 5.8.2 du professeur.

## Choix du jeu de données BUSCO

La référence retenue pour les comparaisons finales est **`crustacea_odb12`, datée du 22 mai 2026, avec 1 536 groupes BUSCO**. Elle est adaptée aux crustacés étudiés, y compris l'isopode *Jaera praehirsuta*, et commune aux résultats locaux et à ceux fournis par le professeur pour les génomes trop volumineux. Ce choix permet de rechercher les mêmes groupes dans les 11 génomes sans relancer les calculs lourds sur le cluster local.

Les premières analyses MetaEuk en `arthropoda_odb10` et les essais Miniprot en `crustacea_odb12.2` sont conservés comme historique. La mention d'`odb12.2` dans les entrées anciennes décrit ces essais et ne remplace pas la référence finale `crustacea_odb12`.

Les fichiers effectivement consultés pour sélectionner les résultats sont les `full_table.tsv` et les `short_summary*.txt`. Les résumés JSON servent à une lecture automatisée. Les fichiers intermédiaires de Miniprot, `missing_busco_list.tsv` et tous les journaux ne sont pas nécessairement présents dans l'extraction sélective de l'archive du professeur ; ils ne sont donc pas exigés comme preuve de présence de chaque résultat dans ce dossier.

Le choix de la référence, le tableau des scores et leur provenance sont documentés dans `Analyses/busco_crustacea_odb12.md`. Les différences de versions BUSCO et Miniprot restent une limite méthodologique à rapporter.

## Outils

### OrthoFinder — Tsiambaka

Commande consignée pour créer l'environnement Python :

```bash
conda create \
    --prefix /data/projet2/conda/env_orthofinder \
    python=3.12 \
    -y
```

Cette commande crée l'environnement Python ; elle ne contient pas l'installation d'OrthoFinder lui-même. Le relevé ultérieur indique OrthoFinder 3.2 ; sa commande d'installation exacte reste à consigner.

### MCScanX

Commande d'installation consignée :

```bash
conda create \
    --prefix /data/projet2/conda/env_mcscanx \
    -c conda-forge \
    -c bioconda \
    mcscanx \
    openjdk \
    -y
```

Le dossier `/data/projet2/conda/pkgs` est le cache des paquets Conda ; les programmes actifs sont utilisés depuis leurs environnements.

Commandes de configuration consignées :

```bash
mkdir -p /data/projet2/conda/pkgs
conda config --prepend pkgs_dirs /data/projet2/conda/pkgs
```

Le nettoyage du cache avec `conda clean --all -y` avait été envisagé en cas de saturation de l'espace disque. Son exécution et le gain d'espace ne sont pas documentés ; il ne doit pas être présenté comme une correction déjà réalisée ni comme une solution au manque de RAM pendant les calculs.

## Bibliographie:
- OrthoFinder: phylogenetic orthology inference for comparative genomics
- MCScanX: a toolkit for detection and evolutionary analysis of gene synteny and collinearity

## Jeudi 29 octobre 2026 : organisation et vérification des résultats BUSCO
**Aurélio**: 2h
### Objectif

Organiser les fichiers du projet, identifier les résultats BUSCO disponibles
en `crustacea_odb12` et documenter leur provenance, leurs versions et leurs scores
avant les analyses de synténie.

### 1. Organisation des dossiers

Les dossiers BUSCO sont désormais regroupés sous :

```text
/data/projet2/Syntenie_des_decapodes/Busco/
├── busco_downloads/
├── busco_metaeuk/
├── busco_miniprot/
└── precomputed_crustacea_odb12/
```

Les analyses et leur documentation sont regroupées sous :

```text
/data/projet2/Syntenie_des_decapodes/Analyses/
├── Diagramme_Sankey/
│   ├── Metaeuk/
│   └── Miniprot/
├── MCscanX/
├── Orthofinder/
└── busco_crustacea_odb12.md
```

### 2. Localisation des tables BUSCO

Commande exécutée pour retrouver les tables en `crustacea_odb12` :

```bash
find /data/projet2/Syntenie_des_decapodes/Busco/precomputed_crustacea_odb12/BUSCO \
  -type f \
  -path '*/run_crustacea_odb12/full_table.tsv' \
  -print
```

**Résultat :** 11 fichiers `full_table.tsv` ont été retrouvés,
correspondant aux dix décapodes étudiés et à l’isopode
*Jaera praehirsuta* utilisé comme groupe externe.

Malgré son nom, le dossier `precomputed_crustacea_odb12/BUSCO/`
regroupe actuellement les résultats locaux et ceux fournis par
l’enseignant pour les génomes trop volumineux pour notre cluster.

### 3. Vérification des en-têtes

Commande exécutée :

```bash
find /data/projet2/Syntenie_des_decapodes/Busco/precomputed_crustacea_odb12/BUSCO \
  -type f \
  -path '*/run_crustacea_odb12/full_table.tsv' \
  -print -exec head -n 12 {} \;
```

**Résultat :** les onze tables indiquent la même référence :

- Jeu de données : `crustacea_odb12`
- Date de création : 22 mai 2026
- Nombre de groupes BUSCO recherchés : 1 536
- Nombre de génomes ayant servi à construire la référence : 25

Ces 25 génomes sont ceux de la référence BUSCO et ne correspondent
pas au nombre de génomes de notre projet.

### 4. Consultation des résumés et des versions utilisées

Commande exécutée :

```bash
find /data/projet2/Syntenie_des_decapodes/Busco/precomputed_crustacea_odb12/BUSCO \
  -type f \
  -name 'short_summary*.txt' \
  -print -exec cat {} \;
```

**Résultat :** 22 résumés ont été affichés, correspondant à
11 analyses. Chaque analyse possède deux résumés concordants :
un dans le dossier `run_crustacea_odb12/` et un résumé spécifique
dans son dossier parent.

Toutes les analyses utilisent le mode `euk_genome_min`,
Miniprot et HMMER 3.4.

Deux ensembles de versions sont présents :

| Origine | Nombre de génomes | BUSCO | Miniprot |
|---|---:|---|---|
| Calculs locaux | 6 | 6.1.0 | 0.18-r281 |
| Résultats fournis par l’enseignant | 5 | 5.8.2 | 0.13-r248 |

Les résultats de l’enseignant concernent les accessions suivantes :

- `GCF_015104395.2`
- `GCF_036320965.1`
- `GCF_038502225.1`
- `GCF_040412425.1`
- `GCF_040958095.1`
cat >> /data/projet2/Syntenie_des_decapodes/cahier_labo.md <<'EOF_CAHIER_SVG'

## Ajout de l’export SVG aux comparaisons de contenu chromosomique
**Aurélio** : 30 min

Produire des figures vectorielles pour les comparaisons entre les 11 génomes, soit 55 paires distinctes. Le format SVG permet d’agrandir les figures sans perte de qualité et facilite leur intégration dans le rapport.

Pour les cartes de Jaccard, les valeurs positives sont désormais inscrites directement dans les cases. Les fichiers HTML sont conservés pour consulter les informations détaillées au survol.

### Scripts et fichiers d’entrée

Les deux scripts modifiés sont :

- `scripts/comparaison_contenu_chr.py` : production des cartes de similarité de Jaccard en HTML et SVG, accompagnées des tableaux TSV.
- `scripts/sankey_syntenie.py` : production des diagrammes Sankey en HTML et SVG, accompagnés des tableaux TSV et des bilans JSON.

Les comparaisons utilisent le master enrichi :

```text
/data/projet2/Syntenie_des_decapodes/genomes/master_positions_busco.tsv
```

Ce fichier contient les marqueurs BUSCO retenus, leurs positions et les informations permettant de distinguer chromosomes et scaffolds. L’export SVG ne nécessite pas de télécharger à nouveau les séquences génomiques.

### Environnement et difficultés rencontrées

L’export SVG des cartes de Jaccard utilise directement la bibliothèque standard de Python. L’export des Sankey repose sur Plotly, Kaleido et Chrome.

Lors du premier lancement des Sankey, la validation des données a fonctionné, mais l’export SVG a échoué dès la première comparaison. Les fichiers HTML et TSV de cette comparaison ont été conservés. L’option `--require-svg` a interrompu le traitement pour éviter de répéter cet échec sur les 55 paires.

Le diagnostic avec `ldd` a révélé plusieurs bibliothèques Linux manquantes pour Chrome : ATK/AT-SPI, CUPS, certaines bibliothèques X11, GBM, Cairo, Pango et ALSA.

Les dépendances ont été installées dans l’environnement existant :

```bash
conda install -y --prefix /data/projet2/conda/env_sankey \
  --override-channels -c conda-forge \
  'at-spi2-core>=2.46' 'libcups<3' \
  xorg-libxcomposite xorg-libxdamage xorg-libxfixes xorg-libxrandr \
  mesalib cairo pango alsa-lib
```

Un lanceur a été créé pour permettre à Chrome de trouver les bibliothèques de cet environnement :

```text
/data/projet2/conda/chrome/chrome-cluster.sh
```

Ce lanceur configure également les emplacements des caches et fichiers temporaires sous `/data/projet2/`. Les paquets Conda sont stockés dans `/data/projet2/conda/pkgs`, sans installation nécessitant `sudo`.

Après correction, la commande de vérification affiche :

```text
Google Chrome for Testing 142.0.7444.175
```

Cette vérification confirme le démarrage de Chrome. La validation complète nécessite ensuite la réussite d’un petit export SVG, puis la génération des figures.

### Commandes de génération

Depuis la racine du projet :

```bash
conda activate /data/projet2/conda/env_sankey
cd /data/projet2/Syntenie_des_decapodes
```

Cartes de Jaccard :

```bash
python scripts/comparaison_contenu_chr.py \
  --all-pairs \
  --master-tsv genomes/master_positions_busco.tsv \
  --out-dir Analyses/Jaccard
```

Diagrammes Sankey, après réussite du test d’export :

```bash
python scripts/sankey_syntenie.py \
  --all-pairs \
  --master-tsv genomes/master_positions_busco.tsv \
  --outdir Analyses/Diagramme_Sankey \
  --runtime-dir /data/projet2/conda \
  --browser-path /data/projet2/conda/chrome/chrome-cluster.sh \
  --require-svg \
  --overwrite
```

### Outputs et utilisation

Les sorties sont enregistrées dans :

```text
/data/projet2/Syntenie_des_decapodes/Analyses/Jaccard/
/data/projet2/Syntenie_des_decapodes/Analyses/Diagramme_Sankey/
```

Les SVG servent à la lecture des valeurs et à la préparation des figures du rapport. Les HTML permettent l’exploration interactive, tandis que les TSV conservent les valeurs numériques exactes.

Dans les cartes SVG de Jaccard, les scores positifs sont affichés à trois décimales, avec une indication spécifique pour les valeurs inférieures à 0,001. Les cases sans nombre correspondent à un score nul.

Cette étape améliore la présentation des comparaisons de contenu chromosomique. L’interprétation reste fondée sur les marqueurs partagés et leur répartition entre chromosomes. La conservation de leur ordre doit être examinée séparément avec les dotplots et les analyses de voisinage.

À ce stade, le démarrage de Chrome est confirmé ; la réussite de l’export SVG et la production complète des 55 comparaisons restent à consigner après exécution.

EOF_CAHIER_SVG
Les effectifs indiqués dans chaque résumé sont cohérents :
S + D + F + M = 1 536 et C = S + D.

### 5. Documentation des résultats et du choix de référence

Le fichier de synthèse est situé à :

```text
/data/projet2/Syntenie_des_decapodes/Analyses/busco_crustacea_odb12.md
```

Édition du document avec Nano :

```bash
cd /data/projet2/Syntenie_des_decapodes/Analyses
nano busco_crustacea_odb12.md
```

Ce document rassemble :

- le tableau des scores BUSCO et des identifiants des génomes ;
- la justification du choix de `crustacea_odb12` ;
- la provenance des résultats ;
- les versions des logiciels utilisées.

`crustacea_odb12` a été retenu car il est adapté aux crustacés étudiés
et commun aux résultats locaux et aux résultats de l’enseignant.
Il permet de comparer les mêmes groupes de marqueurs entre génomes
sans imposer de nouveaux calculs lourds.

Les anciennes analyses en `arthropoda_odb10` et
`crustacea_odb12.2` restent conservées comme historique.

### 6. Fichiers utilisés et description des sorties

| Fichier ou dossier | Description et utilisation |
|---|---|
| `full_table.tsv` | Résultats détaillés : identifiant BUSCO, statut, séquence, coordonnées, brin, score et longueur. Une ligne `Missing` peut ne contenir que l'identifiant et le statut ; un groupe `Duplicated` peut avoir plusieurs lignes. Fichier central pour extraire les positions des marqueurs. |
| `run_crustacea_odb12/short_summary.txt` | Résumé lisible des scores, effectifs, paramètres et versions. |
| `short_summary.specific.crustacea_odb12.*.txt` | Résumé spécifique placé dans le dossier parent de l’analyse ; même bilan que le résumé précédent. |
| `short_summary.specific.crustacea_odb12.*.json` | Résumé structuré destiné aux traitements automatiques. |
| `logs/` et `precomputed_crustacea_odb12/log/` | Journaux disponibles pour retrouver les diagnostics et les problèmes d’exécution. |
| `Analyses/busco_crustacea_odb12.md` | Document de synthèse et de justification des résultats retenus. |

Pour cet inventaire, les vérifications ont été effectuées directement
avec `find`, `head` et `cat`, sans nouveau script d’analyse.

Les sorties de ces commandes ont été affichées dans le terminal :
elles n’ont pas créé de nouveau fichier TSV ou CSV et n’ont pas
modifié les résultats BUSCO.

### 7. Points à prendre en compte et prochaines étapes

- Les versions de BUSCO et de Miniprot diffèrent entre les deux séries :
  cette différence doit être conservée dans la description des méthodes.
- Le seuil initial de 90 % de BUSCO à copie unique n’est pas atteint
  par *Penaeus vannamei*, *Macrobrachium nipponense* et
  *Cherax quadricarinatus*. Leur inclusion doit être justifiée.
- Chez *Jaera praehirsuta*, 371 des 1 492 BUSCO complets présentent
  des codons stop internes, soit E = 24,9 %. Ce point devra être
  examiné avant une utilisation des séquences pour la phylogénie.

- [ ] Vérifier les correspondances entre séquences et vrais chromosomes.
- [ ] Extraire les marqueurs complets à copie unique et leurs positions.
- [ ] Déterminer les marqueurs communs à chaque comparaison.

### 8. Résumé et recul sur les résultats BUSCO

Les 11 analyses sélectionnées disposent d'une table de positions et de résumés concordants en `crustacea_odb12`. La majorité des génomes présente une forte proportion de marqueurs complets. Cela évalue la récupération des marqueurs BUSCO et constitue une base de travail pour la synténie, dont les mesures restent à réaliser.

Les scores C, S, D, F, M et E sont en pourcentage. L'effectif S est le nombre de groupes complets à copie unique.

| Espèce | Identifiant du génome | C | S | D | F | M | Effectif S | E |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| *Jaera praehirsuta* | GCA_965208005.1 | 97,1 | 94,6 | 2,5 | 1,0 | 1,9 | 1 453 | 24,9 |
| *Penaeus chinensis* | GCF_019202785.1 | 96,1 | 96,0 | 0,1 | 1,8 | 2,1 | 1 474 | 6,8 |
| *Portunus trituberculatus* | GCF_017591435.1 | 98,4 | 98,0 | 0,4 | 0,8 | 0,8 | 1 505 | 7,3 |
| *Penaeus vannamei* | GCF_042767895.1 | 86,5 | 85,3 | 1,2 | 5,7 | 7,8 | 1 310 | 7,8 |
| *Eriocheir sinensis* | GCF_024679095.1 | 98,9 | 95,1 | 3,8 | 0,3 | 0,8 | 1 460 | 5,5 |
| *Scylla paramamosain* | GCF_035594125.1 | 99,9 | 99,2 | 0,7 | 0,1 | 0,1 | 1 523 | 8,1 |
| *Macrobrachium rosenbergii* | GCF_040412425.1 | 97,3 | 96,7 | 0,5 | 2,3 | 0,5 | 1 486 | 3,4 |
| *Procambarus clarkii* | GCF_040958095.1 | 98,5 | 91,9 | 6,6 | 0,9 | 0,6 | 1 411 | 2,0 |
| *Macrobrachium nipponense* | GCF_015104395.2 | 90,5 | 87,3 | 3,2 | 7,0 | 2,5 | 1 341 | 4,3 |
| *Panulirus ornatus* | GCF_036320965.1 | 97,8 | 96,9 | 0,9 | 1,8 | 0,4 | 1 488 | 2,3 |
| *Cherax quadricarinatus* | GCF_038502225.1 | 88,5 | 87,5 | 1,0 | 5,5 | 6,0 | 1 344 | 2,4 |

**Définitions.** C = complets, S = complets à copie unique, D = complets dupliqués, F = fragmentés, M = manquants. E désigne la proportion des BUSCO complets contenant des codons stop internes. Dans les résumés consultés, les effectifs entiers vérifient C = S + D et S + D + F + M = 1 536 pour chaque génome ; de petits écarts dans les sommes des pourcentages proviennent des arrondis. Ce contrôle concerne les résumés et ne remplace pas le comptage des identifiants dans les tables intégrales.

**Comparabilité et provenance.** Le recours aux machines plus puissantes du professeur a permis de terminer les cinq calculs bloqués localement. Les six calculs locaux et les cinq résultats du professeur utilisent la même référence et Miniprot, mais des versions différentes du logiciel et du prédicteur. On ne peut pas chiffrer l'effet de ces différences avec les seuls résumés ; elles doivent être mentionnées dans les méthodes et prises en compte dans l'interprétation.

**Choix des génomes.** *P. vannamei* (C = 86,5 %, S = 85,3 %) et *C. quadricarinatus* (C = 88,5 %, S = 87,5 %) sont sous le seuil de 90 % pour les deux indicateurs. *M. nipponense* atteint C = 90,5 %, mais S = 87,3 %. Le critère initial doit préciser s'il porte sur C ou S, et le maintien de ces espèces doit être justifié. Le nombre de marqueurs comparables devra être fourni pour chaque paire ; un score ne doit pas être interprété sans connaître ce nombre.

**Duplication et qualité des séquences.** *P. clarkii* présente le plus fort taux de duplication de cette série (D = 6,6 %, soit 102 groupes). Les résumés ne permettent pas d'attribuer une cause biologique ou technique à ce résultat. Chez *Jaera*, 371 des 1 492 BUSCO complets contiennent des codons stop internes (E = 24,9 %). Les marqueurs concernés devront être identifiés avant une éventuelle utilisation des séquences en phylogénie ; le résumé ne précise pas combien se trouvent parmi les marqueurs à copie unique. Les autres génomes ont un E compris entre 2,0 % et 8,1 %.

**Portée pour la synténie.** Les effectifs à copie unique vont de 1 310 à 1 523 par génome. Ce sont des candidats pour l'extraction, avant contrôle des coordonnées et de leur localisation sur de vrais chromosomes. Le nombre de marqueurs communs, la conservation du contenu chromosomique et la conservation de l'ordre ne sont pas encore établis par les résultats consignés dans cette vérification. Les scores de complétude seuls ne démontrent ni fusion, ni fission, ni inversion, et ne permettent pas de classer les paires de génomes selon leur conservation synténique.

### 9. Contrôles restant à effectuer et traçabilité

- [ ] Lire les tables avec le séparateur tabulation ; gérer les lignes `Missing` sans coordonnées et les groupes `Duplicated` à plusieurs lignes.
- [ ] Pour les gènes du brin négatif dont les bornes sont décroissantes, conserver les coordonnées originales et le brin, puis dériver les bornes minimale et maximale pour l'analyse.
- [ ] Sélectionner les marqueurs complets à copie unique communs aux génomes comparés, avec des positions exploitables, et consigner les exclusions.

### Création et contrôle du tableau maître des positions BUSCO

Regrouper les positions des marqueurs BUSCO complets à copie unique des onze génomes dans un fichier CSV commun, à partir des résultats existants en `crustacea_odb12`. Cette étape ne relance pas BUSCO : elle prépare les données pour les comparaisons de synténie.

### Environnement et fichiers utilisés

Le traitement et le contrôle utilisent Python et Pandas dans l'environnement Conda `/data/projet2/conda/env_busco`. Plotly n'est pas nécessaire pour cette extraction.

| Élément | Emplacement ou rôle |
|---|---|
| Script de création | `/data/projet2/Syntenie_des_decapodes/scripts/master_csv_odb12.py` |
| Dossier des onze résultats | `/data/projet2/Syntenie_des_decapodes/Busco/precomputed_crustacea_odb12/BUSCO/` |
| Fichier d'entrée par génome | `<dossier_du_génome>/run_crustacea_odb12/full_table.tsv` |
| Fichier produit | `/data/projet2/Syntenie_des_decapodes/Analyses/Diagramme_Sankey/Miniprot/output/master_positions_busco.csv` |

Les entrées comprennent les six résultats locaux et les cinq résultats du professeur, tous en `crustacea_odb12`. Les différences de versions BUSCO et Miniprot décrites précédemment restent associées à ces résultats.

### Adaptation du script de création

Le script a été adapté pour :

- utiliser le chemin actuel sous `Busco/precomputed_crustacea_odb12/BUSCO/` ;
- corriger le nom de la référence en `run_crustacea_odb12` ;
- reconnaître les deux préfixes de dossiers présents : `BUSCO_` et `resultats_busco_`, en ignorant notamment `busco_downloads/` ; le motif littéral `startswith("*.fna")` ne convenait pas à cette recherche ;
- extraire l'accession complète avec sa version, sans conserver tout le nom du fichier FASTA dans `Organisme` ;
- lire les dix colonnes tabulées des tables BUSCO ;
- retenir les lignes `Complete` et exclure les identifiants apparaissant plusieurs fois dans une même table, sans choisir arbitrairement une copie ;
- vérifier les coordonnées numériques et le brin, puis calculer `Start = min(bornes)` et `End = max(bornes)`, sans décalage de position ;
- conserver les identifiants de séquences au lieu de les renommer artificiellement `Chr 1`, `Chr 2`, etc. ;
- concaténer les données dans un CSV unique et les trier par génome, séquence, position et identifiant BUSCO.

La version proposée utilise `to_csv(..., mode="x")` : elle refuse de remplacer un CSV déjà existant. Aucun tableau individuel ni aucune figure n'est produit par cette version du script.

### Problème rencontré au lancement et solution

Depuis le dossier `scripts/`, une première tentative a utilisé :

```bash
./master_csv_odb12.py
```

L'invite indiquait alors `(base)`. Les messages obtenus étaient notamment :

```text
./master_csv_odb12.py: line 1: import: command not found
./master_csv_odb12.py: line 2: import: command not found
./master_csv_odb12.py: line 3: import: command not found
./master_csv_odb12.py: line 8: PROJECT_DIR: command not found
./master_csv_odb12.py: line 10: syntax error near unexpected token `('
```

Le fichier Python avait été interprété par le shell. Il s'agissait d'un problème de lancement du script d'extraction, sans nouveau calcul BUSCO.

La commande de lancement corrigée retenue est :

```bash
cd /data/projet2/Syntenie_des_decapodes/scripts
conda activate /data/projet2/conda/env_busco
python master_csv_odb12.py
```

L'ajout d'une ligne `#!/usr/bin/env python3` et l'utilisation de `chmod +x` avaient également été proposés pour permettre le lancement direct ; leur réalisation n'est pas confirmée dans les sorties transmises. La sortie de création du CSV n'a pas été transmise, mais le fichier a ensuite été lu et contrôlé avec succès dans `env_busco`.

### Description du fichier de sortie

`master_positions_busco.csv` est un fichier texte séparé par des virgules, avec un en-tête et sans colonne d'index Pandas. Il contient une ligne par couple `(Organisme, Busco_id)` retenu.

| Colonne | Description |
|---|---|
| `Organisme` | Accession versionnée de l'assemblage, par exemple `GCF_035594125.1` |
| `Chromosome` | Copie provisoire de `Sequence` ; l'identité d'un chromosome réel n'est pas encore validée |
| `Sequence` | Identifiant original de la séquence sur laquelle BUSCO localise le marqueur |
| `Busco_id` | Identifiant du groupe BUSCO complet à copie unique |
| `Start` | Minimum des deux bornes BUSCO natives |
| `End` | Maximum des deux bornes BUSCO natives |
| `Strand` | Brin d'origine, `+` ou `-` |

Le script ne crée pas de colonnes `raw_start` ou `raw_end`. Les bornes initiales restent consultables dans les `full_table.tsv` sources, qui ne sont pas modifiés. Aucune conversion BED ou convention de décalage 0-based/1-based n'est appliquée.

### Contrôle du CSV effectué dans le terminal

Commande exécutée et sortie transmises depuis l'environnement `env_busco` :

```bash
conda activate /data/projet2/conda/env_busco

python - <<'PY'
import pandas as pd

path = (
    "/data/projet2/Syntenie_des_decapodes/"
    "Analyses/Diagramme_Sankey/Miniprot/output/"
    "master_positions_busco.csv"
)

df = pd.read_csv(path)

print("BUSCO à copie unique par génome :")
print(df.groupby("Organisme").size().to_string())

print("\nNombre de génomes :", df["Organisme"].nunique())
print("Nombre de positions :", len(df))
print(
    "Doublons marqueur/génome :",
    df.duplicated(["Organisme", "Busco_id"]).sum(),
)
print(
    "Coordonnées manquantes :",
    df[["Start", "End"]].isna().sum().sum(),
)
print("Bornes inversées :", (df["Start"] > df["End"]).sum())
PY
```

Résultats par génome :

| Identifiant du génome | Espèce | Positions à copie unique |
|---|---|---:|
| GCA_965208005.1 | *Jaera praehirsuta* | 1 453 |
| GCF_015104395.2 | *Macrobrachium nipponense* | 1 341 |
| GCF_017591435.1 | *Portunus trituberculatus* | 1 505 |
| GCF_019202785.1 | *Penaeus chinensis* | 1 474 |
| GCF_024679095.1 | *Eriocheir sinensis* | 1 460 |
| GCF_035594125.1 | *Scylla paramamosain* | 1 523 |
| GCF_036320965.1 | *Panulirus ornatus* | 1 488 |
| GCF_038502225.1 | *Cherax quadricarinatus* | 1 344 |
| GCF_040412425.1 | *Macrobrachium rosenbergii* | 1 486 |
| GCF_040958095.1 | *Procambarus clarkii* | 1 411 |
| GCF_042767895.1 | *Penaeus vannamei* | 1 310 |
| **Total** | **11 génomes** | **15 795** |

Bilan du contrôle :

```text
Nombre de génomes : 11
Nombre de positions : 15795
Doublons marqueur/génome : 0
Coordonnées manquantes : 0
Bornes inversées : 0
```

Le contrôle a seulement affiché son résultat dans le terminal ; il n'a créé ni `qc_genomes.tsv`, ni `exclusions.tsv`, ni nouveau CSV.

### Recul sur les résultats et état du workflow

Les onze effectifs correspondent exactement aux nombres de BUSCO complets à copie unique S indiqués dans les résumés. Le total de 15 795 positions est donc cohérent avec les résultats de départ. Le contrôle confirme l'unicité des couples marqueur/génome, l'absence de coordonnées manquantes et la remise en ordre des bornes.

Ces 15 795 lignes représentent des occurrences de marqueurs réparties entre les génomes, et non 15 795 groupes BUSCO distincts ou communs aux onze espèces. Les ensembles communs restent à déterminer. Ce contrôle ne remplace pas un comptage séparé des groupes D/F/M dans les tables intégrales.

La colonne `Chromosome` reste provisoire : une séquence BUSCO peut correspondre à un chromosome, un scaffold ou une séquence mitochondriale. Il faut l'associer aux métadonnées NCBI avant de sélectionner les marqueurs chromosomiques et de calculer les similarités. Aucun résultat de macrosynténie, de colinéarité ou de réarrangement n'est encore établi par ce seul CSV.

La recherche suivante sous `genomes/` n'a retourné aucune sortie :

```bash
find /data/projet2/Syntenie_des_decapodes/genomes \
  -type f \
  \( -name '*assembly_report.txt' -o -name '*sequence_report.jsonl' \) \
  -print
```

Il faut donc récupérer les rapports par séquence nécessaires à l'enrichissement du CSV. Leur téléchargement sur le cluster n'est pas encore confirmé dans cette entrée.

- [x] Créer le CSV commun des marqueurs complets à copie unique.
- [x] Vérifier les onze effectifs et les contrôles de structure du CSV.
- [ ] Associer les séquences aux chromosomes réels, longueurs et catégories NCBI.
- [ ] Sélectionner les marqueurs chromosomiques communs pour chaque paire.
- [ ] Calculer les similarités de contenu et d'adjacence, puis produire les figures.

## Mercredi 28 octobre

**Jade** · [1h]

- Lecture des sources bibliographiques pour le choix de la méthode de quantification de la synténie
- Pistes envisagées : distance personnalisée à partir des BUSCO (ordre des gènes, distance de points de rupture, DCJ), puis arbre NJ/UPGMA à partir de la matrice de distances

Sources vues

- Walden N., Schranz M. E. (2023). Synteny identifies reliable orthologs for phylogenomics and comparative genomics of the Brassicaceae. *Genome Biol. Evol.* 15(3), evad034. https://doi.org/10.1093/gbe/evad034 : BUSCO mono-copie comme base pour la macro-synténie
- Rubert D. P., Stoye J., Martinez F. H. V. (2020). Distance and similarity measures in comparative genomics. *CTD-SBC 2020*, 7–12. https://doi.org/10.5753/ctd.2020.11361 : mesures de conservation (ACI, distance de points de rupture)
- Bergeron A., Swenson K. M. (2024). A century of genomic rearrangements. In *Models and Methods for Biological Evolution*, 117–139, Wiley. https://doi.org/10.1002/9781394284252.ch5 : modèles DCJ et distances d'édition
- Paradis E., Schliep K. (2018). ape 5.0: An environment for modern phylogenetics and evolutionary analyses in R. *Bioinformatics* 35(3), 526–528. https://doi.org/10.1093/bioinformatics/bty633 : arbres NJ/UPGMA à partir de matrices de distances
- *Nature Ecology & Evolution* (2024), 8, 513–527. https://doi.org/10.1038/s41559-024-02329-4 : "gene painting" des BUSCO et groupes de liaison ancestraux (ALG)

## Jeudi 29 octobre

**Jade** · [40 mins]

- Suite de la lecture des sources
- Discussion avec **Tsiambaka** et **Aurelio** et choix de **syngraph** pour l'analyse de synténie
- Raisons du choix :
  - évite une grande partie du travail manuel nécessaire pour construire des matrices de distances personnalisées
  - accepte en entrée des sorties BUSCO modifiées
  - permet l'inférence des réarrangements (fissions, fusions, translocations) et des états ancestraux à partir des tables BUSCO

Sources lues

- bioRxiv (2023). Inferring inter-chromosomal rearrangements and ancestral linkage groups from synteny. https://doi.org/10.1101/2023.09.17.558111 : inférence des réarrangements inter-chromosomiques et ALG
- bioRxiv (2026). 338 coleopteran genomes reveal exceptional rearrangement variation… https://doi.org/10.64898/2026.07.17.739156 : hétérogénéité des taux de réarrangement chez les arthropodes [titre complet à compléter]
- Mackintosh A. J. F. *syngraph: toolkit for evolutionary analyses of linkage groups*. https://github.com/A-J-F-Mackintosh/syngraph : graphe de synténie, inférence des réarrangements, états ancestraux à partir de tables BUSCO

## Vendredi 30 octobre

**Jade** · [20 mins]

- Création de l'environnement conda pour syngraph

Commandes utilisées
#Dans projet2/conda
```
conda create -n env_syngraph python=3.8 -y
conda activate env_syngraph
conda config --env --add channels conda-forge 
conda install -c conda-forge networkx=2.4 pandas docopt tqdm ete3 pygraphviz matplotlib -y
```
#Dans scripts/
```
git clone https://github.com/A-J-F-Mackintosh/syngraph.git
```
[syngraph doit etre run depuis son propre dossier syngraph, pour atteindre ses python dependencies (sinon il faudrait update votre _$PYTHONPATH_ )]

**Tsiamba** ~2h
## Création d'un environnement dans /data/projet2/conda/env_dotplot
- commande: conda create \
    -p /data/projet2/conda/env_dotplot \
    -c conda-forge \
    python=3.8 numpy pandas matplotlib scipy plotly \
    -y

J'ai essayé les outils Orthofinder et MCscanX mais qui n'ont pas marché, j'ai enlevé les environnements des outils ainsi que leurs fichiers.yml que j'ai push dans le repository sur Github.
Ensuite j'ai fais 2 scripts : 
- dotplot_all_pairs.py
- dotplot_all_pairs_V2.py

Le premier a donné de bons résultats mais sans échelles et avec des couleurs pas très belles mais le deuxième semble plutôt meilleur.

Ce script va permettre de voir explicitement les gènes conservés entre toutes les combinaisons possibles des 11 génomes, donc 55 en total.
On a en input les 11 fichiers.tsv et en output 55 fichiers.png des graphes, + 2 fichiers : best one et worst one.

=> Tâches à faire : je dois git push l'environnement, le script de dotplot et faire un README de dotplot.


## Samedi 31 octobre — Diagnostic et correction du conflit numpy / Pillow dans env_syngraph

**Jade** · [45mins]

### Problème

Premier lancement de `syngraph build` dans `env_syngraph` : échec à l'import de matplotlib, via Pillow.

```
File ".../PIL/_typing.py", line 10, in <module>
    NumpyArray = npt.NDArray[Any]
AttributeError: module 'numpy.typing' has no attribute 'NDArray'
```

### Diagnostic

- Le README de syngraph impose Python 3.8, networkx 2.4 et numpy 1.20.3 (build `py38h9894fe3_0`), mais n'épingle pas Pillow.
- Le solveur a installé un Pillow récent  dont `PIL/_typing.py` utilise `numpy.typing.NDArray`, absent de numpy 1.20.3 (ajouté en numpy 1.21 [à vérifier dans la documentation numpy]).
- Cause : incompatibilité entre le numpy imposé par le README et un Pillow trop récent, pas un défaut de syngraph.

```bash
python -c "import numpy, PIL; print('numpy', numpy.__version__, '| pillow', PIL.__version__)"
```

### Correction

- Option retenue : conserver le numpy du README et rétrograder Pillow (pas de montée de numpy, pour ne pas s'écarter des versions indiquées par les auteurs).
- Commande :

```bash
conda install -c conda-forge "pillow<10"
```

- Résultat : Pillow 9.5.0, numpy 1.20.3 inchangé.
- Problème annexe : le cache conda bloquait le téléchargement des paquets ; correction avec ```conda clean -all```.

### Vérification

```bash
python -c "import matplotlib; import matplotlib.pyplot; print(matplotlib.__version__)"
```

- Import OK (matplotlib 3.7.1).
- `syngraph build -d ../../Analyses/Syngraph/busco_input/ -m -o test` s'exécute et produit `test.pickle`.

### Environnement final

- **Environnement syngraph** (`/data/projet2/conda/env_syngraph`) :
  - Python 3.8.20, networkx 2.4, numpy 1.20.3, pandas 2.0.0, matplotlib 3.7.1, pillow 9.5.0, ete3 3.1.3, pygraphviz 1.11, docopt 0.6.2, tqdm 4.67.1, more-itertools 10.5.0.

## Samedi 31 octobre 2026: diagrammes Sankey par paire à partir de BUSCO crustacea_odb12

**Aurélio**: ~2h
### Objectif et place dans le projet

Produire deux diagrammes Sankey à partir des résultats BUSCO existants : une comparaison entre deux espèces du même genre, *Macrobrachium nipponense* et *Macrobrachium rosenbergii*, et une comparaison entre l'isopode externe *Jaera praehirsuta* et le décapode *Scylla paramamosain*.

Cette étape ne relance pas BUSCO. Le script lit directement les `full_table.tsv` et les en-têtes des FASTA génomiques. Le fichier `master_positions_busco.csv`, construit précédemment, n'est pas une entrée de ce traitement.

Les mentions `proches` et `eloignes` correspondent aux paires choisies pour cette analyse ; elles ne résultent pas d'un calcul de distance ou d'un classement exhaustif des onze espèces. La comparaison optionnelle interne aux décapodes, *Penaeus vannamei* contre *Scylla paramamosain*, est disponible dans le script mais aucun HTML de cette troisième paire n'a été fourni pour cette entrée.

### Script et environnement

| Élément | Emplacement ou version |
|---|---|
| Script utilisé sur le cluster | `/data/projet2/Syntenie_des_decapodes/scripts/sankey_syntenie.py` |
| Environnement Conda | `/data/projet2/conda/env_sankey` |
| Définition de l'environnement | `/data/projet2/Syntenie_des_decapodes/envs/env_sankey.yml` |
| Python demandé dans le YAML | `3.12` |
| Plotly demandé dans le YAML | `6.9.0` |
| Référence BUSCO utilisée | `crustacea_odb12`, sans mélange avec `crustacea_odb12.2` ou `arthropoda_odb10` |

Le script a été fourni initialement sous le nom `sankey_pair_odb12.py`, puis enregistré sur le cluster sous le nom `sankey_syntenie.py`. Les commandes de cette entrée utilisent ce dernier nom. La version développée ici comporte des contrôles de format, une gestion explicite des fichiers FASTA et des sorties portant les deux noms d'espèces, les accessions et l'étiquette de comparaison.

L'environnement contient Python, pip et Plotly. Kaleido et Chrome/Chromium ne sont nécessaires que pour l'export SVG optionnel. La commande retenue ci-dessous utilise `--no-svg` et produit des HTML autonomes consultables hors ligne.

### Entrées BUSCO

Le script connaît les onze chemins fournis, mais seules les quatre tables des deux paires sélectionnées sont nécessaires à cette exécution. Le dossier parent est :

```text
/data/projet2/Syntenie_des_decapodes/Busco/precomputed_crustacea_odb12/BUSCO/
```

Les quatre chemins relatifs à ce dossier sont :

```text
BUSCO_GCF_015104395.2_ASM1510439v2_genomic.fna/run_crustacea_odb12/full_table.tsv
BUSCO_GCF_040412425.1_ASM4041242v1_genomic.fna/run_crustacea_odb12/full_table.tsv
resultats_busco_GCA_965208005.1_qmJaePrae1.hap1.1_genomic.fna/run_crustacea_odb12/full_table.tsv
resultats_busco_GCF_035594125.1_ASM3559412v1_genomic.fna/run_crustacea_odb12/full_table.tsv
```

| Assemblage | Espèce | Paire |
|---|---|---|
| `GCF_015104395.2` | *Macrobrachium nipponense* | `proches` |
| `GCF_040412425.1` | *Macrobrachium rosenbergii* | `proches` |
| `GCA_965208005.1` | *Jaera praehirsuta* | `eloignes` |
| `GCF_035594125.1` | *Scylla paramamosain* | `eloignes` |

### Entrées FASTA et identification des séquences

Les FASTA sont recherchés sous :

```text
/data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data/<accession>/
```

Les noms des quatre FASTA décompressés recherchés sont :

```text
GCF_015104395.2_ASM1510439v2_genomic.fna
GCF_040412425.1_ASM4041242v1_genomic.fna
GCA_965208005.1_qmJaePrae1.hap1.1_genomic.fna
GCF_035594125.1_ASM3559412v1_genomic.fna
```

La colonne `Sequence` de BUSCO est associée exactement au premier identifiant de l'en-tête FASTA, version comprise. Les mentions explicites de chromosome sont utilisées pour enrichir les étiquettes sans perdre l'identifiant d'origine. Les termes scaffold, contig et mitochondrie sont distingués ; les préfixes RefSeq `NW_` et `NT_` ne sont pas requalifiés en chromosomes.

Une vérification par `grep '^>'` sur le FASTA d'*Eriocheir sinensis* a montré des en-têtes `NC_…` portant les mentions `chromosome 1`, `chromosome 2`, etc. Cela a motivé l'utilisation des en-têtes, mais cette observation sur une espèce ne valide pas à elle seule les chromosomes des autres assemblages.

Pour *Jaera*, le dossier contient à la fois le `.fna` de 852 Mo et son `.fna.gz` de 256 Mo. La première version du script s'arrêtait avec `attendu exactement un ... trouve 2`. La sélection a été adaptée pour tous les génomes : lorsqu'un `.fna` et son `.fna.gz` de même nom coexistent, le `.fna` est choisi ; si seul le `.gz` existe, il est lu directement. Plusieurs noms différents restent ambigus et nécessitent une sélection explicite par `--fasta-file ACCESSION=CHEMIN`. Aucun fichier génomique n'a besoin d'être déplacé ou supprimé.

Cette règle de priorité ne constitue pas une vérification de l'égalité des contenus des deux fichiers. Les identifiants du fichier choisi restent contrôlés contre les séquences BUSCO.

### Filtrage et construction des liens

1. Lire les tables avec le séparateur tabulation et identifier les colonnes par leur nom. Les colonnes `Sequence`, `Start`/`Gene Start` et `End`/`Gene End` sont nécessaires pour des résultats génomiques.
2. Vérifier les statuts, les coordonnées et la référence déclarée. Les ensembles complets d'identifiants BUSCO doivent être identiques entre les deux tables ; des dates de création du lineage différentes, lorsqu'elles sont renseignées, sont refusées.
3. Ne retenir que les identifiants associés à une seule ligne de statut `Complete` dans chaque table. Tous les identifiants répétés sont exclus, même si les lignes sont identiques. Les statuts `Duplicated`, `Fragmented` et `Missing` ne contribuent pas aux liens.
4. Calculer l'intersection des marqueurs retenus dans les deux génomes de la paire.
5. Pour chaque marqueur commun, relever sa séquence dans l'espèce A et sa séquence dans l'espèce B. Compter les marqueurs pour chaque couple de séquences.
6. Tracer deux colonnes de nœuds, une par espèce. La largeur d'un lien représente son nombre de BUSCO ; un BUSCO contribue exactement 1 à un lien. Les coordonnées originales et le brin sont conservés dans la table des marqueurs, sans conversion de convention ni réorganisation de leur ordre.

Il n'y a pas de filtre limitant les marqueurs aux chromosomes, de suppression des petits liens ou de regroupement artificiel des scaffolds.

### Commandes retenues pour reproduire le traitement

```bash
conda activate /data/projet2/conda/env_sankey
cd /data/projet2/Syntenie_des_decapodes/scripts

mkdir -p /data/projet2/Syntenie_des_decapodes/envs/tmp_pip
export TMPDIR=/data/projet2/Syntenie_des_decapodes/envs/tmp_pip

# Autotests sans données biologiques
python sankey_syntenie.py --self-test

# Contrôle des tables et lecture des en-têtes FASTA, sans écrire les résultats
python sankey_syntenie.py --fasta-root --dry-run

# Génération des deux figures HTML et des tableaux
python sankey_syntenie.py --fasta-root --no-svg
```

Ces commandes constituent la procédure de reproduction retenue. Les éléments directement attestés dans l'échange sont la réussite initiale de neuf autotests, les sorties de validation des tables, la lecture de trois FASTA avant l'erreur d'ambiguïté pour *Jaera*, puis la fourniture des deux HTML finaux. La version corrigée a ensuite passé douze autotests synthétiques locaux ; leur réexécution sur le cluster n'a pas été documentée par une nouvelle sortie de terminal.

Le parcours des FASTA est séquentiel et peut prendre plusieurs minutes sans nouveau message pendant la lecture d'un fichier. Cette étape est effectuée également en mode `--dry-run`.

### Incident d'installation et correction retenue

La création Conda s'est terminée, puis l'installation pip a échoué avec :

```text
OSError: [Errno 28] No space left on device
```

Les contrôles transmis indiquaient 49 Go libres sur `/data`, mais seulement 8,8 Mo sur `/`, qui contient `/tmp` et `/home/vitale`. Les inodes n'étaient pas saturés et le cache pip occupait environ 10,7 Mo. La correction proposée a donc été de placer les fichiers temporaires sur `/data` et de désactiver le cache pip pour terminer l'installation dans l'environnement déjà créé :

```bash
TMPDIR=/data/projet2/Syntenie_des_decapodes/envs/tmp_pip \
python -m pip install --no-cache-dir 'plotly==6.9.0'
```

La sortie de cette réinstallation n'a pas été fournie. Les HTML obtenus attestent toutefois qu'une génération Plotly a ensuite abouti ; ils ne constituent pas un inventaire complet des versions Python installées sur le cluster.

### Sorties et vérifications disponibles

Le dossier de sortie configuré est :

```text
/data/projet2/Syntenie_des_decapodes/Analyses/Diagramme_Sankey/
```

Les deux fichiers fournis et examinés sont :

```text
sankey_proches_Macrobrachium_nipponense_GCF_015104395.2__Macrobrachium_rosenbergii_GCF_040412425.1_crustacea_odb12.html
sankey_eloignes_Jaera_praehirsuta_GCA_965208005.1__Scylla_paramamosain_GCF_035594125.1_crustacea_odb12.html
```

Pour chaque préfixe de comparaison, le script prévoit aussi :

| Suffixe | Contenu |
|---|---|
| `_liens.tsv` | Identifiants des séquences source et cible, nombre de BUSCO par lien |
| `_busco_communs.tsv` | Identifiant de chaque BUSCO retenu, séquences, coordonnées et brins dans les deux génomes |
| `_exclusions.tsv` | Marqueurs non retenus et motifs de chaque côté |
| `_sequences.tsv` | Correspondance entre identifiants, rôles, chromosomes mentionnés et en-têtes FASTA |
| `_bilan.json` | Chemins, empreintes des tables BUSCO, paramètres de comparaison, décomptes, version Plotly et état SVG |
| `.svg` | Export optionnel si demandé et si Kaleido et son navigateur fonctionnent |

Seuls les HTML ont été transmis pour examen. La présence et le contenu des TSV et bilans JSON restent à contrôler sur le cluster ; aucun SVG de ces résultats biologiques n'a été fourni. Les décomptes ci-dessous ont été recalculés à partir des données de nœuds et de liens embarquées dans les HTML, sans dépendre de leur apparence à l'écran.

### Résultats vérifiés

| Indicateur | Paire `proches` | Paire `eloignes` |
|---|---:|---:|
| BUSCO complets à copie unique communs | 1 309 | 1 440 |
| Couples de séquences reliés par au moins un BUSCO | 79 | 433 |
| Séquences représentées dans l'espèce A | 49 chez *M. nipponense* | 11 chez *J. praehirsuta* |
| Séquences représentées dans l'espèce B | 59 chez *M. rosenbergii* | 54 chez *S. paramamosain* |
| Somme des poids des liens | 1 309 | 1 440 |

La somme des poids correspond exactement au nombre de BUSCO annoncé dans chaque titre et dans les sorties de validation du terminal. Les deux diagrammes portent sur des intersections propres à chaque paire ; ils n'utilisent pas nécessairement les mêmes marqueurs.

**Nature des séquences représentées, d'après les étiquettes des figures :**

| Espèce | Étiquettes des séquences | Répartition des BUSCO communs |
|---|---|---|
| *M. nipponense* | 49 chromosomes annoncés dans les en-têtes | 1 309 sur ces séquences |
| *M. rosenbergii* | 58 chromosomes et 1 scaffold | 1 308 sur les chromosomes, 1 sur le scaffold |
| *J. praehirsuta* | 11 identifiants `OZ…`, sans nom de chromosome affiché | 1 440 sur ces séquences ; rôle chromosomique non établi par le HTML |
| *S. paramamosain* | 48 chromosomes et 6 scaffolds | 1 371 sur les chromosomes, 69 sur les scaffolds |

Il s'agit uniquement des séquences portant au moins un marqueur commun retenu. Ces nombres ne sont ni un inventaire complet de l'assemblage ni une détermination du caryotype. En particulier, les 11 séquences de *Jaera* ne doivent pas être appelées « 11 chromosomes » sans consulter les métadonnées correspondantes.

### Interprétation de la paire proche

Les 1 309 marqueurs communs se répartissent entre 79 couples de séquences. Les liens majeurs révèlent une concentration des marqueurs entre certaines paires de chromosomes, par exemple :

| *M. nipponense* | *M. rosenbergii* | BUSCO communs dans ce lien |
|---|---|---:|
| Chromosome 21 — `NC_087212.1` | Chromosome 5 — `NC_089745.1` | 45 |
| Chromosome 20 — `NC_061089.1` | Chromosome 6 — `NC_089746.1` | 43 |
| Chromosome 35 — `NC_061096.1` | Chromosome 14 — `NC_089754.1` | 42 |

À titre descriptif, en conservant le lien de plus grand poids pour chacune des 49 séquences sources, leur somme est de 1 185 marqueurs sur 1 309, soit 90,5 %. Cela indique une forte concentration du contenu BUSCO vers une séquence cible principale par séquence source. Ce calcul est directionnel et ne démontre pas une correspondance réciproque un-à-un.

Cette organisation est compatible avec une conservation importante du contenu chromosomique des marqueurs étudiés entre les deux *Macrobrachium*. Les numéros des chromosomes sont propres à chaque assemblage : le chromosome 21 d'une espèce peut correspondre principalement au chromosome 5 de l'autre sans que la différence de numéro représente à elle seule un réarrangement.

Le Sankey ne montre pas l'ordre des marqueurs. Il ne suffit donc pas à conclure à une colinéarité, à dater un événement ou à identifier formellement une inversion, une fusion ou une fission.

### Interprétation de la paire éloignée

Les 1 440 marqueurs communs se répartissent entre 433 couples de séquences. Les plus grands liens ne contiennent que 18 BUSCO, par exemple `OZ242389.1` de *Jaera* vers le chromosome 1 de *Scylla* (`NC_087151.1`), et `OZ242393.1` vers le chromosome 2 de *Scylla* (`NC_087152.1`). Les marqueurs d'une séquence de *Jaera* sont donc plus dispersés entre les séquences cibles que dans la comparaison proche.

Cette dispersion est compatible avec une correspondance moins concentrée du contenu génomique à cette échelle taxonomique. Elle dépend aussi du découpage des assemblages : 11 séquences sources sont représentées chez *Jaera*, contre 54 séquences cibles chez *Scylla*, dont 6 scaffolds. Les 69 marqueurs portés par ces scaffolds sont conservés dans le diagramme et ne sont pas attribués artificiellement à des chromosomes.

Le nombre de liens, 433 contre 79, ne mesure ni une distance phylogénétique ni un nombre de réarrangements. Une étude des coordonnées, de l'ordre des marqueurs et des métadonnées d'assemblage est nécessaire pour tester ces hypothèses.

La paire éloignée possède davantage de BUSCO communs que la paire proche, 1 440 contre 1 309. Cela n'est pas contradictoire : cet effectif dépend de la présence, de la détection et du statut single-copy des marqueurs dans chacun des génomes. Un nombre plus élevé de marqueurs retenus ne signifie pas une plus grande proximité évolutive. Les marqueurs exclus du Sankey ne sont pas nécessairement des gènes perdus : ils peuvent être dupliqués, fragmentés, non détectés ou exclus pour ambiguïté.


### Dimanche 01 Novembre 2026
**Tsiamba** ~2h15
Le script dotplot_all_pairs_V2.py a été renommé en dotplot_all_pairs.py. Les différents outputs ont été mis dans /data/projet2/Syntenie_des_decapodes/Analyses/dotplots_all_pairs.
Le dossier contient un README.md qui explique brièvement comment marche le script et les différents résultats.

### Analyses et interprétation des outputs de dotplot_all_pairs.py:

`dotplot_all_pairs.py` identifie les BUSCO présents dans les deux génomes, compare leurs positions et calcule un score de
conservation de leur ordre.

Les résultats sont enregistrés dans :

```text
Analyses/dotplots_all_pairs/synteny_scores.csv
```

Chaque ligne du fichier contient :

- `genome_1` : premier génome comparé ;
- `genome_2` : second génome comparé ;
- `synteny_score` : score de conservation de l'ordre des BUSCO ;
- `busco_partages` : nombre de BUSCO communs ;
- `paires_sequences` : nombre de paires de séquences utilisées pour le calcul.

Le score de synténie est compris approximativement entre 0 et 1. Un score élevé
indique que les BUSCO communs suivent une organisation relativement régulière
dans les deux génomes. Dans le dot plot, cela se traduit généralement par une
diagonale nette ou par plusieurs blocs proches d'une diagonale. Un score faible
correspond à une organisation plus dispersée des marqueurs et à une conservation
moins nette de leur ordre.

### Paire la mieux conservée — BEST_CONSERVED

La paire ayant obtenu le score le plus élevé est :

```text
GCF_019202785.1_ASM1920278v2
vs
GCF_042767895.1_ASM4276789v1
```

Cette comparaison correspond à :

```text
Penaeus chinensis
vs
Penaeus vannamei
```

Résultats enregistrés dans `synteny_scores.csv` :

```text
Score de synténie   : 0.5365
BUSCO partagés      : 1267
Paires de séquences : 43
```

Le fichier associé est :

```text
BEST_CONSERVED__GCF_019202785.1_ASM1920278v2__vs__GCF_042767895.1_ASM4276789v1__score_0.5365.png
```

Le dot plot présente une diagonale principale très nette et une succession
régulière de blocs colorés. Les BUSCO communs sont donc principalement
positionnés dans un ordre similaire entre les deux génomes.

Cette organisation indique une conservation relativement importante de l'ordre
des marqueurs BUSCO. Les quelques points éloignés de la diagonale peuvent
correspondre à des marqueurs déplacés, à de petites réorganisations, à des
différences d'assemblage ou à des séquences qui ne sont pas directement
comparables.

Cette paire possède le score le plus élevé des 55 comparaisons, mais le score
0.5365 ne signifie pas que 53,65 % des génomes sont identiques. Il s'agit d'un
indicateur de conservation de l'ordre des BUSCO utilisés dans l'analyse.

### Paire la moins conservée — WORST_CONSERVED

La paire ayant obtenu le score le plus faible est :

```text
GCF_017591435.1_ASM1759143v1
vs
GCF_036320965.1_ASM3632096v1
```

Cette comparaison correspond à :

```text
Portunus trituberculatus
vs
Panulirus ornatus
```

Résultats enregistrés dans `synteny_scores.csv` :

```text
Score de synténie   : 0.1729
BUSCO partagés      : 1458
Paires de séquences : 49
```

Le fichier associé est :

```text
WORST_CONSERVED__GCF_017591435.1_ASM1759143v1__vs__GCF_036320965.1_ASM3632096v1__score_0.1729.png
```

Le dot plot montre une organisation beaucoup plus dispersée. Une diagonale
reste visible dans certaines régions, mais elle est fragmentée et accompagnée
de nombreux points éloignés. Les BUSCO communs sont donc moins souvent
regroupés selon une relation positionnelle régulière entre les deux génomes.

Cette dispersion est compatible avec une conservation plus faible de l'ordre
des marqueurs. Elle peut être liée à une divergence évolutive plus importante,
à des réarrangements chromosomiques possibles, à des différences entre les
assemblages ou à la présence de séquences fragmentées en scaffolds et en
contigs.

### Comparaison des deux paires

| Élément | Paire BEST_CONSERVED | Paire WORST_CONSERVED |
|---|---:|---:|
| Génome 1 | GCF_019202785.1_ASM1920278v2 | GCF_017591435.1_ASM1759143v1 |
| Génome 2 | GCF_042767895.1_ASM4276789v1 | GCF_036320965.1_ASM3632096v1 |
| Score de synténie | 0.5365 | 0.1729 |
| BUSCO partagés dans le CSV | 1 267 | 1 458 |
| Paires de séquences | 43 | 49 |
| Aspect du dot plot | Diagonale nette et blocs réguliers | Organisation fragmentée et dispersée |

La paire WORST_CONSERVED possède davantage de BUSCO partagés que la paire
BEST_CONSERVED. Cela montre que le nombre de marqueurs communs ne suffit pas à
mesurer la conservation de la synténie. Deux génomes peuvent partager beaucoup
de BUSCO, tout en présentant une organisation différente de ces marqueurs sur
leurs séquences.

Les nombres affichés dans les titres des images peuvent être différents des
valeurs du fichier `synteny_scores.csv`, car le script applique des filtres
supplémentaires lors de la construction des blocs conservés et du dot plot.
Les valeurs de référence pour le classement des paires sont celles du fichier
`synteny_scores.csv`.

### Interprétation générale

La paire *Penaeus chinensis* - *Penaeus vannamei* présente la relation
positionnelle la plus régulière entre les BUSCO parmi les 55 comparaisons.
Cette organisation est compatible avec une conservation importante de certains
blocs génomiques.

La paire *Portunus trituberculatus* - *Panulirus ornatus* présente la relation
la plus dispersée selon la métrique utilisée. Les BUSCO restent nombreux et
partagés, mais leur ordre et leur répartition entre les séquences sont moins
conservés.

Ces résultats ne permettent pas de conclure directement à un nombre précis
d'inversions, de fusions, de fissions ou de translocations. Un score faible
peut être causé à la fois par une divergence biologique réelle et par des
facteurs techniques, comme la fragmentation d'un assemblage ou la présence de
scaffolds et de contigs.

Une analyse complémentaire est donc nécessaire pour :

- vérifier quelles séquences correspondent à de vrais chromosomes ;
- distinguer les chromosomes, les scaffolds et les contigs ;
- examiner l'ordre exact des BUSCO dans chaque bloc ;
- identifier les inversions et les ruptures de colinéarité ;
- rechercher d'éventuelles fusions, fissions ou translocations ;
- tenir compte des différences de versions de BUSCO et de Miniprot entre les
  résultats locaux et ceux fournis par l'enseignant.

Les dot plots constituent ainsi une première analyse comparative de la synténie.
Ils permettent de classer les paires selon la régularité de l'organisation des
marqueurs BUSCO, mais ne constituent pas à eux seuls une preuve définitive de
réarrangements chromosomiques.


Je vais créer le fichier envs/env_dotplot.yml afin de le mettre sur github et mettre à jour le versions.txt qui contient les versions des outils utilisés.

## Mise à jour du projet et synchronisation avec GitHub
Je viens de:
 git add .gitignore cahier_labo.md versions.txt scripts/dotplot_all_pairs.py
et push sur github.

## 4 novembre 2026 — Comparaison du contenu chromosomique par Jaccard
**Aurélio** : 1h

### Objectif et méthode

Après les Sankey en `crustacea_odb12`, nous avons quantifié la conservation du contenu en BUSCO des chromosomes des deux *Macrobrachium* et comparé la répartition des marqueurs entre les séquences de *Jaera praehirsuta* et les chromosomes de *Scylla paramamosain*.

Le script `scripts/comparaison_contenu_chr.py` utilise Python 3 et lit les deux tableaux `*_liens.tsv` et `*_sequences.tsv` produits par `sankey_syntenie.py` pour chaque paire. Le premier donne le nombre de BUSCO complets à copie unique communs par couple de séquences. Le second identifie les séquences et leur rôle d'après les en-têtes FASTA.

- **Paire proche.** Retenir les BUSCO situés sur des chromosomes dans les deux assemblages.
- **Paire éloignée.** Garder les séquences `OZ…` de *Jaera* sous leurs identifiants d’origine et retenir uniquement les chromosomes du côté de *Scylla*. Le statut des séquences de *Jaera* reste à vérifier dans le rapport d’assemblage.

Pour chaque couple de séquences, on calcule **Jaccard = BUSCO partagés / (BUSCO côté A + BUSCO côté B − BUSCO partagés)**. Les deux effectifs par séquence sont recalculés après filtrage, dans le même ensemble de marqueurs pour la paire. Le tableau détaillé donne également la fraction partagée de chaque côté.

### Commandes de reproduction et sorties

```bash
cd /data/projet2/Syntenie_des_decapodes
python3 scripts/comparaison_contenu_chr.py --pair proches
python3 scripts/comparaison_contenu_chr.py --pair eloignes
```

Les entrées sont lues dans `Analyses/Diagramme_Sankey/`. Les résultats sont écrits dans `Analyses/Diagramme_Sankey/Contenu_chromosomes/`, avec le préfixe `macrobrachium_` ou `jaera_scylla_` selon la paire.

| Suffixe | Contenu |
|---|---|
| `_carte_jaccard.html` | Carte à ouvrir dans un navigateur. Un clic sur une case affiche le couple, le score et les effectifs. |
| `_matrice_jaccard.tsv` | Matrice des scores, avec les séquences du premier génome en lignes. |
| `_contenu_chromosomes.tsv` | Détail des scores, effectifs et fractions partagées par couple de séquences. |

### Résultats et interprétation

Les chiffres ont été vérifiés sur les tableaux reconstruits à partir des deux HTML du Sankey. Les commandes ci-dessus documentent la reproduction sur le cluster.

| Paire | BUSCO du Sankey | Retenus après filtre | Couples avec au moins un BUSCO partagé | Dimensions de la matrice |
|---|---:|---:|---:|---|
| *M. nipponense* × *M. rosenbergii* | 1 309 | 1 308 | 78 | 49 × 58 chromosomes |
| *J. praehirsuta* × *S. paramamosain* | 1 440 | 1 371 | 405 | 11 séquences × 48 chromosomes |

Chez les *Macrobrachium*, le chromosome 21 de *M. nipponense* et le chromosome 5 de *M. rosenbergii* partagent leurs **45 BUSCO retenus**, soit un **Jaccard de 1**. La case se situe hors de la diagonale, car les axes suivent la numérotation propre à chaque assemblage. Le bloc 21 × 5 du dotplot permet d’examiner l’ordre des marqueurs dont la carte résume le contenu.

Pour *Jaera–Scylla*, le score maximal observé est **0,102** entre `OZ242390.1` et le chromosome 7 de *Scylla*. Ce couple partage **9 BUSCO** sur les 62 et 35 marqueurs retenus de chaque côté. Les marqueurs sont davantage répartis entre les séquences cibles dans cette comparaison. Les paires reposent sur des ensembles de BUSCO, des filtres et des assemblages différents, ce qui limite l’interprétation directe de l’écart entre leurs scores.


---
## 5 novembre 2026 — Balayage paramétrique de *syngraph* (-m et -r) sur les génomes de décapodes

**Jade** · [2h]

### Objectif et méthode

Après la mise en place de l'environnement et l'analyse initiale du graphe de synténie (`decapod_syngraph_run.pickle`), nous avons mené un balayage paramétrique systématique pour évaluer la robustesse des reconstructions caryotypiques ancestrales sur les 11 espèces de décapodes (*Scylla paramamosain* comme référence, *Jaera praehirsuta* en outgroup).

L'analyse teste l'impact combiné de deux paramètres clés de *syngraph* :
- Le nombre minimal de marqueurs par bloc de synténie locale (`-m` de 1 à 5).
- Le modèle de réarrangement (`-r 2` : fissions et fusions ; `-r 3` : fissions, fusions et translocations).

### Commandes de reproduction et sorties

Exécution des scripts d'inférence depuis le dossier de travail du cluster :

```bash
cd /data/projet2/Syntenie_des_decapodes/scripts/syngraph

# Exemple pour r2 et r3 aux seuils m1 à m5
python syngraph infer -g decapod_syngraph_run.pickle -t ../../Analyses/Syngraph/phylo_tree/phylotree.newick -s Scylla_paramamosain -r 2 -m 1 -o decapod_inferred_r2_m1
python syngraph infer -g decapod_syngraph_run.pickle -t ../../Analyses/Syngraph/phylo_tree/phylotree.newick -s Scylla_paramamosain -r 3 -m 1 -o decapod_inferred_r3_m1
# (Répété pour -m 2, 3, 4 et les runs par défaut -m 5 dans Run_r2-m5 / Run_r3-m5)



## Jeudi 5 novembre 2026 — Extension aux 55 paires et reconstruction du master chromosomique
**Aurélio**: 1h30
### But général

Étendre les analyses de contenu BUSCO aux **55 paires distinctes des 11 génomes**, soit 11 × 10 / 2. Chaque paire utilise ses propres BUSCO complets à copie unique communs aux deux assemblages. Les analyses portent sur la répartition des marqueurs entre séquences, puis sur la similarité du contenu des chromosomes identifiés.

Le travail a aussi consisté à réorganiser les entrées et les sorties après un nettoyage destiné à libérer de l’espace sur le cluster.

### Difficultés rencontrées après le nettoyage

Le dossier des génomes téléchargés avec NCBI Datasets et d’anciens dossiers BUSCO ont été supprimés pour libérer de la place. Le master conservé dans l’ancienne arborescence Miniprot avait également été supprimé. Cette situation a révélé deux dépendances des premières versions des scripts.

- Les positions BUSCO étaient obtenues à partir des `full_table.tsv` ou du master de positions. Les TSV BUSCO encore disponibles permettaient de reconstruire ce dernier.
- L’option `--fasta-root` parcourait les FASTA génomiques pour obtenir les noms des chromosomes et distinguer chromosomes, scaffolds et séquences mitochondriales. Après la suppression de `genomes/ncbi_dataset`, ce chemin ne permettait plus de récupérer ces informations.

La première relance de `master_csv_odb12.py` dans `env_sankey` a rencontré l’erreur `ModuleNotFoundError: No module named 'pandas'`. Le retour à l’environnement `env_busco`, utilisé pour l’extraction initiale, a été proposé. Un extrait du CSV régénéré a ensuite été transmis.

Cet extrait montrait que **`Chromosome` était une copie de `Sequence`**, par exemple `OZ242385.1` dans les deux colonnes. Le CSV retrouvait donc les positions des marqueurs et les identifiants des séquences, mais la correspondance biologique avec les chromosomes restait à reconstruire.

Le nettoyage de Conda a aussi conduit à vérifier les emplacements des environnements et du cache. La configuration contrôlée place les environnements de travail sous `/data/projet2/conda` et le cache Conda dans `/data/projet2/conda/pkgs`. L’environnement utilisé pour les nouvelles analyses est `/data/projet2/conda/env_sankey`.

### Récupération ciblée des correspondances NCBI

Les fichiers `assembly_report.txt` des **versions exactes des 11 assemblages** ont été récupérés depuis NCBI. Ils donnent les accessions GenBank et RefSeq des séquences, leur rôle, la molécule associée et son type. Leur contenu a permis de reconstruire la table `identifiant_chr_scaffold.tsv`, d’environ **7,8 Mo**.

Cette table remplace l’information auparavant extraite des en-têtes FASTA. La jointure utilise le couple **accession d’assemblage versionnée + identifiant de séquence versionné**. Les accessions d’origine sont conservées. Chaque correspondance possède une URL permettant de retrouver le rapport source.

Le rôle de la séquence est établi à partir du rapport d’assemblage. Une séquence de rôle `assembled-molecule` et de type `Chromosome` reçoit le nom du chromosome déclaré. Les scaffolds et les séquences mitochondriales conservent leurs catégories respectives.

La vérification a notamment résolu le cas de *Jaera praehirsuta*.

| Identifiant | Affectation dans le rapport GCA_965208005.1 |
|---|---|
| `OZ242385.1` | Chromosome 1 |
| `OZ242386.1` à `OZ242394.1` | Chromosomes 2 à 10 |
| `OZ242395.1` | Chromosome 11 |
| `OZ242396.1` | Mitochondrie |

Le préfixe `OZ` doit donc être interprété avec les métadonnées de cet assemblage. Cette correspondance permet désormais d’appliquer le filtre chromosomique à *Jaera*, comme aux décapodes. [Rapport NCBI de Jaera praehirsuta](https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/965/208/005/GCA_965208005.1_qmJaePrae1.hap1.1/GCA_965208005.1_qmJaePrae1.hap1.1_assembly_report.txt).

Les nombres de chromosomes obtenus dans les rapports correspondent au tableau de sélection des génomes.

| Assemblage | Espèce | Chromosomes identifiés dans le rapport |
|---|---|---:|
| `GCF_015104395.2` | *Macrobrachium nipponense* | 49 |
| `GCF_036320965.1` | *Panulirus ornatus* | 73 |
| `GCF_038502225.1` | *Cherax quadricarinatus* | 100 |
| `GCF_040412425.1` | *Macrobrachium rosenbergii* | 59 |
| `GCF_040958095.1` | *Procambarus clarkii* | 94 |
| `GCA_965208005.1` | *Jaera praehirsuta* | 11 |
| `GCF_017591435.1` | *Portunus trituberculatus* | 50 |
| `GCF_019202785.1` | *Penaeus chinensis* | 43 |
| `GCF_024679095.1` | *Eriocheir sinensis* | 70 |
| `GCF_035594125.1` | *Scylla paramamosain* | 49 |
| `GCF_042767895.1` | *Penaeus vannamei* | 44 |

Ces nombres décrivent les assemblages. Le nombre de chromosomes représentés dans une comparaison dépend des BUSCO communs retenus sur chacun d’eux.

### Organisation retenue pour les fichiers

Tous les chemins ci-dessous sont relatifs à `/data/projet2/Syntenie_des_decapodes/`.

| Élément | Emplacement retenu |
|---|---|
| Trois scripts de la chaîne | `scripts/` |
| Résultats BUSCO sources | `Busco/precomputed_crustacea_odb12/BUSCO/<dossier_du_genome>/run_crustacea_odb12/full_table.tsv` |
| Correspondances des séquences | `genomes/identifiant_chr_scaffold.tsv` |
| Master TSV enrichi | `genomes/master_positions_busco.tsv` |
| Sorties Sankey regroupées | `Analyses/Diagramme_Sankey/` |
| Sorties Jaccard | `Analyses/Jaccard/` |

Le dossier `Miniprot/` qui était sous `Analyses/Diagramme_Sankey/` a été déplacé vers `Busco/busco_miniprot/`. Les sorties Sankey ont ensuite été regroupées directement dans `Analyses/Diagramme_Sankey/`, et les anciens dossiers de runs ont été supprimés. Les commandes ci-dessous utilisent cette organisation.

### Étape 1 — But → script → sortie du master TSV

**But.** Réunir les positions BUSCO des 11 génomes et leur ajouter les identifiants chromosomiques vérifiés, pour disposer d’une entrée commune aux deux analyses.

**Script.** `scripts/generer_master_tsv.py`, placé à côté de `sankey_syntenie.py` dont il réutilise les fonctions de lecture. Le traitement repose sur la bibliothèque standard de Python.

Par défaut, le générateur lit les 11 `full_table.tsv` déjà disponibles et la table `genomes/identifiant_chr_scaffold.tsv`. Il vérifie la référence `crustacea_odb12`, les ensembles de groupes BUSCO et les dates de création du lineage lorsqu’elles sont présentes. Il retient les marqueurs `Complete` dont l’identifiant apparaît une seule fois dans la table du génome. Les identifiants répétés sont exclus intégralement. Chaque séquence retenue doit posséder une correspondance dans les métadonnées.

```bash
cd /data/projet2/Syntenie_des_decapodes
conda activate /data/projet2/conda/env_sankey
python scripts/generer_master_tsv.py
```

**Sortie.** `genomes/master_positions_busco.tsv`, avec une ligne par couple génome–BUSCO retenu.

| Colonne ou groupe de colonnes | Signification |
|---|---|
| `Organisme`, `Espece` | Accession versionnée de l’assemblage et espèce |
| `Sequence` | Identifiant original de la séquence qui porte le BUSCO |
| `Chromosome` | Nom attribué par le rapport d’assemblage, renseigné pour les chromosomes |
| `Type_sequence` | Catégorie de la séquence, notamment chromosome, scaffold ou mitochondrie |
| `Busco_id`, `Start`, `End`, `Strand` | Identifiant du marqueur, coordonnées et brin conservés |
| `Status`, `Lineage`, `Lineage_date` | Statut retenu et référence BUSCO documentée |
| `Verification_BUSCO` | Origine du contrôle, `full_table_verifie` ou `CSV_prefiltre_declare` |
| `Source_BUSCO`, `Source_sequence` | Fichier d’origine des positions et URL du rapport d’assemblage |

L’option `--input-csv` permet aussi d’enrichir un ancien master CSV déjà filtré. Dans ce cas, la sélection single-copy et la référence BUSCO reposent sur le traitement amont et sont signalées par `CSV_prefiltre_declare`. La lecture directe des tables intégrales constitue la procédure par défaut. Le générateur protège le master existant et propose `--overwrite` pour autoriser son remplacement.

### Étape 2 — But → script → sorties Sankey

**But.** Visualiser la répartition des BUSCO complets à copie unique communs pour chacune des 55 paires de génomes.

**Script.** `scripts/sankey_syntenie.py`. L’option `--master-tsv` charge directement les positions et les catégories contenues dans le master. L’option `--all-pairs` génère une comparaison pour chaque paire distincte. Les noms de fichiers contiennent les espèces et les accessions. Les noms historiques `proches` et `eloignes` sont conservés pour les paires correspondantes.

```bash
python scripts/sankey_syntenie.py \
  --all-pairs \
  --master-tsv genomes/master_positions_busco.tsv \
  --no-svg \
  --outdir Analyses/Diagramme_Sankey
```

**Sorties.** Les fichiers de chaque paire sont placés directement dans `Analyses/Diagramme_Sankey/`.

| Sortie | Contenu |
|---|---|
| `.html` | Diagramme Sankey autonome consultable dans un navigateur |
| `_liens.tsv` | Nombre de BUSCO par couple de séquences |
| `_busco_communs.tsv` | Marqueurs communs, séquences, positions et brins |
| `_sequences.tsv` | Noms, rôles et sources des séquences représentées |
| `_exclusions.tsv` | Marqueurs écartés de l’intersection et motifs disponibles |
| `_bilan.json` | Effectifs, chemins, empreinte du master et provenance des métadonnées |
| `comparaisons.tsv` | Inventaire des comparaisons terminées et de leurs préfixes de fichiers |

Les Sankey conservent les marqueurs communs portés par les chromosomes et les scaffolds, avec leur catégorie. Les noms de chromosomes viennent désormais du master. Le chargement des données est mutualisé entre les comparaisons. L’option `--no-svg` produit les HTML et tableaux avec Plotly et évite le lancement de Kaleido pour chaque paire.

### Étape 3 — But → script → sorties Jaccard

**But.** Quantifier la similarité du contenu BUSCO des chromosomes identifiés, pour les mêmes 55 paires.

**Script.** `scripts/comparaison_contenu_chr.py`, avec lecture directe du master TSV. Ce mode applique par défaut le filtre `chromosomes` aux deux génomes, y compris *Jaera*. Pour chaque paire, les effectifs et les dénominateurs sont recalculés après ce filtre, sur les BUSCO communs retenus.

```bash
python scripts/comparaison_contenu_chr.py \
  --all-pairs \
  --master-tsv genomes/master_positions_busco.tsv \
  --out-dir Analyses/Jaccard
```

**Sorties.** Les fichiers sont écrits dans `Analyses/Jaccard/`.

| Sortie | Contenu |
|---|---|
| `_carte_jaccard.html` | Carte interactive des scores par couple de chromosomes |
| `_matrice_jaccard.tsv` | Matrice des similarités |
| `_contenu_chromosomes.tsv` | Effectifs partagés, effectifs de chaque côté, Jaccard et fractions partagées |
| `resume_jaccard_chromosomes.tsv` | Statut, nombres de marqueurs retenus et exclus, dimensions et score maximal par comparaison |

Un clic sur une case de la carte affiche les deux chromosomes, leur score et les effectifs BUSCO. Le score est calculé comme **nombre de BUSCO partagés / nombre de BUSCO présents dans au moins un des deux ensembles**. Les chromosomes restent ordonnés selon leur nom dans chaque assemblage. Une correspondance forte peut donc se situer hors de la diagonale, comme le couple chromosome 21 de *M. nipponense*–chromosome 5 de *M. rosenbergii* examiné précédemment.

La lecture directe du master rend ce calcul indépendant de l’emplacement des sorties Sankey. Le regroupement des anciens fichiers de runs n’impose donc aucune nouvelle lecture des FASTA.

### Contrôles réalisés et état des résultats

La validation locale a porté sur **19 tests**, comprenant 12 autotests de lecture et de filtrage, puis 7 tests du nouveau workflow. Ces derniers ont vérifié la création du master à partir des tables intégrales et d’un ancien CSV, la protection d’une sortie existante, le refus de métadonnées manquantes ou contradictoires et la cohérence du lineage.

Le traitement complet a produit 55 Sankey et 55 cartes Jaccard sur des données synthétiques. Les tableaux de scores obtenus directement depuis le master étaient identiques à ceux obtenus depuis les sorties Sankey. Les correspondances NCBI avaient également été contrôlées sur les identifiants présents dans les deux HTML biologiques déjà fournis.

Le regroupement des fichiers Sankey directement dans leur dossier final a été signalé depuis le cluster. Les nouveaux bilans des 55 paires et le master enrichi complet restent à examiner pour consigner les effectifs biologiques finaux. Les résultats numériques des deux comparaisons initiales figurent dans les entrées précédentes.

Cette étape fournit une chaîne reproductible allant des positions BUSCO conservées à un master enrichi, puis aux Sankey et aux cartes de contenu chromosomique. L’étude de l’ordre des marqueurs et de leurs voisinages constitue une analyse complémentaire à mener avec les coordonnées du master.

## Samedi 07 Novembre - Ajout de l’export SVG aux comparaisons de contenu chromosomique
**Aurélio** : 2h

Produire des figures vectorielles pour les comparaisons entre les 11 génomes, soit 55 paires distinctes. Le format SVG permet d’agrandir les figures sans perte de qualité et facilite leur intégration dans le rapport.

Pour les cartes de Jaccard, les valeurs positives sont désormais inscrites directement dans les cases. Les fichiers HTML sont conservés pour consulter les informations détaillées au survol.

### Scripts et fichiers d’entrée

Les deux scripts modifiés sont :

- `scripts/comparaison_contenu_chr.py` : production des cartes de similarité de Jaccard en HTML et SVG, accompagnées des tableaux TSV.
- `scripts/sankey_syntenie.py` : production des diagrammes Sankey en HTML et SVG, accompagnés des tableaux TSV et des bilans JSON.

Les comparaisons utilisent le master enrichi :

```text
/data/projet2/Syntenie_des_decapodes/genomes/master_positions_busco.tsv
```

Ce fichier contient les marqueurs BUSCO retenus, leurs positions et les informations permettant de distinguer chromosomes et scaffolds. L’export SVG ne nécessite pas de télécharger à nouveau les séquences génomiques.

### Environnement et difficultés rencontrées

L’export SVG des cartes de Jaccard utilise directement la bibliothèque standard de Python. L’export des Sankey repose sur Plotly, Kaleido et Chrome.

Lors du premier lancement des Sankey, la validation des données a fonctionné, mais l’export SVG a échoué dès la première comparaison. Les fichiers HTML et TSV de cette comparaison ont été conservés. L’option `--require-svg` a interrompu le traitement pour éviter de répéter cet échec sur les 55 paires.

Le diagnostic avec `ldd` a révélé plusieurs bibliothèques Linux manquantes pour Chrome : ATK/AT-SPI, CUPS, certaines bibliothèques X11, GBM, Cairo, Pango et ALSA.

Les dépendances ont été installées dans l’environnement existant :

```bash
conda install -y --prefix /data/projet2/conda/env_sankey \
  --override-channels -c conda-forge \
  'at-spi2-core>=2.46' 'libcups<3' \
  xorg-libxcomposite xorg-libxdamage xorg-libxfixes xorg-libxrandr \
  mesalib cairo pango alsa-lib
```

Un lanceur a été créé pour permettre à Chrome de trouver les bibliothèques de cet environnement :

```text
/data/projet2/conda/chrome/chrome-cluster.sh
```

Ce lanceur configure également les emplacements des caches et fichiers temporaires sous `/data/projet2/`. Les paquets Conda sont stockés dans `/data/projet2/conda/pkgs`, sans installation nécessitant `sudo`.

Après correction, la commande de vérification affiche :

```text
Google Chrome for Testing 142.0.7444.175
```

Cette vérification confirme le démarrage de Chrome. La validation complète nécessite ensuite la réussite d’un petit export SVG, puis la génération des figures.

### Commandes de génération

Depuis la racine du projet :

```bash
conda activate /data/projet2/conda/env_sankey
cd /data/projet2/Syntenie_des_decapodes
```

Cartes de Jaccard :

```bash
python scripts/comparaison_contenu_chr.py \
  --all-pairs \
  --master-tsv genomes/master_positions_busco.tsv \
  --out-dir Analyses/Jaccard
```

Diagrammes Sankey, après réussite du test d’export :

```bash
python scripts/sankey_syntenie.py \
  --all-pairs \
  --master-tsv genomes/master_positions_busco.tsv \
  --outdir Analyses/Diagramme_Sankey \
  --runtime-dir /data/projet2/conda \
  --browser-path /data/projet2/conda/chrome/chrome-cluster.sh \
  --require-svg \
  --overwrite
```

### Outputs et utilisation

Les sorties sont enregistrées dans :

```text
/data/projet2/Syntenie_des_decapodes/Analyses/Jaccard/
/data/projet2/Syntenie_des_decapodes/Analyses/Diagramme_Sankey/
```

Les SVG servent à la lecture des valeurs et à la préparation des figures du rapport. Les HTML permettent l’exploration interactive, tandis que les TSV conservent les valeurs numériques exactes.

Dans les cartes SVG de Jaccard, les scores positifs sont affichés à trois décimales, avec une indication spécifique pour les valeurs inférieures à 0,001. Les cases sans nombre correspondent à un score nul.

Cette étape améliore la présentation des comparaisons de contenu chromosomique. L’interprétation reste fondée sur les marqueurs partagés et leur répartition entre chromosomes. La conservation de leur ordre doit être examinée séparément avec les dotplots et les analyses de voisinage.

À ce stade, le démarrage de Chrome est confirmé ; la réussite de l’export SVG et la production complète des 55 comparaisons restent à consigner après exécution.

### But

Compléter les comparaisons de contenu chromosomique par une annotation des BUSCO classés dupliqués. L’objectif est de visualiser leur répartition entre chromosomes tout en conservant les analyses de référence fondées sur les BUSCO complets à copie unique.

### Scripts et inputs

Création de deux fichiers dans `scripts/` :

- `generer_master_duplication_gene.py` : extraction des positions des BUSCO complets et dupliqués depuis les 11 `full_table.tsv`.
- `busco_duplications.py` : fonctions partagées de validation et de comptage, utilisées automatiquement par le générateur et les scripts graphiques.

Les correspondances entre identifiants de séquences, chromosomes et scaffolds proviennent de :

```text
genomes/identifiant_chr_scaffold.tsv
```

Le générateur produit :

```text
genomes/master_duplication_gene.tsv
genomes/master_duplication_gene_bilan.json
```

Ce master complémentaire conserve une ligne par locus, avec le statut BUSCO, les coordonnées, le chromosome ou scaffold et les nombres de copies dans le génome et sur la séquence. Il contient les statuts `Complete` et `Duplicated`, car les BUSCO à copie unique sont nécessaires au calcul du dénominateur des annotations.

Les lignes répétant un même locus sont dédoublonnées. Les incohérences de statut, de coordonnées ou de métadonnées sont signalées. Aucun téléchargement de génome ni nouveau calcul BUSCO n’a été nécessaire.

### Modification des figures

Les scripts `sankey_syntenie.py` et `comparaison_contenu_chr.py` acceptent désormais l’option :

```bash
--duplication-master genomes/master_duplication_gene.tsv
```

Le master initial `genomes/master_positions_busco.tsv` reste utilisé pour calculer les correspondances entre espèces.

Pour chaque chromosome, l’annotation indique :

- le nombre de familles BUSCO classées `Duplicated` présentes ;
- le nombre total de familles BUSCO complètes présentes ;
- leur proportion : `100 × familles D / familles complètes` ;
- le nombre de copies dupliquées présentes sur ce chromosome.

Chaque famille est comptée une seule fois par chromosome, indépendamment de son nombre de copies. Une famille dupliquée répartie sur plusieurs chromosomes peut donc contribuer aux annotations de plusieurs chromosomes.

Ces valeurs sont calculées avant l’intersection des marqueurs communs à la paire. Leur dénominateur diffère ainsi de celui des effectifs représentés dans les liens.

Les cartes Jaccard présentent des barres orange marginales. Les Sankey affichent les valeurs de duplication dans les libellés. Les HTML permettent également de consulter les identifiants BUSCO et leurs positions. Les scores Jaccard et les épaisseurs des liens Sankey restent calculés sur les BUSCO à copie unique.

### Difficultés rencontrées et corrections

L’export des Sankey a également rencontré un dépassement du délai de 60 secondes, accompagné du message `Resorting to unclean kill browser`. Le script attendait la fermeture du navigateur avant d’enregistrer le SVG.

L’export a été corrigé pour enregistrer et vérifier le SVG avant la fermeture de Chrome. Le délai de rendu a été porté à 180 secondes par défaut, avec un délai séparé pour le nettoyage du navigateur. Un SVG complet est conservé si seule la fermeture bloque. Le rendu utilise le Plotly.js local et désactive le chargement de MathJax en ligne.

### Outputs et vérification

Les résultats sont enregistrés dans :

```text
Analyses/Diagramme_Sankey/
Analyses/Jaccard/
```

Les noms ont été raccourcis selon le modèle :

```text
sankey_Espece1_Espece2.html
sankey_Espece1_Espece2.svg
jaccard_Espece1_Espece2.html
jaccard_Espece1_Espece2.svg
```

Les fichiers `*_duplications.tsv` détaillent les annotations, y compris pour les séquences absentes des figures faute de BUSCO à copie unique communs.

### Figures retenues pour le rapport

Quatre figures sont conservées pour les deux comparaisons principales :

- Jaccard et Sankey de *Macrobrachium nipponense* × *Macrobrachium rosenbergii* ;
- Jaccard et Sankey d’*Eriocheir sinensis* × *Scylla paramamosain*.

Chez Macrobrachium, le chromosome 21 de M. nipponense partage ses 45 marqueurs BUSCO avec le chromosome 5 de M. rosenbergii (Jaccard = 1). Le chromosome 1 présente une autre répartition : 62 de ses 67 marqueurs se retrouvent sur les chromosomes 3 et 19 de M. rosenbergii.

Chez les crabes, les chromosomes 36 et 62 d’E. sinensis partagent respectivement 35 et 11 marqueurs avec le chromosome 20 de S. paramamosain, couvrant ainsi ses 46 marqueurs. Ces correspondances montrent qu’un ensemble de marqueurs peut rester groupé sur un chromosome chez une espèce et se répartir sur deux chez l’autre. Une fusion ou une fission reste une hypothèse à tester.
