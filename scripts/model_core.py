"""Stud-grid placements and conservative contact checks for ordinary LEGO parts.

Coordinates: x/z are first stud centres; bottom/height are in plate units.
Upright placements and a bounded set of side-mounted tiles are supported.
Round bodies use enclosing rectangles. This is not a physical strength solver.
"""
from dataclasses import dataclass
from collections import defaultdict
from math import isfinite


@dataclass(frozen=True)
class Part:
    width: int
    depth: int
    height: int
    name: str
    studs: bool = True
    stud_height_ldu: int = 4
    # Masks use rotation-0 grid centres. None means the full rectangle.
    top_stud_mask: tuple[tuple[float, float], ...] | None = None
    bottom_stud_mask: tuple[tuple[float, float], ...] | None = None
    # Native LDraw body-top centre and rotation into the rotation-0 grid.
    # None defaults to long native X -> grid Z for nonsquare ordinary parts.
    native_origin: tuple[float, float, float] = (0, 0, 0)
    native_rotation: int | None = None
    # Optional stepped surfaces: (local x, local z, plate offset/height).
    top_stud_height_offsets: tuple[tuple[float, float, int], ...] = ()
    body_height_mask: tuple[tuple[int, int, int], ...] | None = None
    bottom_stud_height_offsets: tuple[tuple[float, float, int], ...] = ()
    body_bottom_mask: tuple[tuple[int, int, int], ...] = ()


