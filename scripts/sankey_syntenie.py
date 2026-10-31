#!/usr/bin/env python3
"""Sankey de BUSCO single-copy communs; Python >= 3.9, Plotly pour les figures.

Aucune connexion reseau, aucun acces au depot, aucune inference de chromosome.
Lancer --help, --inventory ou --self-test sans installer Plotly.
"""
import argparse
import csv
import gzip
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

BASE = Path('/data/projet2/Syntenie_des_decapodes')
BUSCO_ROOT = BASE / 'Busco/precomputed_crustacea_odb12/BUSCO'
OUTPUT = BASE / 'Analyses/Diagramme_Sankey'
FASTA_ROOT = BASE / 'genomes/ncbi_dataset/data'
# Les 11 dossiers exacts fournis. Pas de glob ni de selection implicite de version.
FOLDERS = (
    'BUSCO_GCF_015104395.2_ASM1510439v2_genomic.fna',
    'BUSCO_GCF_036320965.1_ASM3632096v1_genomic.fna',
    'BUSCO_GCF_038502225.1_ASM3850222v1_genomic.fna',
    'BUSCO_GCF_040412425.1_ASM4041242v1_genomic.fna',
    'BUSCO_GCF_040958095.1_FALCON_Pclarkii_2.0_genomic.fna',
    'resultats_busco_GCA_965208005.1_qmJaePrae1.hap1.1_genomic.fna',
    'resultats_busco_GCF_017591435.1_ASM1759143v1_genomic.fna',
    'resultats_busco_GCF_019202785.1_ASM1920278v2_genomic.fna',
    'resultats_busco_GCF_024679095.1_ASM2467909v1_genomic.fna',
    'resultats_busco_GCF_035594125.1_ASM3559412v1_genomic.fna',
    'resultats_busco_GCF_042767895.1_ASM4276789v1_genomic.fna',
)
ACCESSIONS = tuple(re.search(r'GC[AF]_\d+\.\d+', x).group() for x in FOLDERS)
SPECIES = {
    ACCESSIONS[0]: 'Macrobrachium nipponense',
    ACCESSIONS[3]: 'Macrobrachium rosenbergii',
    ACCESSIONS[5]: 'Jaera praehirsuta',
    ACCESSIONS[9]: 'Scylla paramamosain',
    ACCESSIONS[10]: 'Penaeus vannamei',
}
PAIRS = {
    'proches': (ACCESSIONS[0], ACCESSIONS[3]),
    'eloignes': (ACCESSIONS[5], ACCESSIONS[9]),
    'eloignes_decapodes': (ACCESSIONS[10], ACCESSIONS[9]),
}
STATUSES = {'Complete', 'Duplicated', 'Fragmented', 'Missing'}


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class Hit:
    sequence: str
    start: int
    end: int
    strand: str


@dataclass
class Table:
    path: Path
    universe: set
    single: dict
    excluded: dict
    metadata: dict
    stats: dict


def normalized(value):
    return re.sub(r'[^a-z0-9]', '', value.lower())


