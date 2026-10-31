#!/usr/bin/env python3
"""
Dotplots de synténie BUSCO pour toutes les paires de génomes.

- Chromosomes du génome 2 réordonnés selon leur meilleur partenaire
  dans le génome 1 (blocs conservés sur la diagonale).
- Chromosomes inversés retournés pour rester sur la diagonale.
- BUSCO appartenant à un bloc conservé : colorés (couleur du chr. du génome 1).
- Autres BUSCO : gris.
- Axes : noms des chromosomes + lignes de séparation.

Usage :
    python dotplot_all_pairs_V2.py --input-dir DIR_TSV --out-dir DIR_OUT \
        [--min-chrom-size 10] [--min-shared 5] [--min-block 10]
"""

import argparse
import glob
import os
import re
import sys
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import plotly.express as px
import plotly.graph_objects as go


PALETTE = (
    px.colors.qualitative.Alphabet
    + px.colors.qualitative.Dark24
)
GREY = "#aaaaaa"
GAP = 1_000_000


# ---------------------------------------------------------------------
# Lecture des données
# ---------------------------------------------------------------------

def find_tsv_files(input_dir):
    """Recherche les fichiers TSV directement dans input_dir."""
    files = sorted(glob.glob(os.path.join(input_dir, "*.tsv")))

    if len(files) == 0:
        print(
            f"[ERREUR] Aucun fichier TSV trouvé dans : {input_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    return files


def genome_name(path):
    """Nom du génome = nom du fichier sans l'extension .tsv."""
    return os.path.splitext(os.path.basename(path))[0]


def safe_name(name):
    """Nettoie un nom pour l'utiliser dans un nom de fichier."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def load_tsv(path):
    """
    Charge un fichier à 4 colonnes : busco_id, chromosome, start, end
    (séparées par tabulation ou espaces).
    """
    df = pd.read_csv(
        path,
        sep=r"\s+",
        header=None,
        comment="#",
        dtype=str,
        engine="python",
    )

    if df.shape[1] < 4:
        raise ValueError(
            f"{path} contient {df.shape[1]} colonnes. "
            f"Il faut au minimum 4 colonnes."
        )

    df = df.iloc[:, :4].copy()
    df.columns = ["busco_id", "sequence", "start", "end"]

    # Retirer une éventuelle ligne d'en-tête
    first_row = " ".join(df.iloc[0].astype(str).str.lower().tolist())
    if "busco" in first_row or "chrom" in first_row or "start" in first_row:
        df = df.iloc[1:].copy()

    df["start"] = pd.to_numeric(df["start"], errors="coerce")
    df["end"] = pd.to_numeric(df["end"], errors="coerce")

    df = df.dropna(subset=["busco_id", "sequence", "start", "end"]).copy()

    # Brin négatif : start peut être > end -> on prend le plus petit
    df["position"] = df[["start", "end"]].min(axis=1)

    df = df[["busco_id", "sequence", "position"]].rename(
        columns={"position": "start"}
    )

    # Supprimer les BUSCO dupliqués
    duplicated = df["busco_id"].duplicated(keep=False)
    if duplicated.any():
        duplicated_ids = df.loc[duplicated, "busco_id"].unique()
        print(
            f"[ATTENTION] {os.path.basename(path)} : "
            f"{len(duplicated_ids)} BUSCO dupliqués supprimés"
        )
        df = df[~df["busco_id"].isin(duplicated_ids)].copy()

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------
# Score de synténie
# ---------------------------------------------------------------------

def find_sequence_pairs(merged, min_shared):
    """
    Pour chaque séquence du génome 1, trouve la séquence du génome 2
    partageant le plus de BUSCO.
    """
    pairs = []

    for seq1, group in merged.groupby("sequence_1"):
        counts = group["sequence_2"].value_counts()
        if counts.empty:
            continue

        seq2 = counts.idxmax()
        n_shared = int(counts.max())

        if n_shared >= min_shared:
            pairs.append((seq1, seq2, n_shared))

    return pairs


def calculate_score(genome1, genome2, min_shared=5):
    """
    Score de conservation de l'ordre (0 à 1), basé sur |rho| de Spearman
    pondéré par le nombre de BUSCO de chaque paire de séquences.
    """
    merged = genome1.merge(genome2, on="busco_id", suffixes=("_1", "_2"))

    shared_genes = len(merged)

    if shared_genes < min_shared:
        return 0.0, shared_genes, 0

    pairs = find_sequence_pairs(merged, min_shared)

    if not pairs:
        return 0.0, shared_genes, 0

    weighted_scores = []
    weights = []

    for seq1, seq2, n in pairs:
        subset = merged[
            (merged["sequence_1"] == seq1) & (merged["sequence_2"] == seq2)
        ]

        if len(subset) < 3:
            continue

        rho, _ = spearmanr(subset["start_1"], subset["start_2"])

        if np.isnan(rho):
            continue

        weighted_scores.append(abs(float(rho)) * n)
        weights.append(n)

    if not weights:
        return 0.0, shared_genes, len(pairs)

    score = sum(weighted_scores) / sum(weights)

    return score, shared_genes, len(pairs)


# ---------------------------------------------------------------------
# Préparation des données du dotplot
# ---------------------------------------------------------------------

def make_offsets(order, lengths):
    """Positions cumulées de début de chaque chromosome."""
    offsets, info, cumulative = {}, [], 0
    for seq in order:
        offsets[seq] = cumulative
        info.append((seq, cumulative, cumulative + int(lengths[seq])))
        cumulative += int(lengths[seq]) + GAP
    return offsets, info


def prepare_plot_data(genome1, genome2, min_chrom_size, min_block):
    """
    Renvoie (plot_df, info1, info2).

    plot_df : busco_id, chromosome_1, chromosome_2, x, y, conserved
    info1/info2 : liste de (chromosome, début_cumulé, fin_cumulée)
    """
    merged = genome1.merge(genome2, on="busco_id", suffixes=("_1", "_2"))

    if merged.empty:
        return pd.DataFrame(), [], []

    # Garder les séquences avec assez de BUSCO partagés
    c1 = merged["sequence_1"].value_counts()
    c2 = merged["sequence_2"].value_counts()

    merged = merged[
        merged["sequence_1"].isin(c1[c1 >= min_chrom_size].index)
        & merged["sequence_2"].isin(c2[c2 >= min_chrom_size].index)
    ].copy()

    if merged.empty:
        return pd.DataFrame(), [], []

    len1 = merged.groupby("sequence_1")["start_1"].max()
    len2 = merged.groupby("sequence_2")["start_2"].max()
    counts = merged.groupby(["sequence_1", "sequence_2"]).size()

    # Ordre du génome 1 : taille décroissante
    order1 = len1.sort_values(ascending=False).index.tolist()

    # Ordre du génome 2 : meilleur partenaire non encore placé
    order2 = []
    for s1 in order1:
        for s2 in counts[s1].sort_values(ascending=False).index:
            if s2 not in order2:
                order2.append(s2)
                break

    # Chromosomes du génome 2 restants
    for s2 in len2.sort_values(ascending=False).index:
        if s2 not in order2:
            order2.append(s2)

    # Orientation : retourner le chr2 si corrélation négative
    # avec son meilleur partenaire
    flip = {}
    for s2 in order2:
        s1 = counts.xs(s2, level=1).idxmax()
        sub = merged[
            (merged["sequence_1"] == s1) & (merged["sequence_2"] == s2)
        ]
        rho = 0.0
        if len(sub) >= 3:
            rho, _ = spearmanr(sub["start_1"], sub["start_2"])
            if np.isnan(rho):
                rho = 0.0
        flip[s2] = bool(rho < 0)

    do_flip = merged["sequence_2"].map(flip).astype(bool)

    pos2 = np.where(
        do_flip,
        merged["sequence_2"].map(len2) - merged["start_2"],
        merged["start_2"],
    )

    off1, info1 = make_offsets(order1, len1)
    off2, info2 = make_offsets(order2, len2)

    merged["x"] = merged["start_1"] + merged["sequence_1"].map(off1)
    merged["y"] = pos2 + merged["sequence_2"].map(off2)

    # Bloc conservé = paire (chr1, chr2) avec au moins min_block BUSCO
    n_pair = merged.groupby(["sequence_1", "sequence_2"])[
        "busco_id"
    ].transform("size")
    merged["conserved"] = n_pair >= min_block

    plot_df = merged[
        ["busco_id", "sequence_1", "sequence_2", "x", "y", "conserved"]
    ].rename(
        columns={
            "sequence_1": "chromosome_1",
            "sequence_2": "chromosome_2",
        }
    )

    return plot_df, info1, info2


# ---------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------

def make_png(
    genome1, genome2, name1, name2, output_path, min_chrom_size, min_block
):
    """Crée un dotplot PNG."""

    plot_df, info1, info2 = prepare_plot_data(
        genome1, genome2, min_chrom_size, min_block
    )

    if plot_df.empty:
        print(f"[ATTENTION] Aucun point pour {name1} vs {name2}")
        return False

    color_map = {
        seq: PALETTE[i % len(PALETTE)]
        for i, (seq, _, _) in enumerate(info1)
    }

    grey = plot_df[~plot_df["conserved"]]
    colored = plot_df[plot_df["conserved"]]

    fig, ax = plt.subplots(figsize=(10, 10))

    # Gris en fond, blocs conservés par-dessus
    ax.scatter(grey["x"], grey["y"], s=8, c=GREY, alpha=0.7, linewidths=0)
    ax.scatter(
        colored["x"],
        colored["y"],
        s=10,
        c=colored["chromosome_1"].map(color_map).tolist(),
        alpha=0.9,
        linewidths=0,
    )

    # Lignes de séparation entre chromosomes
    for _, start, _ in info1[1:]:
        ax.axvline(start - GAP / 2, color="grey", lw=0.4, alpha=0.5)
    for _, start, _ in info2[1:]:
        ax.axhline(start - GAP / 2, color="grey", lw=0.4, alpha=0.5)

    # Noms des chromosomes au centre de chacun
    ax.set_xticks([(s + e) / 2 for _, s, e in info1])
    ax.set_xticklabels([n for n, _, _ in info1], rotation=90, fontsize=6)
    ax.set_yticks([(s + e) / 2 for _, s, e in info2])
    ax.set_yticklabels([n for n, _, _ in info2], fontsize=6)
    ax.tick_params(length=0)
    ax.set_xlim(0, info1[-1][2])
    ax.set_ylim(0, info2[-1][2])

    ax.set_xlabel(name1)
    ax.set_ylabel(name2)
    ax.set_title(
        f"Synténie BUSCO : {name1} vs {name2}\n"
        f"{len(plot_df)} BUSCO communs "
        f"({len(colored)} en blocs conservés)"
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=250, bbox_inches="tight")
    plt.close(fig)

    print(f"[INFO] PNG créé : {output_path}")
    return True


def make_html(
    genome1,
    genome2,
    name1,
    name2,
    output_path,
    min_chrom_size,
    min_block,
    title_prefix,
):
    """Crée un dotplot HTML interactif."""

    plot_df, info1, info2 = prepare_plot_data(
        genome1, genome2, min_chrom_size, min_block
    )

    if plot_df.empty:
        print(f"[ATTENTION] Aucun point HTML pour {name1} vs {name2}")
        return False

    color_map = {
        seq: PALETTE[i % len(PALETTE)]
        for i, (seq, _, _) in enumerate(info1)
    }

    def hover(df):
        return df.apply(
            lambda r: (
                f"BUSCO : {r['busco_id']}<br>"
                f"{name1} : {r['chromosome_1']}<br>"
                f"{name2} : {r['chromosome_2']}"
            ),
            axis=1,
        )

    fig = go.Figure()

    grey = plot_df[~plot_df["conserved"]]
    if not grey.empty:
        fig.add_trace(
            go.Scattergl(
                x=grey["x"],
                y=grey["y"],
                mode="markers",
                marker={"size": 5, "color": GREY, "opacity": 0.6},
                name="non conservé",
                text=hover(grey),
                hoverinfo="text",
            )
        )

    for chromosome, _, _ in info1:
        sub = plot_df[
            plot_df["conserved"] & (plot_df["chromosome_1"] == chromosome)
        ]
        if sub.empty:
            continue

        fig.add_trace(
            go.Scattergl(
                x=sub["x"],
                y=sub["y"],
                mode="markers",
                marker={
                    "size": 6,
                    "color": color_map[chromosome],
                    "opacity": 0.9,
                },
                name=str(chromosome),
                text=hover(sub),
                hoverinfo="text",
            )
        )

    fig.update_layout(
        title=(
            f"{title_prefix}"
            f"Synténie BUSCO : {name1} vs {name2} "
            f"({len(plot_df)} BUSCO communs)"
        ),
        xaxis_title=name1,
        yaxis_title=name2,
        xaxis={
            "tickmode": "array",
            "tickvals": [(s + e) / 2 for _, s, e in info1],
            "ticktext": [n for n, _, _ in info1],
            "tickangle": 90,
            "range": [0, info1[-1][2]],
        },
        yaxis={
            "tickmode": "array",
            "tickvals": [(s + e) / 2 for _, s, e in info2],
            "ticktext": [n for n, _, _ in info2],
            "range": [0, info2[-1][2]],
        },
        height=800,
        plot_bgcolor="white",
    )

    fig.write_html(output_path, include_plotlyjs=True)

    print(f"[INFO] HTML créé : {output_path}")
    return True


# ---------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compare tous les génomes deux par deux."
    )
    parser.add_argument(
        "--input-dir", required=True, help="Dossier contenant les TSV."
    )
    parser.add_argument(
        "--out-dir", required=True, help="Dossier de sortie."
    )
    parser.add_argument(
        "--min-chrom-size",
        type=int,
        default=10,
        help="BUSCO partagés minimum par séquence pour l'afficher.",
    )
    parser.add_argument(
        "--min-shared",
        type=int,
        default=5,
        help="BUSCO communs minimum pour calculer le score.",
    )
    parser.add_argument(
        "--min-block",
        type=int,
        default=10,
        help="BUSCO minimum par paire de chromosomes pour colorer un bloc.",
    )

    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    files = find_tsv_files(args.input_dir)
    print(f"[INFO] {len(files)} fichiers TSV trouvés.")

    if len(files) != 11:
        print(f"[ATTENTION] {len(files)} fichiers trouvés au lieu de 11.")

    genomes = {}

    for path in files:
        name = genome_name(path)
        print(f"[INFO] Chargement : {name}")

        try:
            genomes[name] = load_tsv(path)
        except Exception as error:
            print(
                f"[ERREUR] Problème avec {path} : {error}", file=sys.stderr
            )
            sys.exit(1)

        print(f"[INFO]   -> {len(genomes[name])} BUSCO utilisables")

    names = list(genomes.keys())
    total_pairs = len(names) * (len(names) - 1) // 2

    print(f"[INFO] Nombre de paires à comparer : {total_pairs}")

    # ---- Scores ----
    results = []

    for number, (name1, name2) in enumerate(combinations(names, 2), start=1):
        print(f"[SCORE {number}/{total_pairs}] {name1} vs {name2}")

        score, shared, sequence_pairs = calculate_score(
            genomes[name1], genomes[name2], min_shared=args.min_shared
        )

        results.append(
            {
                "genome_1": name1,
                "genome_2": name2,
                "synteny_score": round(score, 4),
                "busco_partages": shared,
                "paires_sequences": sequence_pairs,
            }
        )

    scores = (
        pd.DataFrame(results)
        .sort_values(
            by=["synteny_score", "busco_partages"], ascending=[False, False]
        )
        .reset_index(drop=True)
    )

    scores_path = os.path.join(args.out_dir, "synteny_scores.csv")
    scores.to_csv(scores_path, index=False)

    best = scores.iloc[0]
    worst = scores.iloc[-1]

    best_pair = (best["genome_1"], best["genome_2"])
    worst_pair = (worst["genome_1"], worst["genome_2"])

    print()
    print("=" * 70)
    print("PAIRE LA PLUS CONSERVÉE")
    print(f"{best['genome_1']} vs {best['genome_2']}")
    print(f"Score : {best['synteny_score']}")
    print(f"BUSCO partagés : {best['busco_partages']}")
    print("=" * 70)
    print("PAIRE LA PLUS ÉLOIGNÉE")
    print(f"{worst['genome_1']} vs {worst['genome_2']}")
    print(f"Score : {worst['synteny_score']}")
    print(f"BUSCO partagés : {worst['busco_partages']}")
    print("=" * 70)

    # ---- Dotplots : PNG pour toutes les paires, HTML pour best/worst ----
    for number, (name1, name2) in enumerate(combinations(names, 2), start=1):

        current = scores[
            ((scores["genome_1"] == name1) & (scores["genome_2"] == name2))
            | ((scores["genome_1"] == name2) & (scores["genome_2"] == name1))
        ].iloc[0]

        score = float(current["synteny_score"])

        if (name1, name2) == best_pair:
            label = "BEST_CONSERVED__"
            html_title = "BEST_CONSERVED - "
        elif (name1, name2) == worst_pair:
            label = "WORST_CONSERVED__"
            html_title = "WORST_CONSERVED - "
        else:
            label = ""
            html_title = None

        prefix = (
            f"{label}"
            f"{safe_name(name1)}__vs__{safe_name(name2)}__"
            f"score_{score:.4f}"
        )

        png_path = os.path.join(args.out_dir, f"{prefix}.png")

        print()
        print(f"[PLOT {number}/{total_pairs}] {name1} vs {name2}")

        make_png(
            genomes[name1],
            genomes[name2],
            name1,
            name2,
            png_path,
            args.min_chrom_size,
            args.min_block,
        )

        if html_title is not None:
            html_path = os.path.join(args.out_dir, f"{prefix}.html")

            make_html(
                genomes[name1],
                genomes[name2],
                name1,
                name2,
                html_path,
                args.min_chrom_size,
                args.min_block,
                html_title,
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
