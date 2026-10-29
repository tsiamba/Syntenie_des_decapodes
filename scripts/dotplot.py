
"""
dotplot.py

Analyse automatique de synthenie a partir de plusieurs fichiers full_table.tsv
de BUSCO (un par genome). Pour chaque paire de genomes :
  1. Identifie les genes BUSCO "Complete" communs
  2. Calcule un score de conservation de l'ordre des genes (correlation de
     Spearman, par paire de chromosomes orthologues les plus probables)
  3. Produit un tableau recapitulatif (synteny_scores.csv)
  4. Genere automatiquement le dot plot pour :
       - la paire la PLUS conservee (score le plus eleve)
       - la paire la MOINS conservee / la plus eloignee (score le plus bas)
     Chaque dot plot est sauvegarde en DEUX versions, comme le diagramme de
     Sankey de l'equipe (sankey_syntenie.py) :
       - un .png statique (matplotlib) : leger, pratique pour le rapport/README
       - un .html interactif (plotly) : zoom, survol pour voir le busco_id et
         les deux chromosomes, exactement comme fig.write_html(...) dans le
         script Sankey

Usage :
    python3 busco_synteny_analysis.py \
        --input-dir /data/projet2/Syntenie_des_decapodes \
        --lineage crustacea_odb12 \
        --out-dir plots \
        --min-chrom-size 15

Recherche des fichiers :
    Le script cherche TOUS les "run_<lineage>/full_table.tsv" n'importe ou
    sous --input-dir, peu importe la structure de dossiers utilisee par
    chaque membre de l'equipe (ex: resultats_busco_XXX/, mais aussi
    busco_metaeuk/busco_output/resultats_busco_XXX/,
    busco_miniprot/busco_output/..., ou precomputed_crustacea_odb12/...).
    Ca garantit que tout le monde travaille sur la meme base de donnees
    (meme lineage BUSCO), meme si les resultats de chacun sont ranges
    differemment sur le serveur.

    Si plusieurs full_table.tsv sont trouves pour la meme accession
    (ex: calcule deux fois par deux personnes), le script garde le fichier
    le plus recent (date de modification) et affiche un avertissement.

Dependances :
    pip install pandas matplotlib scipy plotly --break-system-packages
"""

import argparse
import glob
import os
import re
import sys
from itertools import combinations

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.stats import spearmanr
import plotly.express as px
import plotly.graph_objects as go


BUSCO_COLUMNS = ["busco_id", "status", "sequence", "start", "end", "strand", "score", "length"]


# ----------------------------------------------------------------------
# Chargement des donnees
# ----------------------------------------------------------------------

def find_full_tables(input_dir, lineage):
    """
    Cherche TOUS les full_table.tsv correspondant au lineage donne,
    n'importe ou sous input_dir (recherche recursive). Ca permet de
    rassembler les resultats de toute l'equipe meme s'ils sont ranges
    dans des sous-dossiers differents (resultats_busco_*/,
    busco_metaeuk/busco_output/resultats_busco_*/,
    busco_miniprot/busco_output/..., precomputed_crustacea_odb12/...),
    du moment qu'ils utilisent le meme lineage BUSCO.

    Si plusieurs fichiers correspondent a la meme accession, garde celui
    modifie le plus recemment et previent par un avertissement (pour
    reperer un eventuel doublon calcule par deux personnes differentes).
    """
    pattern = os.path.join(input_dir, "**", f"run_{lineage}", "full_table.tsv")
    files = glob.glob(pattern, recursive=True)

    if not files:
        print(f"[ATTENTION] Aucun full_table.tsv trouve pour le lineage "
              f"'{lineage}' sous {input_dir}.", file=sys.stderr)
        return {}

    # Regrouper par accession (GCF_xxxxxxxxx.x ou GCA_xxxxxxxxx.x)
    candidates = {}
    for f in files:
        m = re.search(r"(GC[AF]_\d+\.\d+)", f)
        if not m:
            continue
        acc = m.group(1)
        candidates.setdefault(acc, []).append(f)

    genomes = {}
    for acc, paths in candidates.items():
        if len(paths) > 1:
            # Garder le plus recent, avertir sur les doublons
            paths_sorted = sorted(paths, key=os.path.getmtime, reverse=True)
            print(f"[ATTENTION] {len(paths)} fichiers full_table.tsv trouves "
                  f"pour {acc} (lineage {lineage}) :")
            for p in paths_sorted:
                print(f"    - {p}")
            print(f"    -> on garde le plus recent : {paths_sorted[0]}")
            genomes[acc] = paths_sorted[0]
        else:
            genomes[acc] = paths[0]

    return genomes