def read_table(path, allow_missing_lineage=False):
    """Read named, tab-separated genome columns; repeated IDs are all excluded."""
    path = Path(path)
    if not path.is_file():
        raise InputError(f'Fichier absent : {path}')
    header = None
    metadata = {}
    rows = defaultdict(list)
    statuses = Counter()
    with path.open(encoding='utf-8-sig') as handle:
        for number, line in enumerate(handle, 1):
            line = line.rstrip('\r\n')
            if not line.strip():
                continue
            if line.lstrip().startswith('#'):
                comment = line.lstrip()[1:].strip()
                match = re.search(r'lineage dataset is:\s*(\S+)', comment, re.I)
                if match:
                    name = match.group(1)
                    if metadata.get('lineage', name) != name:
                        raise InputError(f'{path}:{number}: plusieurs lineages')
                    metadata['lineage'] = name
                    date = re.search(r'Creation date:\s*([^,\)]+)', comment, re.I)
                    if date:
                        metadata['creation_date'] = date.group(1).strip()
                candidate = comment.split('\t')
            else:
                candidate = line.split('\t')
            keys = [normalized(x) for x in candidate]
            if 'buscoid' in keys and 'status' in keys:
                if header is not None:
                    raise InputError(f'{path}:{number}: en-tete repete (tables concatenees ?)')
                aliases = {'genestart': 'start', 'geneend': 'end'}
                keys = [aliases.get(x, x) for x in keys]
                if len(set(keys)) != len(keys):
                    raise InputError(f'{path}:{number}: colonnes dupliquees')
                required = {'buscoid', 'status', 'sequence', 'start', 'end'}
                if not required <= set(keys):
                    raise InputError(f'{path}:{number}: colonnes genomiques requises : {sorted(required)}')
                header = {key: idx for idx, key in enumerate(keys)}
                continue
            if line.lstrip().startswith('#'):
                continue
            if header is None:
                raise InputError(f'{path}:{number}: en-tete BUSCO TSV genomique absent')
            fields = [x.strip() for x in candidate]

            def field(key):
                idx = header.get(key, len(fields))
                return fields[idx] if idx < len(fields) else ''

            busco, status = field('buscoid'), field('status')
            if not busco or status not in STATUSES:
                raise InputError(f'{path}:{number}: identifiant/statut BUSCO invalide : {busco!r}, {status!r}')
            hit = None
            if status != 'Missing':
                seq = field('sequence')
                try:
                    start, end = int(field('start')), int(field('end'))
                except ValueError:
                    raise InputError(f'{path}:{number}: coordonnees genomiques entieres requises') from None
                # Preserve the raw coordinate orientation; no coordinate-system conversion.
                if not seq or seq == '-' or min(start, end) < 0:
                    raise InputError(f'{path}:{number}: sequence/coordonnees invalides')
                strand = field('strand')
                if strand not in {'', '+', '-', '.'}:
                    raise InputError(f'{path}:{number}: brin invalide : {strand!r}')
                hit = Hit(seq, start, end, strand)
            rows[busco].append((status, hit))
            statuses[status] += 1
    if header is None or not rows:
        raise InputError(f'{path}: table vide ou sans donnees BUSCO')
    lineage = metadata.get('lineage')
    if lineage is None:
        if not allow_missing_lineage:
            raise InputError(f'{path}: lineage absent de l\'en-tete; verifier la provenance, puis utiliser --allow-missing-lineage si justifie')
        print(f'AVERTISSEMENT : lineage non verifiable dans {path}', file=sys.stderr)
    elif lineage != 'crustacea_odb12':
        raise InputError(f'{path}: lineage {lineage!r}, attendu crustacea_odb12 exactement')
    single, excluded = {}, {}
    for busco, records in rows.items():
        if len(records) > 1:
            excluded[busco] = 'identifiant_repete'
        elif records[0][0] == 'Complete':
            single[busco] = records[0][1]
        else:
            excluded[busco] = records[0][0]
    return Table(path, set(rows), single, excluded, metadata, {
        'rows_by_status': dict(statuses), 'unique_busco_ids': len(rows),
        'single_copy_retained': len(single),
        'excluded_by_reason': dict(Counter(excluded.values())),
    })


def compare(left, right):
    if left.universe != right.universe:
        raise InputError('Ensembles d\'identifiants BUSCO differents : table incomplete ou references incompatibles '
                         f'(uniquement A={len(left.universe - right.universe)}, '
                         f'uniquement B={len(right.universe - left.universe)}).')
    dates = [x.metadata.get('creation_date') for x in (left, right)]
    if all(dates) and dates[0] != dates[1]:
        raise InputError(f'Dates de creation du lineage differentes : {dates}')
    common = sorted(left.single.keys() & right.single.keys())
    if not common:
        raise InputError('Aucun BUSCO Complete a copie unique commun aux deux tables.')
    links = Counter((left.single[b].sequence, right.single[b].sequence) for b in common)
    return common, links


