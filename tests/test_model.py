"""Fixtures catch illegal geometry/contact and exporter coordinate regressions."""
import unittest

try:
    from scripts.model_core import Piece, validate, ldraw_line
except ImportError:
    Piece = validate = ldraw_line = None


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Piece, "Placement/validation engine must exist")

    def test_intersecting_bodies_rejected(self):
        pieces = [Piece("3003", 19, 0, 0, 0), Piece("3003", 19, 1, 1, 1)]
        self.assertGreater(len(validate(pieces)["collisions"]), 0)

    def test_side_touch_does_not_count_as_connection(self):
        pieces = [Piece("3003", 19, 0, 0, 0), Piece("3003", 19, 2, 0, 0)]
        self.assertEqual(validate(pieces)["connected_components"], 2)

    def test_bridging_plate_connects_base_bricks(self):
        pieces = [Piece("3003", 19, 0, 0, 0), Piece("3003", 19, 2, 0, 0),
                  Piece("3020", 19, 0, 3, 0, 90)]
        report = validate(pieces)
        self.assertEqual(report["connected_components"], 1)
        self.assertEqual(report["unsupported"], [])
        self.assertEqual(report["collisions"], [])

    def test_floating_piece_rejected(self):
        pieces = [Piece("3003", 19, 0, 0, 0), Piece("3003", 19, 0, 4, 0)]
        self.assertEqual(validate(pieces)["unsupported"], [1])

    def test_tile_cannot_supply_top_stud_connection(self):
        pieces = [Piece("3068b", 0, 0, 0, 0), Piece("3003", 19, 0, 1, 0)]
        self.assertEqual(validate(pieces)["unsupported"], [1])

    def test_external_height_includes_cone_tip_stud(self):
        # Official 3942c body is48LDU and tip stud adds4LDU:52*.4mm.
        self.assertAlmostEqual(validate([Piece("3942c", 72, 0, 0, 0)])["height_cm"], 2.08)

    def test_center_stud_accepts_half_stud_cap(self):
        for part, height in (("3942c", 6), ("87580", 1)):
            with self.subTest(part=part):
                base = Piece(part, 71, 2, 0, 4)
                self.assertEqual(base.top_studs(), {(2.5, 4.5)})
                report = validate([base, Piece("4589", 297, 2.5, height, 4.5)])
                self.assertEqual(report["unsupported"], [])
                self.assertEqual(report["collisions"], [])
                self.assertEqual(report["connected_components"], 1)

    def test_cone_corner_has_no_stud(self):
        report = validate([Piece("3942c", 71, 0, 0, 0),
                           Piece("4073", 297, 0, 6, 0)])
        self.assertEqual(report["unsupported"], [1])
        self.assertEqual(report["connected_components"], 2)

    def test_half_stud_body_overlap_rejected(self):
        report = validate([Piece("3005", 19, 0, 0, 0),
                           Piece("3005", 19, .5, 0, .5)])
        self.assertEqual(report["collisions"], [(0, 1)])

    def test_half_stud_side_touch_is_not_collision_or_connection(self):
        report = validate([Piece("3005", 19, .5, 0, .5),
                           Piece("3005", 19, 1.5, 0, .5)])
        self.assertEqual(report["collisions"], [])
        self.assertEqual(report["connected_components"], 2)

    def test_half_stud_offset_requires_exact_stud_contact(self):
        report = validate([Piece("3003", 19, 0, 0, 0),
                           Piece("3005", 19, .5, 3, .5)])
        self.assertEqual(report["unsupported"], [1])

    def test_invalid_coordinate_grid_rejected(self):
        for value in (.25, float("inf"), float("nan"), "0"):
            for axis in ("x", "z"):
                with self.subTest(value=value, axis=axis), self.assertRaises(ValueError):
                    Piece("3005", 19, **{"x": 0, "bottom": 0, "z": 0, axis: value})
        with self.assertRaises(ValueError):
            Piece("3005", 19, 0, .5, 0)

    def test_ordinary_and_tile_top_studs(self):
        ordinary = Piece("3023", 19, .5, 0, 1.5, 90)
        self.assertEqual(ordinary.footprint(), {(.5, 1.5), (1.5, 1.5)})
        self.assertEqual(ordinary.top_studs(), ordinary.footprint())
        self.assertEqual(Piece("3068b", 19, 0, 0, 0).top_studs(), set())

    def test_cardinal_rotations_preserve_dimensions_and_rigid_transform(self):
        expected = {
            0: (2, 4, [0, 0, 1, 0, 1, 0, -1, 0, 0]),
            90: (4, 2, [1, 0, 0, 0, 1, 0, 0, 0, 1]),
            180: (2, 4, [0, 0, -1, 0, 1, 0, 1, 0, 0]),
            270: (4, 2, [-1, 0, 0, 0, 1, 0, 0, 0, -1]),
        }
        for rotation, (width, depth, matrix) in expected.items():
            with self.subTest(rotation=rotation):
                try:
                    piece = Piece("3001", 19, 0, 0, 0, rotation)
                except ValueError as exc:
                    self.fail(f"Cardinal rotation must be accepted: {exc}")
                self.assertEqual((piece.width, piece.depth), (width, depth))
                self.assertEqual(list(map(int, ldraw_line(piece).split()[5:14])), matrix)

    def test_non_cardinal_rotation_rejected(self):
        for angle in (-90, 45, 360):
            with self.subTest(angle=angle), self.assertRaises(ValueError):
                Piece("3001", 19, 0, 0, 0, angle)

    def test_new_part_body_heights_and_top_studs(self):
        from scripts.model_core import PARTS
        for part, height, studs in (("15068", 2, 0), ("11477", 2, 0),
                                    ("3039", 3, 2), ("3040b", 3, 1), ("3659", 3, 4),
                                    ("98283", 3, 2), ("2412b", 1, 0)):
            with self.subTest(part=part):
                self.assertIn(part, PARTS)
                p = Piece(part, 71, 0, 0, 0)
                self.assertEqual(p.top, height)
                self.assertEqual(len(p.top_studs()), studs)

    def test_slope_high_row_studs_rotate_with_body(self):
        from scripts.model_core import PARTS
        self.assertIn("3039", PARTS)
        expected = {0: {(0, 1), (1, 1)}, 90: {(0, 0), (0, 1)},
                    180: {(0, 0), (1, 0)}, 270: {(1, 0), (1, 1)}}
        for angle, studs in expected.items():
            p = Piece("3039", 71, 0, 0, 0, angle)
            self.assertEqual(p.top_studs(), studs)
            f = ldraw_line(p, center=0).split()
            pos, m = list(map(float, f[2:5])), list(map(float, f[5:14]))
            # Official 3039 high studs are native (x=+/-10,y=0,z=0),
            # while its body centre is z=-10, not the file origin.
            actual = {(round((pos[0] + m[0]*x)/20, 6),
                       round((pos[2] + m[6]*x)/20, 6)) for x in (-10, 10)}
            self.assertEqual(actual, studs)

    def test_narrow_steep_slope_native_high_stud_and_supports(self):
        for angle in (0, 90, 180, 270):
            p = Piece("3040b", 71, 4, 3, 6, angle)
            f = ldraw_line(p, center=0).split()
            # The official part's single upper stud is at native (0,0,0).
            pos = tuple(map(float, f[2:5]))
            self.assertEqual(p.top_studs(), {(pos[0]/20, pos[2]/20)})
            self.assertEqual(p.bottom_studs(), p.footprint())
            self.assertEqual(len(p.bottom_studs()), 2)

    def test_arch_uses_only_bottom_end_connections(self):
        from scripts.model_core import PARTS
        self.assertIn("3659", PARTS)
        for angle, ends in ((0, {(0, 0), (0, 3)}), (90, {(0, 0), (3, 0)}),
                            (180, {(0, 0), (0, 3)}), (270, {(0, 0), (3, 0)})):
            arch = Piece("3659", 19, 0, 1, 0, angle)
            self.assertEqual(arch.bottom_studs(), ends)
            supports = [Piece("3024", 19, x, 0, z) for x, z in sorted(ends)]
            report = validate(supports + [arch])
            self.assertEqual(report["unsupported"], [])
            self.assertEqual(report["connected_components"], 1)
        report = validate([Piece("3024", 19, 0, 0, 1),
                           Piece("3659", 19, 0, 1, 0)])
        self.assertEqual(report["unsupported"], [1])

    def test_curved_slopes_contact_low_row_only_at_bottom(self):
        from scripts.model_core import PARTS
        for part, width in (("15068", 2), ("11477", 1)):
            self.assertIn(part, PARTS)
            p = Piece(part, 71, 0, 1, 0)
            self.assertEqual(p.bottom_studs(), {(x, 0) for x in range(width)})
            self.assertEqual(validate([Piece("3024", 19, 0, 0, 1), p])["unsupported"], [1])
            self.assertEqual(validate([Piece("3024", 19, 0, 0, 0), p])["unsupported"], [])

    def test_curved_slopes_native_origin_and_direction(self):
        from scripts.model_core import PARTS
        for part, width in (("15068", 2), ("11477", 1)):
            self.assertIn(part, PARTS)
            for angle, high_direction in ((0, (0, 1)), (90, (-1, 0)),
                                          (180, (0, -1)), (270, (1, 0))):
                p = Piece(part, 71, 2, 3, 4, angle)
                f = ldraw_line(p, center=0).split()
                pos, m = list(map(float, f[2:5])), list(map(float, f[5:14]))
                # Official curved slopes have body y=-16..0; native z=+20 is high.
                self.assertEqual(pos[1] - 16, -p.top*8)
                self.assertEqual(pos[1], -p.bottom*8)
                self.assertEqual((m[2], m[8]), high_direction)
                self.assertEqual((p.width, p.depth), (2, width) if angle % 180 else (width, 2))

    def test_large_arch_excludes_void_bottom_and_lower_top_steps(self):
        from scripts.model_core import PARTS
        self.assertIn("6108", PARTS)
        for angle in (0, 90, 180, 270):
            arch = Piece("6108", 19, 0, 1, 0, angle)
            self.assertEqual(arch.top, 10)
            expected_ends = {(0, 0), (11, 0)} if angle % 180 else {(0, 0), (0, 11)}
            expected_tops = {(n, 0) for n in range(2, 10)} if angle % 180 else {(0, n) for n in range(2, 10)}
            self.assertEqual(arch.bottom_studs(), expected_ends)
            self.assertEqual(arch.top_studs(), expected_tops)
            supports = [Piece("3024", 19, x, 0, z) for x, z in sorted(expected_ends)]
            unsupported_cap = Piece("3024", 19, 0, 10, 0)
            report = validate(supports + [arch, unsupported_cap])
            self.assertEqual(report["unsupported"], [3])
            self.assertEqual(report["collisions"], [])

    def test_large_arch_lower_ledges_support_infill_at_actual_heights(self):
        for angle in (0, 90, 180, 270):
            arch = Piece("6108", 19, 0, 0, 0, angle)
            self.assertTrue(hasattr(arch, "top_contacts"), "Height-aware top contacts required")
            expected = {(n, h, 0) if angle % 180 else (0, h, n)
                        for n, h in enumerate((3, 6, 9, 9, 9, 9, 9, 9, 9, 9, 6, 3))}
            self.assertEqual(arch.top_contacts(), expected)
            caps = [Piece("3005", 19, x, y, z) for x, y, z in expected if y < 9]
            report = validate([arch] + caps)
            self.assertEqual(report["collisions"], [])
            self.assertEqual(report["unsupported"], [])
            self.assertEqual(report["connected_components"], 1)
            x, _, z = sorted(expected)[0]
            self.assertTrue(validate([arch, Piece("3005", 19, x, 2, z)])["collisions"])

    def test_cheese_slope_bottom_aligns_despite_rounded_crest(self):
        from scripts.model_core import PARTS
        self.assertIn("54200", PARTS)
        p = Piece("54200", 71, .5, 1, .5)
        self.assertEqual(p.top, 3)
        self.assertEqual(p.bottom_studs(), {(.5, .5)})
        self.assertEqual(p.top_contacts(), set())
        f = ldraw_line(p, center=0).split()
        self.assertEqual(float(f[3]), -8)  # Native bottom y=0 meets plate top.
        # Rounded physical crest is 15.6 LDU above bottom, inside16LDU envelope.
        self.assertAlmostEqual(float(f[3]) - 15.6, -23.6)
        report = validate([Piece("3024", 19, .5, 0, .5), p])
        self.assertEqual(report["unsupported"], [])
        self.assertEqual(report["collisions"], [])

    def test_curved_slope_raised_row_accepts_plate_infill(self):
        for part, width in (("15068", 2), ("11477", 1)):
            for angle in (0, 90, 180, 270):
                cap = Piece(part, 71, 2, 0, 2, angle)
                self.assertTrue(hasattr(cap, "bottom_contacts"), "Height-aware bottom contacts required")
                low = cap.bottom_studs()
                high = cap.footprint() - low
                self.assertEqual(cap.bottom_contacts(), {(x, 0, z) for x, z in low}
                                 | {(x, 1, z) for x, z in high})
                infill = [Piece("3024", 71, x, 0, z) for x, z in high]
                report = validate([cap] + infill)
                self.assertEqual(report["collisions"], [])
                self.assertEqual(report["connected_components"], 1)
                x, z = sorted(low)[0]
                self.assertTrue(validate([cap, Piece("3024", 71, x, 0, z)])["collisions"])

    def test_curved_slope_can_connect_through_raised_row(self):
        cap = Piece("11477", 71, 0, 1, 0)
        self.assertTrue(hasattr(cap, "bottom_contacts"), "Height-aware bottom contacts required")
        report = validate([Piece("3024", 71, 0, 0, 1),
                           Piece("3024", 71, 0, 1, 1), cap])
        self.assertEqual(report["unsupported"], [])
        self.assertEqual(report["collisions"], [])
        self.assertEqual(report["connected_components"], 1)

    def test_ldr_origin_is_top_face_and_rotation_is_rigid(self):
        # 2 x 4 brick rotated to 4 x 2, at corner (0,0), bottom=3 plates.
        fields = ldraw_line(Piece("3001", 19, 0, 3, 0, 90), center=0).split()
        self.assertEqual(fields[:5], ["1", "19", "30", "-48", "10"])
        # Official 3001.dat has its LONG axis on X, so grid rotation90
        # corresponds to the identity LDraw transform (source: outer quads).
        self.assertEqual(fields[5:14], ["1", "0", "0", "0", "1", "0", "0", "0", "1"])
        self.assertEqual(fields[14], "3001.dat")

    def test_official_plate_mesh_matches_planned_footprint(self):
        # Official 3035 outer bounds are X +/-80, Z +/-40 LDU.
        # Grid placement is short-X (4), long-Z (8), first stud at (0,0).
        f = ldraw_line(Piece("3035", 0, 0, 0, 0), center=0).split()
        pos = list(map(float, f[2:5]))
        m = list(map(float, f[5:14]))
        points = [(pos[0] + m[0]*x + m[2]*z,
                   pos[2] + m[6]*x + m[8]*z)
                  for x in (-80, 80) for z in (-40, 40)]
        self.assertEqual((min(p[0] for p in points), max(p[0] for p in points)), (-10, 70))
        self.assertEqual((min(p[1] for p in points), max(p[1] for p in points)), (-10, 150))


