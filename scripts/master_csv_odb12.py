#!/usr/bin/env python3
import os
import re
import pandas as pd

# ==========================================
# 1. GESTION DES DOSSIERS
# ==========================================
PROJECT_DIR = "/data/projet2/Syntenie_des_decapodes"

BUSCO_BASE_DIR = os.path.join(
    PROJECT_DIR,
    "Busco",
    "precomputed_crustacea_odb12",
    "BUSCO",
)

LINEAGE_DIR = "run_crustacea_odb12"

DIR_OUTPUT = os.path.join(
    PROJECT_DIR,
    "Analyses",
    "Diagramme_Sankey",
    "Miniprot",
    "output",
)

# ==========================================
# 2. EXTRACTION DES MARQUEURS À COPIE UNIQUE
# ==========================================
all_genomes_data = []
genomes_seen = set()

columns = [
    "Busco_id", "Status", "Sequence", "Start", "End",
    "Strand", "Score", "Length", "OrthoDB", "Description",
]

print("Extraction des positions BUSCO...")

for folder in sorted(os.listdir(BUSCO_BASE_DIR)):

    # Les deux types de dossiers présents dans ton projet.
    if not folder.startswith(("resultats_busco_", "BUSCO_")):
        continue

    full_table_path = os.path.join(
        BUSCO_BASE_DIR,
        folder,
        LINEAGE_DIR,
        "full_table.tsv",
    )

    if not os.path.isfile(full_table_path):
        raise FileNotFoundError(
            f"Table BUSCO introuvable : {full_table_path}"
        )

    # Récupération de l'accession, sans le nom complet du FASTA.
    match = re.search(r"GC[AF]_\d+\.\d+", folder)
    if match is None:
        raise ValueError(f"Accession introuvable dans : {folder}")

    genome_name = match.group(0)

    if genome_name in genomes_seen:
        raise ValueError(
            f"Plusieurs dossiers correspondent à {genome_name}"
        )
    genomes_seen.add(genome_name)

    df = pd.read_csv(
        full_table_path,
        sep="\t",
        comment="#",
        header=None,
        names=columns,
        dtype={"Busco_id": str, "Sequence": str, "Strand": str},
    )

    # Complete correspond aux marqueurs complets à copie unique.
    df_comp = df[df["Status"] == "Complete"].copy()

    # Exclusion des identifiants ayant plusieurs lignes dans la table.
    repeated_ids = df.loc[
        df["Busco_id"].duplicated(keep=False),
        "Busco_id",
    ]
    df_comp = df_comp[
        ~df_comp["Busco_id"].isin(repeated_ids)
    ].copy()

    coordinates = df_comp[["Start", "End"]].apply(
        pd.to_numeric, errors="raise"
    )

    if (
        coordinates.isna().any().any()
        or (coordinates < 0).any().any()
        or (coordinates % 1 != 0).any().any()
    ):
        raise ValueError(f"Coordonnées invalides pour {genome_name}")

    if (
        df_comp["Sequence"].isna().any()
        or not df_comp["Strand"].isin(["+", "-"]).all()
    ):
        raise ValueError(
            f"Séquence ou brin invalide pour {genome_name}"
        )

    # Remise des bornes dans l'ordre croissant, sans décalage.
    # Le brin d'origine est conservé.
    df_comp["Start"] = coordinates.min(axis=1).astype("int64")
    df_comp["End"] = coordinates.max(axis=1).astype("int64")

    # Conservation des identifiants réels des séquences.
    # Aucun renommage artificiel en Chr 1, Chr 2, etc.
    df_comp["Chromosome"] = df_comp["Sequence"]
    df_comp["Organisme"] = genome_name

    df_csv = df_comp[
        [
            "Organisme", "Chromosome", "Sequence",
            "Busco_id", "Start", "End", "Strand",
        ]
    ]

    all_genomes_data.append(df_csv)

    print(
        f" -> {genome_name} : "
        f"{len(df_csv)} marqueurs à copie unique retenus"
    )

# ==========================================
# 3. CRÉATION DU TABLEAU COMMUN
# ==========================================
if not all_genomes_data:
    raise SystemExit("Aucune table BUSCO trouvée.")

df_master = pd.concat(all_genomes_data, ignore_index=True)

if df_master.empty:
    raise SystemExit("Aucun marqueur à copie unique retenu.")

df_master = df_master.sort_values(
    ["Organisme", "Sequence", "Start", "Busco_id"]
).reset_index(drop=True)

os.makedirs(DIR_OUTPUT, exist_ok=True)

master_csv_path = os.path.join(
    DIR_OUTPUT,
    "master_positions_busco.csv",
)

# mode="x" protège un éventuel fichier déjà existant.
df_master.to_csv(
    master_csv_path,
    index=False,
    encoding="utf-8",
    mode="x",
)

print(f"\nGénomes traités : {len(genomes_seen)}")
print(f"Positions enregistrées : {len(df_master)}")
print(f"Master CSV sauvegardé : {master_csv_path}")
