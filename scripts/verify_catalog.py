#!/usr/bin/env python3
"""Verify BOM color pairs against actual BrickLink catalog color images.

Only a matching catalog link immediately wrapping the corresponding part/color
image counts as evidence. Generic color selectors never count. No stock claims.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, default=Path('/tmp/ayasofya-bricklink-catalog'))
    parser.add_argument('--offline', action='store_true', help='Use existing saved responses only')
    args = parser.parse_args()
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    bom = ROOT / 'dist/parca-listesi.csv'
    rows = list(csv.DictReader(bom.read_text(encoding='utf-8-sig').splitlines()))
    for row in rows:
        row['catalog_part_id'] = row.get('bricklink_part_id') or row['part_id']
    sources = {}
    results = []
    for part in sorted({row['catalog_part_id'] for row in rows}):
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', part):
            raise ValueError(f'Unsafe catalog item ID: {part}')
        url = f'https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo={part}'
        path = args.cache_dir / f'{part}.html'
        error = None
        if not args.offline:
            fetch = subprocess.run(['curl', '-sSL', '--fail', '--max-time', '30', url, '-o', str(path)], capture_output=True, text=True)
            if fetch.returncode:
                error = fetch.stderr.strip()
        colors = []
        evidence = {}
        if path.exists() and not error:
            raw = path.read_bytes()
            html = raw.decode('utf-8', errors='replace')
            # Match the catalog's actual color-image cards, not idColor options.
            pattern = (r'<A\s+HREF="/v2/catalog/catalogitem\.page\?P='
                       + re.escape(part)
                       + r'&idColor=(\d+)"><IMG\b[^>]*\bSRC="(/P/\1/'
                       + re.escape(part) + r'\.(?:JPG|PNG|GIF))"[^>]*></A>')
            for match in re.finditer(pattern, html, re.I):
                color = int(match.group(1))
                colors.append(color)
                evidence[color] = {'image_url': 'https://www.bricklink.com' + match.group(2),
                                   'html_excerpt': match.group(0)}
            sources[part] = {
                'url': url, 'retrieved_at_utc': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                'sha256': hashlib.sha256(raw).hexdigest(),
                'observed_catalog_image_color_ids': sorted(set(colors)),
            }
        else:
            sources[part] = {'url': url, 'error': error or 'No cached response'}
        for row in [r for r in rows if r['catalog_part_id'] == part]:
            color = int(row['bricklink_color_id'])
            results.append({
                'part_id': row['part_id'], 'bricklink_part_id': part,
                'bricklink_color_id': color, 'color': row['color'],
                'quantity': int(row['quantity']),
                'status': 'verified_catalog_color_image' if color in evidence else 'unknown',
                'source_url': url, 'evidence': evidence.get(color),
            })
    report = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'bom_sha256': hashlib.sha256(bom.read_bytes()).hexdigest(),
        'scope': 'Actual part/color image entries in BrickLink Reference Catalog. Not live stock, price, rarity, set-inventory or structural validation.',
        'method': 'Exact part ID and color ID must occur together in a catalog image card linking that same part/color. Dropdowns are excluded.',
        'unique_parts': len(sources), 'part_color_pairs': len(results),
        'verified_pairs': sum(r['status'] == 'verified_catalog_color_image' for r in results),
        'unknown_pairs': sum(r['status'] == 'unknown' for r in results),
        'sources': sources, 'results': results,
    }
    target = ROOT / 'dist/katalog-dogrulama.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['unique_parts', 'part_color_pairs', 'verified_pairs', 'unknown_pairs']}))
    for result in results:
        if result['status'] == 'unknown':
            print('UNKNOWN', result['part_id'], result['color'])
    return 0 if report['unknown_pairs'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
