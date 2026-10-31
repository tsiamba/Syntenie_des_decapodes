#!/usr/bin/env python3

import argparse
import glob
import os
import re
import sys
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.stats import spearmanr
import plotly.express as px
import plotly.graph_objects as go


def find_tsv_files(input_dir):
    """Recherche les fichiers TSV directement dans input_dir."""

    files = sorted(
        glob.glob(os.path.join(input_dir, "*.tsv"))
    )

    if len(files) == 0:
        print(
            f"[ERREUR] Aucun fichier TSV trouvé dans : {input_dir}",
            file=sys.stderr
        )
        sys.exit(1)

    return files


def genome_name(path):
    """Nom du génome = nom du fichier sans l'extension .tsv."""

    return os.path.splitext(
        os.path.basename(path)
    )[0]


def safe_name(name):
    """Nettoie un nom pour l'utiliser dans un nom de fichier."""

    return re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        name
    )


def load_tsv(path):
    """
    Charge un fichier TSV à 4 colonnes :

        busco_id    chromosome    start    end

    Les colonnes doivent être séparées par une tabulation
    ou par des espaces.
    """

    df = pd.read_csv(
        path,
        sep=r"\s+",
        header=None,
        comment="#",
        dtype=str,
        engine="python"
    )

    if df.shape[1] < 4:
        raise ValueError(
            f"{path} contient {df.shape[1]} colonnes. "
            f"Il faut au minimum 4 colonnes."
        )

    # On conserve les quatre premières colonnes
    df = df.iloc[:, :4].copy()

    df.columns = [
        "busco_id",
        "sequence",
        "start",
        "end"
    ]

    # Si une ligne d'en-tête existe, on la retire
    first_row = " ".join(
        df.iloc[0].astype(str).str.lower().tolist()
    )

    if (
        "busco" in first_row
        or "chrom" in first_row
        or "start" in first_row
    ):
        df = df.iloc[1:].copy()

    df["start"] = pd.to_numeric(
        df["start"],
        errors="coerce"
    )

    df["end"] = pd.to_numeric(
        df["end"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "busco_id",
            "sequence",
            "start",
            "end"
        ]
    ).copy()

    # Pour les gènes du brin négatif, start peut être supérieur à end.
    # On utilise la plus petite coordonnée comme position.
    df["position"] = df[["start", "end"]].min(axis=1)

    df = df[
        [
            "busco_id",
            "sequence",
            "position"
        ]
    ].rename(
        columns={
            "position": "start"
        }
    )

    # Supprimer les BUSCO dupliqués
    duplicated = df["busco_id"].duplicated(
        keep=False
    )

    if duplicated.any():
        duplicated_ids = df.loc[
            duplicated,
            "busco_id"
        ].unique()

        print(
            f"[ATTENTION] {os.path.basename(path)} : "
            f"{len(duplicated_ids)} BUSCO dupliqués supprimés"
        )

        df = df[
            ~df["busco_id"].isin(duplicated_ids)
        ].copy()

    return df.reset_index(drop=True)


def find_sequence_pairs(merged, min_shared):
    """
    Pour chaque séquence du génome 1, trouve la séquence
    du génome 2 partageant le plus de BUSCO.
    """

    pairs = []

    for seq1, group in merged.groupby("sequence_1"):
        counts = group["sequence_2"].value_counts()

        if counts.empty:
            continue

        seq2 = counts.idxmax()
        n_shared = int(counts.max())

        if n_shared >= min_shared:
            pairs.append(
                (
                    seq1,
                    seq2,
                    n_shared
                )
            )

    return pairs


