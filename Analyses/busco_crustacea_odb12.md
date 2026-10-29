## Résultats BUSCO — crustacea_odb12

- Jeu de données : `crustacea_odb12`
- Nombre de marqueurs recherchés par génome : 1 536
- Méthode : Miniprot
- Scores exprimés en pourcentage.

| Espèce | Identifiant du génome | Complets C | Copie unique S | Dupliqués D | Fragmentés F | Manquants M |
|---|---|---:|---:|---:|---:|---:|
| *Jaera praehirsuta* | GCA_965208005.1 | 97,1 | 94,6 | 2,5 | 1,0 | 1,9 |
| *Penaeus chinensis* | GCF_019202785.1 | 96,1 | 96,0 | 0,1 | 1,8 | 2,1 |
| *Portunus trituberculatus* | GCF_017591435.1 | 98,4 | 98,0 | 0,4 | 0,8 | 0,8 |
| *Penaeus vannamei* | GCF_042767895.1 | 86,5 | 85,3 | 1,2 | 5,7 | 7,8 |
| *Eriocheir sinensis* | GCF_024679095.1 | 98,9 | 95,1 | 3,8 | 0,3 | 0,8 |
| *Scylla paramamosain* | GCF_035594125.1 | 99,9 | 99,2 | 0,7 | 0,1 | 0,1 |
| *Macrobrachium rosenbergii* | GCF_040412425.1 | 97,3 | 96,7 | 0,5 | 2,3 | 0,5 |
| *Procambarus clarkii* | GCF_040958095.1 | 98,5 | 91,9 | 6,6 | 0,9 | 0,6 |
| *Macrobrachium nipponense* | GCF_015104395.2 | 90,5 | 87,3 | 3,2 | 7,0 | 2,5 |
| *Panulirus ornatus* | GCF_036320965.1 | 97,8 | 96,9 | 0,9 | 1,8 | 0,4 |
| *Cherax quadricarinatus* | GCF_038502225.1 | 88,5 | 87,5 | 1,0 | 5,5 | 6,0 |

**Définitions :** C = complets (S + D) ; S = complets à copie unique ;
D = complets dupliqués ; F = fragmentés ; M = manquants.

## Choix Génomes de Référence: crustacea_odb12

Nous avons retenu le jeu de données `crustacea_odb12`, daté du
22 mai 2026 et comprenant 1 536 groupes de marqueurs BUSCO,
pour les comparaisons finales du projet.

Ce choix repose sur trois raisons :

1. **Une référence adaptée aux espèces étudiées.**
   Le jeu `crustacea_odb12` est consacré aux crustacés, groupe auquel
   appartiennent les dix décapodes étudiés ainsi que l’isopode
   *Jaera praehirsuta*, utilisé comme groupe externe. Il correspond
   donc plus précisément à notre échantillonnage que le jeu plus
   général `arthropoda_odb10` utilisé lors des premières analyses.

2. **Une référence commune aux résultats locaux et précalculés.**
   Certains génomes étaient trop volumineux pour être analysés avec
   les ressources disponibles sur notre cluster. Les résultats
   fournis par l’enseignant pour ces génomes utilisent
   `crustacea_odb12`. Nous avons retenu cette même référence pour
   réunir les résultats locaux et ceux de l’enseignant sans imposer
   de nouveaux calculs lourds.

3. **Des marqueurs comparables entre génomes.**
   L’utilisation du même jeu de données permet de rechercher les
   mêmes groupes BUSCO dans tous les génomes. Les en-têtes des onze
   tables confirment le même nom de référence, la même date de
   création et le même nombre de marqueurs. Les résultats obtenus
   avec `arthropoda_odb10` ou `crustacea_odb12.2` restent conservés
   comme historique et ne sont pas mélangés directement à cette
   série finale.

### Versions des logiciels et limites

Toutes les analyses retenues utilisent Miniprot, mais deux ensembles
de versions sont présents :

| Origine des résultats | Nombre de génomes | BUSCO | Miniprot |
|---|---:|---|---|
| Calculs locaux | 6 | 6.1.0 | 0.18-r281 |
| Résultats fournis par l’enseignant | 5 | 5.8.2 | 0.13-r248 |

Le jeu de données est donc commun, tandis que les versions des
logiciels diffèrent. Cette différence doit être conservée dans la
description des méthodes et prise en compte dans l’interprétation
des résultats.

Pour les comparaisons principales de synténie, nous retiendrons les
marqueurs complets à copie unique communs aux génomes comparés, avec
des positions exploitables. Le nombre de marqueurs effectivement
retenus sera indiqué pour chaque comparaison.
