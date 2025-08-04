import unittest
import random
import quadtree

class TestProductionQuadtree(unittest.TestCase):
    def setUp(self):
        self.bounds = (0, 0, 100, 100)

    def test_insert_and_contains(self):
        qt = quadtree.Quadtree(*self.bounds, max_points=4)
        pts = [(10, 20), (30, 40), (50, 60), (70, 80)]
        for x, y in pts:
            qt.insert(x, y)
        for x, y in pts:
            self.assertTrue(qt.contains(x, y))
        self.assertFalse(qt.contains(999, 999))

    def test_subdivides(self):
        qt = quadtree.Quadtree(*self.bounds, max_points=2)
        # Insert enough points to force subdivision
        for i in range(8):
            qt.insert(i*10, i*10)
        self.assertGreaterEqual(qt.subdivisions(), 1)

    def test_large(self):
        qt = quadtree.Quadtree(*self.bounds, max_points=4)
        for _ in range(1000):
            x, y = random.uniform(0, 100), random.uniform(0, 100)
            qt.insert(x, y)
        # Check random points
        points = qt.get_points()
        for pt in points[:10]:
            self.assertTrue(qt.contains(pt[0], pt[1]))

    def test_many_quadtrees(self):
        for count in [10, 100]:
            trees = []
            for _ in range(count):
                qt = quadtree.Quadtree(*self.bounds, max_points=4)
                for i in range(10):
                    qt.insert(random.uniform(0, 100), random.uniform(0, 100))
                trees.append(qt)
            self.assertEqual(len(trees), count)

if __name__ == "__main__":
    unittest.main()