def calculate_score(
    genome1,
    genome2,
    min_shared=5
):
    """
    Calcule le score de conservation de l'ordre.

    Le score varie approximativement de 0 à 1 :
      - proche de 1 : ordre conservé ;
      - proche de 0 : ordre peu conservé.

    abs(rho) est utilisé : une inversion régulière garde un score élevé.
    """

    merged = genome1.merge(
        genome2,
        on="busco_id",
        suffixes=("_1", "_2")
    )

    shared_genes = len(merged)

    if shared_genes < min_shared:
        return 0.0, shared_genes, 0

    pairs = find_sequence_pairs(
        merged,
        min_shared
    )

    if not pairs:
        return 0.0, shared_genes, 0

    weighted_scores = []
    weights = []

    for seq1, seq2, n in pairs:

        subset = merged[
            (merged["sequence_1"] == seq1)
            &
            (merged["sequence_2"] == seq2)
        ].copy()

        if len(subset) < 3:
            continue

        rho, _ = spearmanr(
            subset["start_1"],
            subset["start_2"]
        )

        if np.isnan(rho):
            continue

        weighted_scores.append(
            abs(float(rho)) * n
        )

        weights.append(n)

    if not weights:
        return 0.0, shared_genes, len(pairs)

    score = sum(weighted_scores) / sum(weights)

    return score, shared_genes, len(pairs)


def cumulative_positions(df, min_chrom_size):
    """
    Convertit les positions de plusieurs séquences en positions cumulées.
    """

    counts = df["sequence"].value_counts()

    valid_sequences = counts[
        counts >= min_chrom_size
    ].index

    df = df[
        df["sequence"].isin(valid_sequences)
    ].copy()

    if df.empty:
        return pd.DataFrame()

    max_positions = (
        df.groupby("sequence")["start"]
        .max()
        .sort_values(ascending=False)
    )

    offsets = {}
    cumulative = 0

    for sequence in max_positions.index:
        offsets[sequence] = cumulative

        cumulative += (
            int(max_positions[sequence])
            + 1_000_000
        )

    df["cum_pos"] = df.apply(
        lambda row: (
            row["start"]
            + offsets[row["sequence"]]
        ),
        axis=1
    )

    return df


def prepare_plot_data(
    genome1,
    genome2,
    min_chrom_size
):
    """Prépare les coordonnées des BUSCO communs."""

    merged = genome1.merge(
        genome2,
        on="busco_id",
        suffixes=("_1", "_2")
    )

    if merged.empty:
        return pd.DataFrame()

    df1 = merged[
        [
            "busco_id",
            "sequence_1",
            "start_1"
        ]
    ].rename(
        columns={
            "sequence_1": "sequence",
            "start_1": "start"
        }
    )

    df2 = merged[
        [
            "busco_id",
            "sequence_2",
            "start_2"
        ]
    ].rename(
        columns={
            "sequence_2": "sequence",
            "start_2": "start"
        }
    )

    df1 = cumulative_positions(
        df1,
        min_chrom_size
    )

    df2 = cumulative_positions(
        df2,
        min_chrom_size
    )

    if df1.empty or df2.empty:
        return pd.DataFrame()

    plot_df = df1[
        [
            "busco_id",
            "sequence",
            "cum_pos"
        ]
    ].rename(
        columns={
            "sequence": "chromosome_1",
            "cum_pos": "x"
        }
    )

    plot_df = plot_df.merge(
        df2[
            [
                "busco_id",
                "sequence",
                "cum_pos"
            ]
        ].rename(
            columns={
                "sequence": "chromosome_2",
                "cum_pos": "y"
            }
        ),
        on="busco_id"
    )

    return plot_df


def make_png(
    genome1,
    genome2,
    name1,
    name2,
    output_path,
    min_chrom_size
):
    """Crée un dotplot PNG."""

    plot_df = prepare_plot_data(
        genome1,
        genome2,
        min_chrom_size
    )

    if plot_df.empty:
        print(
            f"[ATTENTION] Aucun point pour "
            f"{name1} vs {name2}"
        )
        return False

    chromosomes = sorted(
        plot_df["chromosome_1"].unique()
    )

    cmap = cm.get_cmap(
        "tab20",
        max(len(chromosomes), 1)
    )

    color_map = {
        chromosome: cmap(i)
        for i, chromosome in enumerate(chromosomes)
    }

    point_colors = plot_df[
        "chromosome_1"
    ].map(color_map)

    fig, ax = plt.subplots(
        figsize=(10, 10)
    )

    ax.scatter(
        plot_df["x"],
        plot_df["y"],
        s=5,
        c=point_colors,
        alpha=0.75,
        linewidths=0
    )

    ax.set_xlabel(
        f"Position cumulée dans {name1}"
    )

    ax.set_ylabel(
        f"Position cumulée dans {name2}"
    )

    ax.set_title(
        f"Synténie BUSCO : {name1} vs {name2}\n"
        f"{len(plot_df)} BUSCO communs"
    )

    ax.set_xticks([])
    ax.set_yticks([])

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=250,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(
        f"[INFO] PNG créé : {output_path}"
    )

    return True


