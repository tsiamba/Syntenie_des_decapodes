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
import os
import re
import sys
from itertools import combinations
from collections import Counter, defaultdict
from dataclasses import dataclass, field
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
    ACCESSIONS[1]: 'Panulirus ornatus',
    ACCESSIONS[2]: 'Cherax quadricarinatus',
    ACCESSIONS[3]: 'Macrobrachium rosenbergii',
    ACCESSIONS[4]: 'Procambarus clarkii',
    ACCESSIONS[5]: 'Jaera praehirsuta',
    ACCESSIONS[6]: 'Portunus trituberculatus',
    ACCESSIONS[7]: 'Penaeus chinensis',
    ACCESSIONS[8]: 'Eriocheir sinensis',
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
    sha256: str = ''
    sequence_metadata: dict = field(default_factory=dict)


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
    }, hashlib.sha256(path.read_bytes()).hexdigest())


def read_master_csv(path, needed, enriched=False):
    """Read a legacy CSV or the enriched TSV, once, without changing sequence IDs."""
    path = Path(path)
    records = {accession: defaultdict(list) for accession in ACCESSIONS}
    sequence_metadata = {accession: {} for accession in ACCESSIONS}
    dates = {accession: set() for accession in ACCESSIONS}
    verification = {accession: set() for accession in ACCESSIONS}
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t' if enriched else ',')
        required = {'Organisme', 'Sequence', 'Busco_id', 'Start', 'End', 'Strand'}
        if enriched:
            required |= {'Chromosome', 'Type_sequence', 'Status', 'Lineage'}
        if not required <= set(reader.fieldnames or []):
            raise InputError(f'{path}: colonnes CSV requises : {sorted(required)}')
        for number, row in enumerate(reader, 2):
            if any(row.get(column) is None for column in required):
                raise InputError(f'{path}:{number}: ligne CSV incomplete')
            accession = row['Organisme'].strip()
            if accession not in records:
                raise InputError(f'{path}:{number}: accession inconnue : {accession!r}')
            busco, sequence = row['Busco_id'].strip(), row['Sequence'].strip()
            try:
                start, end = int(row['Start']), int(row['End'])
            except (ValueError, TypeError):
                raise InputError(f'{path}:{number}: coordonnees entieres requises') from None
            strand = row['Strand'].strip()
            if not busco or not sequence or sequence == '-' or min(start, end) < 0 or strand not in {'', '+', '-', '.'}:
                raise InputError(f'{path}:{number}: identifiant, sequence, coordonnees ou brin invalide')
            if enriched:
                if row['Status'] != 'Complete' or row['Lineage'] != 'crustacea_odb12':
                    raise InputError(f'{path}:{number}: attendu Complete et crustacea_odb12')
                role, chromosome = row['Type_sequence'].strip(), row['Chromosome'].strip()
                if not role or (role == 'chromosome' and not chromosome):
                    raise InputError(f'{path}:{number}: role ou nom de chromosome absent')
                if role != 'chromosome' and chromosome:
                    raise InputError(f'{path}:{number}: nom de chromosome associe a une sequence de role {role}')
                entry = dict(role=role, chromosome=chromosome, header='', source=row.get('Source_sequence', ''))
                previous = sequence_metadata[accession].get(sequence)
                if previous is not None and previous != entry:
                    raise InputError(f'{path}:{number}: metadonnees contradictoires pour {accession}/{sequence}')
                sequence_metadata[accession][sequence] = entry
                date = (row.get('Lineage_date') or '').strip()
                if date:
                    dates[accession].add(date)
                verification[accession].add(row.get('Verification_BUSCO') or 'non_renseignee')
            records[accession][busco].append(Hit(sequence, start, end, strand))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    tables = {}
    for accession in needed:
        groups = records[accession]
        if not groups:
            raise InputError(f'{path}: aucune position pour {accession}')
        single = {busco: hits[0] for busco, hits in groups.items() if len(hits) == 1}
        excluded = {busco: 'identifiant_repete' for busco, hits in groups.items() if len(hits) > 1}
        metadata = {'source_format': 'master_tsv' if enriched else 'master_csv', 'assembly': accession,
                                   'lineage_verification': 'non_stocke_dans_le_CSV',
                                   'selection': 'master_fourni_deja_filtre_Complete_single_copy'}
        if enriched:
            metadata.update(lineage='crustacea_odb12', lineage_verification=sorted(verification[accession]))
            if len(dates[accession]) > 1:
                raise InputError(f'{path}: plusieurs dates de lineage pour {accession}')
            if dates[accession]:
                metadata['creation_date'] = next(iter(dates[accession]))
        tables[accession] = Table(path, set(groups), single, excluded, metadata,
                                  {'rows_in_master': sum(map(len, groups.values())),
                                   'unique_busco_ids': len(groups), 'single_copy_retained': len(single),
                                   'excluded_by_reason': dict(Counter(excluded.values()))}, digest,
                                  sequence_metadata[accession])
    print(f'Master charge : {len(tables)} genomes. Les statuts BUSCO et le lineage proviennent du filtrage amont.', flush=True)
    return tables