PARTS = {
    "3001": Part(2, 4, 3, "Brick 2 x 4"),
    "3002": Part(2, 3, 3, "Brick 2 x 3"),
    "3003": Part(2, 2, 3, "Brick 2 x 2"),
    "3004": Part(1, 2, 3, "Brick 1 x 2"),
    "3005": Part(1, 1, 3, "Brick 1 x 1"),
    "3009": Part(1, 6, 3, "Brick 1 x 6"),
    "3010": Part(1, 4, 3, "Brick 1 x 4"),
    "3020": Part(2, 4, 1, "Plate 2 x 4"),
    "3021": Part(2, 3, 1, "Plate 2 x 3"),
    "3022": Part(2, 2, 1, "Plate 2 x 2"),
    "3023": Part(1, 2, 1, "Plate 1 x 2"),
    "3024": Part(1, 1, 1, "Plate 1 x 1"),
    "3031": Part(4, 4, 1, "Plate 4 x 4"),
    "60474": Part(4, 4, 1, "Plate Round 4 x 4 with Hole",
                  top_stud_mask=tuple((x,z) for x in range(4) for z in range(4) if (x,z) not in ((0,0),(0,3),(3,0),(3,3))),
                  bottom_stud_mask=tuple((x,z) for x in range(4) for z in range(4) if (x,z) not in ((0,0),(0,3),(3,0),(3,3)))),
    "3034": Part(2, 8, 1, "Plate 2 x 8"),
    "3035": Part(4, 8, 1, "Plate 4 x 8"),
    "3068b": Part(2, 2, 1, "Tile 2 x 2 with Groove", False, 0),
    "3069b": Part(1, 2, 1, "Tile 1 x 2 with Groove", False, 0),
    "2431": Part(1, 4, 1, "Tile 1 x 4", False, 0),
    "3941": Part(2, 2, 3, "Brick Round 2 x 2 with Axle Hole"),
    # Official cone/jumper geometry has one centre stud, not four corner studs.
    "3942c": Part(2, 2, 6, "Cone 2 x 2 x 2 with Completely Open Stud", top_stud_mask=((.5, .5),)),
    "4589": Part(1, 1, 3, "Cone 1 x 1"),
    "87580": Part(2, 2, 1, "Plate 2 x 2 with One Centre Stud", top_stud_mask=((.5, .5),)),
    "3062b": Part(1, 1, 3, "Brick Round 1 x 1 Open Stud"),
    "4073": Part(1, 1, 1, "Plate Round 1 x 1"),
    # Official LDraw 15068/11477: body y=-16..0; low edge at native -Z.
    # Official s/15068s01 and s/11477s01: high-row walls stop at y=-8,
    # allowing one plate below that row; its stud cavities reach y=-12.
    "15068": Part(2, 2, 2, "Slope Curved 2 x 2", False, 0,
                  native_origin=(0, -16, 0), native_rotation=0,
                  bottom_stud_height_offsets=((0, 1, 1), (1, 1, 1)),
                  body_bottom_mask=((0, 1, 1), (1, 1, 1))),
    "11477": Part(1, 2, 2, "Slope Curved 1 x 2", False, 0,
                  native_origin=(0, -16, 0), native_rotation=0,
                  bottom_stud_height_offsets=((0, 1, 1),),
                  body_bottom_mask=((0, 1, 1),)),
    # 54200 native crest is rounded to y=-15.6; use nominal16LDU envelope
    # and native bottom y=0 so the attachment plane remains exact.
    "54200": Part(1, 1, 2, "Slope 30 1 x 1 x 2/3", False, 0,
                  native_origin=(0, -16, 0), native_rotation=0),
    # 3039 high studded row is native z=0; body bounds z=-30..10.
    "3039": Part(2, 2, 3, "Slope 45 2 x 2", top_stud_mask=((0, 1), (1, 1)),
                 native_origin=(0, 0, -10), native_rotation=0),
    "3040b": Part(1, 2, 3, "Slope 45 2 x 1", top_stud_mask=((0, 1),),
                   native_origin=(0, 0, -10), native_rotation=0),
    "3659": Part(1, 4, 3, "Arch 1 x 4", bottom_stud_mask=((0, 0), (0, 3))),
    # Official 6108 outer columns are 3/6 plates tall, with central eight at9.
    # The interior arch void remains a conservative solid collision envelope.
    "6108": Part(1, 12, 9, "Arch 1 x 12 x 3",
                 bottom_stud_mask=((0, 0), (0, 11)),
                 top_stud_height_offsets=((0, 0, -6), (0, 1, -3), (0, 10, -3), (0, 11, -6)),
                 body_height_mask=tuple((0, z, h) for z, h in
                                        enumerate((3, 6, 9, 9, 9, 9, 9, 9, 9, 9, 6, 3)))),
    "98283": Part(1, 2, 3, "Brick 1 x 2 with Masonry Profile"),
    "2412b": Part(1, 2, 1, "Tile 1 x 2 Grille with Bottom Groove", False, 0),
    "98138": Part(1, 1, 1, "Tile Round 1 x 1 with Groove", False, 0),
    "87087": Part(1, 1, 3, "Brick 1 x 1 with Stud on One Side"),
    "32952": Part(1, 1, 5, "Brick 1 x 1 x 1 2/3 with Studs on One Side"),
    # Official sources: 49308 has a centred 2x2 socket pattern inside a3x3
    # envelope; dishes attach only by their central socket, not their rims.
    "49308": Part(3, 3, 4, "Cylinder 3 x 3 with Dome Top and Open Stud",
                  top_stud_mask=((1, 1),),
                  bottom_stud_mask=((.5, .5), (.5, 1.5), (1.5, .5), (1.5, 1.5))),
    "3960": Part(4, 4, 2, "Dish 4 x 4 Inverted",
                 top_stud_mask=((1.5, 1.5),), bottom_stud_mask=((1.5, 1.5),)),
    "4740": Part(2, 2, 1, "Dish 2 x 2 Inverted",
                 top_stud_mask=((.5, .5),), bottom_stud_mask=((.5, .5),)),
    "4032": Part(2, 2, 1, "Plate Round 2 x 2 with Axle Hole"),
    "30055": Part(1, 4, 6, "Fence Spindled 1 x 4 x 2", top_stud_mask=((0, 0), (0, 3))),
    "60592": Part(1, 2, 6, "Window Frame 1 x 2 x 2 Flat Front"),
    "2877": Part(1, 2, 3, "Brick 1 x 2 with Grille Profile"),
    "43888": Part(1, 1, 18, "Brick Round 1 x 1 x 6 with Square Base"),
    "3633": Part(1, 4, 3, "Fence Lattice 1 x 4 x 1", False, 0),
    "30136": Part(1, 2, 3, "Brick 1 x 2 Log"),
    "3070b": Part(1, 1, 1, "Tile 1 x 1 with Groove", False, 0),
    "3794b": Part(1, 2, 1, "Plate 1 x 2 with Groove and One Centre Stud",
                  top_stud_mask=((0, .5),)),
}

CARDINAL_MATRICES = {
    0: (1, 0, 0, 0, 1, 0, 0, 0, 1),
    90: (0, 0, -1, 0, 1, 0, 1, 0, 0),
    180: (-1, 0, 0, 0, 1, 0, 0, 0, -1),
    270: (0, 0, 1, 0, 1, 0, -1, 0, 0),
}


def rotate_vector(matrix, vector):
    return tuple(sum(matrix[3*i+j]*vector[j] for j in range(3)) for i in range(3))


def transform_point(position, matrix, point):
    return tuple(a+b for a, b in zip(position, rotate_vector(matrix, point)))