def stem_for(label, pair):
    a, b = pair
    return f'sankey_{label}_{SPECIES[a].replace(" ", "_")}_{a}__{SPECIES[b].replace(" ", "_")}_{b}_crustacea_odb12'


def read_fasta_labels(root, accession, needed, explicit_path=None):
    """Exact sequence ID matching only; keep header evidence and sequence role."""
    directory = Path(root) / accession
    if explicit_path is not None:
        candidates = [Path(explicit_path)]
        if not candidates[0].is_file():
            raise InputError(f'FASTA explicitement selectionne absent : {candidates[0]}')
    else:
        plain = sorted(directory.glob(accession + '*_genomic.fna'))
        compressed = sorted(directory.glob(accession + '*_genomic.fna.gz'))
        # Prefer the uncompressed file only for the exact same basename.
        # Different assembly names remain ambiguous, regardless of compression.
        shadowed = [p for p in compressed if Path(str(p)[:-3]) in plain]
        candidates = plain + [p for p in compressed if p not in shadowed]
        if shadowed:
            print(f'FASTA {accession}: priorite au .fna ; {len(shadowed)} fichier(s) .gz de meme nom ignores')
    if len(candidates) != 1:
        raise InputError(f'{directory}: attendu exactement un {accession}*_genomic.fna[.gz], trouve {len(candidates)}. '
                         'Choisir avec --fasta-file ACCESSION=CHEMIN')
    path = candidates[0]
    opener = gzip.open if path.suffix == '.gz' else open
    labels, seen = {}, set()
    with opener(path, 'rt', encoding='utf-8') as handle:
        for line in handle:
            if not line.startswith('>'):
                continue
            header = line[1:].strip()
            if not header:
                raise InputError(f'{path}: en-tete FASTA vide')
            sequence = header.split(maxsplit=1)[0]
            if sequence in seen:
                raise InputError(f'{path}: identifiant FASTA repete : {sequence}')
            seen.add(sequence)
            if sequence not in needed:
                continue
            description = header[len(sequence):].strip()
            match = re.search(r'\bchromosome\s+([^,;\s]+)', description, re.I)
            chromosome = match.group(1) if match else ''
            if chromosome.lower() in {'unknown', 'unplaced', 'unlocalized'}:
                chromosome = ''
            # A scaffold mentioning a chromosome remains a scaffold.
            if re.search(r'\bscaffold\b', description, re.I):
                role = 'scaffold'
            elif re.search(r'\bcontig\b', description, re.I):
                role = 'contig'
            elif re.search(r'\bmitochondri', description, re.I):
                role = 'mitochondrial'
            elif sequence.startswith(('NW_', 'NT_')):
                role = 'contig_ou_scaffold'
            elif chromosome:
                role = 'chromosome'
            else:
                role = 'non_precise'
            labels[sequence] = dict(header=header, chromosome=chromosome, role=role)
    missing = needed - labels.keys()
    if missing:
        raise InputError(f'{path}: {len(missing)} identifiants BUSCO sans correspondance FASTA exacte, '
                         f'exemples : {sorted(missing)[:5]}. Verifier version et identifiants RefSeq/GenBank.')
    return dict(path=str(path.resolve()), labels=labels)


def sequence_label(sequence, metadata):
    entry = metadata.get('labels', {}).get(sequence)
    if not entry:
        return sequence
    role, chromosome = entry['role'], entry['chromosome']
    if role == 'chromosome':
        return f'chromosome {chromosome} [{sequence}]'
    if chromosome:
        return f'{role} {sequence} (chromosome mentionne : {chromosome})'
    return f'{role} [{sequence}]' if role != 'non_precise' else sequence


def _svg_worker(figure_json, path, queue):
    try:
        import plotly.io as pio
        pio.from_json(figure_json).write_image(path, format='svg')
        queue.put('')
    except Exception as exc:
        queue.put(f'{type(exc).__name__}: {exc}'[:2000])