def read_master_tsv(path, needed):
    return read_master_csv(path, needed, enriched=True)


def compare(left, right):
    master_input = all(table.metadata.get('source_format') in {'master_csv', 'master_tsv'} for table in (left, right))
    if not master_input and left.universe != right.universe:
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
    """Short, stable file names; comparison labels remain in the manifest/audit."""
    a, b = pair
    return f'sankey_{SPECIES[a].replace(" ", "_")}_{SPECIES[b].replace(" ", "_")}'


def legacy_stem_for(label, pair):
    """Previous long prefix, for reading historical outputs when needed."""
    a, b = pair
    return f'sankey_{label}_{SPECIES[a].replace(" ", "_")}_{a}__{SPECIES[b].replace(" ", "_")}_{b}_crustacea_odb12'


def all_comparisons():
    """One comparison per unordered pair; preserve names and directions of old pairs."""
    named = {frozenset(pair): (label, pair) for label, pair in PAIRS.items()}
    return [named.get(frozenset(pair), ('comparaison', pair))
            for pair in combinations(ACCESSIONS, 2)]


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
    return dict(path=str(path.resolve()), kind='fasta', labels=labels)


def read_sequence_metadata(path, needed):
    """Load verified sequence roles from a table derived from assembly reports."""
    path = Path(path)
    result = {acc: dict(path=str(path.resolve()), kind='assembly_report', labels={}) for acc in needed}
    seen = set()
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        required = {'assembly', 'sequence_id', 'role', 'chromosome'}
        if not required <= set(reader.fieldnames or []):
            raise InputError(f'{path}: colonnes TSV requises : {sorted(required)}')
        for number, row in enumerate(reader, 2):
            if any(row.get(column) is None for column in required):
                raise InputError(f'{path}:{number}: ligne incomplete')
            accession, sequence = row['assembly'].strip(), row['sequence_id'].strip()
            key = (accession, sequence)
            if not accession or not sequence or key in seen:
                raise InputError(f'{path}:{number}: identifiant vide ou repete : {key}')
            seen.add(key)
            role, chromosome = row['role'].strip(), row['chromosome'].strip()
            if not role or (role == 'chromosome' and not chromosome):
                raise InputError(f'{path}:{number}: role ou nom de chromosome absent')
            if accession in needed and sequence in needed[accession]:
                result[accession]['labels'][sequence] = dict(
                    role=role, chromosome=chromosome, header='', source=row.get('source_url', ''))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    for accession, sequences in needed.items():
        missing = sequences - result[accession]['labels'].keys()
        if missing:
            raise InputError(f'{path}: {len(missing)} sequences sans correspondance pour {accession}, '
                             f'exemples : {sorted(missing)[:5]}')
        result[accession]['sha256'] = digest
        print(f'Metadonnees {accession}: {len(sequences)} sequences identifiees', flush=True)
    return result


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


def _validate_svg(path):
    """Only a complete, nonempty SVG document can be accepted after rendering."""
    import xml.etree.ElementTree as ET
    root = ET.parse(path).getroot()
    if root.tag.rsplit('}', 1)[-1] != 'svg' or len(root) == 0:
        raise ValueError('document SVG vide ou racine incorrecte')


