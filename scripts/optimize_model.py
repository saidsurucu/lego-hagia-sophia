"""Repack enclosed ordinary material; preserve every potentially visible part.

Only ordinary rectangular bricks/plates seal flood-fill cells. Shaped parts,
windows and arches are treated as air, so their bounding boxes cannot hide a
visible part. No new material is added to cavities. Base seam ties stay intact.
This minimizes piece count, not a claimed live seller price.
"""
from collections import Counter, defaultdict, deque

from scripts.model_core import PARTS, Piece

BRICKS = ('3007', '2456', '3001', '3002', '3003', '3009', '3010', '3004', '3005')
PLATES = ('3035', '3031', '3034', '3020', '3021', '3022', '3023', '3024')
DIRECTIONS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def voxels(piece):
    return {(x, y, z) for x, z in piece.footprint()
            for y in range(piece.bottom, piece.top)}


def hidden_indices(pieces):
    ordinary = {i: voxels(p) for i, p in enumerate(pieces)
                if p.mount == 'up' and p.part in BRICKS + PLATES}
    solid = set().union(*ordinary.values()) if ordinary else set()
    if not solid:
        return set()
    bounds = [(min(c[a] for c in solid)-1, max(c[a] for c in solid)+1) for a in range(3)]
    start = tuple(b[0] for b in bounds)
    air = {start}
    queue = deque([start])
    while queue:
        x, y, z = queue.popleft()
        for dx, dy, dz in DIRECTIONS:
            c = x+dx, y+dy, z+dz
            if (c not in solid and c not in air and
                    all(lo <= v <= hi for v, (lo, hi) in zip(c, bounds))):
                air.add(c)
                queue.append(c)
    return {i for i, cells in ordinary.items()
            if not pieces[i].section.startswith('Taban') and
            all((x+dx, y+dy, z+dz) not in air
                for x, y, z in cells for dx, dy, dz in DIRECTIONS)}


def optimize_interior(pieces):
    hidden = hidden_indices(pieces)
    groups = defaultdict(list)
    for i in sorted(hidden):
        p = pieces[i]
        groups[p.section].append(p)
    result = [p for i, p in enumerate(pieces) if i not in hidden]
    for section, original in groups.items():
        # Hidden material uses one common catalogued colour instead of scarce
        # facade colours. The exterior retains its exact original placements.
        color = 71
        remaining = set().union(*(voxels(p) for p in original))
        replacement = []
        for y in sorted({c[1] for c in remaining}):
            # Tall bricks first; residual one/two plate offsets stay as plates.
            for catalogue in (BRICKS, PLATES):
                choices = []
                for part in catalogue:
                    d = PARTS[part]
                    for rotation in ((0,) if d.width == d.depth else (0, 90)):
                        w, depth = (d.depth, d.width) if rotation else (d.width, d.depth)
                        choices.append((w*depth, rotation == (90 if y % 2 else 0), part, rotation, w, depth))
                for _, _, part, rotation, w, depth in sorted(choices, reverse=True):
                    for x, z in sorted((x, z) for x, yy, z in remaining if yy == y):
                        p = Piece(part, color, x, y, z, rotation, section)
                        cells = voxels(p)
                        if cells <= remaining:
                            replacement.append(p)
                            remaining -= cells
        if remaining:
            raise ValueError('Unpacked interior material')
        # Greedy packing can lose on awkward shapes: keep the original then.
        result.extend(replacement if len(replacement) < len(original) else original)
    return result


def write_report(original, optimized, destination):
    """Publish auditable quantities without inventing supplier prices."""
    import csv
    import json
    from pathlib import Path
    from scripts.model_core import BRICKLINK_PART_IDS, COLORS
    out = Path(destination)
    before = Counter((p.part, p.color) for p in original)
    after = Counter((p.part, p.color) for p in optimized)
    removed = Counter(original) - Counter(optimized)
    added = Counter(optimized) - Counter(original)
    hidden = hidden_indices(original)
    protected = Counter(p for i, p in enumerate(original) if i not in hidden)
    report = {
        'before_pieces': len(original), 'after_pieces': len(optimized),
        'fewer_pieces': len(original)-len(optimized),
        'piece_reduction_percent': round(100*(len(original)-len(optimized))/len(original), 2),
        'removed_placements': sum(removed.values()), 'added_placements': sum(added.values()),
        'protected_original_placements_unchanged': not bool(protected-Counter(optimized)),
        'ordinary_volume_unchanged':
            Counter(c for p in removed.elements() for c in voxels(p)) ==
            Counter(c for p in added.elements() for c in voxels(p)),
        'price_savings_verified': False,
        'pricing_note': 'Parça sayısı optimizasyonudur. Güncel satıcı fiyatı, stok, minimum sipariş ve kargo doğrulanmadı; parasal tasarruf iddiası içermez. CSV miktar farklarını aynı satıcının birim fiyatlarıyla çarpın.',
    }
    (out/'maliyet-optimizasyonu.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    with (out/'parca-degisimleri.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('bricklink_part_id', 'bricklink_color_id', 'color', 'before', 'after', 'quantity_delta'))
        for part, color in sorted(before.keys() | after.keys()):
            if before[part, color] != after[part, color]:
                writer.writerow((BRICKLINK_PART_IDS.get(part, part), COLORS[color]['bricklink'],
                                 COLORS[color]['name'], before[part, color], after[part, color],
                                 after[part, color]-before[part, color]))
