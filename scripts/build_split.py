#!/usr/bin/env python3
"""Check the collected sessions and write the fixed scene-based split.

Reads configs/dataset_v1.json, validates every session of the listed scenes,
drops exact duplicate images, and writes
datasets/platform/<version>/split_manifest.csv plus summary.json. An existing
split is never overwritten: the split is fixed before training.

    python scripts/build_split.py [--backup]
"""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import tarfile

import cv2

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'datasets' / 'platform'
REQUIRED = ['image_id', 'scene_id', 'session_id', 'image_path', 'source_stamp_ns',
            'width', 'height', 'platform_variant', 'nominal_height_m']
SPLIT_FIELDS = ['image_id', 'scene_id', 'session_id', 'split', 'image_path']


def check_session(session_dir, scene_id):
    """Return the manifest rows of one session; raise on any inconsistency."""
    rows = list(csv.DictReader((session_dir / 'manifest.csv').open(encoding='utf-8')))
    pngs = {p.name for p in session_dir.glob('*.png')}
    if not rows:
        raise ValueError(f'{session_dir}: empty manifest')
    if {r['image_path'] for r in rows} != pngs or len(rows) != len(pngs):
        raise ValueError(f'{session_dir}: manifest rows and PNG files differ')
    stamps = [int(r['source_stamp_ns']) for r in rows]
    if stamps != sorted(set(stamps)):
        raise ValueError(f'{session_dir}: source timestamps not strictly increasing')
    for row in rows:
        empty = [f for f in REQUIRED if not row[f]]
        if empty:
            raise ValueError(f"{row['image_id']}: empty fields {empty}")
        if row['scene_id'] != scene_id or row['session_id'] != session_dir.name:
            raise ValueError(f"{row['image_id']}: scene/session id does not match folder")
        image = cv2.imread(str(session_dir / row['image_path']))
        if image is None:
            raise ValueError(f"{row['image_id']}: PNG does not decode")
        if image.shape[:2] != (int(row['height']), int(row['width'])):
            raise ValueError(f"{row['image_id']}: size differs from manifest")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument('--config', default=str(ROOT / 'configs' / 'dataset_v1.json'))
    parser.add_argument('--backup', action='store_true',
                        help='also write datasets/backups/<version>_raw.tar.gz')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    out_dir = DATASET / config['version']
    split_path = out_dir / 'split_manifest.csv'
    if split_path.exists():
        raise SystemExit(f'{split_path} already exists; the split is fixed.')

    expected_heights = sorted(config['capture']['heights_m'])
    groups = [(s['scene_id'], s['split'], True) for s in config['scenes']]
    flight = config.get('flight_eval')
    if flight:
        groups.append((flight['scene_id'], flight['split'], False))

    records, dropped, seen = [], [], {}
    for scene_id, split, is_capture in groups:
        sessions = sorted(p.parent for p in (DATASET / scene_id).glob('*/manifest.csv'))
        if not sessions:
            raise ValueError(f'{scene_id}: no sessions found')
        heights = []
        for session_dir in sessions:
            rows = check_session(session_dir, scene_id)
            heights.append(float(rows[0]['nominal_height_m']))
            for row in rows:
                digest = hashlib.sha256(
                    (session_dir / row['image_path']).read_bytes()
                ).hexdigest()
                if digest in seen:
                    dropped.append({'image_id': row['image_id'], 'duplicate_of': seen[digest]})
                    continue
                seen[digest] = row['image_id']
                records.append({**row, 'split': split, 'rel_path': (
                    session_dir.relative_to(DATASET) / row['image_path']).as_posix()})
        if is_capture and sorted(heights) != expected_heights:
            raise ValueError(f'{scene_id}: session heights {sorted(heights)}, '
                             f'expected one session per {expected_heights}')

    out_dir.mkdir(parents=True, exist_ok=True)
    with split_path.open('x', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=SPLIT_FIELDS)
        writer.writeheader()
        for r in records:
            writer.writerow({'image_id': r['image_id'], 'scene_id': r['scene_id'],
                             'session_id': r['session_id'], 'split': r['split'],
                             'image_path': r['rel_path']})

    def count(key):
        return {split: dict(sorted(Counter(
            key(r) for r in records if r['split'] == split).items()))
            for split in sorted({r['split'] for r in records})}

    summary = {
        'version': config['version'],
        'images': len(records),
        'per_split': dict(sorted(Counter(r['split'] for r in records).items())),
        'positive_negative': count(
            lambda r: 'negative' if r['platform_variant'] == 'none' else 'positive'),
        'height_m': count(lambda r: r['nominal_height_m']),
        'scenes': count(lambda r: r['scene_id']),
        'platform_variant': count(lambda r: r['platform_variant']),
        'dropped_duplicates': dropped,
    }
    (out_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'scenes'}, indent=2))

    if args.backup:
        backup = DATASET.parent / 'backups' / f"{config['version']}_raw.tar.gz"
        backup.parent.mkdir(exist_ok=True)
        with tarfile.open(backup, 'x:gz') as tar:
            for scene_id, _, _ in groups:
                tar.add(DATASET / scene_id, arcname=scene_id)
            tar.add(out_dir, arcname=config['version'])
        print(f'Backup: {backup}')


if __name__ == '__main__':
    main()