# LDraw and BrickLink use different colour IDs.
COLORS = {
    0: {"name": "Black", "tr": "Siyah", "bricklink": 11, "hex": "1B2A34"},
    19: {"name": "Tan", "tr": "Bej", "bricklink": 2, "hex": "D7BA8C"},
    28: {"name": "Dark Tan", "tr": "Koyu bej", "bricklink": 69, "hex": "897D62"},
    70: {"name": "Reddish Brown", "tr": "Kızıl kahverengi", "bricklink": 88, "hex": "5F3109"},
    71: {"name": "Light Bluish Gray", "tr": "Açık mavimsi gri", "bricklink": 86, "hex": "969696"},
    72: {"name": "Dark Bluish Gray", "tr": "Koyu mavimsi gri", "bricklink": 85, "hex": "646464"},
    84: {"name": "Medium Nougat", "tr": "Orta nugat", "bricklink": 150, "hex": "AA7D55"},
    484: {"name": "Dark Orange", "tr": "Koyu turuncu", "bricklink": 68, "hex": "91501C"},
    297: {"name": "Pearl Gold", "tr": "İnci altın", "bricklink": 115, "hex": "AA7F2E"},
}

# BrickLink consolidated the grooved tile variant; LDraw retains its filename.
BRICKLINK_PART_IDS = {"3068b": "3068", "3069b": "3069", "3062b": "3062", "3070b": "3070", "3040b": "3040"}