def load_full_table(path):
    """Charge un full_table.tsv, ne garde que les genes Complete non dupliques."""
    df = pd.read_csv(path, sep="\t", comment="#", header=None,
                      names=BUSCO_COLUMNS, usecols=range(8))
    df = df[df["status"] == "Complete"].copy()
    df["start"] = pd.to_numeric(df["start"], errors="coerce")
    df = df.dropna(subset=["start"])

    dup_ids = df["busco_id"][df["busco_id"].duplicated(keep=False)]
    if len(dup_ids) > 0:
        df = df[~df["busco_id"].isin(dup_ids.unique())]

    return df[["busco_id", "sequence", "start"]]


# ----------------------------------------------------------------------
# Calcul du score de synthenie entre deux genomes
# ----------------------------------------------------------------------

def best_chromosome_pairs(merged, min_shared=5):
    """
    Pour chaque chromosome du genome 1, trouve le chromosome du genome 2
    qui partage le plus de genes avec lui (= chromosome orthologue probable).
    Retourne une liste de tuples (chr_1, chr_2, nb_genes_partages).
    """
    pairs = []
    for chr1, group in merged.groupby("sequence_1"):
        counts = group["sequence_2"].value_counts()
        if len(counts) == 0:
            continue
        best_chr2 = counts.idxmax()
        n_shared = counts.max()
        if n_shared >= min_shared:
            pairs.append((chr1, best_chr2, n_shared))
    return pairs


def synteny_score(g1, g2, min_shared=5):
    """
    Calcule un score global de synthenie entre deux genomes :
    moyenne (ponderee par le nb de genes) des |rho| de Spearman sur
    chaque paire de chromosomes orthologues identifiee.

    Retourne (score, nb_genes_communs_total, nb_paires_chromosomes)
    """
    merged = g1.merge(g2, on="busco_id", suffixes=("_1", "_2"))
    if len(merged) < min_shared:
        return 0.0, len(merged), 0

    pairs = best_chromosome_pairs(merged, min_shared=min_shared)
    if not pairs:
        return 0.0, len(merged), 0

    weighted_rhos = []
    weights = []
    for chr1, chr2, n in pairs:
        sub = merged[(merged["sequence_1"] == chr1) & (merged["sequence_2"] == chr2)]
        if len(sub) < 3:
            continue
        rho, _ = spearmanr(sub["start_1"], sub["start_2"])
        if np.isnan(rho):
            continue
        weighted_rhos.append(abs(rho) * n)
        weights.append(n)

    if not weights:
        return 0.0, len(merged), len(pairs)

    score = sum(weighted_rhos) / sum(weights)
    return score, len(merged), len(pairs)


# ----------------------------------------------------------------------
# Dot plot
# ----------------------------------------------------------------------

def compute_cumulative_offsets(df, min_chrom_size=10):
    counts = df["sequence"].value_counts()
    valid_seqs = counts[counts >= min_chrom_size].index.tolist()
    df = df[df["sequence"].isin(valid_seqs)].copy()

    seq_max = df.groupby("sequence")["start"].max().sort_values(ascending=False)
    ordered_seqs = seq_max.index.tolist()

    offsets = {}
    cumulative = 0
    for seq in ordered_seqs:
        offsets[seq] = cumulative
        cumulative += seq_max[seq] + 1_000_000

    df["cum_pos"] = df.apply(lambda r: r["start"] + offsets[r["sequence"]], axis=1)
    return df, offsets


