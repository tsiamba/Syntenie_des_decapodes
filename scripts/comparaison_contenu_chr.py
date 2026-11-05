#!/usr/bin/env python3
"""Compare le contenu BUSCO des paires du Sankey, dont les 55 paires du projet."""

import argparse
from collections import Counter
import csv
from html import escape
from pathlib import Path
import sys


SANKEY_DIR = Path("/data/projet2/Syntenie_des_decapodes/Analyses/Diagramme_Sankey")
JACCARD_DIR = Path("/data/projet2/Syntenie_des_decapodes/Analyses/Jaccard")
ASSEMBLY_A = "GCF_015104395.2"
ASSEMBLY_B = "GCF_040412425.1"
PREFIX = (
    f"sankey_proches_Macrobrachium_nipponense_{ASSEMBLY_A}"
    f"__Macrobrachium_rosenbergii_{ASSEMBLY_B}_crustacea_odb12"
)
DISTANT_A = "GCA_965208005.1"
DISTANT_B = "GCF_035594125.1"
DISTANT_PREFIX = (
    f"sankey_eloignes_Jaera_praehirsuta_{DISTANT_A}"
    f"__Scylla_paramamosain_{DISTANT_B}_crustacea_odb12"
)


def read_tsv(path, columns):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not set(columns) <= set(reader.fieldnames or []):
            raise ValueError(f"Colonnes attendues dans {path} : {', '.join(columns)}")
        yield from reader


def write_tsv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def chromosome_order(chromosomes):
    def key(sequence):
        label = chromosomes[sequence]
        if label.isdecimal():
            return (0, int(label), sequence)
        return (1, label, sequence)

    return sorted(chromosomes, key=key)


def keep_sequence(assembly, role, mode):
    if mode == "all":
        return True
    return role == "chromosome" or (mode == "auto" and assembly == DISTANT_A)