class SideMountTests(unittest.TestCase):
    def setUp(self):
        from scripts.model_core import PARTS
        self.assertIn("87087", PARTS, "Side-stud host must be modeled")
        self.assertIn("98138", PARTS, "Round rosette tile must be modeled")

    def test_round_tile_matches_side_port_in_all_directions(self):
        for angle in (0, 90, 180, 270):
            host = Piece("87087", 19, 3, 0, 3, angle)
            tile = Piece("98138", 19, 3, 0, 3, angle, mount="side")
            report = validate([host, tile])
            self.assertEqual(report["unsupported"], [])
            self.assertEqual(report["collisions"], [])
            self.assertEqual(report["connected_components"], 1)
            self.assertEqual(tile.bottom_contacts(), set())

    def test_side_tile_without_host_is_unsupported_even_at_ground_anchor(self):
        self.assertEqual(validate([Piece("98138", 19, 3, 0, 3, mount="side")])["unsupported"], [0])

    def test_wrong_facing_or_height_cannot_connect(self):
        host = Piece("87087", 19, 3, 0, 3)
        for tile in (Piece("98138", 19, 3, 0, 3, 180, mount="side"),
                     Piece("98138", 19, 3, 1, 3, mount="side")):
            self.assertEqual(validate([host, tile])["unsupported"], [1])

    def test_side_tile_collision_with_adjacent_wall_detected(self):
        host = Piece("87087", 19, 3, 0, 3)
        tile = Piece("98138", 19, 3, 0, 3, mount="side")
        wall = Piece("3005", 19, 3, 0, 2)
        self.assertIn((1, 2), validate([host, tile, wall])["collisions"])

    def test_round_tile_export_has_exact_side_pose_and_plan_bounds(self):
        tile = Piece("98138", 19, 2, 3, 4, mount="side")
        f = ldraw_line(tile, center=0).split()
        self.assertEqual(list(map(float, f[2:5])), [40, -38, 62])
        self.assertEqual(list(map(int, f[5:14])), [1, 0, 0, 0, 0, -1, 0, 1, 0])
        self.assertEqual(tile.plan_bounds(), (2, 3.6, 3, 4))

    def test_vertical_grille_connects_to_both_tall_host_studs(self):
        from scripts.model_core import PARTS
        self.assertIn("32952", PARTS)
        for angle in (0, 90, 180, 270):
            host = Piece("32952", 19, 3, 0, 3, angle)
            tile = Piece("2412b", 19, 3, 0, 3, angle, mount="side", host_part="32952")
            report = validate([host, tile])
            self.assertEqual(report["unsupported"], [])
            self.assertEqual(report["collisions"], [])
            self.assertEqual(report["connected_components"], 1)
            self.assertEqual(report["minimum_support_studs_above_base"], 2)

    def test_unapproved_mounts_are_rejected(self):
        with self.assertRaises(ValueError):
            Piece("3001", 19, 0, 0, 0, mount="side")
        with self.assertRaises(ValueError):
            Piece("98138", 19, 0, 0, 0, mount="upside_down")
        with self.assertRaises(ValueError):
            Piece("98138", 19, 0, 0, 0, mount="side", host_part="3005")


