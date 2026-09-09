"""Build an exterior-scale Ayasofya model from ordinary upright LEGO parts."""
from math import sqrt, ceil
from collections import defaultdict

from scripts.model_core import PARTS, Piece


BRICKS = ("3001", "3002", "3003", "3010", "3004", "3005")
PLATES = ("3035", "3031", "3034", "3020", "3021", "3022", "3023", "3024")


def rectangle(x0, z0, x1, z1):
    return {(x, z) for x in range(x0, x1) for z in range(z0, z1)}


def disc(cx, cz, radius, side=0):
    return {(x, z) for x in range(48) for z in range(48)
            if (x + .5 - cx) ** 2 + (z + .5 - cz) ** 2 <= radius ** 2
            and (side == 0 or (z + .5 - cz) * side >= 0)}


def boundary(mask, x, z, thickness=1):
    return any((x + dx, z + dz) not in mask
               for dx, dz in ((thickness, 0), (-thickness, 0), (0, thickness), (0, -thickness)))


def pack(pieces, cells, bottom, section, height=1, phase=0, catalogue=None):
    """Greedily tile a same-height material field, alternating seam direction."""
    remaining = dict(cells)
    catalogue = catalogue or (BRICKS if height == 3 else PLATES)
    choices = []
    for part in catalogue:
        d = PARTS[part]
        for angle in ((0,) if d.width == d.depth else (0, 90)):
            w, h = (d.depth, d.width) if angle else (d.width, d.depth)
            choices.append((w * h, angle == (90 if phase % 2 else 0), part, angle, w, h))
    choices.sort(reverse=True)
    order = (lambda c: (c[0], c[1])) if phase % 2 else (lambda c: (c[1], c[0]))
    # Place large rectangles across the entire field before filling curved
    # boundaries. Starting at each jagged edge produces long strips of 1x1s.
    for _, _, part, angle, w, h in choices:
        for x, z in sorted(remaining, key=order):
            if (x, z) not in remaining:
                continue
            color = remaining[x, z]
            footprint = rectangle(x, z, x + w, z + h)
            if all(remaining.get(cell) == color for cell in footprint):
                # Prefer evidenced, readily catalogued Tan for the two 4x4
                # cornice/paving infills; Dark Tan 3031 has weak source evidence.
                actual_color = 19 if part == "3031" and color in (28, 484) else color
                pieces.append(Piece(part, actual_color, x, bottom, z, angle, section))
                for cell in footprint:
                    del remaining[cell]
    if remaining:
        raise ValueError(f"Cannot tile {section} at {bottom}: {list(remaining)[:5]}")


def plinth(pieces):
    # Bottom: 4 x 8. Middle: rotated, with a two-stud seam shift in both axes.
    pack(pieces, {c: 0 for c in rectangle(0, 0, 48, 48)}, 0, "Taban · alt kat")
    cuts_x = [0, 2] + list(range(10, 48, 8)) + [48]
    cuts_z = [0, 2] + list(range(6, 48, 4)) + [48]
    for xa, xb in zip(cuts_x, cuts_x[1:]):
        for za, zb in zip(cuts_z, cuts_z[1:]):
            pack(pieces, {c: 0 for c in rectangle(xa, za, xb, zb)}, 1, "Taban · bağlayıcı kat", phase=1)
    pack(pieces, {c: 28 if 2 <= c[0] < 46 and 2 <= c[1] < 46 else 0
                  for c in rectangle(0, 0, 48, 48)}, 2, "Taban · taş zemin")


def upper_buttresses():
    return set().union(*(rectangle(x, z, x + 3, z + 4)
                         for x in (11, 34) for z in (14, 30)))


def exedra_masks():
    for cz, side in ((14, -1), (34, 1)):
        for cx in (16, 32):
            yield (cx, cz, side, disc(cx, cz, 4, side) - disc(24, cz, 8, side))


def lower_mask():
    mask = rectangle(10, 12, 38, 36)
    mask |= disc(24, 14, 8, -1) | disc(24, 34, 8, 1)
    for _, _, _, exedra in exedra_masks():
        mask |= exedra
    mask |= rectangle(16, 5, 32, 9)  # western narthex
    for x in (8, 38):
        for z in (16, 28):
            mask |= rectangle(x, z, x + 2, z + 4)
    return mask


