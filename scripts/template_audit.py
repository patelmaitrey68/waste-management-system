#!/usr/bin/env python3
"""Template audit and (optional) consolidation tool.

Usage:
  python scripts/template_audit.py        # dry-run report
  python scripts/template_audit.py --apply  # move duplicates into templates/ with backups
"""
import argparse
import hashlib
import os
import shutil
import time


def iter_files(root):
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            # consider only template-like files
            if f.endswith(('.html', '.htm')):
                yield os.path.join(dirpath, f)


def file_hash(path):
    h = hashlib.sha1()
    with open(path, 'rb') as fh:
        while True:
            b = fh.read(8192)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Move duplicates into templates/ (creates backups)')
    args = parser.parse_args()

    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    candidate_dirs = [
        os.path.join(base, 'templates'),
        os.path.join(base, 'waste_management', 'templates'),
        os.path.join(base, 'waste', 'templates'),
    ]

    existing_dirs = [d for d in candidate_dirs if os.path.isdir(d)]

    print('Scanning template directories:')
    for d in existing_dirs:
        print(' -', d)

    files = []
    for d in existing_dirs:
        for p in iter_files(d):
            files.append(p)

    by_name = {}
    by_hash = {}
    for p in files:
        name = os.path.basename(p)
        h = file_hash(p)
        by_name.setdefault(name, []).append(p)
        by_hash.setdefault(h, []).append(p)

    duplicates_by_name = {n: v for n, v in by_name.items() if len(v) > 1}
    exact_duplicates = {h: v for h, v in by_hash.items() if len(v) > 1}

    print('\nFound {} template files total.'.format(len(files)))
    print('Found {} duplicated basenames.'.format(len(duplicates_by_name)))
    if duplicates_by_name:
        print('\nDuplicates by basename:')
        for name, paths in duplicates_by_name.items():
            print('\n-', name)
            for p in paths:
                print('   ', p)

    if exact_duplicates:
        print('\nExact duplicate contents (by hash):')
        for h, paths in exact_duplicates.items():
            print('\nHash:', h)
            for p in paths:
                print('   ', p)

    if not args.apply:
        print('\nDry-run complete. To consolidate duplicates into `templates/`, re-run with --apply')
        return

    # --apply: move duplicates (keep first occurrence as canonical)
    canonical_dir = os.path.join(base, 'templates')
    if not os.path.isdir(canonical_dir):
        os.makedirs(canonical_dir, exist_ok=True)

    timestamp = time.strftime('%Y%m%dT%H%M%S')
    moved = []
    for name, paths in duplicates_by_name.items():
        # choose canonical file as the one already in canonical_dir if present, else first path
        canon = None
        for p in paths:
            if os.path.dirname(p) == canonical_dir:
                canon = p
                break
        if not canon:
            canon = paths[0]

        for p in paths:
            if os.path.abspath(p) == os.path.abspath(canon):
                continue
            dest = os.path.join(canonical_dir, name)
            if os.path.exists(dest):
                # create backup of existing dest
                bak = dest + '.bak.' + timestamp
                print('Backing up existing', dest, '->', bak)
                shutil.move(dest, bak)
            print('Moving', p, '->', dest)
            bak_orig = p + '.bak.' + timestamp
            shutil.move(p, bak_orig)
            shutil.move(bak_orig, dest)
            moved.append((p, dest))

    print('\nMoved {} files.'.format(len(moved)))
    for src, dst in moved:
        print(' -', src, '->', dst)


if __name__ == '__main__':
    main()
