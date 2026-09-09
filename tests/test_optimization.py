"""Cost reduction must preserve the exterior and exact occupied volume."""
import unittest
from collections import Counter

from scripts.build_model import build
from scripts.model_core import PARTS


def material(pieces):
    return Counter((x, y, z) for p in pieces if p.mount == 'up'
                   for x, z in p.footprint() for y in range(p.bottom, p.top))


class OptimizationTests(unittest.TestCase):
    def test_opening_exposes_previously_hidden_center(self):
        from scripts.model_core import Piece
        from scripts.optimize_model import hidden_indices
        cube = [Piece('3024', 71, x, y, z)
                for x in range(3) for y in range(3) for z in range(3)]
        self.assertEqual(hidden_indices(cube), {13})
        # Remove the front cell facing the centre: it must no longer be changed.
        opened = [p for p in cube if (p.x, p.bottom, p.z) != (1, 1, 0)]
        self.assertEqual(hidden_indices(opened), set())

    def test_reduces_parts_without_changing_material_or_special_parts(self):
        original = build(optimize=False)
        optimized = build()
        self.assertLess(len(optimized), len(original) - 100)
        self.assertEqual(material(original), material(optimized))
        special = lambda ps: Counter(p for p in ps if p.mount != 'up' or
                                     PARTS[p.part].name not in (
                                         'Brick 2 x 4', 'Brick 2 x 3', 'Brick 2 x 2',
                                         'Brick 1 x 4', 'Brick 1 x 2', 'Brick 1 x 1',
                                         'Brick 1 x 6', 'Brick 2 x 6', 'Brick 2 x 8',
                                         'Plate 2 x 4', 'Plate 2 x 3', 'Plate 2 x 2',
                                         'Plate 1 x 2', 'Plate 1 x 1', 'Plate 4 x 4',
                                         'Plate 2 x 8', 'Plate 4 x 8'))
        self.assertEqual(special(original), special(optimized))
        self.assertEqual([p for p in original if p.section.startswith('Taban')],
                         [p for p in optimized if p.section.startswith('Taban')])

    def test_exposed_original_parts_are_unchanged(self):
        from scripts.optimize_model import hidden_indices
        original = build(optimize=False)
        hidden = hidden_indices(original)
        protected = Counter(p for i, p in enumerate(original) if i not in hidden)
        self.assertFalse(protected - Counter(build()))


if __name__ == '__main__':
    unittest.main()