def export_svg(fig, path, timeout):
    """Bound the optional browser export so HTML/TSV generation can finish."""
    import multiprocessing
    import queue as queue_module
    context = multiprocessing.get_context('spawn')
    queue = context.Queue()
    process = context.Process(target=_svg_worker, args=(fig.to_json(), str(path), queue))
    try:
        process.start()
        process.join(timeout)
        if process.is_alive():
            process.terminate()
            process.join(5)
            raise RuntimeError(f'export SVG interrompu apres {timeout:g} secondes')
        try:
            error = queue.get(timeout=2)
        except queue_module.Empty:
            raise RuntimeError(f'processus SVG termine sans resultat (code {process.exitcode})') from None
        if error:
            raise RuntimeError(error)
        if not path.is_file():
            raise RuntimeError('export SVG sans fichier de sortie')
    finally:
        if process.is_alive():
            process.terminate()
            process.join(5)
        queue.close()


def write_tsv(path, header, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def make_figure(go, label, pair, links, count, fasta=None):
    fasta = fasta or {}
    a, b = pair
    sources = sorted({s for s, _ in links})
    targets = sorted({t for _, t in links})
    # Separate indexes for the two species, even when sequence IDs are identical.
    si = {s: i for i, s in enumerate(sources)}
    ti = {t: len(sources) + i for i, t in enumerate(targets)}
    edges = sorted(links)
    labels = [f'{SPECIES[a]} | {sequence_label(s, fasta.get(a, {}))}' for s in sources]
    labels += [f'{SPECIES[b]} | {sequence_label(t, fasta.get(b, {}))}' for t in targets]
    fig = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(label=[html.escape(x) for x in labels], pad=12, thickness=18,
                  color=['#2878a8'] * len(sources) + ['#db9250'] * len(targets)),
        link=dict(source=[si[s] for s, t in edges], target=[ti[t] for s, t in edges],
                  value=[links[e] for e in edges], color='rgba(68,126,159,0.25)',
                  hovertemplate='%{value} BUSCO<extra></extra>')))
    fig.update_layout(
        title=dict(text=f'{SPECIES[a]} → {SPECIES[b]} — {label}<br>'
                   f'<sup>crustacea_odb12 · {count} BUSCO Complete single-copy communs · identifiants de sequences originaux</sup>'),
        font=dict(size=11), width=1700,
        height=max(750, 22 * max(len(sources), len(targets)) + 180),
        margin=dict(l=40, r=40, t=110, b=50), paper_bgcolor='white')
    return fig