def compare_pair(sankey_dir, out, record, sequence_mode="auto", legacy_names=False, master_tables=None):
    assembly_a, assembly_b = record["assembly_A"], record["assembly_B"]
    prefix = record["prefix"]
    axis_a, axis_b = record["species_A"], record["species_B"]
    if legacy_names:
        output_prefix = "macrobrachium" if record["comparison"] == "proches" else "jaera_scylla"
    else:
        output_prefix = prefix.removeprefix("sankey_")
    if sequence_mode != "auto":
        output_prefix += f"_{sequence_mode}"
    if sequence_mode == "all":
        filter_label = "séquences représentées dans le Sankey, tous rôles confondus"
    elif sequence_mode == "auto" and DISTANT_A in (assembly_a, assembly_b):
        filter_label = "séquences de Jaera et chromosomes de l’autre génome"
    else:
        filter_label = "chromosomes des deux côtés"

    sequences = {}
    if master_tables is not None:
        left, right = master_tables[assembly_a], master_tables[assembly_b]
        common = left.single.keys() & right.single.keys()
        links = Counter((left.single[b].sequence, right.single[b].sequence) for b in common)
        link_rows = ({"source_sequence": a, "target_sequence": b, "n_busco": count}
                     for (a, b), count in sorted(links.items()))
        for accession in (assembly_a, assembly_b):
            for sequence, entry in master_tables[accession].sequence_metadata.items():
                sequences[accession, sequence] = (entry["role"], entry["chromosome"])
    else:
        for row in read_tsv(
            sankey_dir / f"{prefix}_sequences.tsv",
            ("assembly", "sequence_id", "role_in_fasta_header", "chromosome_mentioned"),
        ):
            key = (row["assembly"], row["sequence_id"])
            if key in sequences:
                raise ValueError(f"Séquence répétée dans les métadonnées : {key}")
            sequences[key] = (row["role_in_fasta_header"], row["chromosome_mentioned"])
        link_rows = read_tsv(sankey_dir / f"{prefix}_liens.tsv", ("source_sequence", "target_sequence", "n_busco"))

    shared = {}
    seen = set()
    total_a, total_b = Counter(), Counter()
    names_a, names_b = {}, {}
    n_input = 0
    for row in link_rows:
        a, b = row["source_sequence"], row["target_sequence"]
        count = int(row["n_busco"])
        if count <= 0 or (a, b) in seen:
            raise ValueError(f"Lien répété ou effectif invalide : {a} -> {b}")
        seen.add((a, b))
        n_input += count
        if (assembly_a, a) not in sequences or (assembly_b, b) not in sequences:
            raise ValueError(f"Métadonnées manquantes pour le lien {a} -> {b}")
        role_a, chr_a = sequences[(assembly_a, a)]
        role_b, chr_b = sequences[(assembly_b, b)]
        # Le même univers de marqueurs sert aux deux marges et à l'intersection.
        if not (keep_sequence(assembly_a, role_a, sequence_mode)
                and keep_sequence(assembly_b, role_b, sequence_mode)):
            continue
        shared[a, b] = count
        total_a[a] += count
        total_b[b] += count
        names_a[a] = chr_a if role_a == "chromosome" else ""
        names_b[b] = chr_b if role_b == "chromosome" else ""

    if not shared:
        for suffix in ("_contenu_chromosomes.tsv", "_matrice_jaccard.tsv", "_carte_jaccard.html"):
            (out / (output_prefix + suffix)).unlink(missing_ok=True)
        print(f"Aucun marqueur retenu pour {axis_a} / {axis_b}. Vérifier les rôles dans _sequences.tsv.")
        return ("aucun_marqueur", n_input, 0, n_input, 0, 0, 0, "")
    rows_a = chromosome_order(names_a)
    cols_b = chromosome_order(names_b)
    labels_a = {a: f"chr {names_a[a]} [{a}]" if names_a[a] else a for a in rows_a}
    labels_b = {b: f"chr {names_b[b]} [{b}]" if names_b[b] else b for b in cols_b}
    scores = {}
    details = []
    for a in rows_a:
        for b in cols_b:
            count = shared.get((a, b), 0)
            score = count / (total_a[a] + total_b[b] - count)
            scores[a, b] = score
            details.append((
                a, names_a[a], b, names_b[b], count, total_a[a], total_b[b],
                f"{score:.6f}", f"{count / total_a[a]:.6f}", f"{count / total_b[b]:.6f}",
            ))

    out.mkdir(parents=True, exist_ok=True)
    write_tsv(
        out / f"{output_prefix}_contenu_chromosomes.tsv",
        ("sequence_A", "chromosome_A", "sequence_B", "chromosome_B", "busco_partages",
         "busco_A", "busco_B", "jaccard", "fraction_A", "fraction_B"),
        details,
    )
    write_tsv(
        out / f"{output_prefix}_matrice_jaccard.tsv",
        [f"{axis_a} / {axis_b}"] + [labels_b[b] for b in cols_b],
        ([labels_a[a]] + [f"{scores[a, b]:.6f}" for b in cols_b] for a in rows_a),
    )

    # La carte HTML fonctionne hors ligne sans dépendance graphique.
    heading = "".join(f"<th scope='col'>{escape(labels_b[b])}</th>" for b in cols_b)
    table_rows = []
    for a in rows_a:
        cells = []
        for b in cols_b:
            score = scores[a, b]
            count = shared.get((a, b), 0)
            tip = escape(f"{labels_a[a]} × {labels_b[b]} · Jaccard {score:.6f} · "
                         f"{count} BUSCO partagés sur {total_a[a]} côté A et {total_b[b]} côté B",
                         quote=True)
            lightness = round(98 - 68 * score)
            cells.append(f"<td title='{tip}' style='background:hsl(213 75% {lightness}%)'>"
                         f"<button type='button' aria-label='{tip}'></button></td>")
        table_rows.append(f"<tr><th scope='row'>{escape(labels_a[a])}</th>{''.join(cells)}</tr>")
    n_retained = sum(shared.values())
    (out / f"{output_prefix}_carte_jaccard.html").write_text(
        "<!doctype html><html lang='fr'><meta charset='utf-8'>"
        f"<title>Similarité du contenu BUSCO · {axis_a} et {axis_b}</title>"
        "<style>body{font:15px system-ui;margin:24px}table{border-collapse:collapse}"
        "th,td{border:1px solid #ddd}th{font-size:11px;white-space:nowrap}"
        "thead th:not(:first-child){writing-mode:vertical-rl;text-align:left;padding:4px}"
        "tbody th{text-align:right;padding:0 5px}"
        "td{position:relative;padding:0;min-width:15px;height:15px}"
        "td button{position:absolute;inset:0;width:100%;height:100%;background:transparent;"
        "border:0;padding:0;cursor:pointer}"
        "td button:focus-visible,td button.selected{outline:2px solid #172d49;outline-offset:-2px}"
        "#valeur{position:sticky;top:0;background:#fff;border:1px solid #a3b5cc;"
        "padding:10px;z-index:1;min-height:1.4em}</style>"
        "<h1>Similarité du contenu BUSCO</h1>"
        f"<p>Lignes : <i>{axis_a}</i>. Colonnes : <i>{axis_b}</i>.</p>"
        f"<p>{n_retained} BUSCO communs sur les {filter_label}. "
        f"{n_input - n_retained} exclus par le filtre.</p>"
        + ("<p>Les lignes OZ… désignent les séquences de Jaera telles qu’elles figurent dans le Sankey.</p>"
           if DISTANT_A in (assembly_a, assembly_b) else "") +
        "<p>Jaccard : 0 (clair) à 1 (foncé).</p>"
        "<p id='valeur' role='status'>Clique sur une case pour afficher ses valeurs ici.</p>"
        f"<table id='matrice'><thead><tr><th></th>{heading}</tr></thead>"
        f"<tbody>{''.join(table_rows)}</tbody></table>"
        "<script>"
        "const matrix = document.getElementById('matrice');"
        "const value = document.getElementById('valeur');"
        "let selected;"
        "matrix.addEventListener('click', (event) => {"
        "  const cell = event.target.closest('button');"
        "  if (!cell) return;"
        "  if (selected) selected.classList.remove('selected');"
        "  cell.classList.add('selected');"
        "  selected = cell;"
        "  value.textContent = cell.getAttribute('aria-label');"
        "});"
        "</script></html>",
        encoding="utf-8",
    )
    print(f"BUSCO communs dans le Sankey : {n_input}")
    print(f"BUSCO retenus sur les {filter_label} : {n_retained}")
    print(f"BUSCO exclus par le filtre chromosomique : {n_input - n_retained}")
    print(f"Matrice : {len(rows_a)} × {len(cols_b)} séquences. Résultats : {out}")
    return ("ok", n_input, n_retained, n_input - n_retained,
            len(rows_a), len(cols_b), len(shared), f"{max(scores.values()):.6f}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair", choices=("proches", "eloignes"), default="proches")
    parser.add_argument("--all-pairs", action="store_true", help="Lit les 55 paires de comparaisons.tsv")
    parser.add_argument("--sankey-dir", type=Path, default=SANKEY_DIR)
    parser.add_argument("--master-tsv", type=Path, help="Master enrichi, lecture directe sans les sorties Sankey")
    parser.add_argument("--out-dir", type=Path, default=JACCARD_DIR, help="Par défaut : Analyses/Jaccard")
    parser.add_argument("--sequence-mode", choices=("auto", "chromosomes", "all"),
                        help="Défaut avec master : chromosomes ; ancien mode Sankey : auto")
    args = parser.parse_args(argv)
    args.sequence_mode = args.sequence_mode or ("chromosomes" if args.master_tsv else "auto")
    if args.all_pairs and args.pair != "proches":
        parser.error("--all-pairs et --pair sont des sélections alternatives")
    master_tables = None
    if args.master_tsv is not None:
        import sankey_syntenie as sankey
        comparisons = sankey.all_comparisons() if args.all_pairs else [(args.pair, sankey.PAIRS[args.pair])]
        needed = sorted({accession for _, pair in comparisons for accession in pair})
        master_tables = sankey.read_master_tsv(args.master_tsv, needed)
        dates = {table.metadata['creation_date'] for table in master_tables.values() if 'creation_date' in table.metadata}
        if len(dates) > 1:
            raise ValueError("Dates de création du lineage différentes dans le master")
        records = [dict(comparison=label, assembly_A=pair[0], species_A=sankey.SPECIES[pair[0]],
                        assembly_B=pair[1], species_B=sankey.SPECIES[pair[1]], prefix=sankey.stem_for(label, pair))
                   for label, pair in comparisons]
    elif args.all_pairs:
        records = list(read_tsv(args.sankey_dir / "comparaisons.tsv",
                               ("comparison", "assembly_A", "assembly_B", "species_A", "species_B", "prefix")))
        pairs = [frozenset((r["assembly_A"], r["assembly_B"])) for r in records]
        genomes = set().union(*pairs) if pairs else set()
        if len(records) != 55 or len(set(pairs)) != 55 or len(genomes) != 11 or any(len(p) != 2 for p in pairs):
            raise ValueError("comparaisons.tsv doit contenir les 55 paires distinctes des 11 génomes")
    else:
        record = dict(comparison=args.pair)
        if args.pair == "proches":
            record.update(assembly_A=ASSEMBLY_A, assembly_B=ASSEMBLY_B, prefix=PREFIX,
                          species_A="M. nipponense", species_B="M. rosenbergii")
        else:
            record.update(assembly_A=DISTANT_A, assembly_B=DISTANT_B, prefix=DISTANT_PREFIX,
                          species_A="J. praehirsuta", species_B="S. paramamosain")
        records = [record]
    prefixes = [record["prefix"] for record in records]
    if len(set(prefixes)) != len(prefixes) or any(not p or "/" in p or "\\" in p or p in {".", ".."} for p in prefixes):
        raise ValueError("Préfixes invalides ou répétés dans comparaisons.tsv")
    # Validate presence before starting to write any pair.
    if master_tables is None:
        for prefix in prefixes:
            for suffix in ("_liens.tsv", "_sequences.tsv"):
                path = args.sankey_dir / (prefix + suffix)
                if not path.is_file():
                    raise ValueError(f"Entrée absente : {path}")
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    summary = out / (f"resume_jaccard_{args.sequence_mode}.tsv" if args.all_pairs
                     else f"resume_jaccard_{args.pair}_{args.sequence_mode}.tsv")
    # An interrupted rerun must not leave a previous summary presented as current.
    summary.unlink(missing_ok=True)
    rows = []
    for index, record in enumerate(records, 1):
        print(f"Jaccard {index}/{len(records)} : {record['species_A']} / {record['species_B']}", flush=True)
        try:
            result = compare_pair(args.sankey_dir, out, record, args.sequence_mode,
                                  legacy_names=not args.all_pairs, master_tables=master_tables)
            message = ""
        except (OSError, ValueError, TypeError) as exc:
            result = ("erreur", "", "", "", "", "", "", "")
            message = str(exc)
            print(f"Erreur sur cette paire : {message}", file=sys.stderr)
        rows.append((record["assembly_A"], record["species_A"], record["assembly_B"], record["species_B"],
                     record["prefix"], args.sequence_mode, *result, message))
    temporary = summary.with_suffix(".tmp.tsv")
    write_tsv(temporary, ("assembly_A", "species_A", "assembly_B", "species_B", "sankey_prefix", "mode",
                          "status", "busco_input", "busco_retained", "busco_excluded", "n_sequences_A",
                          "n_sequences_B", "n_nonzero_links", "max_jaccard", "message"), rows)
    temporary.replace(summary)
    completed = sum(row[6] == "ok" for row in rows)
    print(f"Terminé : {completed}/{len(records)} cartes. Résumé : {summary}")
    return 0 if completed == len(records) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        raise SystemExit(f"Erreur : {error}") from None
