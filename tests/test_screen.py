import unittest

class TestScreen(unittest.TestCase):

    def test_grid(self):
        from pygaming.screen.geometry_manager import Grid
        from pygaming.screen.anchors import TOP_LEFT, CENTER, BOTTOM_RIGHT, TOP_RIGHT
        grid = Grid(0, 0)
        grid.add(0, 0, 10, 12)
        grid.add(0, 1, 10, 12)
        grid.add(1, 0, 10, 12)
        self.assertEqual(grid.get(0, 0, TOP_LEFT, TOP_LEFT), (0, 0), "The top left object should be in (0, 0)")
        self.assertEqual(grid.get(0, 0, CENTER, TOP_LEFT), (5, 6), "The center of the top left object should be 5, 6.")
        grid.add(1, 1, 12, 14)
        self.assertEqual(grid.get(1, 1, TOP_LEFT, TOP_LEFT), (10, 12), "The 1,1 component should be in 10, 10")
        self.assertEqual(grid.get(1, 0, TOP_LEFT, TOP_LEFT), (0, 12), "The 1,0 component should be in 0, 12")
        self.assertEqual(grid.get(0, 1, BOTTOM_RIGHT, TOP_LEFT), (20, 12), "The 0, 1 component should have its bottom right in  20, 12 if justified top left")
        self.assertEqual(grid.get(0, 1, BOTTOM_RIGHT, TOP_RIGHT), (22, 12), "The 0, 1 component should have its bottom right in  22, 12 if justified top tight")
        grid.remove(1, 1)
        self.assertEqual(grid.get(1, 0, BOTTOM_RIGHT, BOTTOM_RIGHT), (10, 24))
        grid.remove(1, 0)
        grid.add(1, 0, 15, 12, 1, 2)
        self.assertEqual(grid.get(1, 0, TOP_LEFT, TOP_LEFT), (0, 12))
        self.assertEqual(grid.get(1, 0, BOTTOM_RIGHT, BOTTOM_RIGHT), (20, 24))
        self.assertRaises(ValueError, lambda : grid.get(1, 1))

        grid = Grid(100, 50)
        grid.add(0, 0, 10, 12)
        grid.add(0, 1, 10, 12)
        grid.add(1, 0, 10, 12)
        self.assertEqual(grid.get(0, 0, TOP_LEFT, TOP_LEFT), (100, 50), "The top left object should be in (0, 0)")
        self.assertEqual(grid.get(0, 0, CENTER, TOP_LEFT), (105, 56), "The center of the top left object should be 5, 6.")
        grid.add(1, 1, 12, 14)
        self.assertEqual(grid.get(1, 1, TOP_LEFT, TOP_LEFT), (110, 62), "The 1,1 component should be in 10, 10")
        self.assertEqual(grid.get(1, 0, TOP_LEFT, TOP_LEFT), (100, 62), "The 1,0 component should be in 0, 12")
        self.assertEqual(grid.get(0, 1, BOTTOM_RIGHT, TOP_LEFT), (120, 62), "The 0, 1 component should have its bottom right in  20, 12 if justified top left")
        self.assertEqual(grid.get(0, 1, BOTTOM_RIGHT, TOP_RIGHT), (122, 62), "The 0, 1 component should have its bottom right in  22, 12 if justified top tight")
        grid.remove(1, 1)
        self.assertEqual(grid.get(1, 0, BOTTOM_RIGHT, BOTTOM_RIGHT), (110, 74))
        grid.remove(1, 0)
        grid.add(1, 0, 15, 12, 1, 2)
        self.assertEqual(grid.get(1, 0, TOP_LEFT, TOP_LEFT), (100, 62))
        self.assertEqual(grid.get(1, 0, BOTTOM_RIGHT, BOTTOM_RIGHT), (120, 74))
        self.assertRaises(ValueError, lambda : grid.get(1, 1))

        grid = Grid(100, 50, CENTER)
        grid.add(0, 0, 10, 12)
        grid.add(0, 1, 10, 12)
        grid.add(1, 0, 10, 12)
        self.assertEqual(grid.get(0, 0, TOP_LEFT, TOP_LEFT), (90, 38), "The top left object should be in (0, 0)")

if __name__ == '__main__':
    unittest.main()