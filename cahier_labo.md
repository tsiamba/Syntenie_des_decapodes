
# Dimanche 13 sept: Choix des génomes.
Les génomes ont été choisis selon plusieur critères, qui, dans l'ordre d'importance, sont les suivants:
- 1. Tous les génomes ont des chromosome level assembly;
- 2. Tous les génomes de décapodes ont des scores BUSCO GC d'au moins 90%, pour avoir une bonne complétude; 
- 3. Les génomes avec les meilleures contig N50 ont été choisis de manière à garder une bonne contiguité;
- 4. Les génomes ont été choisis de manière à garder une diversité phylogénétique au sein de decapoda.

Création de l'environnement conda : 1er essai, Tsiambaka (Semaine du 14/09/26, je ne sais plus quel jour)
Installation de bioconda, busco (Jade)
Analyse busco (Aurelio)
Git init, git push (Tsiambaka)
Droits et permissions (Jade/Aurelio)
Ajout des génomes (Jade)
Ajout de l'isopode GenBank (Tsiambaka)

Création du cahier de labo (Tsiambaka)

Dimanche 20 sept Modification readme / Set up gitignore / Copie du repository / Set up git pull push (Aurélio) - 2h
Lundi 21 sept Modification gitignore un nouvelle environnement pour busco / lancer analyse busco (Aurélio) - 1h
Vendredi 25 septembre Essayé de faire marcher busco problème serveur saturé par le script 8 coeurs -> 4 coeurs  / Modification du script et rerun busco (Aurélio) - 2h
Dimanche 27 septembre Problème avec certain génomes qui sature le serveur / Création d'un fichier log ou j'ai affiché tout ce que busco m'a renvoyer (Aurélio) - 1h
Dimanche 27 Septembre : Lancement de BUSCO sur Isopode Jarea (Tsiambaka), lancement avec 3 coeurs sur le serveur, Analyse a duré 24190 secondes
Lundi 28 septembre Vérification des analyses busco et modification du fichier log pour ajouter les dernières info sur l'analyse busco essayer de comprendre le problème d'analyse busco (Aurélio) - 45 min
Mardi 29 septembre Vérification de la fin de l'analyse busco modification du script pour relancer sur ceux qui sont pas passez update le fichier log (Aurélio) - 20 min


Commandes : gunzip -k /data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data/GCA_965208005.1/GCA_965208005.1_qmJaePrae1.hap1.1_genomic.fna.gz
pour dézipepr le genome puis FNA=$(find /data/projet2/Syntenie_des_decapodes/genomes/ncbi_dataset/data/GCA_965208005.1 -name "*_genomic.fna")
echo "$FNA" pour lancer l'analyse BUSCO ~ 1h

scp vitale@ptu.bigest-icube.fr:/data/projet2/Syntenie_des_decapodes/log_analyse_busco.md . 
-> à executer en dehors de ssh récupérer les fichier depuis le cluster

script d'analyse busco