def make_dotplot(g1, g2, name1, name2, out_path, min_chrom_size=10, point_size=4):
    merged = g1.merge(g2, on="busco_id", suffixes=("_1", "_2"))
    if len(merged) == 0:
        print(f"[ATTENTION] Aucun gene commun entre {name1} et {name2}, dot plot ignore.")
        return

    sub1 = merged[["busco_id", "sequence_1", "start_1"]].rename(
        columns={"sequence_1": "sequence", "start_1": "start"})
    sub1_off, offsets1 = compute_cumulative_offsets(sub1, min_chrom_size)

    sub2 = merged[["busco_id", "sequence_2", "start_2"]].rename(
        columns={"sequence_2": "sequence", "start_2": "start"})
    sub2_off, offsets2 = compute_cumulative_offsets(sub2, min_chrom_size)

    plot_df = sub1_off[["busco_id", "sequence", "cum_pos"]].rename(
        columns={"sequence": "chrom_1", "cum_pos": "x"})
    plot_df = plot_df.merge(
        sub2_off[["busco_id", "cum_pos"]].rename(columns={"cum_pos": "y"}), on="busco_id")

    chroms = plot_df["chrom_1"].unique()
    cmap = cm.get_cmap("tab20", max(len(chroms), 1))
    color_map = {c: cmap(i) for i, c in enumerate(chroms)}
    colors = plot_df["chrom_1"].map(color_map)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(plot_df["x"], plot_df["y"], s=point_size, c=colors, alpha=0.7, linewidths=0)

    for off in offsets1.values():
        ax.axvline(off, color="grey", linewidth=0.3, alpha=0.4)
    for off in offsets2.values():
        ax.axhline(off, color="grey", linewidth=0.3, alpha=0.4)

    ax.set_xlabel(f"Position dans {name1}")
    ax.set_ylabel(f"Position dans {name2}")
    ax.set_title(f"Synthenie BUSCO : {name1} vs {name2}\n({len(plot_df)} genes marqueurs communs)")
    ax.set_xticks([])
    ax.set_yticks([])

    plt.tight_layout()
    plt.savefig(out_path, dpi=250)
    plt.close(fig)
    print(f"[INFO] Dot plot sauvegarde : {out_path}")


