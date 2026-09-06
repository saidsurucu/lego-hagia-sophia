"""End-to-end checks catch missing components, illegal placements and BOM drift."""
import collections
import csv
import io
import unittest
import xml.etree.ElementTree as ET

try:
    from scripts.build_model import build
    from scripts.export_model import ldr_text, csv_text, wanted_xml
    from scripts.model_core import COLORS, validate
except ImportError:
    build = None


class DeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pieces = build() if build else []

    def test_model_has_supported_connected_real_parts(self):
        self.assertTrue(self.pieces, "Ayasofya generator must produce a model")
        report = validate(self.pieces)
        self.assertEqual(report["collisions"], [])
        self.assertEqual(report["unsupported"], [])
        self.assertEqual(report["connected_components"], 1)
        self.assertEqual(report["out_of_base"], [])

    def test_model_has_four_separate_minarets_and_both_half_domes(self):
        self.assertTrue(self.pieces, "Ayasofya generator must produce a model")
        minaret_tips = [p for p in self.pieces if p.part == "4589" and p.section.startswith("Minare · ")]
        positions = {(p.x, p.z) for p in minaret_tips}
        self.assertEqual(len(minaret_tips), 4)
        self.assertEqual(len(positions), 4)
        self.assertEqual(len({x for x, _ in positions}), 2)
        self.assertEqual(len({z for _, z in positions}), 2)
        for tip in minaret_tips:
            tower = " · ".join(tip.section.split(" · ")[:2])
            self.assertEqual(tip.top, max(p.top for p in self.pieces
                                         if p.section == tower or p.section.startswith(tower + " · ")))
        for section in ("Ana kubbe", "Batı yarım kubbe", "Doğu yarım kubbe"):
            self.assertTrue(any(p.section == section or p.section.startswith(section + " · ")
                                for p in self.pieces), section)

    def test_exports_match_actual_ldr_part_color_counts(self):
        self.assertTrue(self.pieces, "Ayasofya generator must produce a model")
        counts = collections.Counter()
        for line in ldr_text(self.pieces).splitlines():
            f = line.split()
            if f and f[0] == "1":
                self.assertEqual(len(f), 15)
                part = f[14].removesuffix(".dat")
                counts[{"3068b": "3068", "3069b": "3069", "3062b": "3062", "3070b": "3070", "3040b": "3040"}.get(part, part), COLORS[int(f[1])]["bricklink"]] += 1
        rows = list(csv.DictReader(io.StringIO(csv_text(self.pieces))))
        self.assertEqual({(r.get("bricklink_part_id", r["part_id"]), int(r["bricklink_color_id"])): int(r["quantity"])
                          for r in rows}, dict(counts))
        xml = ET.fromstring(wanted_xml(self.pieces))
        self.assertEqual({(i.findtext("ITEMID"), int(i.findtext("COLOR"))): int(i.findtext("MINQTY"))
                          for i in xml}, dict(counts))

    def test_build_sequence_places_supports_before_upper_parts(self):
        self.assertTrue(self.pieces, "Ayasofya generator must produce a model")
        surfaces = set()
        for p in self.pieces:
            matching = {port[:3] + tuple(-n for n in port[3:]) for port in p.socket_ports_ldu()}
            if p.bottom or p.mount == "side":
                self.assertTrue(matching & surfaces, p)
            if p.part in ("15068", "11477"):
                self.assertTrue(matching <= surfaces,
                                f"Every curved-cap support, including raised-row infill, must precede {p}")
            surfaces.update(p.stud_ports_ldu())

    def test_ldr_preserves_model_placement_order(self):
        from scripts.model_core import ldraw_line
        # The mesh audit pairs model.json and LDR records positionally. A
        # different export sort also risks placing caps before their infill.
        records = [line for line in ldr_text(self.pieces).splitlines() if line.startswith("1 ")]
        self.assertEqual(records, [ldraw_line(p) for p in self.pieces])


if __name__ == "__main__":
    unittest.main()
