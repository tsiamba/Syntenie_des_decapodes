#!/usr/bin/env python3
"""BUSCO duplication annotations, independent of the single-copy pairwise analyses.

The supplementary master contains Complete AND Duplicated loci. Keeping the
single-copy loci is necessary for the per-sequence denominator: distinct complete
BUSCO families, before the intersection of markers between species. No genomic
sequence, network connection, pandas or plotting package is needed.
"""
import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path
import re


LINEAGE = 'crustacea_odb12'
COLUMNS = ['Organisme', 'Espece', 'Sequence', 'Chromosome', 'Type_sequence',
           'Busco_id', 'Start', 'End', 'Strand', 'Status', 'Copies_genome',
           'Copies_sequence', 'Lineage', 'Lineage_date', 'Source_BUSCO',
           'Source_BUSCO_SHA256', 'Source_sequence']


def _normal(value):
    return re.sub(r'[^a-z0-9]', '', value.lower())


def _locus_key(row):
    return row['sequence'], min(row['start'], row['end']), max(row['start'], row['end'])


def _validate_families(groups, source):
    """De-duplicate identical loci, rejecting incompatible status/strand claims."""
    result, duplicates = {}, 0
    for busco, rows in groups.items():
        statuses = {row['status'] for row in rows}
        if len(statuses) != 1:
            raise ValueError(f'{source}: statuts contradictoires pour {busco}: {sorted(statuses)}')
        status = next(iter(statuses))
        unique = {}
        for row in rows:
            key = _locus_key(row) if status != 'Missing' else ('', 0, 0)
            previous = unique.get(key)
            if previous is not None:
                if previous['strand'] != row['strand']:
                    raise ValueError(f'{source}: brins contradictoires au meme locus pour {busco}: {key}')
                duplicates += 1
            else:
                unique[key] = row
        loci = sorted(unique.values(), key=lambda row: (*_locus_key(row), row['strand']))
        if status == 'Complete' and len(loci) != 1:
            raise ValueError(f'{source}: {busco} est Complete mais porte {len(loci)} loci; '
                             'ne pas requalifier automatiquement ces lignes en Duplicated')
        if status == 'Duplicated' and len(loci) < 2:
            raise ValueError(f'{source}: {busco} est Duplicated mais porte moins de deux loci distincts')
        result[busco] = {'status': status, 'loci': loci}
    return result, duplicates


def read_full_table(path):
    """Read named genome columns from an original BUSCO full_table.tsv."""
    path = Path(path)
    if not path.is_file():
        raise ValueError(f'Fichier BUSCO absent : {path}')
    header, metadata = None, {}
    groups = defaultdict(list)
    row_counts = Counter()
    with path.open(encoding='utf-8-sig') as handle:
        for number, raw in enumerate(handle, 1):
            line = raw.rstrip('\r\n')
            if not line.strip():
                continue
            comment = line.lstrip().startswith('#')
            content = line.lstrip()[1:].strip() if comment else line
            match = re.search(r'lineage dataset is:\s*(\S+)', content, re.I)
            if comment and match:
                name = match.group(1)
                if metadata.get('lineage', name) != name:
                    raise ValueError(f'{path}:{number}: plusieurs lineages')
                metadata['lineage'] = name
                date = re.search(r'Creation date:\s*([^,\)]+)', content, re.I)
                if date:
                    creation_date = date.group(1).strip()
                    if metadata.get('creation_date', creation_date) != creation_date:
                        raise ValueError(f'{path}:{number}: plusieurs dates de lineage')
                    metadata['creation_date'] = creation_date
            fields = [field.strip() for field in content.split('\t')]
            keys = [_normal(field) for field in fields]
            if 'buscoid' in keys and 'status' in keys:
                if header is not None:
                    raise ValueError(f'{path}:{number}: en-tete repete, tables concatenees ?')
                keys = [{'genestart': 'start', 'geneend': 'end'}.get(key, key) for key in keys]
                if len(set(keys)) != len(keys) or not {'buscoid', 'status', 'sequence', 'start', 'end'} <= set(keys):
                    raise ValueError(f'{path}:{number}: en-tete TSV genomique invalide')
                header = dict(zip(keys, range(len(keys))))
                continue
            if comment:
                continue
            if header is None:
                raise ValueError(f'{path}:{number}: en-tete TSV genomique absent')

            def field(name):
                index = header.get(name, len(fields))
                return fields[index] if index < len(fields) else ''

            busco, status = field('buscoid'), field('status')
            if not busco or status not in {'Complete', 'Duplicated', 'Fragmented', 'Missing'}:
                raise ValueError(f'{path}:{number}: identifiant ou statut BUSCO invalide')
            row = dict(busco_id=busco, status=status, sequence='', start=0, end=0, strand='')
            if status != 'Missing':
                try:
                    start, end = int(field('start')), int(field('end'))
                except ValueError:
                    raise ValueError(f'{path}:{number}: coordonnees entieres requises') from None
                sequence, strand = field('sequence'), field('strand')
                if not sequence or sequence == '-' or min(start, end) < 0 or strand not in {'', '.', '+', '-'}:
                    raise ValueError(f'{path}:{number}: sequence, coordonnees ou brin invalide')
                row.update(sequence=sequence, start=start, end=end, strand=strand)
            groups[busco].append(row)
            row_counts[status] += 1
    if header is None or not groups:
        raise ValueError(f'{path}: table BUSCO vide')
    if metadata.get('lineage') != LINEAGE:
        raise ValueError(f'{path}: lineage attendu {LINEAGE}, trouve {metadata.get("lineage")!r}')
    families, duplicates = _validate_families(groups, path)
    return dict(path=str(path.resolve()), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                metadata=metadata, families=families, universe=set(families),
                stats={'raw_rows_by_status': dict(row_counts), 'duplicate_locus_rows_removed': duplicates,
                       'families_by_status': dict(Counter(group['status'] for group in families.values()))})