def make_dotplot_html(g1, g2, name1, name2, out_path, min_chrom_size=10):
    """
    Version interactive (plotly) du dot plot, dans le meme esprit que
    sankey_syntenie.py : sauvegarde en .html avec fig.write_html(...),
    et affiche un message de confirmation du meme style.

    Au survol d'un point, on voit : le busco_id, le chromosome d'origine
    dans chaque genome, et les positions.
    """
    merged = g1.merge(g2, on="busco_id", suffixes=("_1", "_2"))
    if len(merged) == 0:
        print(f"[ATTENTION] Aucun gene commun entre {name1} et {name2}, dot plot HTML ignore.")
        return

    sub1 = merged[["busco_id", "sequence_1", "start_1"]].rename(
        columns={"sequence_1": "sequence", "start_1": "start"})
    sub1_off, offsets1 = compute_cumulative_offsets(sub1, min_chrom_size)

    sub2 = merged[["busco_id", "sequence_2", "start_2"]].rename(
        columns={"sequence_2": "sequence", "start_2": "start"})
    sub2_off, offsets2 = compute_cumulative_offsets(sub2, min_chrom_size)

    plot_df = sub1_off[["busco_id", "sequence", "cum_pos"]].rename(
        columns={"sequence": "chromosome_1", "cum_pos": "x"})
    plot_df = plot_df.merge(
        sub2_off[["busco_id", "sequence", "cum_pos"]].rename(
            columns={"sequence": "chromosome_2", "cum_pos": "y"}),
        on="busco_id"
    )

    if len(plot_df) == 0:
        print(f"[ATTENTION] Aucun point a tracer pour {name1} vs {name2} "
              f"(apres filtre min-chrom-size={min_chrom_size}), dot plot HTML ignore.")
        return

    # Une couleur par chromosome du genome 1, coherent avec le dot plot PNG
    chroms = sorted(plot_df["chromosome_1"].unique())
    base_colors = px.colors.qualitative.Alphabet + px.colors.qualitative.Dark24
    color_map = {c: base_colors[i % len(base_colors)] for i, c in enumerate(chroms)}

    fig = go.Figure()
    for chrom in chroms:
        sub = plot_df[plot_df["chromosome_1"] == chrom]
        fig.add_trace(go.Scattergl(
            x=sub["x"], y=sub["y"],
            mode="markers",
            marker=dict(size=4, color=color_map[chrom], opacity=0.7),
            name=str(chrom),
            text=sub.apply(
                lambda r: f"BUSCO: {r['busco_id']}<br>"
                          f"{name1} - {r['chromosome_1']}<br>"
                          f"{name2} - {r['chromosome_2']}", axis=1),
            hoverinfo="text",
        ))

    fig.update_layout(
        title_text=f"Synthenie BUSCO : {name1} vs {name2} ({len(plot_df)} genes marqueurs communs)",
        xaxis_title=f"Position dans {name1}",
        yaxis_title=f"Position dans {name2}",
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        legend_title_text=f"Chromosome ({name1})",
        height=800,
        plot_bgcolor="white",
    )

    fig.write_html(out_path)
    print(f"Dot plot interactif sauvegarde : {out_path}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Analyse automatique de synthenie BUSCO (toutes paires de genomes)")
    parser.add_argument("--input-dir", required=True, help="Dossier racine dans lequel chercher (recursif)")
    parser.add_argument("--lineage", default="crustacea_odb12",
                         help="Nom du lineage BUSCO a utiliser (defaut: crustacea_odb12, "
                              "conformement a la consigne du tuteur)")
    parser.add_argument("--out-dir", default="plots", help="Dossier de sortie pour les plots et le CSV")
    parser.add_argument("--min-chrom-size", type=int, default=10,
                         help="Nb minimum de genes BUSCO par scaffold pour le garder")
    parser.add_argument("--names", default=None,
                         help="Fichier CSV optionnel 'accession,nom_espece' pour des titres lisibles")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Noms d'especes optionnels
    display_names = {}
    if args.names and os.path.exists(args.names):
        names_df = pd.read_csv(args.names, header=None, names=["accession", "species"])
        display_names = dict(zip(names_df["accession"], names_df["species"]))

    # 1. Trouver et charger tous les genomes
    genome_files = find_full_tables(args.input_dir, args.lineage)
    if len(genome_files) < 2:
        print(f"[ERREUR] Moins de 2 genomes trouves pour le lineage '{args.lineage}' "
              f"dans {args.input_dir}. Verifiez le chemin et le nom du lineage.", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] {len(genome_files)} genomes trouves : {list(genome_files.keys())}")

    genomes = {}
    for acc, path in genome_files.items():
        print(f"[INFO] Chargement {acc} ...")
        genomes[acc] = load_full_table(path)
        print(f"[INFO]   -> {len(genomes[acc])} genes BUSCO complets")

    # 2. Calculer le score de synthenie pour toutes les paires
    results = []
    accessions = list(genomes.keys())
    for acc1, acc2 in combinations(accessions, 2):
        score, n_shared, n_pairs = synteny_score(genomes[acc1], genomes[acc2])
        results.append({
            "genome_1": acc1,
            "genome_2": acc2,
            "synteny_score": round(score, 4),
            "genes_partages": n_shared,
            "paires_chromosomes": n_pairs,
        })
        print(f"[INFO] {acc1} vs {acc2} : score={score:.3f} "
              f"({n_shared} genes communs, {n_pairs} paires de chromosomes)")

    scores_df = pd.DataFrame(results).sort_values("synteny_score", ascending=False)
    csv_path = os.path.join(args.out_dir, "synteny_scores.csv")
    scores_df.to_csv(csv_path, index=False)
    print(f"\n[INFO] Tableau des scores sauvegarde : {csv_path}")
    print(scores_df.to_string(index=False))

    # 3. Identifier la paire la plus conservee et la plus eloignee
    best = scores_df.iloc[0]
    worst = scores_df.iloc[-1]

    def label(acc):
        return display_names.get(acc, acc)

    print(f"\n[INFO] Paire la PLUS conservee : {best['genome_1']} vs {best['genome_2']} "
          f"(score={best['synteny_score']:.3f})")
    print(f"[INFO] Paire la MOINS conservee : {worst['genome_1']} vs {worst['genome_2']} "
          f"(score={worst['synteny_score']:.3f})")

    # 4. Generer les deux dot plots automatiquement (version PNG statique
    #    + version HTML interactive, meme principe que sankey_syntenie.py)
    make_dotplot(
        genomes[best["genome_1"]], genomes[best["genome_2"]],
        label(best["genome_1"]), label(best["genome_2"]),
        os.path.join(args.out_dir, "dotplot_meilleure_conservation.png"),
        min_chrom_size=args.min_chrom_size,
    )
    make_dotplot_html(
        genomes[best["genome_1"]], genomes[best["genome_2"]],
        label(best["genome_1"]), label(best["genome_2"]),
        os.path.join(args.out_dir, "dotplot_meilleure_conservation.html"),
        min_chrom_size=args.min_chrom_size,
    )

    make_dotplot(
        genomes[worst["genome_1"]], genomes[worst["genome_2"]],
        label(worst["genome_1"]), label(worst["genome_2"]),
        os.path.join(args.out_dir, "dotplot_plus_eloignes.png"),
        min_chrom_size=args.min_chrom_size,
    )
    make_dotplot_html(
        genomes[worst["genome_1"]], genomes[worst["genome_2"]],
        label(worst["genome_1"]), label(worst["genome_2"]),
        os.path.join(args.out_dir, "dotplot_plus_eloignes.html"),
        min_chrom_size=args.min_chrom_size,
    )

    print("\n[INFO] Analyse terminee.")


if __name__ == "__main__":
    main()
