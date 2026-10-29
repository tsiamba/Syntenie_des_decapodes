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

## Jeudi 29 octobre 2026 — Aurélio : organisation et vérification des résultats BUSCO

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