def lower_body(pieces):
    mask = lower_mask()
    for course in range(6):
        cells = {}
        for x, z in mask:
            edge = boundary(mask, x, z, 2)
            # Solid perimeter plus aligned internal ribs, leaving open voids.
            # An extra 2x2 pier carries the western roof's infill plate.
            roof_pier = 26 <= x < 28 and (14 <= z < 16 or z == 25 or 34 <= z < 36)
            if not edge and not (x % 4 < 2 or z % 6 == 0 or roof_pier):
                continue
            color = (84 if course >= 3 else 19) if edge else 71
            if edge:
                if course == 0:
                    color = 28
                elif course == 3:
                    color = 84
                if course in (1, 2) and boundary(mask, x, z):
                    if (x in (10, 37) and z in (14, 19, 24, 29, 33)) or (z == 5 and x in (18, 22, 25, 29)):
                        color = 0
                if z >= 40 and x in (23, 24) and course in (1, 2, 4):
                    color = 0
                if z == 5 and x in (23, 24) and course < 3:
                    color = 70
            window_z = z in (14, 15, 19, 20, 24, 25, 29, 30)
            if course in (1, 2) and window_z:
                if x in (10, 37):
                    continue
                if x in (11, 36):
                    color = 0
            cells[x, z] = color
        pack(pieces, cells, 3 + course * 3, "Alt gövde ve payandalar", height=3, phase=course)
    for x in (10, 37):
        for z in (14, 19, 24, 29):
            pieces.append(Piece("60592", 19, x, 6, z, section="Yan cephe · gerçek pencere çerçeveleri"))
    pack(pieces, {c: 71 for c in mask}, 21, "Alt gövde · çatı bağlama plakası")

    # Stepped aisle roof strips stand on the continuous lower roof plate.
    for t in range(3):
        roof = rectangle(10 + t, 12, 14, 36) | rectangle(34, 12, 38 - t, 36)
        pack(pieces, {c: 71 for c in roof - upper_buttresses() - set().union(*(m for _, _, _, m in exedra_masks()))}, 22 + t, "Yan nef çatıları", phase=t)


def upper_body(pieces):
    pylons = upper_buttresses()
    for course in range(6):
        pack(pieces, {c: 19 if course in (0, 5) else 84 for c in pylons},
             22 + course * 3, "Yüksek cephe payandaları", height=3, phase=course)
    for y in (40, 41):
        pack(pieces, {c: 71 for c in pylons}, y, "Payanda çatı başlıkları", phase=y)
    mask = rectangle(14, 14, 34, 34)
    for course in range(6):
        cells = {}
        for x, z in mask:
            if x in (14, 33):
                continue  # Thin plate courses draw the monumental facade arch.
            edge = boundary(mask, x, z, 2)
            if not edge and not (x % 4 < 2 or z % 6 == 0):
                continue
            color = 84 if edge else 71
            if edge and course == 0:
                color = 19
            if z in (14, 33) and x in (17, 20, 23, 26, 29, 32) and course in (3, 4):
                color = 0
            if x in (15, 32) and 18 <= z < 30:
                color = 484
                if course in (1, 3) and z in (19, 20, 23, 24, 27, 28):
                    color = 0
            cells[x, z] = color
        pack(pieces, cells, 22 + course * 3, "Ana gövde · yüksek pencere duvarları", height=3, phase=course)
    # Structural, genuinely open arches stand one stud ahead of the tympanum.
    for x in (14, 33):
        for y in range(22, 40, 3):
            side = {(x, z): 19 for z in (*range(14, 18), *range(30, 34))}
            pack(pieces, side, y, "Büyük kemer · taş yan duvarlar", height=3, phase=y)
        for y in (22, 25, 28):
            pack(pieces, {(x,z): 484 for z in range(18,30)}, y,
                 "Alt pencere sırası · kırmızı alınlık", height=3, phase=y)
        pieces.append(Piece("6108", 19, x, 31, 18, section="Anıtsal kemer · gerçek açıklık"))
        for z, levels in ((18, (34, 37)), (19, (37,)), (28, (37,)), (29, (34, 37))):
            for y in levels:
                pieces.append(Piece("3005", 84, x, y, z, section="Anıtsal kemer · üst taş dolgusu"))
    pack(pieces, {c: 19 for c in mask}, 40, "Ana gövde · üst bağlama plakası")

    drum = disc(24, 24, 10)
    for course in range(2):
        cells = {}
        for x, z in drum:
            edge = boundary(drum, x, z, 2)
            if not edge and not (x % 4 < 2 or z % 6 == 0):
                continue
            color = 72 if edge else 71
            if boundary(drum, x, z) and (x + z) % 3 == 0:
                color = 0
            cells[x, z] = color
        pack(pieces, cells, 41 + course * 3, "Kubbe kasnağı · pencere halkası", height=3, phase=course)


