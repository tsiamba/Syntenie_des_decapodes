#!/usr/bin/env python3
"""Compare le contenu BUSCO des paires du Sankey, dont les 55 paires du projet."""

import argparse
from collections import Counter
import colorsys
import csv
from html import escape
import json
from pathlib import Path
import re
import sys
import tempfile
import xml.etree.ElementTree as ET


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


def output_stem(record):
    """Stable short filenames; accessions remain in tables and figure labels."""
    from sankey_syntenie import SPECIES
    names = [SPECIES.get(record[f"assembly_{side}"], record[f"species_{side}"])
             for side in ("A", "B")]
    slugs = [re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") for name in names]
    if not all(slugs):
        raise ValueError("Nom d'espèce vide pour le nom de sortie")
    return "jaccard_" + "_".join(slugs)


def duplication_summary(stat):
    if stat is None:
        return "D : non documenté"
    return (f"D : {stat['duplicated_families']}/{stat['complete_families']} familles "
            f"({stat['duplication_percent']:.1f} %) ; {stat['duplicated_copies']} copies D")


def duplication_tip(label, stat):
    text = f"{label} · {duplication_summary(stat)}"
    if stat is not None and stat["loci"]:
        text += " · Loci D : " + "; ".join(
            f"{hit['busco_id']} [{hit['sequence']}:{hit['start']}-{hit['end']} "
            f"{hit['strand'] or '.'}] ({hit['copies_in_genome']} copies dans le génome)"
            for hit in stat["loci"])
    return text


def duplication_for_sequences(data, accession, sequences, metadata):
    from busco_duplications import sequence_stats
    result = {}
    for sequence in sequences:
        stat = sequence_stats(data, accession, sequence)
        if stat is None:
            raise ValueError(f"Duplication non documentée pour {accession} / {sequence}")
        role, chromosome = metadata[accession, sequence]
        if (stat["role"], stat["chromosome"]) != (role, chromosome):
            raise ValueError(f"Métadonnées contradictoires dans les masters pour {accession} / {sequence}")
        result[sequence] = stat
    return result


def duplication_button(label, stat, vertical=False):
    tip = escape(duplication_tip(label, stat), quote=True)
    dimension = "height" if vertical else "width"
    orientation = "dup-column" if vertical else "dup-row"
    value = (f"<span>{stat['duplicated_families']}/{stat['complete_families']}</span>"
             f"<span>{stat['duplication_percent']:.1f} %</span>"
             f"<span>{stat['duplicated_copies']} c.</span>")
    return (f"<button type='button' class='duplication {orientation}' title='{tip}' aria-label='{tip}'>"
            f"<span class='dup-track'><span class='dup-fill' "
            f"style='{dimension}:{stat['duplication_percent']:.6f}%'></span></span>"
            f"<span class='dup-values'>{value}</span></button>")


def write_jaccard_svg(path, rows_a, cols_b, labels_a, labels_b, scores, shared,
                      total_a, total_b, axis_a, axis_b, n_input, filter_label,
                      duplication_a=None, duplication_b=None):
    """Write an autonomous vector heatmap with positive scores printed in cells."""
    namespace = "http://www.w3.org/2000/svg"
    ET.register_namespace("", namespace)
    cell = 44
    left = max(250, 8 * max(len(labels_a[a]) for a in rows_a) + 30)
    top = max(250, 7 * max(len(labels_b[b]) for b in cols_b) + 85)
    annotated = duplication_a is not None and duplication_b is not None
    if annotated:
        top += 150
    matrix_width, matrix_height = len(cols_b) * cell, len(rows_a) * cell
    right = max(60, 4 * max(len(labels_b[b]) for b in cols_b) + 25)
    if annotated:
        right = max(right, 370)
    width = max(1100, left + matrix_width + right, left + 1000)
    height = top + matrix_height + (205 if annotated else 140)
    svg = ET.Element(f"{{{namespace}}}svg", {
        "width": str(width), "height": str(height), "viewBox": f"0 0 {width} {height}",
        "role": "img", "aria-labelledby": "figure-title figure-description",
    })

    def element(parent, tag, attributes=None, text=None):
        node = ET.SubElement(parent, f"{{{namespace}}}{tag}", attributes or {})
        node.text = text
        return node

    def color(score):
        lightness = round(98 - 68 * score)
        rgb = colorsys.hls_to_rgb(213 / 360, lightness / 100, 0.75)
        return "#" + "".join(f"{round(channel * 255):02x}" for channel in rgb)

    def label(x, y, text, size=12, **attributes):
        attributes = {key.replace("_", "-"): str(value) for key, value in attributes.items()}
        return element(svg, "text", {
            "x": str(x), "y": str(y), "font-family": "Arial, sans-serif",
            "font-size": str(size), "fill": "#203040", **attributes,
        }, text)

    n_retained = sum(shared.values())
    element(svg, "title", {"id": "figure-title"}, f"Jaccard — {axis_a} et {axis_b}")
    element(svg, "desc", {"id": "figure-description"},
            f"Lignes : {axis_a}. Colonnes : {axis_b}. {n_retained} marqueurs communs sur les {filter_label}. "
            "Les scores positifs sont inscrits dans les cases. Les cases sans nombre ont un score de zéro.")
    element(svg, "rect", {"width": str(width), "height": str(height), "fill": "white"})
    label(24, 32, "Similarité du contenu BUSCO — Jaccard", size=22, font_weight="bold")
    label(24, 58, f"{axis_a} × {axis_b}", size=16)
    label(24, 81, f"{n_retained} BUSCO communs retenus ; {n_input - n_retained} exclus par le filtre.")
    label(left, 107, f"Colonnes : {axis_b}", size=13, font_weight="bold")
    label(30, top + matrix_height / 2, f"Lignes : {axis_a}", size=13, font_weight="bold",
          text_anchor="middle", transform=f"rotate(-90 30 {top + matrix_height / 2})")

    for column, b in enumerate(cols_b):
        x, y = left + (column + 0.5) * cell, top - (140 if annotated else 10)
        label(x, y, labels_b[b], size=11, transform=f"rotate(-60 {x} {y})")
        if annotated:
            stat = duplication_b[b]
            group = element(svg, "g", {"class": "duplication-column"})
            element(group, "title", text=duplication_tip(labels_b[b], stat))
            element(group, "rect", {"x": str(x - 8), "y": str(top - 117),
                                    "width": "16", "height": "70", "fill": "#fff1df"})
            bar_height = 70 * stat["duplication_percent"] / 100
            element(group, "rect", {"x": str(x - 8), "y": str(top - 47 - bar_height),
                                    "width": "16", "height": str(bar_height), "fill": "#d97706"})
            label(x, top - 32, f"{stat['duplicated_families']}/{stat['complete_families']}", size=9,
                  text_anchor="middle")
            label(x, top - 20, f"{stat['duplication_percent']:.1f}%", size=9, text_anchor="middle")
            label(x, top - 8, f"{stat['duplicated_copies']} c.", size=9, text_anchor="middle")
    if annotated:
        label(left + matrix_width + 20, top - 14, "D / familles complètes ; copies D", size=11,
              font_weight="bold")
    for row, a in enumerate(rows_a):
        label(left - 10, top + (row + 0.5) * cell + 4, labels_a[a], text_anchor="end")
        if annotated:
            stat = duplication_a[a]
            x, y = left + matrix_width + 20, top + (row + 0.5) * cell
            group = element(svg, "g", {"class": "duplication-row"})
            element(group, "title", text=duplication_tip(labels_a[a], stat))
            element(group, "rect", {"x": str(x), "y": str(y - 7), "width": "90",
                                    "height": "14", "fill": "#fff1df"})
            element(group, "rect", {"x": str(x), "y": str(y - 7),
                                    "width": str(90 * stat["duplication_percent"] / 100),
                                    "height": "14", "fill": "#d97706"})
            label(x + 100, y + 4, f"{stat['duplicated_families']}/{stat['complete_families']} "
                  f"({stat['duplication_percent']:.1f} %) ; {stat['duplicated_copies']} c.", size=10)
        for column, b in enumerate(cols_b):
            score = scores[a, b]
            x, y = left + column * cell, top + row * cell
            group = element(svg, "g", {"class": "matrix-cell"})
            element(group, "title", text=f"{labels_a[a]} × {labels_b[b]} · Jaccard {score:.6f} · "
                    f"{shared.get((a, b), 0)} BUSCO partagés sur {total_a[a]} côté A et {total_b[b]} côté B")
            element(group, "rect", {
                "x": str(x), "y": str(y), "width": str(cell), "height": str(cell),
                "fill": color(score), "stroke": "#d2dbe5", "stroke-width": "0.5",
            })
            if score > 0:
                text = "<0.001" if score < 0.001 else f"{score:.3f}"
                element(group, "text", {
                    "class": "score", "x": str(x + cell / 2), "y": str(y + cell / 2),
                    "text-anchor": "middle", "dominant-baseline": "central",
                    "font-family": "Arial, sans-serif", "font-size": "9",
                    "fill": "white" if round(98 - 68 * score) <= 55 else "#142b45",
                }, text)

    legend_y = top + matrix_height + 38
    label(left, legend_y, "Score de Jaccard", size=12, font_weight="bold")
    bar_y = legend_y + 12
    for step in range(100):
        element(svg, "rect", {"x": str(left + step * 3), "y": str(bar_y),
                              "width": "3.1", "height": "15", "fill": color(step / 99)})
    for value in (0, 0.25, 0.5, 0.75, 1):
        label(left + value * 300, bar_y + 32, f"{value:g}", size=10, text_anchor="middle")
    label(left + 335, bar_y + 12, "Cases sans nombre : J = 0. Scores positifs affichés à trois décimales.", size=11)
    label(left, bar_y + 57, f"Filtre : {filter_label}.", size=11)
    if annotated:
        label(left, bar_y + 80, "Orange : proportion de familles BUSCO classées D ; barres de 0 à 100 %. c. = copies D.", size=11)
        label(left, bar_y + 99, "Annotations calculées avant le filtre des marqueurs communs ; les liens et Jaccard utilisent les copies uniques.", size=11)
        label(left, bar_y + 118, "Une famille D peut figurer sur plusieurs chromosomes : les nombres par chromosome ne s'additionnent pas en un total génomique.", size=11)

    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=".jaccard_",
                                         suffix=".tmp.svg", delete=False) as handle:
            temporary = Path(handle.name)
            ET.ElementTree(svg).write(handle, encoding="utf-8", xml_declaration=True)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def compare_pair(sankey_dir, out, record, sequence_mode="auto", legacy_names=False, master_tables=None,
                 svg=True, duplication_data=None):
    assembly_a, assembly_b = record["assembly_A"], record["assembly_B"]
    prefix = record["prefix"]
    axis_a, axis_b = record["species_A"], record["species_B"]
    # The legacy_names argument remains accepted for callers; all new outputs use short names.
    output_prefix = output_stem(record)
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
        for suffix in ("_contenu_chromosomes.tsv", "_matrice_jaccard.tsv", ".html", ".svg", "_duplications.tsv"):
            (out / (output_prefix + suffix)).unlink(missing_ok=True)
        print(f"Aucun marqueur retenu pour {axis_a} / {axis_b}. Vérifier les rôles dans _sequences.tsv.")
        return ("aucun_marqueur", n_input, 0, n_input, 0, 0, 0, "")
    rows_a = chromosome_order(names_a)
    cols_b = chromosome_order(names_b)
    labels_a = {a: f"chr {names_a[a]} [{a}]" if names_a[a] else a for a in rows_a}
    labels_b = {b: f"chr {names_b[b]} [{b}]" if names_b[b] else b for b in cols_b}
    duplication_a = duplication_b = None
    if duplication_data is not None:
        duplication_a = duplication_for_sequences(duplication_data, assembly_a, rows_a, sequences)
        duplication_b = duplication_for_sequences(duplication_data, assembly_b, cols_b, sequences)
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
    duplication_table = out / f"{output_prefix}_duplications.tsv"
    if duplication_data is None:
        duplication_table.unlink(missing_ok=True)
    else:
        rows = []
        for accession, species, represented in ((assembly_a, axis_a, rows_a), (assembly_b, axis_b, cols_b)):
            for sequence, stat in sorted(duplication_data["assemblies"][accession]["sequences"].items()):
                rows.append((accession, species, sequence, stat["role"], stat["chromosome"],
                             int(sequence in represented), stat["single_families"], stat["duplicated_families"],
                             stat["complete_families"], stat["duplicated_copies"],
                             f"{stat['duplication_percent']:.6f}", ";".join(stat["busco_ids"]),
                             json.dumps(stat["loci"], ensure_ascii=False)))
        write_tsv(duplication_table,
                  ("assembly", "species", "sequence_id", "role", "chromosome", "represented_in_figure",
                   "single_families", "duplicated_families", "complete_families", "duplicated_copies",
                   "duplication_percent", "duplicated_busco_ids", "duplicated_loci_json"), rows)

    # La carte HTML fonctionne hors ligne sans dépendance graphique.
    heading = "".join(f"<th scope='col'>{escape(labels_b[b])}</th>" for b in cols_b)
    if duplication_data is not None:
        heading += "<th scope='col' class='dup-heading'>BUSCO classés D</th>"
    column_annotations = ""
    if duplication_b is not None:
        column_annotations = ("<tr class='dup-stats'><th>D / familles complètes<br>% ; copies D</th>" +
                              "".join(f"<th>{duplication_button(labels_b[b], duplication_b[b], True)}</th>"
                                      for b in cols_b) + "<th>Échelle des barres : 0–100 %</th></tr>")
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
            cells.append(f"<td class='matrix-cell' title='{tip}' style='background:hsl(213 75% {lightness}%)'>"
                         f"<button type='button' aria-label='{tip}'></button></td>")
        if duplication_a is not None:
            cells.append(f"<td class='dup-stats'>{duplication_button(labels_a[a], duplication_a[a])}</td>")
        table_rows.append(f"<tr><th scope='row'>{escape(labels_a[a])}</th>{''.join(cells)}</tr>")
    n_retained = sum(shared.values())
    (out / f"{output_prefix}.html").write_text(
        "<!doctype html><html lang='fr'><meta charset='utf-8'>"
        f"<title>Similarité du contenu BUSCO · {escape(axis_a)} et {escape(axis_b)}</title>"
        "<style>body{font:15px system-ui;margin:24px}table{border-collapse:collapse}"
        "th,td{border:1px solid #ddd}th{font-size:11px;white-space:nowrap}"
        "thead tr.labels th:not(:first-child):not(.dup-heading){writing-mode:vertical-rl;text-align:left;padding:4px}"
        "tbody th{text-align:right;padding:0 5px}"
        "td.matrix-cell{position:relative;padding:0;min-width:15px;height:15px}"
        "table.annotated td.matrix-cell{width:44px;min-width:44px;height:44px;box-sizing:border-box}"
        "td.matrix-cell button{position:absolute;inset:0;width:100%;height:100%;background:transparent;"
        "border:0;padding:0;cursor:pointer}"
        "button:focus-visible,button.selected{outline:2px solid #172d49;outline-offset:-2px}"
        ".matrix-wrap{max-width:100%;overflow:auto}.dup-stats{background:#fffaf3;padding:3px}"
        ".duplication{border:0;background:transparent;cursor:pointer;font:10px Arial,sans-serif;color:#713f12}"
        ".dup-track{display:block;position:relative;background:#ffedd5}.dup-fill{display:block;background:#d97706}"
        ".dup-stats th{padding:0}.dup-column{width:44px;min-width:44px;box-sizing:border-box;padding:3px 0}"
        ".dup-column .dup-track{height:70px;width:14px;margin:0 auto 3px}"
        ".dup-column .dup-fill{position:absolute;bottom:0;width:100%}.dup-column .dup-values span{display:block}"
        ".dup-row{display:flex;align-items:center;gap:6px;white-space:nowrap;padding:2px 6px}"
        ".dup-row .dup-track{width:90px;height:12px;flex-shrink:0}.dup-row .dup-fill{height:100%}"
        ".dup-row .dup-values{display:flex;gap:6px}.dup-heading{white-space:normal;min-width:255px}"
        "#valeur{position:sticky;top:0;background:#fff;border:1px solid #a3b5cc;"
        "padding:10px;z-index:1;min-height:1.4em}</style>"
        "<h1>Similarité du contenu BUSCO</h1>"
        f"<p>Lignes : <i>{escape(axis_a)}</i>. Colonnes : <i>{escape(axis_b)}</i>.</p>"
        f"<p>{n_retained} BUSCO communs sur les {filter_label}. "
        f"{n_input - n_retained} exclus par le filtre.</p>"
        + ("<p>Les lignes OZ… désignent les séquences de Jaera telles qu’elles figurent dans le Sankey.</p>"
           if DISTANT_A in (assembly_a, assembly_b) else "") +
        "<p>Jaccard : 0 (clair) à 1 (foncé).</p>"
        + ("<p>Orange : familles BUSCO classées D / familles BUSCO complètes présentes sur chaque séquence ; "
           "barres de 0 à 100 %. c. = copies D. Les annotations utilisent les tables complètes de chaque espèce, "
           "avant le filtre des marqueurs communs à la paire. Une famille D peut figurer sur plusieurs chromosomes : "
           "les nombres par chromosome ne s’additionnent pas en un total génomique. "
           "Les séquences non représentées dans la carte sont conservées dans le tableau _duplications.tsv.</p>"
           if duplication_data is not None else "") +
        "<p id='valeur' role='status'>Clique sur une case pour afficher ses valeurs ici.</p>"
        f"<div class='matrix-wrap'><table id='matrice' class='{'annotated' if duplication_data is not None else 'plain'}'>"
        f"<thead><tr class='labels'><th></th>{heading}</tr>{column_annotations}</thead>"
        f"<tbody>{''.join(table_rows)}</tbody></table></div>"
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
    svg_path = out / f"{output_prefix}.svg"
    if svg:
        write_jaccard_svg(svg_path, rows_a, cols_b, labels_a, labels_b, scores, shared,
                          total_a, total_b, axis_a, axis_b, n_input, filter_label, duplication_a, duplication_b)
    else:
        svg_path.unlink(missing_ok=True)
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
    parser.add_argument("--duplication-master", type=Path,
                        help="Master Complete + Duplicated ; ajoute les annotations sans changer les Jaccard")
    parser.add_argument("--out-dir", type=Path, default=JACCARD_DIR, help="Par défaut : Analyses/Jaccard")
    parser.add_argument("--no-svg", action="store_true", help="Désactive la carte SVG avec les valeurs imprimées")
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
        import sankey_syntenie as sankey
        if args.pair == "proches":
            record.update(assembly_A=ASSEMBLY_A, assembly_B=ASSEMBLY_B, prefix=PREFIX,
                          species_A=sankey.SPECIES[ASSEMBLY_A], species_B=sankey.SPECIES[ASSEMBLY_B])
        else:
            record.update(assembly_A=DISTANT_A, assembly_B=DISTANT_B, prefix=DISTANT_PREFIX,
                          species_A=sankey.SPECIES[DISTANT_A], species_B=sankey.SPECIES[DISTANT_B])
        short = sankey.stem_for(args.pair, (record["assembly_A"], record["assembly_B"]))
        if all((args.sankey_dir / (short + suffix)).is_file() for suffix in ("_liens.tsv", "_sequences.tsv")):
            record["prefix"] = short
        records = [record]
    prefixes = [record["prefix"] for record in records]
    if len(set(prefixes)) != len(prefixes) or any(not p or "/" in p or "\\" in p or p in {".", ".."} for p in prefixes):
        raise ValueError("Préfixes invalides ou répétés dans comparaisons.tsv")
    output_names = [output_stem(record) for record in records]
    if len(set(output_names)) != len(output_names):
        raise ValueError("Les noms courts de sortie entrent en collision ; vérifier les noms des espèces")
    duplication_data = None
    if args.duplication_master is not None:
        from busco_duplications import load_duplication_master, validate_against_tables
        needed = sorted({record[f"assembly_{side}"] for record in records for side in ("A", "B")})
        duplication_data = load_duplication_master(args.duplication_master, needed)
        if master_tables is not None:
            validate_against_tables(duplication_data, master_tables)
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
                                  legacy_names=not args.all_pairs, master_tables=master_tables, svg=not args.no_svg,
                                  duplication_data=duplication_data)
            message = ""
        except (OSError, ValueError, TypeError) as exc:
            result = ("erreur", "", "", "", "", "", "", "")
            message = str(exc)
            print(f"Erreur sur cette paire : {message}", file=sys.stderr)
        rows.append((record["assembly_A"], record["species_A"], record["assembly_B"], record["species_B"],
                     record["prefix"], args.sequence_mode, *result, message, output_stem(record),
                     str(args.duplication_master.resolve()) if args.duplication_master is not None else ""))
    temporary = summary.with_suffix(".tmp.tsv")
    write_tsv(temporary, ("assembly_A", "species_A", "assembly_B", "species_B", "sankey_prefix", "mode",
                          "status", "busco_input", "busco_retained", "busco_excluded", "n_sequences_A",
                          "n_sequences_B", "n_nonzero_links", "max_jaccard", "message", "output_prefix",
                          "duplication_master"), rows)
    temporary.replace(summary)
    completed = sum(row[6] == "ok" for row in rows)
    print(f"Terminé : {completed}/{len(records)} cartes. Résumé : {summary}")
    return 0 if completed == len(records) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        raise SystemExit(f"Erreur : {error}") from None