@dataclass(frozen=True)
class Piece:
    part: str
    color: int
    x: int | float
    bottom: int
    z: int | float
    rotation: int = 0
    section: str = "Model"
    mount: str = "up"
    host_part: str = "87087"

    def __post_init__(self):
        if self.part not in PARTS or self.color not in COLORS:
            raise ValueError(f"Unknown part/colour: {self.part}/{self.color}")
        if self.rotation not in (0, 90, 180, 270):
            raise ValueError("Only upright cardinal rotations are supported")
        if self.mount not in ("up", "side"):
            raise ValueError("Only upright and predefined side-tile mounts are supported")
        if self.mount == "side" and (self.part not in ("98138", "2412b")
                                      or self.host_part not in ("87087", "32952")):
            raise ValueError("Side mounts require an approved tile and side-stud host")
        if any(not isinstance(v, (int, float)) or not isfinite(v) or v % .5 != 0
               for v in (self.x, self.z)):
            raise ValueError("Horizontal placements must align with the half-stud grid")
        if not isinstance(self.bottom, int):
            raise ValueError("Bottom must align with the integer plate grid")
        if self.bottom < 0:
            raise ValueError("Parts cannot extend below the table")

    @property
    def width(self):
        return PARTS[self.part].depth if self.rotation % 180 else PARTS[self.part].width

    @property
    def depth(self):
        return PARTS[self.part].width if self.rotation % 180 else PARTS[self.part].depth

    @property
    def top(self):
        return self.bottom + PARTS[self.part].height

    def footprint(self):
        """Full rectangular grid positions, including half-stud offsets."""
        return {(self.x + dx, self.z + dz) for dx in range(self.width)
                for dz in range(self.depth)}

    def _rotate_mask(self, mask):
        if mask is None:
            return self.footprint()
        width, depth = PARTS[self.part].width, PARTS[self.part].depth
        result = set()
        for dx, dz in mask:
            if self.rotation == 90:
                dx, dz = depth - 1 - dz, dx
            elif self.rotation == 180:
                dx, dz = width - 1 - dx, depth - 1 - dz
            elif self.rotation == 270:
                dx, dz = dz, width - 1 - dx
            result.add((self.x + dx, self.z + dz))
        return result

    def top_studs(self):
        """Stud centres on the highest body plane; use top_contacts for ledges."""
        return {(x, z) for x, y, z in self.top_contacts() if y == self.top}

    def top_contacts(self):
        """All actual top studs as (x, y, z), with y in plate units."""
        part = PARTS[self.part]
        if self.mount != "up" or not part.studs:
            return set()
        offsets = {}
        for dx, dz, offset in part.top_stud_height_offsets:
            for cell in self._rotate_mask(((dx, dz),)):
                offsets[cell] = offset
        return {(x, self.top + offsets.get((x, z), 0), z)
                for x, z in self._rotate_mask(part.top_stud_mask)}

    def body_columns(self):
        """Conservative collision columns as (x, z, height in plates)."""
        part = PARTS[self.part]
        if self.mount != "up":
            return set()
        if part.body_height_mask is None:
            return {(x, z, part.height) for x, z in self.footprint()}
        return {(x, z, height) for dx, dz, height in part.body_height_mask
                for x, z in self._rotate_mask(((dx, dz),))}

    def bottom_studs(self):
        """Attachment centres at the lowest body plane, excluding arch voids."""
        return {(x, z) for x, y, z in self.bottom_contacts() if y == self.bottom}

    def bottom_contacts(self):
        """All bottom attachments as (x, y, z), including raised undersides."""
        part = PARTS[self.part]
        if self.mount != "up":
            return set()
        offsets = {}
        for dx, dz, offset in part.bottom_stud_height_offsets:
            for cell in self._rotate_mask(((dx, dz),)):
                offsets[cell] = offset
        return {(x, self.bottom + offsets.get((x, z), 0), z)
                for x, z in self._rotate_mask(part.bottom_stud_mask)}

    def body_spans(self):
        """Collision columns as (x, z, bottom offset, top offset), in plates."""
        starts = {}
        for dx, dz, offset in PARTS[self.part].body_bottom_mask:
            for cell in self._rotate_mask(((dx, dz),)):
                starts[cell] = offset
        return {(x, z, starts.get((x, z), 0), height)
                for x, z, height in self.body_columns()}

    def stud_ports_ldu(self):
        """Male ports: (X,Y,Z,nX,nY,nZ), uncentered LDraw coordinates."""
        ports = {(20*x, -8*y, 20*z, 0, -1, 0) for x, y, z in self.top_contacts()}
        if self.mount == "up" and self.part in ("87087", "32952"):
            position, matrix = ldraw_transform(self, center=0)
            for y in ((10,) if self.part == "87087" else (10, 30)):
                ports.add(transform_point(position, matrix, (0, y, -10))
                          + rotate_vector(matrix, (0, 0, -1)))
        return ports

    def socket_ports_ldu(self):
        """Female ports use the opposing outward normal at the mating plane."""
        if self.mount == "up":
            return {(20*x, -8*y, 20*z, 0, 1, 0) for x, y, z in self.bottom_contacts()}
        position, matrix = ldraw_transform(self, center=0)
        centers = ((0, 8, 0),) if self.part == "98138" else ((-10, 8, 0), (10, 8, 0))
        return {transform_point(position, matrix, c) + rotate_vector(matrix, (0, 1, 0))
                for c in centers}

    def body_boxes_ldu(self):
        """Actual side-tile boxes or upright conservative stud-column boxes."""
        if self.mount == "up":
            return [((20*x-10, 20*x+10), (-8*(self.bottom+end), -8*(self.bottom+start)),
                     (20*z-10, 20*z+10)) for x, z, start, end in self.body_spans()]
        from itertools import product
        position, matrix = ldraw_transform(self, center=0)
        extents = ((-10, 10), (0, 8), (-10, 10)) if self.part == "98138" else ((-20, 20), (0, 8), (-10, 10))
        points = [transform_point(position, matrix, c) for c in product(*extents)]
        return [tuple((min(c[a] for c in points), max(c[a] for c in points)) for a in range(3))]

    def plan_bounds(self):
        """Projected (x0,z0,x1,z1) in grid-cell units for guide diagrams."""
        boxes = self.body_boxes_ldu()
        return ((min(b[0][0] for b in boxes)+10)/20,
                (min(b[2][0] for b in boxes)+10)/20,
                (max(b[0][1] for b in boxes)+10)/20,
                (max(b[2][1] for b in boxes)+10)/20)


def ldraw_transform(piece, center=23.5):
    """Native-to-model rigid pose; side anchors identify the host brick grid."""
    if piece.mount == "side":
        yaw = CARDINAL_MATRICES[piece.rotation]
        if piece.part == "98138":
            local_matrix, local_position = (1, 0, 0, 0, 0, -1, 0, 1, 0), (0, 10, -18)
        else:
            local_matrix, local_position = (0, 0, 1, 1, 0, 0, 0, 1, 0), (0, 20, -18)
        matrix = tuple(sum(yaw[3*i+k]*local_matrix[3*k+j] for k in range(3))
                       for i in range(3) for j in range(3))
        host_position = ((piece.x-center)*20, -8*(piece.bottom+PARTS[piece.host_part].height),
                         (piece.z-center)*20)
        return transform_point(host_position, yaw, local_position), matrix
    x = (piece.x + (piece.width - 1) / 2 - center) * 20
    z = (piece.z + (piece.depth - 1) / 2 - center) * 20
    # Grid sizes follow the name (short x long); official basic LDraw parts
    # have the long axis on X. Convert conventions at the export boundary.
    part = PARTS[piece.part]
    native_rotation = part.native_rotation
    if native_rotation is None:
        native_rotation = 270 if part.width != part.depth else 0
    angle = (piece.rotation + native_rotation) % 360
    matrix = CARDINAL_MATRICES[angle]
    origin = part.native_origin
    x -= matrix[0]*origin[0] + matrix[2]*origin[2]
    z -= matrix[6]*origin[0] + matrix[8]*origin[2]
    y = -piece.top * 8 - origin[1]
    return (x, y, z), matrix


