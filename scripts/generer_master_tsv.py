#!/usr/bin/env python3
"""Construit le master BUSCO TSV avec les chromosomes identifies dans les rapports NCBI.

Placer ce script a cote de sankey_syntenie.py. Python >= 3.9, bibliotheque standard.
Par defaut, les 11 full_table.tsv sont lus. --input-csv reutilise l'ancien CSV prefiltre.
"""
import argparse
from collections import Counter
import csv
from pathlib import Path
import sys
import tempfile

import sankey_syntenie as sankey


BASE = Path('/data/projet2/Syntenie_des_decapodes')
COLUMNS = ['Organisme', 'Espece', 'Sequence', 'Chromosome', 'Type_sequence',
           'Busco_id', 'Start', 'End', 'Strand', 'Status', 'Lineage', 'Lineage_date',
           'Verification_BUSCO', 'Source_BUSCO', 'Source_sequence']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input-csv', type=Path, help='Ancien master_positions_busco.csv deja filtre single-copy')
    parser.add_argument('--busco-root', type=Path, default=sankey.BUSCO_ROOT)
    parser.add_argument('--metadata', type=Path, default=BASE / 'genomes/identifiant_chr_scaffold.tsv')
    parser.add_argument('--out', type=Path, default=BASE / 'genomes/master_positions_busco.tsv')
    parser.add_argument('--overwrite', action='store_true', help='Autorise le remplacement du master TSV existant')
    args = parser.parse_args(argv)
    if args.out.exists() and not args.overwrite:
        raise sankey.InputError(f'Sortie existante : {args.out}. Choisir un autre --out ou --overwrite.')
    if args.out.resolve() == args.metadata.resolve() or (args.input_csv and args.out.resolve() == args.input_csv.resolve()):
        raise sankey.InputError('La sortie doit etre differente des entrees')

    if args.input_csv:
        tables = sankey.read_master_csv(args.input_csv, list(sankey.ACCESSIONS))
        verification = 'CSV_prefiltre_declare'
    else:
        tables = {}
        for accession, folder in zip(sankey.ACCESSIONS, sankey.FOLDERS):
            print(f'Lecture BUSCO {accession}', flush=True)
            tables[accession] = sankey.read_table(args.busco_root / folder / 'run_crustacea_odb12/full_table.tsv')
        universes = {frozenset(table.universe) for table in tables.values()}
        if len(universes) != 1:
            raise sankey.InputError('Les 11 full_table.tsv doivent avoir le meme ensemble de groupes BUSCO')
        verification = 'full_table_verifie'
    dates = {table.metadata['creation_date'] for table in tables.values() if 'creation_date' in table.metadata}
    if len(dates) > 1:
        raise sankey.InputError(f'Plusieurs dates de creation du lineage : {sorted(dates)}')
    needed = {accession: {hit.sequence for hit in table.single.values()} for accession, table in tables.items()}
    metadata = sankey.read_sequence_metadata(args.metadata, needed)
    output_rows = []
    for accession in sankey.ACCESSIONS:
        table = tables[accession]
        counts = Counter()
        for busco, hit in sorted(table.single.items(), key=lambda item: (item[1].sequence, min(item[1].start, item[1].end), item[0])):
            entry = metadata[accession]['labels'][hit.sequence]
            chromosome = entry['chromosome'] if entry['role'] == 'chromosome' else ''
            output_rows.append((accession, sankey.SPECIES[accession], hit.sequence, chromosome, entry['role'],
                                busco, hit.start, hit.end, hit.strand, 'Complete', 'crustacea_odb12',
                                table.metadata.get('creation_date', ''), verification, str(table.path.resolve()),
                                entry.get('source', '')))
            counts[entry['role']] += 1
        print(f'{accession}: {len(table.single)} positions retenues, roles {dict(counts)}, '
              f'{len(table.excluded)} marqueurs exclus', flush=True)
    if not output_rows:
        raise sankey.InputError('Aucune position retenue')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='', dir=args.out.parent,
                                         prefix='.master_', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
            writer.writerow(COLUMNS)
            writer.writerows(output_rows)
        # Validate the exact file that will become the master.
        sankey.read_master_tsv(temporary, list(sankey.ACCESSIONS))
        if args.out.exists() and not args.overwrite:
            raise sankey.InputError(f'Sortie creee pendant le traitement : {args.out}')
        temporary.replace(args.out)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f'Master cree : {args.out} ({len(output_rows)} positions, 11 genomes)')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (sankey.InputError, OSError, UnicodeError) as error:
        print(f'ERREUR : {error}', file=sys.stderr)
        sys.exit(2)