def _svg_worker(figure_json, path, queue, timeout):
    """Write before closing Chrome: successful rendering must survive slow cleanup."""
    import asyncio

    async def render():
        import kaleido
        import plotly
        plotlyjs = Path(plotly.__file__).resolve().parent / 'package_data' / 'plotly.min.js'
        if not plotlyjs.is_file():
            raise RuntimeError(f'Plotly.js local absent : {plotlyjs}')
        # Sankey labels use plain text. No MathJax CDN request is necessary.
        page = kaleido.PageGenerator(plotly=plotlyjs.as_uri(), mathjax=False)
        renderer = kaleido.Kaleido(n=1, timeout=timeout, page_generator=page)
        rendered = False

        async def report_browser():
            # Report ownership even if Chrome stalls during initialization.
            while True:
                browser = getattr(renderer, 'subprocess', None)
                if browser is not None:
                    queue.put(('browser_pid', browser.pid))
                    return
                await asyncio.sleep(0.05)

        reporter = asyncio.create_task(report_browser())
        try:
            await renderer.open()
            payload = await renderer.calc_fig(json.loads(figure_json), opts={'format': 'svg'})
            Path(path).write_bytes(payload)
            _validate_svg(path)
            rendered = True
            queue.put(('rendered', None))
        except Exception as exc:
            queue.put(('error', f'{type(exc).__name__}: {exc}'[:2000]))
        finally:
            reporter.cancel()
            try:
                await renderer.close()
            except Exception as exc:
                queue.put(('cleanup_error' if rendered else 'error', f'{type(exc).__name__}: {exc}'[:2000]))

    try:
        asyncio.run(render())
    except Exception as exc:
        queue.put(('error', f'{type(exc).__name__}: {exc}'[:2000]))