def inward_rotation(x, z, cx, cz):
    dx, dz = cx - x, cz - z
    return (270 if dx > 0 else 90) if abs(dx) > abs(dz) else (0 if dz > 0 else 180)


def smooth_dome(pieces, cx, cz, radius, bottom, rise, name, mask=None, finial=False, spherical=False):
    """Fill stud columns under real curved/sloped caps; all caps stay upright."""
    mask = set(mask if mask is not None else disc(cx, cz, radius))
    remaining = set(mask)
    caps = []
    def surface_level(distance):
        if not spherical:
            return max(2, round(rise * sqrt(max(0, 1 - (distance / radius) ** 2))))
        # Convert plate heights to stud units before fitting a spherical cap.
        h = rise * .4
        sphere_radius = (radius * radius + h * h) / (2 * h)
        height = sqrt(max(0, sphere_radius * sphere_radius - distance * distance)) - (sphere_radius - h)
        return max(2, round(height / .4))
    # Odd grid around the centre leaves a single centred 2x2 crown module.
    for x in range(cx - 1 - 2 * ceil(radius / 2), cx + ceil(radius), 2):
        for z in range(cz - 1 - 2 * ceil(radius / 2), cz + ceil(radius), 2):
            cells = rectangle(x, z, x + 2, z + 2)
            if not cells <= remaining:
                continue
            crown = finial and x == cx - 1 and z == cz - 1
            dist = sqrt((x + 1 - cx) ** 2 + (z + 1 - cz) ** 2)
            if spherical and not crown:
                # Narrow strips around the shoulder avoid broad square facets.
                continue
            level = surface_level(dist)
            part = "87580" if crown else "15068"
            if crown:
                level = rise
            caps.append((Piece(part, 71, x, bottom + level - PARTS[part].height, z,
                               0 if crown else inward_rotation(x + 1, z + 1, cx, cz), name), cells))
            remaining -= cells
    # Curved 1x2 edge strips, then small cheese slopes close the circular edge.
    for x, z in sorted(remaining):
        if (x, z) not in remaining:
            continue
        dx, dz = cx - x - .5, cz - z - .5
        rotate = inward_rotation(x + .5, z + .5, cx, cz)
        candidates = [(1, 2, 0 if dz > 0 else 180), (2, 1, 270 if dx > 0 else 90)]
        if abs(dx) > abs(dz):
            candidates.reverse()
        part, cells = "54200", {(x, z)}
        for w, d, angle in candidates:
            pair = rectangle(x, z, x + w, z + d)
            if pair <= remaining:
                part, cells, rotate = "11477", pair, angle
                break
        center_x = sum(a + .5 for a, _ in cells) / len(cells)
        center_z = sum(b + .5 for _, b in cells) / len(cells)
        dist = sqrt((center_x - cx) ** 2 + (center_z - cz) ** 2)
        if spherical and part == "11477" and dist > 6.5:
            part = "3040b"
        level = max(PARTS[part].height, surface_level(dist))
        caps.append((Piece(part, 71, x, bottom + level - PARTS[part].height, z, rotate, name), cells))
        remaining -= cells
    fills = defaultdict(dict)
    for cap, cells in caps:
        for y in range(bottom, cap.bottom):
            fills[y].update({cell: 71 for cell in cells})
    for y, cells in sorted(fills.items()):
        pack(pieces, cells, y, name + " · iç taşıyıcı", phase=y)
    for cap, cells in caps:
        if cap.part in ("15068", "11477"):
            raised_row = cells - cap.bottom_studs()
            pack(pieces, {c: 71 for c in raised_row}, cap.bottom,
                 name + " · kavis altı dolgu", phase=cap.rotation // 90)
    pieces.extend(cap for cap, _ in caps)
    return bottom + rise


def domes(pieces):
    for cx, cz, side, mask in exedra_masks():
        pack(pieces, {c: 19 for c in mask}, 22, "İkincil yarım kubbe · duvar", height=3)
        smooth_dome(pieces, cx, cz, 4, 25, 5, "İkincil kavisli kubbeler", mask)
    for cz, side, name in ((14, -1, "Batı yarım kubbe"), (34, 1, "Doğu yarım kubbe")):
        mask = disc(24, cz, 8, side)
        for course in range(2):
            cells = {c: (0 if course == 1 and boundary(mask, *c)
                          and (c[0] + c[1]) % 3 == 0 else 84) for c in mask}
            pack(pieces, cells, 22 + course * 3, name + " · pencere kasnağı", height=3, phase=course)
        smooth_dome(pieces, 24, cz, 8, 28, 9, name, mask)
    top = smooth_dome(pieces, 24, 24, 10, 47, 16, "Ana kubbe · kavisli kaplama", finial=True, spherical=True)
    pieces.append(Piece("3062b", 297, 23.5, top, 23.5, section="Kubbe alemi"))
    pieces.append(Piece("4589", 297, 23.5, top + 3, 23.5, section="Kubbe alemi · sivri uç"))


def southern_annexes(pieces):
    """Three separate low, domed volumes echo the photograph's foreground."""
    for cz, name in ((15, "Güney eki · batı"), (24, "Güney eki · orta"), (33, "Güney eki · doğu")):
        mask = disc(43, cz, 3.4)
        courses = {15: 5, 24: 4, 33: 3}[cz]
        for course in range(courses):
            cells = {c: 19 for c in mask}
            for x, z in mask:
                if course in (1, 2) and x == 45 and z in (cz - 2, cz + 1):
                    cells[x, z] = 0
                elif course == 0:
                    cells[x, z] = 28
            pack(pieces, cells, 3 + course * 3, name, height=3, phase=course)
        bottom = 3 + courses * 3
        top = smooth_dome(pieces, 43, cz, 3.4, bottom, 6, name + " · kavisli kubbe", finial=True)
        pieces.append(Piece("4740", 71, 42, top, cz - 1, section=name + " · alem kaidesi"))
        pieces.append(Piece("4073", 297, 42.5, top + 1, cz - .5, section=name + " · alem"))


def minarets(pieces):
    configs = ((7, 7, 19, 13, "Minare · kuzeybatı"),
               (37, 7, 19, 13, "Minare · güneybatı"),
               (7, 37, 19, 12, "Minare · kuzeydoğu"),
               (37, 37, 70, 13, "Minare · güneydoğu tuğla"))
    for x, z, color, shaft_courses, name in configs:
        for course in range(2):
            pack(pieces, {c: (28 if course == 0 else 19) for c in rectangle(x, z, x + 4, z + 4)},
                 3 + course * 3, name, height=3, phase=course)
        for sx, sz, angle in ((x, z, 0), (x + 2, z, 0), (x, z + 2, 180), (x + 2, z + 2, 180)):
            pieces.append(Piece("3039", 19, sx, 9, sz, angle, name + " · eğimli kaide"))
        y = 12
        shaft = "3941"
        for _ in range(shaft_courses):
            pieces.append(Piece(shaft, color, x + 1, y, z + 1, section=name))
            y += 3
        # One continuous two-stud shaft keeps all four minarets legible.
        for _ in range(2):
            pieces.append(Piece("60474", 19, x, y, z, section=name + " · yuvarlak şerefe"))
            y += 1
        for _ in range(4):
            pieces.append(Piece(shaft, color, x + 1, y, z + 1, section=name + " · üst gövde"))
            y += 3
        pieces.append(Piece("3942c", 71, x + 1, y, z + 1, section=name + " · uzun külah"))
        pieces.append(Piece("4589", 71, x + 1.5, y + 6, z + 1.5, section=name + " · külah ucu"))


def carve(pieces, cells, bottom, top):
    """Cut ordinary grid material before installing complete façade modules."""
    result = []
    for p in pieces:
        affected = p.mount == "up" and p.bottom < top and p.top > bottom and bool(p.footprint() & cells)
        if not affected:
            result.append(p)
            continue
        if p.part not in (*BRICKS, *PLATES, "2877", "30136"):
            raise ValueError(f"Cannot carve shaped part: {p}")
        if bottom <= p.bottom and p.top <= top:
            pack(result, {c: p.color for c in p.footprint() - cells}, p.bottom, p.section,
                 height=PARTS[p.part].height)
        else:
            for y in range(p.bottom, p.top):
                remain = p.footprint() - cells if bottom <= y < top else p.footprint()
                pack(result, {c: p.color for c in remain}, y, p.section, phase=y)
    pieces[:] = result


def architecture_modules(pieces):
    for z in (19, 29):
        pieces.append(Piece("3005", 19, 10, 3, z, section="Pencere çerçevesi · ikinci alt destek"))
    # Seven narrow lower windows and five upper windows echo the tympanum.
    for host_x, recess_x, facing in ((15, 14, 270), (32, 33, 90)):
        for z in (18, 20, 22, 24, 26, 28, 30):
            carve(pieces, {(host_x, z), (recess_x, z)}, 25, 31)
            pieces.append(Piece("32952", 19, host_x, 25, z, facing, "Alt pencere sırası · taşıyıcı"))
            pieces.append(Piece("3024", 84, host_x, 30, z, section="Alt pencere sırası · dolgu"))
            pieces.append(Piece("2412b", 71, host_x, 25, z, facing,
                                "Alt pencere sırası · dikey ızgara", "side", "32952"))
    for host_x, recess_x, facing in ((16, 15, 270), (31, 32, 90)):
        for z, bottom in ((19, 32), (21, 33), (23, 34), (25, 33), (27, 32)):
            if host_x == 31:
                # The south inner wall sits outside the interior lattice.
                for y in range(22, bottom):
                    occupied = any(p.mount == "up" and p.bottom <= y < p.top and (host_x, z) in p.footprint() for p in pieces)
                    if not occupied:
                        pieces.append(Piece("3024", 71, host_x, y, z, section="Üst pencere sırası · iç destek"))
            carve(pieces, {(host_x, z), (recess_x, z)}, bottom, bottom + 6)
            pieces.append(Piece("32952", 19, host_x, bottom, z, facing, "Üst pencere sırası · taşıyıcı"))
            pieces.append(Piece("3024", 84, host_x, bottom + 5, z, section="Üst pencere sırası · dolgu"))
            pieces.append(Piece("2412b", 71, host_x, bottom, z, facing,
                                "Üst pencere sırası · dikey ızgara", "side", "32952"))
    # Fluted piers and stone roundels are deliberate repeated façade modules.
    for x, facing in ((11, 270), (36, 90)):
        for z in (15, 31):
            for y in (22, 28):
                carve(pieces, {(x, z), (x, z + 1)}, y, y + 3)
                pieces.append(Piece("2877", 19, x, y, z, 180 if x == 11 else 0, "Payanda · oluklu düşey şerit"))
            carve(pieces, {(x, z)}, 37, 40)
            pieces.append(Piece("87087", 19, x, 37, z, facing, "Payanda · madalyon taşıyıcısı"))
            pieces.append(Piece("98138", 28, x, 37, z, facing, "Payanda · taş madalyon", "side"))
    for x in (7, 37):
        for z in (7, 37):
            carve(pieces, {(x + 3, z + 1), (x + 3, z + 2)}, 6, 9)
            pieces.append(Piece("30136", 19, x + 3, 6, z + 1, section="Minare kaidesi · yuvarlatılmış düşey profil"))
    # Curved stone caps follow the rounded ends of the monumental pylons.
    for x in (11, 34):
        for z in (14, 30):
            for dx in range(3):
                for dz, angle in ((0, 0), (2, 180)):
                    cap = Piece("11477", 19, x + dx, 42, z + dz, angle,
                                "Payanda başlığı · kavisli taş")
                    raised = cap.footprint() - cap.bottom_studs()
                    pack(pieces, {c: 19 for c in raised}, 42, "Payanda başlığı · kavis altı dolgu")
                    pieces.append(cap)


def entrance_portico(pieces):
    for course in range(6):
        cells = {c: 19 for c in rectangle(16, 3, 32, 5)}
        for x in (18, 21, 24, 27, 30):
            if course in (1, 2, 3):
                cells[x, 3] = 0
        pack(pieces, cells, 3 + course * 3, "Batı girişi · kapalı narteks", height=3, phase=course)
    for y in (21, 22):
        pack(pieces, {c: 71 for c in rectangle(16, 3, 32, 5)}, y,
             "Batı girişi · alçak kurşun çatı", phase=y)
    for y in range(3):
        pack(pieces, {c: 19 for c in rectangle(17, y, 31, 3)}, 3 + y,
             "Batı girişi · basamaklar", phase=y)


def courtyard_modules(pieces):
    for z in (16, 20, 24, 28):
        pieces.append(Piece("30055", 19, 3, 3, z, section="Avlu · açık taş korkuluk"))
    # Compact domed pavilion evokes the fountain in the supplied photograph.
    for x in (42, 45):
        for z in (42, 45):
            for y in (3, 6):
                pieces.append(Piece("3062b", 19, x, y, z, section="Şadırvan · yuvarlak sütun"))
    pieces.append(Piece("3031", 19, 42, 9, 42, section="Şadırvan · korniş"))
    pieces.append(Piece("4032", 71, 43, 10, 43, section="Şadırvan · kubbe kasnağı"))
    pieces.append(Piece("49308", 71, 42.5, 11, 42.5, section="Şadırvan · düzgün kubbe"))
    pieces.append(Piece("4740", 71, 43, 15, 43, section="Şadırvan · alem kaidesi"))
    pieces.append(Piece("4073", 297, 43.5, 16, 43.5, section="Şadırvan · alem"))


def surface_details(pieces):
    """Replace selected exposed brick faces by official embossed masonry bricks."""
    layers = defaultdict(set)
    for p in pieces:
        layers[p.bottom].update(p.footprint())
    result = []
    for p in pieces:
        if p.part not in BRICKS or p.color not in (19, 28, 84) or (p.bottom // 3) % 2:
            result.append(p)
            continue
        footprint = p.footprint()
        outside = layers[p.bottom]
        faces = [({(p.x, z) for z in range(p.z, p.z + p.depth)}, (-1, 0)),
                 ({(p.x + p.width - 1, z) for z in range(p.z, p.z + p.depth)}, (1, 0)),
                 ({(x, p.z) for x in range(p.x, p.x + p.width)}, (0, -1)),
                 ({(x, p.z + p.depth - 1) for x in range(p.x, p.x + p.width)}, (0, 1))]
        skin = set()
        for face, (dx, dz) in faces:
            if all((x + dx, z + dz) not in outside for x, z in face):
                skin |= face
        if not skin:
            result.append(p)
            continue
        pack(result, {c: p.color for c in skin}, p.bottom, p.section + " · taş dokusu",
             height=3, catalogue=("98283", "3005"))
        pack(result, {c: p.color for c in footprint - skin}, p.bottom, p.section, height=3)
    pieces[:] = result
    # The visible paving is tiled; footprints under the building stay studded.
    occupied = lower_mask() | set().union(*(disc(43, cz, 3.4) for cz in (15, 24, 33)))
    occupied |= set().union(*(rectangle(x, z, x + 4, z + 4) for x in (7, 37) for z in (7, 37)))
    occupied |= rectangle(16, 3, 32, 5) | rectangle(17, 0, 31, 3)
    occupied |= rectangle(3, 16, 4, 32) | rectangle(42, 42, 46, 46)
    floor = rectangle(2, 2, 46, 46) - occupied
    pack(pieces, {c: 19 if 20 <= c[0] < 28 and c[1] < 5 else 28 for c in floor},
         3, "Avlu · düz taş kaplama", catalogue=("2431", "3068b", "3069b", "3070b"))
    # Grilles suggest lead roof ribs on the two long aisle ridges.
    for x in (12, 34):
        for z in (19, 21, 23, 25, 27):
            pieces.append(Piece("2412b", 71, x, 25, z, section="Yan nef · kurşun çatı detayları"))


def build(optimize=True):
    pieces = []
    plinth(pieces)
    lower_body(pieces)
    upper_body(pieces)
    domes(pieces)
    southern_annexes(pieces)
    minarets(pieces)
    architecture_modules(pieces)
    entrance_portico(pieces)
    courtyard_modules(pieces)
    surface_details(pieces)
    if optimize:
        from scripts.optimize_model import optimize_interior
        pieces = optimize_interior(pieces)
    return sorted(pieces, key=lambda p: (p.bottom, (2 if p.mount == "side" else 1 if p.part in ("15068", "11477") else 0), p.z, p.x, p.part))


if __name__ == "__main__":
    from scripts.export_model import deliver
    from scripts.optimize_model import write_report
    pieces = build()
    deliver(pieces)
    write_report(build(optimize=False), pieces, 'dist')
