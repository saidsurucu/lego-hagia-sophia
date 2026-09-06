#!/usr/bin/env python3
"""Cache official LDraw geometry and its dependencies; preserve license headers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://library.ldraw.org/library/official/'
CACHE = ROOT / 'assets' / 'ldraw'

def dependencies(text):
    for line in text.splitlines():
        fields = line.strip().split(maxsplit=14)
        if len(fields) == 15 and fields[0] == '1':
            yield fields[14].replace('\\', '/').lower()

def fetch(name, seen, manifest):
    name = name.replace('\\', '/').lower()
    if name in seen:
        return
    seen.add(name)
    if '..' in Path(name).parts or Path(name).is_absolute():
        raise ValueError(f'Unsafe LDraw reference: {name}')
    existing = next((CACHE / kind / name for kind in ('parts', 'p')
                     if (CACHE / kind / name).exists()), None)
    if existing:
        target = existing
        data = target.read_bytes()
        source = BASE + target.relative_to(CACHE).as_posix()
    else:
        for kind in ('parts', 'p'):
            source = BASE + kind + '/' + name
            try:
                response = subprocess.run(['curl', '-sSL', '--max-time', '45', '-w', '\n%{http_code}', source], capture_output=True, check=True)
                data, status = response.stdout.rsplit(b'\n', 1)
                time.sleep(1.05)
                if status == b'404':
                    continue
                if status != b'200':
                    raise RuntimeError(f'HTTP {status.decode()} for {source}')
                target = CACHE / kind / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                print(f'Fetched {kind}/{name}', flush=True)
                break
            except subprocess.CalledProcessError:
                raise
        else:
            raise FileNotFoundError(f'No official LDraw geometry: {name}')
    decoded = data.decode('utf-8-sig', errors='replace')
    manifest[target.relative_to(CACHE).as_posix()] = {
        'source': source,
        'sha256': hashlib.sha256(data).hexdigest(),
        'license_headers': [line for line in decoded.splitlines()
                            if line.startswith('0 !LICENSE')],
    }
    for child in dependencies(decoded):
        fetch(child, seen, manifest)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parts', nargs='*', help='part IDs or .dat names')
    parser.add_argument('--model', type=Path, help='fetch all root .ldr references')
    args = parser.parse_args()
    names = [part if part.endswith('.dat') else part + '.dat' for part in args.parts]
    if args.model:
        names.extend(dependencies(args.model.read_text()))
    CACHE.mkdir(parents=True, exist_ok=True)
    manifest_path = CACHE / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    try:
        seen = set()
        for name in names:
            fetch(name, seen, manifest)
    finally:
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(f'{len(seen)} geometry files available')

if __name__ == '__main__':
    main()
