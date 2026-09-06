#!/usr/bin/env python3
"""Independent mesh-bounds check of exported LDraw versus the placement grid.

Reads actual official triangle/quad vertices, recursively applying references.
Does not import the generator, exporter, or their part dimensions.
This checks placement extents, not physical stability or detailed intersections.
"""
import argparse
from functools import lru_cache
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'assets' / 'ldraw'

def apply(values, point):
    return tuple(values[i] + sum(values[3+3*i+j] * point[j]
                                for j in range(3)) for i in range(3))

@lru_cache(None)
def vertices(name):
    name = name.replace('\\', '/').lower()
    path = next((CACHE/k/name for k in ('parts', 'p') if (CACHE/k/name).exists()), None)
    if path is None:
        raise FileNotFoundError(name)
    result = []
    for line in path.read_text(errors='replace').splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] in ('3', '4'):
            result.extend(tuple(map(float, fields[i:i+3]))
                          for i in range(2, len(fields), 3))
        elif fields[0] == '1':
            matrix = list(map(float, fields[2:14]))
            result.extend(apply(matrix, point)
                          for point in vertices(' '.join(fields[14:])))
    return tuple(result)

def bounds(points):
    points = tuple(points)
    return tuple((min(p[i] for p in points), max(p[i] for p in points))
                 for i in range(3))

def audit(model, ldr, base_studs=48):
    placements = json.loads(model.read_text())
    records = [line.split() for line in ldr.read_text().splitlines()
               if line.startswith('1 ')]
    errors = []
    native = {}
    # Measured main-body frames; side studs project beyond these brick walls.
    host_heights = {'87087': 3, '32952': 5}
    host_poses = {(p['part'], p['x'], p['z'], p['bottom'], p['rotation'])
                  for p in placements if p.get('mount', 'up') == 'up'}
    side_count = 0
    if len(placements) != len(records):
        errors.append({'error': 'record_count', 'grid': len(placements), 'ldr': len(records)})
    for i, (placed, fields) in enumerate(zip(placements, records), 1):
        part = placed['part']
        if fields[14] != part+'.dat' or int(fields[1]) != placed['color']:
            errors.append({'record': i, 'error': 'part_or_color_mismatch'})
            continue
        if part not in native:
            native[part] = bounds(vertices(part+'.dat'))
        extent = native[part]
        actual = bounds(apply(list(map(float, fields[2:14])), point)
                        for point in product(*extent))
        if placed.get('mount', 'up') == 'side':
            side_count += 1
            host = placed.get('host_part', '87087')
            if host not in host_heights or part not in ('98138', '2412b'):
                errors.append({'record': i, 'error': 'unsupported_side_mount'})
                continue
            pose = (host, placed['x'], placed['z'], placed['bottom'], placed['rotation'])
            if pose not in host_poses:
                errors.append({'record': i, 'error': 'missing_matching_side_host'})
            # Both hosts' side wall is Z=-10. The tile's back is nativeY=8,
            # so its top plane must sit at Z=-18. Side stud axes are at Y=10
            # and (32952 only) Y=30. A round tile centres on the upper axis;
            # the 2-stud grille stands vertically centred halfway between them.
            cosine, sine = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}[placed['rotation']]
            def yaw(v):
                return (cosine*v[0]-sine*v[2], v[1], sine*v[0]+cosine*v[2])
            axes = ((1,0,0), (0,0,1), (0,-1,0)) if part == '98138' else ((0,1,0), (0,0,1), (1,0,0))
            columns = [yaw(axis) for axis in axes]
            rotation = [columns[j][a] for a in range(3) for j in range(3)]
            offset = yaw((0, 10 if part == '98138' else 20, -18))
            center = ((placed['x']-base_studs/2+.5)*20,
                      -(placed['bottom']+host_heights[host])*8,
                      (placed['z']-base_studs/2+.5)*20)
            expected_values = [center[a]+offset[a] for a in range(3)] + rotation
        elif placed.get('mount', 'up') == 'up':
            # Infer the nominal connection envelope from official mesh coordinates.
            # Modern curves/cheese slopes have a bottom-plane origin (maxY == 0),
            # unlike ordinary bricks whose body-top plane is native Y == 0.
            raw_width = round((extent[0][1]-extent[0][0])/20)
            raw_depth = round((extent[2][1]-extent[2][0])/20)
            width, depth = sorted((raw_width, raw_depth))
            native_turn = 270 if raw_width > raw_depth else 0
            if placed['rotation'] % 180:
                width, depth = depth, width
            body_top = round(extent[1][0]/8)*8 if abs(extent[1][1]) < .01 else 0
            height = round((extent[1][1]-body_top)/8)
            origin = ((extent[0][0]+extent[0][1])/2, body_top,
                      (extent[2][0]+extent[2][1])/2)
            if part in host_heights:
                # Independent measurements from official host brick wall vertices.
                width = depth = 1
                height = host_heights[part]
                origin = (0, 0, 0)
                native_turn = 0
            turn = (placed['rotation'] + native_turn) % 360
            cosine, sine = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}[turn]
            rotation = [cosine, 0, -sine, 0, 1, 0, sine, 0, cosine]
            center = ((placed['x']-base_studs/2+width/2)*20,
                      -(placed['bottom']+height)*8,
                      (placed['z']-base_studs/2+depth/2)*20)
            translation = [center[a]-sum(rotation[3*a+j]*origin[j] for j in range(3))
                           for a in range(3)]
            expected_values = translation + rotation
        else:
            errors.append({'record': i, 'error': 'unknown_mount'})
            continue
        exported_values = list(map(float, fields[2:14]))
        # Checking orientation separately also catches 180-degree errors in
        # asymmetric slopes whose outer boxes are otherwise indistinguishable.
        matrix_delta = max(abs(a-b) for a,b in zip(exported_values, expected_values))
        if matrix_delta > .01:
            errors.append({'record': i, 'part': part, 'error': 'native_frame_mismatch',
                           'actual_transform': exported_values,
                           'expected_transform': expected_values,
                           'max_delta': matrix_delta})
        expected = bounds(apply(expected_values, point) for point in product(*extent))
        delta = max(abs(actual[a][j]-expected[a][j]) for a in range(3) for j in range(2))
        # Round part primitive approximations can exceed the nominal edge by .001.
        if delta > .01:
            errors.append({'record': i, 'part': part, 'error': 'mesh_grid_extent_mismatch',
                           'actual_ldu': actual, 'expected_ldu': expected, 'max_delta_ldu': delta})
    return {'passed': not errors, 'checked_records': min(len(records), len(placements)),
            'side_mounts_checked': side_count, 'native_part_bounds_ldu': native, 'tolerance_ldu': .01,
            'method': 'Recursive official LDraw vertices; independently inferred nominal body frame, all four cardinal rotations, bounded side-stud host frames, full transform and mesh bounds. No generator imports.',
            'scope': 'Native frame, orientation, outer extents, body height, studs, identity/color/order; not mechanical stability or full mesh intersection.',
            'errors': errors}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, default=ROOT/'dist/model.json')
    parser.add_argument('--ldr', type=Path, default=ROOT/'dist/ayasofya.ldr')
    parser.add_argument('--output', type=Path, default=ROOT/'dist/ldraw-geometri-dogrulama.json')
    args = parser.parse_args()
    report = audit(args.model, args.ldr)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    print(f"Mesh bounds audit: {report['checked_records']} parts; {len(report['errors'])} errors")
    raise SystemExit(0 if report['passed'] else 1)

if __name__ == '__main__':
    main()