def load_duplication_master(path, needed=None):
    """Validate a supplementary master and return JSON-serializable statistics."""
    path = Path(path)
    if not path.is_file():
        raise ValueError(f'Master des duplications absent : {path}')
    groups, sequence_metadata = defaultdict(lambda: defaultdict(list)), defaultdict(dict)
    species, dates, provenance = {}, set(), {}
    declared_counts = {}
    required = set(COLUMNS) - {'Source_BUSCO_SHA256'}
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        if not required <= set(reader.fieldnames or []):
            raise ValueError(f'{path}: colonnes requises : {sorted(required)}')
        for number, row in enumerate(reader, 2):
            if None in row or any(row.get(key) is None for key in required):
                raise ValueError(f'{path}:{number}: ligne TSV incomplete ou trop longue')
            row = {key: value.strip() if value is not None else '' for key, value in row.items()}
            accession, busco, seq = row['Organisme'], row['Busco_id'], row['Sequence']
            status, role, chromosome = row['Status'], row['Type_sequence'], row['Chromosome']
            if not re.fullmatch(r'GC[AF]_\d+\.\d+', accession) or not busco or not seq or seq == '-':
                raise ValueError(f'{path}:{number}: accession, BUSCO ou sequence invalide')
            if not row['Espece'] or species.setdefault(accession, row['Espece']) != row['Espece']:
                raise ValueError(f'{path}:{number}: nom d\'espece absent ou contradictoire')
            if status not in {'Complete', 'Duplicated'} or row['Lineage'] != LINEAGE:
                raise ValueError(f'{path}:{number}: attendu Complete/Duplicated et {LINEAGE}')
            if not role or (role == 'chromosome') != bool(chromosome):
                raise ValueError(f'{path}:{number}: role/nom de chromosome incompatible')
            meta = {'role': role, 'chromosome': chromosome}
            if sequence_metadata[accession].setdefault(seq, meta) != meta:
                raise ValueError(f'{path}:{number}: metadonnees contradictoires pour {accession}/{seq}')
            dates.add(row['Lineage_date'])
            source = (row['Source_BUSCO'], row.get('Source_BUSCO_SHA256', ''))
            if not source[0] or provenance.setdefault(accession, source) != source:
                raise ValueError(f'{path}:{number}: provenance BUSCO absente ou contradictoire')
            if source[1] and not re.fullmatch(r'[0-9a-f]{64}', source[1]):
                raise ValueError(f'{path}:{number}: SHA256 BUSCO invalide')
            try:
                start, end = int(row['Start']), int(row['End'])
                copies, copies_sequence = int(row['Copies_genome']), int(row['Copies_sequence'])
            except ValueError:
                raise ValueError(f'{path}:{number}: coordonnees/comptages entiers requis') from None
            if min(start, end) < 0 or row['Strand'] not in {'', '.', '+', '-'} or min(copies, copies_sequence) < 1:
                raise ValueError(f'{path}:{number}: coordonnees, brin ou nombre de copies invalide')
            item = dict(busco_id=busco, sequence=seq, start=start, end=end,
                        strand=row['Strand'], status=status)
            groups[accession][busco].append(item)
            key = (accession, busco, *_locus_key(item))
            count = (copies, copies_sequence)
            if key in declared_counts:
                raise ValueError(f'{path}:{number}: locus repete dans le master pour {busco}')
            declared_counts[key] = count
    if not groups:
        raise ValueError(f'{path}: master des duplications vide')
    if len(dates) > 1:
        raise ValueError(f'{path}: dates de creation du lineage incompatibles : {sorted(dates)}')
    missing = set(needed or ()) - groups.keys()
    if missing:
        raise ValueError(f'{path}: genomes absents : {sorted(missing)}')
    assemblies = {}
    for accession, raw in groups.items():
        families, _ = _validate_families(raw, f'{path}/{accession}')
        seq_groups = defaultdict(list)
        for busco, family in families.items():
            loci = family['loci']
            local_counts = Counter(locus['sequence'] for locus in loci)
            for locus in loci:
                key = (accession, busco, *_locus_key(locus))
                if declared_counts[key] != (len(loci), local_counts[locus['sequence']]):
                    raise ValueError(f'{path}: nombres de copies incoherents pour {accession}/{busco}')
                locus['copies_in_genome'] = len(loci)
                seq_groups[locus['sequence']].append(locus)
        sequences = {}
        for seq, loci in seq_groups.items():
            singles = {locus['busco_id'] for locus in loci if locus['status'] == 'Complete'}
            duplicated = {locus['busco_id'] for locus in loci if locus['status'] == 'Duplicated'}
            duplicated_loci = [locus for locus in loci if locus['status'] == 'Duplicated']
            complete = len(singles | duplicated)
            sequences[seq] = {
                **sequence_metadata[accession][seq], 'single_families': len(singles),
                'duplicated_families': len(duplicated), 'complete_families': complete,
                'duplicated_copies': len(duplicated_loci),
                'duplication_percent': 100 * len(duplicated) / complete,
                'busco_ids': sorted(duplicated),
                'loci': sorted(duplicated_loci, key=lambda locus: (*_locus_key(locus), locus['busco_id'])),
            }
        assemblies[accession] = {'species': species[accession], 'sequences': sequences,
                                'families': families, 'source_busco': provenance[accession][0],
                                'source_busco_sha256': provenance[accession][1]}
    if needed is not None:
        assemblies = {accession: assemblies[accession] for accession in needed}
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'lineage': LINEAGE, 'lineage_date': next(iter(dates)), 'assemblies': assemblies}


