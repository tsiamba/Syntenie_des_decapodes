#!/usr/bin/env python3
"""Genere genomes/master_duplication_gene.tsv depuis les 11 full_table.tsv.

Une ligne par locus Complete ou Duplicated, sans relancer BUSCO ni telecharger de
genome. Les loci Complete sont inclus pour le denominateur exact des annotations
D / familles completes par chromosome, avant tout filtrage par paire.
Placer ce script, busco_duplications.py et sankey_syntenie.py dans scripts/.
Python >= 3.9, bibliotheque standard uniquement.
"""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys
import tempfile

import busco_duplications as duplication


BASE = Path('/data/projet2/Syntenie_des_decapodes')


def _write_atomic(path, writer):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='',
                                         dir=path.parent, prefix='.duplication_', suffix='.tmp',
                                         delete=False) as handle:
            temporary = Path(handle.name)
            writer(handle)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    import sankey_syntenie as sankey
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--busco-root', type=Path, default=sankey.BUSCO_ROOT)
    parser.add_argument('--metadata', type=Path, default=BASE / 'genomes/identifiant_chr_scaffold.tsv')
    parser.add_argument('--out', type=Path, default=BASE / 'genomes/master_duplication_gene.tsv')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args(argv)
    audit_path = args.out.with_name(args.out.stem + '_bilan.json')
    if not args.overwrite and (args.out.exists() or audit_path.exists()):
        raise ValueError(f'Sortie existante : {args.out} ou {audit_path}; utiliser --overwrite')
    paths = {acc: args.busco_root / folder / 'run_crustacea_odb12/full_table.tsv'
             for acc, folder in zip(sankey.ACCESSIONS, sankey.FOLDERS)}
    sources = [args.metadata, *paths.values()]
    if any(args.out.resolve() == source.resolve() or audit_path.resolve() == source.resolve() for source in sources):
        raise ValueError('Les sorties doivent etre differentes des fichiers d\'entree')
    tables, errors = {}, []
    for accession, path in paths.items():
        try:
            print(f'Lecture BUSCO {accession}', flush=True)
            tables[accession] = duplication.read_full_table(path)
        except (ValueError, OSError, UnicodeError) as exc:
            errors.append(str(exc))
    if errors:
        raise ValueError('\n'.join(errors))
    universes = {frozenset(table['universe']) for table in tables.values()}
    if len(universes) != 1:
        raise ValueError('Les 11 full_table.tsv doivent contenir le meme ensemble de groupes BUSCO')
    dates = {table['metadata'].get('creation_date', '') for table in tables.values()}
    if len(dates) != 1:
        raise ValueError(f'Dates de creation du lineage incompatibles : {sorted(dates)}')
    needed = {acc: {row['sequence'] for family in table['families'].values()
                    if family['status'] in {'Complete', 'Duplicated'} for row in family['loci']}
              for acc, table in tables.items()}
    metadata = sankey.read_sequence_metadata(args.metadata, needed)
    rows = []
    for accession in sankey.ACCESSIONS:
        table = tables[accession]
        for busco, family in sorted(table['families'].items()):
            if family['status'] not in {'Complete', 'Duplicated'}:
                continue
            loci = family['loci']
            counts = Counter(locus['sequence'] for locus in loci)
            for locus in loci:
                entry = metadata[accession]['labels'][locus['sequence']]
                chromosome = entry['chromosome'] if entry['role'] == 'chromosome' else ''
                rows.append((accession, sankey.SPECIES[accession], locus['sequence'], chromosome,
                             entry['role'], busco, locus['start'], locus['end'], locus['strand'],
                             family['status'], len(loci), counts[locus['sequence']], duplication.LINEAGE,
                             table['metadata'].get('creation_date', ''), table['path'], table['sha256'],
                             entry.get('source', '')))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='', dir=args.out.parent,
                                         prefix='.master_duplication_', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
            writer.writerow(duplication.COLUMNS)
            writer.writerows(rows)
        data = duplication.load_duplication_master(temporary, sankey.ACCESSIONS)
        if not args.overwrite and (args.out.exists() or audit_path.exists()):
            raise ValueError('Sortie creee pendant le traitement; utiliser --overwrite')
        temporary.replace(args.out)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    audit = {'master': str(args.out.resolve()), 'sha256': data['sha256'],
             'lineage': duplication.LINEAGE, 'lineage_date': next(iter(dates)),
             'n_loci': len(rows), 'n_assemblies': len(tables),
             'scope': 'Complete et Duplicated; familles completes avant intersection par paire',
             'coordinate_convention': 'coordonnees BUSCO conservees, aucune conversion',
             'metadata': {acc: {key: value for key, value in entry.items() if key != 'labels'}
                          for acc, entry in metadata.items()},
             'inputs': {acc: {key: value for key, value in table.items() if key not in {'families', 'universe'}}
                        for acc, table in tables.items()}}
    _write_atomic(audit_path, lambda handle: json.dump(audit, handle, indent=2, ensure_ascii=False))
    for accession, entry in data['assemblies'].items():
        families = entry['families']
        n_duplicated = sum(family['status'] == 'Duplicated' for family in families.values())
        n_copies = sum(len(family['loci']) for family in families.values() if family['status'] == 'Duplicated')
        print(f'{accession}: {n_duplicated} familles Duplicated, {n_copies} copies D')
    print(f'Master cree : {args.out} ({len(rows)} loci Complete/Duplicated)')
    print(f'Bilan : {audit_path}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, UnicodeError) as exc:
        print(f'ERREUR : {exc}', file=sys.stderr)
        sys.exit(2)