def make_html(
    genome1,
    genome2,
    name1,
    name2,
    output_path,
    min_chrom_size,
    title_prefix
):
    """Crée un dotplot HTML interactif."""

    plot_df = prepare_plot_data(
        genome1,
        genome2,
        min_chrom_size
    )

    if plot_df.empty:
        print(
            f"[ATTENTION] Aucun point HTML pour "
            f"{name1} vs {name2}"
        )
        return False

    chromosomes = sorted(
        plot_df["chromosome_1"].unique()
    )

    colors = (
        px.colors.qualitative.Alphabet
        + px.colors.qualitative.Dark24
    )

    color_map = {
        chromosome: colors[
            i % len(colors)
        ]
        for i, chromosome in enumerate(chromosomes)
    }

    fig = go.Figure()

    for chromosome in chromosomes:

        subset = plot_df[
            plot_df["chromosome_1"] == chromosome
        ].copy()

        hover_text = subset.apply(
            lambda row: (
                f"BUSCO : {row['busco_id']}<br>"
                f"{name1} : {row['chromosome_1']}<br>"
                f"{name2} : {row['chromosome_2']}<br>"
                f"Position {name1} : {row['x']}<br>"
                f"Position {name2} : {row['y']}"
            ),
            axis=1
        )

        fig.add_trace(
            go.Scattergl(
                x=subset["x"],
                y=subset["y"],
                mode="markers",
                marker={
                    "size": 5,
                    "color": color_map[chromosome],
                    "opacity": 0.75
                },
                name=str(chromosome),
                text=hover_text,
                hoverinfo="text"
            )
        )

    fig.update_layout(
        title=(
            f"{title_prefix}"
            f"Synténie BUSCO : {name1} vs {name2} "
            f"({len(plot_df)} BUSCO communs)"
        ),
        xaxis_title=(
            f"Position cumulée dans {name1}"
        ),
        yaxis_title=(
            f"Position cumulée dans {name2}"
        ),
        xaxis={
            "showticklabels": False
        },
        yaxis={
            "showticklabels": False
        },
        height=800,
        plot_bgcolor="white"
    )

    fig.write_html(
        output_path,
        include_plotlyjs=True
    )

    print(
        f"[INFO] HTML créé : {output_path}"
    )

    return True


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Compare tous les génomes deux par deux."
        )
    )

    parser.add_argument(
        "--input-dir",
        required=True,
        help="Dossier contenant les fichiers TSV."
    )

    parser.add_argument(
        "--out-dir",
        required=True,
        help="Dossier de sortie."
    )

    parser.add_argument(
        "--min-chrom-size",
        type=int,
        default=10,
        help=(
            "Nombre minimum de BUSCO par séquence "
            "pour l'inclure dans un dotplot."
        )
    )

    parser.add_argument(
        "--min-shared",
        type=int,
        default=5,
        help=(
            "Nombre minimum de BUSCO communs "
            "pour calculer le score."
        )
    )

    args = parser.parse_args()

    os.makedirs(
        args.out_dir,
        exist_ok=True
    )

    files = find_tsv_files(
        args.input_dir
    )

    print(
        f"[INFO] {len(files)} fichiers TSV trouvés."
    )

    if len(files) != 11:
        print(
            f"[ATTENTION] {len(files)} fichiers trouvés "
            f"au lieu de 11."
        )

    genomes = {}

    for path in files:

        name = genome_name(path)

        print(
            f"[INFO] Chargement : {name}"
        )

        try:
            genomes[name] = load_tsv(path)

        except Exception as error:
            print(
                f"[ERREUR] Problème avec {path} : {error}",
                file=sys.stderr
            )
            sys.exit(1)

        print(
            f"[INFO]   -> "
            f"{len(genomes[name])} BUSCO utilisables"
        )

    names = list(genomes.keys())

    total_pairs = (
        len(names)
        * (len(names) - 1)
        // 2
    )

    print(
        f"[INFO] Nombre de paires à comparer : "
        f"{total_pairs}"
    )

    # ---------------------------------------------------------------
    # Calcul des scores
    # ---------------------------------------------------------------

    results = []

    for number, (name1, name2) in enumerate(
        combinations(names, 2),
        start=1
    ):

        print(
            f"[SCORE {number}/{total_pairs}] "
            f"{name1} vs {name2}"
        )

        score, shared, sequence_pairs = calculate_score(
            genomes[name1],
            genomes[name2],
            min_shared=args.min_shared
        )

        results.append(
            {
                "genome_1": name1,
                "genome_2": name2,
                "synteny_score": round(score, 4),
                "busco_partages": shared,
                "paires_sequences": sequence_pairs
            }
        )

    scores = pd.DataFrame(
        results
    ).sort_values(
        by=[
            "synteny_score",
            "busco_partages"
        ],
        ascending=[
            False,
            False
        ]
    ).reset_index(drop=True)

    scores_path = os.path.join(
        args.out_dir,
        "synteny_scores.csv"
    )

    scores.to_csv(
        scores_path,
        index=False
    )

    # Paire la plus conservée
    best = scores.iloc[0]

    # Paire la plus éloignée
    worst = scores.iloc[-1]

    best_pair = (
        best["genome_1"],
        best["genome_2"]
    )

    worst_pair = (
        worst["genome_1"],
        worst["genome_2"]
    )

    print()
    print("=" * 70)
    print("PAIRE LA PLUS CONSERVÉE")
    print(
        f"{best['genome_1']} vs {best['genome_2']}"
    )
    print(
        f"Score : {best['synteny_score']}"
    )
    print(
        f"BUSCO partagés : {best['busco_partages']}"
    )
    print("=" * 70)
    print("PAIRE LA PLUS ÉLOIGNÉE")
    print(
        f"{worst['genome_1']} vs {worst['genome_2']}"
    )
    print(
        f"Score : {worst['synteny_score']}"
    )
    print(
        f"BUSCO partagés : {worst['busco_partages']}"
    )
    print("=" * 70)

    # ---------------------------------------------------------------
    # Dotplot PNG pour chaque paire
    # HTML seulement pour BEST et WORST
    # ---------------------------------------------------------------

    for number, (name1, name2) in enumerate(
        combinations(names, 2),
        start=1
    ):

        current_score = scores[
            (
                (scores["genome_1"] == name1)
                &
                (scores["genome_2"] == name2)
            )
            |
            (
                (scores["genome_1"] == name2)
                &
                (scores["genome_2"] == name1)
            )
        ].iloc[0]

        score = float(
            current_score["synteny_score"]
        )

        if (name1, name2) == best_pair:
            label = "BEST_CONSERVED__"

        elif (name1, name2) == worst_pair:
            label = "WORST_CONSERVED__"

        else:
            label = ""

        prefix = (
            f"{label}"
            f"{safe_name(name1)}__vs__"
            f"{safe_name(name2)}__"
            f"score_{score:.4f}"
        )

        png_path = os.path.join(
            args.out_dir,
            f"{prefix}.png"
        )

        print()
        print(
            f"[PLOT {number}/{total_pairs}] "
            f"{name1} vs {name2}"
        )

        make_png(
            genomes[name1],
            genomes[name2],
            name1,
            name2,
            png_path,
            args.min_chrom_size
        )

        # HTML de la paire la plus conservée
        if (name1, name2) == best_pair:

            html_path = os.path.join(
                args.out_dir,
                f"{prefix}.html"
            )

            make_html(
                genomes[name1],
                genomes[name2],
                name1,
                name2,
                html_path,
                args.min_chrom_size,
                "BEST_CONSERVED - "
            )

        # HTML de la paire la plus éloignée
        elif (name1, name2) == worst_pair:

            html_path = os.path.join(
                args.out_dir,
                f"{prefix}.html"
            )

            make_html(
                genomes[name1],
                genomes[name2],
                name1,
                name2,
                html_path,
                args.min_chrom_size,
                "WORST_CONSERVED - "
            )

    print()
    print("=" * 70)
    print("[INFO] Analyse terminée.")
    print(f"[INFO] {total_pairs} paires traitées.")
    print(f"[INFO] CSV : {scores_path}")
    print(f"[INFO] Résultats : {args.out_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