class ArchitecturalPartTests(unittest.TestCase):
    def test_one_by_two_jumper_has_rotating_center_stud(self):
        from scripts.model_core import PARTS
        self.assertIn("3794b", PARTS)
        for angle in (0, 90, 180, 270):
            jumper = Piece("3794b", 19, 0, 0, 0, angle)
            center = (.5, 0) if angle % 180 else (0, .5)
            self.assertEqual(jumper.top_studs(), {center})
            self.assertEqual(len(jumper.bottom_studs()), 2)
            report = validate([jumper, Piece("3070b", 19, center[0], 1, center[1])])
            self.assertEqual(report["unsupported"], [])
            self.assertEqual(report["collisions"], [])

    def test_lattice_fence_does_not_supply_top_studs(self):
        from scripts.model_core import PARTS
        self.assertIn("3633", PARTS)
        fence = Piece("3633", 19, 0, 0, 0)
        self.assertEqual(fence.top, 3)
        self.assertEqual(fence.top_contacts(), set())
        self.assertEqual(len(fence.bottom_studs()), 4)
        self.assertEqual(validate([fence, Piece("3024", 19, 0, 3, 0)])["unsupported"], [1])

    def test_verified_upright_palette_dimensions_and_contacts(self):
        from scripts.model_core import PARTS
        for part, shape, top_count, bottom_count in (
                ("49308", (3, 3, 4), 1, 4), ("3960", (4, 4, 2), 1, 1),
                ("4740", (2, 2, 1), 1, 1), ("4032", (2, 2, 1), 4, 4),
                ("30055", (1, 4, 6), 2, 4), ("60592", (1, 2, 6), 2, 2),
                ("2877", (1, 2, 3), 2, 2)):
            self.assertIn(part, PARTS)
            p = Piece(part, 19, 0, 0, 0)
            self.assertEqual((p.width, p.depth, p.top), shape)
            self.assertEqual(len(p.top_contacts()), top_count)
            self.assertEqual(len(p.bottom_contacts()), bottom_count)

    def test_dish_center_socket_does_not_invent_corner_connections(self):
        from scripts.model_core import PARTS
        for part, offset in (("3960", 1.5), ("4740", .5)):
            self.assertIn(part, PARTS)
            dish = Piece(part, 19, 0, 1, 0)
            self.assertEqual(dish.bottom_studs(), {(offset, offset)})
            self.assertEqual(validate([Piece("3024", 19, offset, 0, offset), dish])["unsupported"], [])
            self.assertEqual(validate([Piece("3024", 19, 0, 0, 0), dish])["unsupported"], [1])

    def test_three_stud_dome_has_two_by_two_bottom_and_center_top(self):
        from scripts.model_core import PARTS
        self.assertIn("49308", PARTS)
        dome = Piece("49308", 19, 0, 1, 0)
        self.assertEqual(dome.bottom_studs(), {(.5, .5), (.5, 1.5), (1.5, .5), (1.5, 1.5)})
        self.assertEqual(dome.top_studs(), {(1, 1)})
        pieces = [Piece("3022", 19, .5, 0, .5), dome,
                  Piece("4073", 297, 1, 5, 1)]
        report = validate(pieces)
        self.assertEqual(report["unsupported"], [])
        self.assertEqual(report["collisions"], [])
        self.assertEqual(report["connected_components"], 1)


if __name__ == "__main__":
    unittest.main()