def _stop_svg_processes(process, browser_pid):
    """Stop only the browser/session launched by this export and its worker."""
    notes = []
    if isinstance(browser_pid, int) and browser_pid > 1 and browser_pid != os.getpid():
        try:
            if os.name == 'posix':
                import signal
                group = os.getpgid(browser_pid)
                # Choreographer starts this owned subprocess in a new session.
                if group == browser_pid and group != os.getpgrp():
                    os.killpg(group, signal.SIGKILL)
                else:
                    os.kill(browser_pid, signal.SIGKILL)
            elif os.name == 'nt':
                import subprocess
                subprocess.run(['taskkill', '/PID', str(browser_pid), '/T', '/F'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               timeout=5, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
        except ProcessLookupError:
            pass
        except Exception as exc:
            notes.append(f'nettoyage navigateur : {type(exc).__name__}: {exc}')
    if process.is_alive():
        process.terminate()
        process.join(2)
        if process.is_alive():
            process.kill()
            process.join(2)
        if process.is_alive():
            notes.append('le processus SVG ne s\'est pas termine')
    return notes


def export_svg(fig, path, timeout, cleanup_timeout=10):
    """Separate the rendering deadline from browser cleanup; preserve valid SVG."""
    import multiprocessing
    import queue as queue_module
    import time
    import xml.etree.ElementTree as ET
    context = multiprocessing.get_context('spawn')
    queue = context.Queue()
    process = context.Process(target=_svg_worker, args=(fig.to_json(), str(path), queue, timeout))
    path = Path(path)
    # A previous successful file must never masquerade as this new rendering.
    path.unlink(missing_ok=True)
    browser_pid, cleanup_errors = None, []
    started = None
    accepted = False

    def svg_ready():
        try:
            _validate_svg(path)
            return True
        except (OSError, ValueError, ET.ParseError):
            return False

    def receive(message):
        nonlocal browser_pid
        kind, value = message
        if kind == 'browser_pid':
            browser_pid = value
        elif kind == 'cleanup_error':
            cleanup_errors.append(value)
        elif kind == 'error':
            if svg_ready():
                cleanup_errors.append(value)
            else:
                raise RuntimeError(value)
        return kind

    try:
        process.start()
        started = time.monotonic()
        deadline = started + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                if svg_ready():
                    break
                raise RuntimeError(f'export SVG interrompu apres {timeout:g} secondes (aucun SVG complet)')
            try:
                kind = receive(queue.get(timeout=min(0.2, remaining)))
                if kind == 'rendered':
                    if not svg_ready():
                        raise RuntimeError('le processus a annonce un rendu mais le SVG est incomplet ou invalide')
                    break
            except queue_module.Empty:
                # Also recover a committed file if the worker cannot signal it.
                if svg_ready():
                    break
                if not process.is_alive():
                    raise RuntimeError(f'processus SVG termine sans SVG complet (code {process.exitcode})') from None
        accepted = True
        render_seconds = time.monotonic() - started
        process.join(cleanup_timeout)
        # Drain the small control messages after rendering, rather than joining
        # a worker before consuming its queue.
        while True:
            try:
                receive(queue.get_nowait())
            except queue_module.Empty:
                break
        forced = process.is_alive()
        if forced:
            cleanup_errors.append(f'fermeture du navigateur limitee a {cleanup_timeout:g} secondes')
            cleanup_errors.extend(_stop_svg_processes(process, browser_pid))
        elif process.exitcode or cleanup_errors:
            if process.exitcode:
                cleanup_errors.append(f'processus termine avec le code {process.exitcode} apres production du SVG')
            cleanup_errors.extend(_stop_svg_processes(process, browser_pid))
        _validate_svg(path)
        if cleanup_errors:
            print('AVERTISSEMENT : SVG complet conserve ; ' + ' ; '.join(cleanup_errors), file=sys.stderr)
        return dict(render_seconds=round(render_seconds, 3), cleanup='forced' if forced else ('warning' if cleanup_errors else 'ok'),
                    cleanup_warnings=cleanup_errors, mathjax=False, plotlyjs='local')
    finally:
        if process.is_alive() or not accepted:
            _stop_svg_processes(process, browser_pid)
        if not accepted:
            path.unlink(missing_ok=True)
        queue.close()


def configure_svg_runtime(directory):
    """Keep browser profiles, temporary files and XDG caches in the chosen directory."""
    import tempfile
    directory = Path(directory).resolve()
    locations = {'TMPDIR': directory / 'tmp', 'TMP': directory / 'tmp', 'TEMP': directory / 'tmp',
                 'XDG_CACHE_HOME': directory / 'xdg-cache', 'XDG_CONFIG_HOME': directory / 'xdg-config',
                 'XDG_DATA_HOME': directory / 'xdg-data', 'XDG_STATE_HOME': directory / 'xdg-state'}
    for name, path in locations.items():
        path.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(path)
    tempfile.tempdir = str(locations['TMPDIR'])


def write_tsv(path, header, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def make_figure(go, label, pair, links, count, fasta=None, duplication_data=None):
    fasta = fasta or {}
    a, b = pair
    sources = sorted({s for s, _ in links})
    targets = sorted({t for _, t in links})
    # Separate indexes for the two species, even when sequence IDs are identical.
    si = {s: i for i, s in enumerate(sources)}
    ti = {t: len(sources) + i for i, t in enumerate(targets)}
    edges = sorted(links)
    labels, tooltips = [], []
    for accession, sequences in ((a, sources), (b, targets)):
        for sequence in sequences:
            text = f'{SPECIES[accession]} | {sequence_label(sequence, fasta.get(accession, {}))}'
            node_label = html.escape(text)
            tip = html.escape(text)
            if duplication_data is not None:
                from busco_duplications import duplication_text, sequence_stats
                stat = sequence_stats(duplication_data, accession, sequence)
                if stat is None:
                    raise InputError(f'Annotation de duplication absente : {accession}/{sequence}')
                node_label += '<br>' + html.escape(duplication_text(stat))
                tip += '<br>' + html.escape(duplication_text(stat, details=True)).replace('\n', '<br>')
            labels.append(node_label)
            tooltips.append(tip)
    fig = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(label=labels, customdata=tooltips, hovertemplate='%{customdata}<extra></extra>',
                  pad=22 if duplication_data is not None else 12, thickness=18,
                  color=['#2878a8'] * len(sources) + ['#db9250'] * len(targets)),
        link=dict(source=[si[s] for s, t in edges], target=[ti[t] for s, t in edges],
                  value=[links[e] for e in edges], color='rgba(68,126,159,0.25)',
                  hovertemplate='%{value} BUSCO<extra></extra>')))
    fig.update_layout(
        title=dict(text=f'{SPECIES[a]} → {SPECIES[b]} — {label}<br>'
                   f'<sup>crustacea_odb12 · {count} BUSCO Complete single-copy communs · identifiants de sequences originaux</sup>'),
        font=dict(size=11), width=2200 if duplication_data is not None else 1700,
        height=max(750, (40 if duplication_data is not None else 22) * max(len(sources), len(targets)) + 210),
        margin=dict(l=40, r=40, t=110, b=100 if duplication_data is not None else 50), paper_bgcolor='white')
    if duplication_data is not None:
        fig.add_annotation(x=0, y=0, yshift=-30, xref='paper', yref='paper', xanchor='left', yanchor='top',
                           showarrow=False, align='left', font=dict(size=12, color='#a95000'),
                           text='D : familles classées Duplicated / familles complètes présentes sur la séquence ; copies D : loci présents ici.<br>'
                                'Annotations avant filtrage par paire ; flux = BUSCO single-copy communs. Les familles D peuvent figurer sur plusieurs chromosomes.<br>'
                                'Seules les séquences portant un flux sont dessinées ; les autres figurent dans le tableau _duplications.tsv.')
    return fig


def save_pair(go, plotly_version, directory, label, pair, left, right, common, links, svg,
              fasta=None, svg_timeout=180, duplication_data=None):
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
              ((b, left.excluded.get(b, 'Complete_single_copy' if b in left.single else 'absent_du_master'),
                right.excluded.get(b, 'Complete_single_copy' if b in right.single else 'absent_du_master'))
               for b in sorted((left.universe | right.universe) - set(common))))
    write_tsv(out('_sequences.tsv'),
              ['assembly', 'species', 'sequence_id', 'role_in_fasta_header', 'chromosome_mentioned', 'fasta_header', 'metadata_source'],
              ((acc, SPECIES[acc], seq, entry.get('role', 'non_verifie'), entry.get('chromosome', ''),
                entry.get('header', ''), entry.get('source', fasta.get(acc, {}).get('path', '')))
               for acc, table in zip(pair, (left, right))
               for seq in sorted({table.single[b].sequence for b in common})
               for entry in [fasta.get(acc, {}).get('labels', {}).get(seq, {})]))
    duplication_path = out('_duplications.tsv')
    if duplication_data is not None:
        represented = {pair[0]: {s for s, _ in links}, pair[1]: {t for _, t in links}}
        write_tsv(duplication_path,
                  ['assembly', 'species', 'sequence_id', 'role', 'chromosome', 'represented_in_figure',
                   'single_families', 'duplicated_families', 'complete_families', 'duplicated_copies',
                   'duplication_percent', 'duplicated_busco_ids', 'duplicated_loci_json'],
                  ((accession, SPECIES[accession], sequence, stat['role'], stat['chromosome'],
                    int(sequence in represented[accession]), stat['single_families'], stat['duplicated_families'],
                    stat['complete_families'], stat['duplicated_copies'], f"{stat['duplication_percent']:.6f}",
                    ';'.join(stat['busco_ids']), json.dumps(stat['loci'], ensure_ascii=False))
                   for accession in pair
                   for sequence, stat in sorted(duplication_data['assemblies'][accession]['sequences'].items())))
    else:
        duplication_path.unlink(missing_ok=True)
    fig = make_figure(go, label, pair, links, len(common), fasta, duplication_data)
    fig.write_html(str(out('.html')), include_plotlyjs=True, full_html=True, auto_open=False)
    svg_state = 'non_demande'
    svg_export = None
    # An old SVG must not survive an overwritten analysis as if it were current.
    if out('.svg').exists():
        out('.svg').unlink()
    if svg:
        temporary = out('.tmp.svg')
        try:
            svg_export = export_svg(fig, temporary, svg_timeout)
            temporary.replace(out('.svg'))
            svg_state = 'ok'
        except Exception as exc:
            svg_state = f'indisponible : {type(exc).__name__}: {exc}'
            temporary.unlink(missing_ok=True)
            print(f'AVERTISSEMENT SVG {label} : {svg_state}\nHTML et TSV conserves.', file=sys.stderr)
    audit = {
        'comparison': label, 'species': [SPECIES[x] for x in pair], 'assemblies': list(pair),
        'common_single_copy_buscos': len(common), 'sum_link_weights': sum(links.values()),
        'number_links': len(links), 'plotly_version': plotly_version, 'svg': svg_state, 'svg_export': svg_export,
        'sequence_labels': 'identifiants originaux; noms et roles issus de la source de metadonnees disponible',
        'fasta_sources': {acc: fasta[acc]['path'] for acc in pair if acc in fasta and fasta[acc].get('kind') == 'fasta'},
        'sequence_metadata_sources': {acc: {key: value for key, value in fasta[acc].items() if key != 'labels'}
                                      for acc in pair if acc in fasta},
        'duplication_annotation': ({
            'path': duplication_data['path'], 'sha256': duplication_data['sha256'],
            'lineage': duplication_data['lineage'], 'lineage_date': duplication_data['lineage_date'],
            'denominator': 'distinct complete BUSCO families present on each sequence, before pair filtering',
            'scope': 'all complete loci in the duplication master; annotations do not alter single-copy links',
            'table': duplication_path.name,
        } if duplication_data is not None else None),
        'inputs': [dict(path=str(x.path.resolve()), sha256=x.sha256,
                        metadata=x.metadata, stats=x.stats) for x in (left, right)],
    }
    out('_bilan.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'{label}: {len(common)} BUSCO, {len(links)} liens; {out(".html")}')
    return svg_state


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
    parser.add_argument('--master-csv', type=Path,
                        help='Alternative aux full_table.tsv : master CSV deja filtre Complete single-copy')
    parser.add_argument('--master-tsv', type=Path, help='Master TSV enrichi genere par generer_master_tsv.py')
    parser.add_argument('--duplication-master', type=Path,
                        help='Master Complete + Duplicated genere par generer_master_duplication_gene.py ; annotations sans changer les flux')
    parser.add_argument('--sequence-metadata', type=Path,
                        help='TSV sequence_metadata_11_genomes.tsv derive des rapports NCBI, alternative aux FASTA')
    parser.add_argument('--outdir', type=Path, default=OUTPUT)
    parser.add_argument('--fasta-root', type=Path, nargs='?', const=FASTA_ROOT,
                        help='Lit les noms chromosomes/scaffolds des FASTA NCBI; sans valeur : genomes/ncbi_dataset/data du projet')
    parser.add_argument('--fasta-file', action='append', default=[], metavar='ACCESSION=CHEMIN',
                        help='Selection explicite du FASTA pour un assemblage ; repetable, avec --fasta-root')
    parser.add_argument('--pair', choices=['all'] + list(PAIRS), default='all', help='all = proches + eloignes')
    parser.add_argument('--all-pairs', action='store_true', help='Les 55 paires distinctes des 11 genomes')
    parser.add_argument('--internal-decapods', action='store_true', help='Ajoute Penaeus vannamei vs Scylla a all')
    parser.add_argument('--inventory', action='store_true', help='Liste les 11 chemins et leur presence, sans lecture')
    parser.add_argument('--dry-run', action='store_true', help='Valide les tables selectionnees sans produire de fichiers')
    parser.add_argument('--allow-missing-lineage', action='store_true', help='Accepte une absence de metadata lineage, jamais un autre lineage')
    parser.add_argument('--no-svg', action='store_true', help='Ne tente pas Kaleido')
    parser.add_argument('--require-svg', action='store_true', help='Arrete le traitement si un export SVG echoue')
    parser.add_argument('--runtime-dir', type=Path, help='Dossier des fichiers temporaires et caches du navigateur, par ex. /data/projet2/conda')
    parser.add_argument('--browser-path', type=Path, help='Chemin du Chrome/Chromium a utiliser pour Kaleido')
    parser.add_argument('--svg-timeout', type=float, default=180, help='Delai maximal du rendu SVG, hors nettoyage, en secondes (defaut 180)')
    parser.add_argument('--overwrite', action='store_true', help='Autorise le remplacement des sorties de ces paires')
    parser.add_argument('--self-test', action='store_true', help='Tests synthetiques sans Plotly ni fichiers cluster')
    args = parser.parse_args(argv)
    if not 0 < args.svg_timeout < float('inf'):
        parser.error('--svg-timeout doit etre un nombre positif fini')
    if args.self_test:
        return self_test()
    if args.no_svg and args.require_svg:
        parser.error('--no-svg et --require-svg sont incompatibles')
    if args.runtime_dir is not None:
        configure_svg_runtime(args.runtime_dir)
    if args.browser_path is not None:
        if not args.browser_path.is_file():
            parser.error(f'Navigateur absent : {args.browser_path}')
        os.environ['BROWSER_PATH'] = str(args.browser_path.resolve())
    if args.master_csv is not None and args.master_tsv is not None:
        parser.error('--master-csv et --master-tsv sont des sources alternatives')
    if (args.master_csv is not None or args.master_tsv is not None) and args.inventory:
        parser.error('--inventory liste les full_table.tsv ; utiliser --master-csv avec --dry-run pour le master')
    if args.master_tsv is not None and (args.sequence_metadata is not None or args.fasta_root is not None):
        parser.error('--master-tsv contient deja les metadonnees des sequences')
    if args.sequence_metadata is not None and args.fasta_root is not None:
        parser.error('--sequence-metadata et --fasta-root sont des sources alternatives')
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
    if args.all_pairs and args.pair != 'all':
        parser.error('--all-pairs et --pair sont des selections alternatives')
    if args.internal_decapods and args.pair != 'all':
        parser.error('--internal-decapods accompagne --pair all (ou utiliser --pair eloignes_decapodes)')
    selected = ['proches', 'eloignes'] if args.pair == 'all' else [args.pair]
    if args.internal_decapods:
        selected.append('eloignes_decapodes')
    comparisons = all_comparisons() if args.all_pairs else [(label, PAIRS[label]) for label in selected]
    needed = sorted({acc for _, pair in comparisons for acc in pair})
    if set(fasta_overrides) - set(needed):
        parser.error('--fasta-file contient une accession absente des paires selectionnees')
    errors, tables = [], {}
    if args.master_tsv is not None:
        tables = read_master_tsv(args.master_tsv, needed)
    elif args.master_csv is not None:
        tables = read_master_csv(args.master_csv, needed)
    else:
        for acc in needed:
            try:
                print(f'Lecture BUSCO {acc}', flush=True)
                tables[acc] = read_table(paths[acc], args.allow_missing_lineage)
            except (InputError, OSError, UnicodeError) as exc:
                errors.append(f'{acc}: {exc}')
    prepared = []
    for label, (a, b) in comparisons:
        if a in tables and b in tables:
            try:
                common, links = compare(tables[a], tables[b])
                prepared.append((label, (a, b), tables[a], tables[b], common, links))
                print(f'Valide {label} {a} / {b}: {len(common)} BUSCO single-copy communs, {len(links)} liens', flush=True)
            except InputError as exc:
                errors.append(f'{label} {a} / {b}: {exc}')
    if errors:
        raise InputError('\n'.join(errors))
    fasta = {}
    if args.master_tsv is not None:
        fasta = {acc: dict(path=str(args.master_tsv.resolve()), kind='master_tsv',
                           sha256=tables[acc].sha256, labels=tables[acc].sequence_metadata) for acc in needed}
    elif args.fasta_root is not None:
        for acc in needed:
            used = {tables[acc].single[b].sequence
                    for _, pair, _, _, common, _ in prepared if acc in pair for b in common}
            try:
                print(f'Lecture FASTA {acc} ({needed.index(acc) + 1}/{len(needed)})', flush=True)
                fasta[acc] = read_fasta_labels(args.fasta_root, acc, used, fasta_overrides.get(acc))
                print(f'FASTA {acc}: {len(fasta[acc]["labels"])} sequences associees aux en-tetes')
            except (InputError, OSError, UnicodeError) as exc:
                errors.append(str(exc))
        if errors:
            raise InputError('\n'.join(errors))
    elif args.sequence_metadata is not None:
        used = {acc: {tables[acc].single[b].sequence
                      for _, pair, _, _, common, _ in prepared if acc in pair for b in common}
                for acc in needed}
        fasta = read_sequence_metadata(args.sequence_metadata, used)
    duplication_data = None
    if args.duplication_master is not None:
        from busco_duplications import load_duplication_master, sequence_stats, validate_against_tables
        duplication_data = load_duplication_master(args.duplication_master, needed)
        validate_against_tables(duplication_data, tables)
        for accession in needed:
            used = {tables[accession].single[b].sequence
                    for _, pair, _, _, common, _ in prepared if accession in pair for b in common}
            target = fasta.setdefault(accession, dict(path=duplication_data['path'], kind='duplication_master', labels={}))
            for sequence in used:
                stat = sequence_stats(duplication_data, accession, sequence)
                if stat is None:
                    raise InputError(f'Annotation de duplication absente : {accession}/{sequence}')
                previous = target['labels'].get(sequence)
                if previous is not None and (previous['role'], previous['chromosome']) != (stat['role'], stat['chromosome']):
                    raise InputError(f'Metadonnees chromosome/scaffold contradictoires : {accession}/{sequence}')
                target['labels'].setdefault(sequence, dict(role=stat['role'], chromosome=stat['chromosome'],
                                                          header='', source=duplication_data['path']))
        print(f'Annotations de duplication chargees : {len(needed)} genomes ; valeurs avant filtrage par paire.', flush=True)
    if args.dry_run:
        print(f'Validation terminee : {len(prepared)} paires, {len(tables)} tables BUSCO lues.')
        return 0
    try:
        import plotly
        import plotly.graph_objects as go
    except ImportError:
        raise InputError('Plotly absent : installer avec python3 -m pip install plotly dans un environnement utilisateur') from None
    suffixes = ('.html', '.svg', '_liens.tsv', '_busco_communs.tsv', '_exclusions.tsv', '_sequences.tsv', '_bilan.json', '_duplications.tsv')
    if not args.overwrite:
        existing = [str(args.outdir / (stem_for(label, pair) + suffix))
                    for label, pair, *_ in prepared for suffix in suffixes
                    if (args.outdir / (stem_for(label, pair) + suffix)).exists()]
        if existing:
            raise InputError('Sorties existantes; choisir un autre --outdir ou --overwrite :\n' + '\n'.join(existing))
        if (args.outdir / 'comparaisons.tsv').exists():
            raise InputError('comparaisons.tsv existe deja ; choisir un autre --outdir ou --overwrite')
    args.outdir.mkdir(parents=True, exist_ok=True)
    # Remove an old completion manifest only after explicit overwrite approval via CLI.
    (args.outdir / 'comparaisons.tsv').unlink(missing_ok=True)
    svg_count = 0
    for index, item in enumerate(prepared, 1):
        print(f'Generation {index}/{len(prepared)}', flush=True)
        state = save_pair(go, plotly.__version__, args.outdir, *item, svg=not args.no_svg,
                          fasta=fasta, svg_timeout=args.svg_timeout, duplication_data=duplication_data)
        svg_count += state == 'ok'
        if args.require_svg and state != 'ok':
            raise InputError(f'Export SVG echoue pour {item[1][0]} / {item[1][1]}. '
                             'Voir le _bilan.json ; corriger Chrome/Kaleido puis relancer avec --overwrite.')
    temporary = args.outdir / 'comparaisons.tmp.tsv'
    write_tsv(temporary,
              ['comparison', 'assembly_A', 'species_A', 'assembly_B', 'species_B', 'prefix', 'n_busco', 'n_links'],
              ((label, pair[0], SPECIES[pair[0]], pair[1], SPECIES[pair[1]],
                stem_for(label, pair), len(common), len(links))
               for label, pair, _, _, common, links in prepared))
    temporary.replace(args.outdir / 'comparaisons.tsv')
    print(f'Termine : {len(prepared)} paires. Inventaire : {args.outdir / "comparaisons.tsv"}')
    if not args.no_svg:
        print(f'SVG produits : {svg_count}/{len(prepared)}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f'ERREUR : {exc}', file=sys.stderr)
        sys.exit(2)