def save_pair(go, plotly_version, directory, label, pair, left, right, common, links, svg,
              fasta=None, svg_timeout=60):
    fasta = fasta or {}
    stem = directory / stem_for(label, pair)
    def out(suffix):
        return Path(str(stem) + suffix)
    write_tsv(out('_liens.tsv'), ['source_sequence', 'target_sequence', 'n_busco'],
              ((s, t, links[s, t]) for s, t in sorted(links)))
    write_tsv(out('_busco_communs.tsv'),
              ['busco_id', 'sequence_A', 'start_A', 'end_A', 'strand_A',
               'sequence_B', 'start_B', 'end_B', 'strand_B'],
              ((b, left.single[b].sequence, left.single[b].start, left.single[b].end, left.single[b].strand,
                right.single[b].sequence, right.single[b].start, right.single[b].end, right.single[b].strand)
               for b in common))
    write_tsv(out('_exclusions.tsv'), ['busco_id', 'raison_A', 'raison_B'],
              ((b, left.excluded.get(b, 'Complete_single_copy'), right.excluded.get(b, 'Complete_single_copy'))
               for b in sorted(left.universe - set(common))))
    write_tsv(out('_sequences.tsv'),
              ['assembly', 'species', 'sequence_id', 'role_in_fasta_header', 'chromosome_mentioned', 'fasta_header'],
              ((acc, SPECIES[acc], seq, entry.get('role', 'non_verifie'), entry.get('chromosome', ''), entry.get('header', ''))
               for acc, table in zip(pair, (left, right))
               for seq in sorted({table.single[b].sequence for b in common})
               for entry in [fasta.get(acc, {}).get('labels', {}).get(seq, {})]))
    fig = make_figure(go, label, pair, links, len(common), fasta)
    fig.write_html(str(out('.html')), include_plotlyjs=True, full_html=True, auto_open=False)
    svg_state = 'non_demande'
    # An old SVG must not survive an overwritten analysis as if it were current.
    if out('.svg').exists():
        out('.svg').unlink()
    if svg:
        temporary = out('.tmp.svg')
        try:
            export_svg(fig, temporary, svg_timeout)
            temporary.replace(out('.svg'))
            svg_state = 'ok'
        except Exception as exc:
            svg_state = f'indisponible : {type(exc).__name__}: {exc}'
            temporary.unlink(missing_ok=True)
            print(f'AVERTISSEMENT SVG {label} : {svg_state}\nHTML et TSV conserves.', file=sys.stderr)
    audit = {
        'comparison': label, 'species': [SPECIES[x] for x in pair], 'assemblies': list(pair),
        'common_single_copy_buscos': len(common), 'sum_link_weights': sum(links.values()),
        'number_links': len(links), 'plotly_version': plotly_version, 'svg': svg_state,
        'sequence_labels': 'identifiants originaux; noms et roles explicites des en-tetes FASTA si fournis',
        'fasta_sources': {acc: fasta[acc]['path'] for acc in pair if acc in fasta},
        'inputs': [dict(path=str(x.path.resolve()), sha256=hashlib.sha256(x.path.read_bytes()).hexdigest(),
                        metadata=x.metadata, stats=x.stats) for x in (left, right)],
    }
    out('_bilan.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'{label}: {len(common)} BUSCO, {len(links)} liens; {out(".html")}')


def self_test():
    """Synthetic tests need only the standard library; no cluster paths touched."""
    import tempfile
    import unittest

    class SyntheticTests(unittest.TestCase):
        def setUp(self):
            self.tmp = tempfile.TemporaryDirectory()
            self.addCleanup(self.tmp.cleanup)
            self.root = Path(self.tmp.name)

        def table(self, name, body, lineage='crustacea_odb12', header=None):
            p = self.root / name
            header = header or '# Busco id\tStatus\tSequence\tGene Start\tGene End\tStrand\tScore\tLength'
            p.write_text(f'# The lineage dataset is: {lineage} (Creation date: 2024-01-01)\n'
                         + header + '\n' + body, encoding='utf-8')
            return p

        def test_filter_duplicates_aggregation_and_orientation(self):
            body = ('a\tComplete\tscaffold_9\t20\t10\t-\t90\t10\n'
                    'b\tComplete\tscaffold_9\t30\t40\t+\t90\t10\n'
                    'c\tDuplicated\tx\t1\t9\t+\t90\t9\n'
                    'd\tFragmented\tx\t1\t5\t+\t20\t5\n'
                    'e\tMissing\n'
                    'f\tComplete\tx\t1\t5\t+\t20\t5\n')
            body += 'f\tComplete\tx\t1\t5\t+\t20\t5\n'
            left = read_table(self.table('a.tsv', body))
            right_body = body.replace('scaffold_9', 'same_sequence')
            right_body = right_body.replace('b\tComplete', 'b\tFragmented')
            right = read_table(self.table('b.tsv', right_body))
            common, links = compare(left, right)
            self.assertEqual(common, ['a'])
            self.assertEqual(links, {('scaffold_9', 'same_sequence'): 1})
            self.assertEqual(left.single['a'].start, 20)
            self.assertEqual(left.excluded['f'], 'identifiant_repete')
            _, links2 = compare(left, left)
            self.assertEqual(links2, {('scaffold_9', 'scaffold_9'): 2})

        def test_wrong_lineage_and_bad_coordinates(self):
            for body, lineage in [('a\tMissing\n', 'crustacea_odb12.2'),
                                  ('a\tComplete\tx\tbad\t5\t+\n', 'crustacea_odb12'),
                                  ('a\tUnexpected\n', 'crustacea_odb12')]:
                with self.subTest(body=body), self.assertRaises(InputError):
                    read_table(self.table('bad.tsv', body, lineage))

        def test_missing_empty_header_and_protein_tables(self):
            with self.assertRaises(InputError):
                read_table(self.root / 'absent.tsv')
            for text in ['', 'a\tMissing\n', '# Busco id\tStatus\tSequence\tScore\tLength\na\tMissing\n']:
                p = self.root / 'invalid.tsv'
                p.write_text(text, encoding='utf-8')
                with self.assertRaises(InputError):
                    read_table(p)

        def test_metadata_missing_requires_opt_in(self):
            p = self.root / 'no_lineage.tsv'
            p.write_text('# Busco id\tStatus\tSequence\tStart\tEnd\na\tMissing\n', encoding='utf-8')
            with self.assertRaises(InputError):
                read_table(p)
            self.assertEqual(read_table(p, True).universe, {'a'})

        def test_incompatible_universe_date_and_no_common(self):
            a = read_table(self.table('a.tsv', 'a\tMissing\n'))
            b = read_table(self.table('b.tsv', 'b\tMissing\n'))
            with self.assertRaises(InputError):
                compare(a, b)
            with self.assertRaises(InputError):
                compare(a, a)
            b.universe = {'a'}
            b.metadata['creation_date'] = '2025-01-01'
            with self.assertRaises(InputError):
                compare(a, b)

        def test_exact_paths_and_pairs(self):
            self.assertEqual(len(set(ACCESSIONS)), 11)
            self.assertEqual(PAIRS['proches'], ('GCF_015104395.2', 'GCF_040412425.1'))
            self.assertEqual(PAIRS['eloignes'], ('GCA_965208005.1', 'GCF_035594125.1'))
            self.assertEqual(PAIRS['eloignes_decapodes'][0], 'GCF_042767895.1')

        def test_repeated_header_rejected(self):
            p = self.table('concat.tsv', 'a\tMissing\n# Busco id\tStatus\tSequence\tStart\tEnd\n')
            with self.assertRaises(InputError):
                read_table(p)

        def test_fasta_chromosomes_scaffolds_and_exact_ids(self):
            directory = self.root / ACCESSIONS[0]
            directory.mkdir()
            p = directory / (ACCESSIONS[0] + '_genomic.fna')
            p.write_text('>NC_1.1 Species chromosome 1, assembly\nACGT\n'
                         '>NW_2.1 Species unplaced genomic scaffold, assembly\nACGT\n'
                         '>NW_3.1 Species scaffold chromosome 2, assembly\nACGT\n'
                         '>NC_4.1 Species mitochondrion, complete genome\nACGT\n', encoding='utf-8')
            result = read_fasta_labels(self.root, ACCESSIONS[0], {'NC_1.1', 'NW_2.1', 'NW_3.1', 'NC_4.1'})
            self.assertEqual(result['labels']['NC_1.1']['role'], 'chromosome')
            self.assertEqual(result['labels']['NW_2.1']['role'], 'scaffold')
            self.assertEqual(result['labels']['NW_3.1']['role'], 'scaffold')
            self.assertEqual(result['labels']['NC_4.1']['role'], 'mitochondrial')
            self.assertEqual(sequence_label('NC_1.1', result), 'chromosome 1 [NC_1.1]')
            with self.assertRaises(InputError):
                read_fasta_labels(self.root, ACCESSIONS[0], {'NC_1.2'})

        def test_fasta_ambiguous_files_and_duplicate_headers(self):
            directory = self.root / ACCESSIONS[0]
            directory.mkdir()
            p = directory / (ACCESSIONS[0] + '_genomic.fna')
            p.write_text('>x chromosome 1\nA\n>x chromosome 2\nA\n', encoding='utf-8')
            with self.assertRaises(InputError):
                read_fasta_labels(self.root, ACCESSIONS[0], {'x'})
            other = directory / (ACCESSIONS[0] + '_other_genomic.fna')
            other.write_text('>x\nA\n', encoding='utf-8')
            with self.assertRaises(InputError):
                read_fasta_labels(self.root, ACCESSIONS[0], {'x'})

        def test_explicit_fasta_resolves_compressed_duplicate(self):
            directory = self.root / ACCESSIONS[5]
            directory.mkdir()
            p = directory / (ACCESSIONS[5] + '_genomic.fna')
            p.write_text('>chrA Species chromosome 1, assembly\nACGT\n', encoding='utf-8')
            with gzip.open(str(p) + '.gz', 'wt', encoding='utf-8') as handle:
                handle.write('>other Other sequence\nACGT\n')
            automatic = read_fasta_labels(self.root, ACCESSIONS[5], {'chrA'})
            self.assertEqual(automatic['path'], str(p.resolve()))
            result = read_fasta_labels(self.root, ACCESSIONS[5], {'chrA'}, p)
            self.assertEqual(result['labels']['chrA']['chromosome'], '1')
            self.assertEqual(result['path'], str(p.resolve()))
            with self.assertRaises(InputError):
                read_fasta_labels(self.root, ACCESSIONS[5], {'chrA'}, directory / 'absent.fna')

        def test_compressed_fasta_without_plain_file(self):
            directory = self.root / ACCESSIONS[5]
            directory.mkdir()
            p = directory / (ACCESSIONS[5] + '_genomic.fna.gz')
            with gzip.open(p, 'wt', encoding='utf-8') as handle:
                handle.write('>chrA Species chromosome 1, assembly\nACGT\n')
            result = read_fasta_labels(self.root, ACCESSIONS[5], {'chrA'})
            self.assertEqual(result['path'], str(p.resolve()))

        def test_different_fasta_names_remain_ambiguous(self):
            directory = self.root / ACCESSIONS[5]
            directory.mkdir()
            p = directory / (ACCESSIONS[5] + '_hap1_genomic.fna')
            p.write_text('>chrA Species chromosome 1\nA\n', encoding='utf-8')
            with gzip.open(str(p) + '.gz', 'wt', encoding='utf-8') as handle:
                handle.write('>chrA Species chromosome 1\nA\n')
            other = directory / (ACCESSIONS[5] + '_hap2_genomic.fna.gz')
            with gzip.open(other, 'wt', encoding='utf-8') as handle:
                handle.write('>chrA Species chromosome 1\nA\n')
            with self.assertRaises(InputError):
                read_fasta_labels(self.root, ACCESSIONS[5], {'chrA'})

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SyntheticTests)
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--busco-root', type=Path, default=BUSCO_ROOT, help='Dossier parent des 11 dossiers BUSCO')
    parser.add_argument('--outdir', type=Path, default=OUTPUT)
    parser.add_argument('--fasta-root', type=Path, nargs='?', const=FASTA_ROOT,
                        help='Lit les noms chromosomes/scaffolds des FASTA NCBI; sans valeur : genomes/ncbi_dataset/data du projet')
    parser.add_argument('--fasta-file', action='append', default=[], metavar='ACCESSION=CHEMIN',
                        help='Selection explicite du FASTA pour un assemblage ; repetable, avec --fasta-root')
    parser.add_argument('--pair', choices=['all'] + list(PAIRS), default='all', help='all = proches + eloignes')
    parser.add_argument('--internal-decapods', action='store_true', help='Ajoute Penaeus vannamei vs Scylla a all')
    parser.add_argument('--inventory', action='store_true', help='Liste les 11 chemins et leur presence, sans lecture')
    parser.add_argument('--dry-run', action='store_true', help='Valide les tables selectionnees sans produire de fichiers')
    parser.add_argument('--allow-missing-lineage', action='store_true', help='Accepte une absence de metadata lineage, jamais un autre lineage')
    parser.add_argument('--no-svg', action='store_true', help='Ne tente pas Kaleido')
    parser.add_argument('--svg-timeout', type=float, default=60, help='Delai maximal par export SVG en secondes (defaut 60)')
    parser.add_argument('--overwrite', action='store_true', help='Autorise le remplacement des sorties de ces paires')
    parser.add_argument('--self-test', action='store_true', help='Tests synthetiques sans Plotly ni fichiers cluster')
    args = parser.parse_args(argv)
    if not 0 < args.svg_timeout < float('inf'):
        parser.error('--svg-timeout doit etre un nombre positif fini')
    if args.self_test:
        return self_test()
    fasta_overrides = {}
    for item in args.fasta_file:
        accession, sep, value = item.partition('=')
        if not sep or accession not in ACCESSIONS or not value:
            parser.error('--fasta-file attend ACCESSION=CHEMIN avec une accession du projet')
        if accession in fasta_overrides:
            parser.error(f'--fasta-file repete pour {accession}')
        fasta_overrides[accession] = Path(value)
    if fasta_overrides and args.fasta_root is None:
        parser.error('--fasta-file necessite --fasta-root')
    paths = {acc: args.busco_root / folder / 'run_crustacea_odb12/full_table.tsv'
             for acc, folder in zip(ACCESSIONS, FOLDERS)}
    if args.inventory:
        for acc, path in paths.items():
            print(f'{acc}\t{"present" if path.is_file() else "absent"}\t{path}')
        return 0 if all(p.is_file() for p in paths.values()) else 1
    if args.internal_decapods and args.pair != 'all':
        parser.error('--internal-decapods accompagne --pair all (ou utiliser --pair eloignes_decapodes)')
    selected = ['proches', 'eloignes'] if args.pair == 'all' else [args.pair]
    if args.internal_decapods:
        selected.append('eloignes_decapodes')
    needed = sorted({acc for label in selected for acc in PAIRS[label]})
    if set(fasta_overrides) - set(needed):
        parser.error('--fasta-file contient une accession absente des paires selectionnees')
    errors, tables = [], {}
    for acc in needed:
        try:
            tables[acc] = read_table(paths[acc], args.allow_missing_lineage)
        except (InputError, OSError, UnicodeError) as exc:
            errors.append(f'{acc}: {exc}')
    prepared = []
    for label in selected:
        a, b = PAIRS[label]
        if a in tables and b in tables:
            try:
                common, links = compare(tables[a], tables[b])
                prepared.append((label, (a, b), tables[a], tables[b], common, links))
                print(f'Valide {label}: {len(common)} BUSCO single-copy communs, {len(links)} liens')
            except InputError as exc:
                errors.append(f'{label}: {exc}')
    if errors:
        raise InputError('\n'.join(errors))
    fasta = {}
    if args.fasta_root is not None:
        for acc in needed:
            used = {tables[acc].single[b].sequence
                    for _, pair, _, _, common, _ in prepared if acc in pair for b in common}
            try:
                fasta[acc] = read_fasta_labels(args.fasta_root, acc, used, fasta_overrides.get(acc))
                print(f'FASTA {acc}: {len(fasta[acc]["labels"])} sequences associees aux en-tetes')
            except (InputError, OSError, UnicodeError) as exc:
                errors.append(str(exc))
        if errors:
            raise InputError('\n'.join(errors))
    if args.dry_run:
        return 0
    try:
        import plotly
        import plotly.graph_objects as go
    except ImportError:
        raise InputError('Plotly absent : installer avec python3 -m pip install plotly dans un environnement utilisateur') from None
    suffixes = ('.html', '.svg', '_liens.tsv', '_busco_communs.tsv', '_exclusions.tsv', '_sequences.tsv', '_bilan.json')
    if not args.overwrite:
        existing = [str(args.outdir / (stem_for(label, pair) + suffix))
                    for label, pair, *_ in prepared for suffix in suffixes
                    if (args.outdir / (stem_for(label, pair) + suffix)).exists()]
        if existing:
            raise InputError('Sorties existantes; choisir un autre --outdir ou --overwrite :\n' + '\n'.join(existing))
    args.outdir.mkdir(parents=True, exist_ok=True)
    for item in prepared:
        save_pair(go, plotly.__version__, args.outdir, *item, svg=not args.no_svg,
                  fasta=fasta, svg_timeout=args.svg_timeout)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (InputError, OSError, UnicodeError) as exc:
        print(f'ERREUR : {exc}', file=sys.stderr)
        sys.exit(2)