def sequence_stats(data, accession, sequence):
    """None means unavailable; it must never be silently interpreted as zero D."""
    return data.get('assemblies', {}).get(accession, {}).get('sequences', {}).get(sequence)


def duplication_text(stat, details=False):
    if stat is None:
        return 'Duplications : donnees indisponibles'
    text = (f'D : {stat["duplicated_families"]}/{stat["complete_families"]} familles '
            f'({stat["duplication_percent"]:.1f} %) ; {stat["duplicated_copies"]} copies D')
    if details and stat['loci']:
        positions = [f'{row["busco_id"]} : {row["sequence"]}:{row["start"]}-{row["end"]} '
                     f'({row["strand"] or "."}), {row["copies_in_genome"]} copies dans le genome'
                     for row in stat['loci']]
        text += '\n' + '\n'.join(positions)
    return text


def validate_against_tables(data, tables):
    """Ensure supplied single-copy markers agree with this independent master."""
    for accession, table in tables.items():
        assembly = data.get('assemblies', {}).get(accession)
        if assembly is None:
            raise ValueError(f'Master des duplications : genome absent {accession}')
        date = table.metadata.get('creation_date', '')
        if date and data.get('lineage_date') and date != data['lineage_date']:
            raise ValueError(f'Dates de lineage incompatibles pour {accession}')
        source_format = table.metadata.get('source_format', '')
        recorded_digest = assembly.get('source_busco_sha256', '')
        if source_format not in {'master_csv', 'master_tsv'} and recorded_digest and table.sha256 != recorded_digest:
            raise ValueError(f'Masters contradictoires : le full_table.tsv de {accession} '
                             'ne correspond pas au SHA256 source du master des duplications')
        for busco, hit in table.single.items():
            family = assembly['families'].get(busco)
            if family is None or family['status'] != 'Complete':
                raise ValueError(f'Masters contradictoires : {accession}/{busco} single-copy '
                                 'absent ou classe Duplicated dans le master des duplications')
            locus = family['loci'][0]
            if _locus_key(locus) != (hit.sequence, min(hit.start, hit.end), max(hit.start, hit.end)) or locus['strand'] != hit.strand:
                raise ValueError(f'Masters contradictoires : positions/brin differents pour {accession}/{busco}')
        for seq, meta in getattr(table, 'sequence_metadata', {}).items():
            stat = sequence_stats(data, accession, seq)
            if stat is not None and (stat['role'], stat['chromosome']) != (meta['role'], meta['chromosome']):
                raise ValueError(f'Masters contradictoires : metadonnees differentes pour {accession}/{seq}')