def ldraw_line(piece, center=23.5):
    (x, y, z), matrix = ldraw_transform(piece, center)
    matrix_text = " ".join(map(str, matrix))
    return f"1 {piece.color} {x:g} {y:g} {z:g} {matrix_text} {piece.part}.dat"


def validate(pieces):
    bodies = {}
    ports = defaultdict(set)
    collisions = set()
    parent = list(range(len(pieces)))

    def root(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i, piece in enumerate(pieces):
        # Half-stud voxels catch offset overlaps; round/cone bodies retain
        # conservative rectangular collision envelopes, separate from studs.
        for cx, cz, start, height in piece.body_spans():
            for x in range(int(cx * 2), int(cx * 2) + 2):
                for z in range(int(cz * 2), int(cz * 2) + 2):
                    for y in range(piece.bottom + start, piece.bottom + height):
                        key = x, y, z
                        if key in bodies:
                            collisions.add((bodies[key], i))
                        bodies[key] = i
        for port in piece.stud_ports_ldu():
            ports[port].add(i)

    # Side tiles occupy plate-thick boxes at non-plate-aligned heights.
    # Compare exact bounds with upright columns instead of rounding to voxels.
    boxes = [p.body_boxes_ldu() for p in pieces]
    bounds = [tuple((min(b[a][0] for b in row), max(b[a][1] for b in row))
                    for a in range(3)) for row in boxes]

    def overlaps(a, b):
        return all(a[k][0] < b[k][1] and b[k][0] < a[k][1] for k in range(3))

    for i, piece in enumerate(pieces):
        if piece.mount != "side":
            continue
        for j, other in enumerate(pieces):
            if i == j or (other.mount == "side" and j < i):
                continue
            if overlaps(bounds[i], bounds[j]) and any(overlaps(a, b) for a in boxes[i] for b in boxes[j]):
                collisions.add(tuple(sorted((i, j))))

    unsupported = []
    support_counts = []
    edges = set()
    for i, piece in enumerate(pieces):
        contacts = []
        for port in piece.socket_ports_ldu():
            match = port[:3] + tuple(-n for n in port[3:])
            contacts.extend((port, j) for j in ports.get(match, ()) if j != i)
        if (piece.bottom or piece.mount == "side") and not contacts:
            unsupported.append(i)
        support_counts.append(len(contacts))
        for cell, j in contacts:
            parent[root(i)] = root(j)
            edges.add(tuple(sorted((i, j))))

    groups = defaultdict(list)
    for i in range(len(pieces)):
        groups[root(i)].append(i)
    out_of_base = [i for i, b in enumerate(bounds)
                   if b[0][0] < -10 or b[2][0] < -10 or b[0][1] > 950
                   or b[2][1] > 950 or b[1][1] > 0]
    return {
        "piece_count": len(pieces),
        "collisions": sorted(collisions),
        "unsupported": unsupported,
        "connected_components": len(groups),
        "component_sizes": sorted(map(len, groups.values()), reverse=True),
        "connection_edges": len(edges),
        "out_of_base": out_of_base,
        "minimum_support_studs_above_base": min(
            (support_counts[i] for i, p in enumerate(pieces) if p.bottom or p.mount == "side"), default=0),
        "single_stud_supported_piece_count": sum(
            count == 1 for i, count in enumerate(support_counts) if pieces[i].bottom or pieces[i].mount == "side"),
        "body_height_cm": max((-b[1][0] for b in bounds), default=0) * .04,
        "height_cm": max((-bounds[i][1][0] + (PARTS[p.part].stud_height_ldu if p.mount == "up" else 0)
                          for i, p in enumerate(pieces)), default=0) * .04,
        "method": "Upright stud-column envelopes, exact side-tile bounds and directional LDraw-unit contacts; round parts use conservative rectangular envelopes.",
        "physical_build_tested": False,
        "limitations": "No clutch-force, bending, torsion, manufacturing-tolerance or transport-load simulation. Arch voids retain conservative body envelopes; curved-slope stepped undersides are modeled by stud columns.",
    }
