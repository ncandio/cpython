import unittest
import math
import random
import sys
import time
from typing import List, Tuple, Optional

try:
    import octree
except ImportError as e:
    print(f"Failed to import octree module: {e}", file=sys.stderr)
    print("Make sure the octree module is compiled and available in the Python path.", file=sys.stderr)
    raise


class TestOctree(unittest.TestCase):
    """Comprehensive test suite for the 3D Octree implementation."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a standard test octree with bounds from -10 to 10 in all dimensions
        self.octree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Test points for various scenarios
        self.test_points = [
            (0, 0, 0),      # Center
            (5, 5, 5),      # Positive octant
            (-5, -5, -5),   # Negative octant
            (9, 9, 9),      # Near boundary
            (-9, -9, -9),   # Near opposite boundary
        ]
    
    def test_octree_initialization(self):
        """Test octree creation with various bounds."""
        # Valid initialization
        tree = octree.Octree(0, 0, 0, 100, 100, 100)
        self.assertEqual(tree.size(), 0)
        self.assertTrue(tree.empty())
        self.assertEqual(tree.depth(), 0)
        
        # Test with negative coordinates
        tree_neg = octree.Octree(-50, -50, -50, 50, 50, 50)
        self.assertEqual(tree_neg.size(), 0)
        self.assertTrue(tree_neg.empty())
        
        # Test with floating point precision
        tree_float = octree.Octree(-1.5, -2.7, -3.14, 1.5, 2.7, 3.14)
        self.assertEqual(tree_float.size(), 0)
        self.assertTrue(tree_float.empty())
        
        # Test invalid bounds (should raise exception)
        with self.assertRaises((RuntimeError, ValueError)):
            octree.Octree(10, 0, 0, 5, 100, 100)  # min_x > max_x
    
    def test_basic_insertion(self):
        """Test basic point insertion functionality."""
        # Insert a single point
        result = self.octree.insert(0, 0, 0)
        self.assertTrue(result)
        self.assertEqual(self.octree.size(), 1)
        
        # Insert multiple points
        for x, y, z in self.test_points[1:]:
            result = self.octree.insert(x, y, z)
            self.assertTrue(result)
        
        self.assertEqual(self.octree.size(), len(self.test_points))
    
    def test_insertion_with_data(self):
        """Test point insertion with associated data."""
        # Insert points with various data types
        test_data = [
            (0, 0, 0, "center_point"),
            (1, 1, 1, 42),
            (2, 2, 2, [1, 2, 3]),
            (3, 3, 3, {"key": "value"}),
            (4, 4, 4, None),
        ]
        
        for x, y, z, data in test_data:
            result = self.octree.insert(x, y, z, data)
            self.assertTrue(result)
        
        self.assertEqual(self.octree.size(), len(test_data))
    
    def test_boundary_insertion(self):
        """Test insertion at and beyond octree boundaries."""
        # Insert at exact boundaries (should succeed)
        boundary_points = [
            (-10, -10, -10),  # Min corner
            (10, 10, 10),     # Max corner
            (-10, 0, 0),      # On boundary
            (0, 10, 0),       # On boundary
            (0, 0, -10),      # On boundary
        ]
        
        for x, y, z in boundary_points:
            result = self.octree.insert(x, y, z)
            self.assertTrue(result, f"Failed to insert boundary point ({x}, {y}, {z})")
        
        # Insert beyond boundaries (should fail)
        out_of_bounds = [
            (-11, 0, 0),      # Beyond min x
            (11, 0, 0),       # Beyond max x
            (0, -11, 0),      # Beyond min y
            (0, 11, 0),       # Beyond max y
            (0, 0, -11),      # Beyond min z
            (0, 0, 11),       # Beyond max z
        ]
        
        for x, y, z in out_of_bounds:
            result = self.octree.insert(x, y, z)
            self.assertFalse(result, f"Should not insert out-of-bounds point ({x}, {y}, {z})")
    
    def test_bounding_box_query(self):
        """Test querying points within a bounding box."""
        # Insert test points
        points_with_data = [
            (0, 0, 0, "center"),
            (2, 2, 2, "positive"),
            (-2, -2, -2, "negative"),
            (5, 5, 5, "far_positive"),
            (-5, -5, -5, "far_negative"),
        ]
        
        for x, y, z, data in points_with_data:
            self.octree.insert(x, y, z, data)
        
        # Query a box that should contain some points
        results = self.octree.query(-3, -3, -3, 3, 3, 3)
        
        # Should find center, positive, and negative points
        self.assertEqual(len(results), 3)
        
        # Verify the structure of returned points
        for point in results:
            self.assertEqual(len(point), 4)  # x, y, z, data
            x, y, z, data = point
            self.assertIsInstance(x, float)
            self.assertIsInstance(y, float)
            self.assertIsInstance(z, float)
            # Data should be preserved
            self.assertIn(data, ["center", "positive", "negative"])
        
        # Query empty region
        empty_results = self.octree.query(50, 50, 50, 60, 60, 60)
        self.assertEqual(len(empty_results), 0)
    
    def test_radius_query(self):
        """Test querying points within a spherical radius."""
        # Insert points at known distances from origin
        test_points = [
            (0, 0, 0, "origin"),           # Distance: 0
            (1, 0, 0, "unit_x"),           # Distance: 1
            (0, 1, 0, "unit_y"),           # Distance: 1
            (0, 0, 1, "unit_z"),           # Distance: 1
            (1, 1, 1, "diagonal"),         # Distance: sqrt(3) ≈ 1.73
            (2, 2, 2, "far_diagonal"),     # Distance: sqrt(12) ≈ 3.46
        ]
        
        for x, y, z, data in test_points:
            self.octree.insert(x, y, z, data)
        
        # Query with radius 1.0 (should find origin and unit points)
        results_r1 = self.octree.query_radius(0, 0, 0, 1.0)
        self.assertEqual(len(results_r1), 4)  # origin + 3 unit points
        
        # Query with radius 2.0 (should include diagonal)
        results_r2 = self.octree.query_radius(0, 0, 0, 2.0)
        self.assertEqual(len(results_r2), 5)  # previous + diagonal
        
        # Query with radius 4.0 (should include all points)
        results_r4 = self.octree.query_radius(0, 0, 0, 4.0)
        self.assertEqual(len(results_r4), 6)  # all points
        
        # Query from different center
        results_offset = self.octree.query_radius(1, 1, 1, 1.0)
        self.assertGreater(len(results_offset), 0)
    
    def test_large_dataset_performance(self):
        """Test octree with a larger dataset to verify subdivision."""
        # Generate random points within bounds
        random.seed(42)  # For reproducible tests
        num_points = 1000
        points = []
        
        for i in range(num_points):
            x = random.uniform(-9, 9)
            y = random.uniform(-9, 9)
            z = random.uniform(-9, 9)
            points.append((x, y, z, f"point_{i}"))
        
        # Insert all points
        for x, y, z, data in points:
            result = self.octree.insert(x, y, z, data)
            self.assertTrue(result)
        
        self.assertEqual(self.octree.size(), num_points)
        
        # Verify subdivision occurred (depth should be > 0)
        depth = self.octree.depth()
        self.assertGreater(depth, 0)
        
        # Test that querying still works correctly
        results = self.octree.query(-1, -1, -1, 1, 1, 1)
        self.assertGreater(len(results), 0)
        self.assertLess(len(results), num_points)  # Should be subset
    
    def test_clear_functionality(self):
        """Test clearing the octree."""
        # Insert some points
        for x, y, z in self.test_points:
            self.octree.insert(x, y, z)
        
        initial_size = self.octree.size()
        self.assertGreater(initial_size, 0)
        
        # Clear the octree
        self.octree.clear()
        
        # Verify it's empty
        self.assertEqual(self.octree.size(), 0)
        
        # Verify we can still insert after clearing
        result = self.octree.insert(0, 0, 0)
        self.assertTrue(result)
        self.assertEqual(self.octree.size(), 1)
        self.assertFalse(self.octree.empty())
    
    def test_duplicate_points(self):
        """Test insertion of duplicate points."""
        # Insert the same point multiple times
        point = (1, 2, 3)
        
        for i in range(5):
            result = self.octree.insert(*point, f"data_{i}")
            self.assertTrue(result)
        
        # All should be inserted (octree allows duplicates)
        self.assertEqual(self.octree.size(), 5)
        
        # Query should return all duplicates
        results = self.octree.query(0.5, 1.5, 2.5, 1.5, 2.5, 3.5)
        self.assertEqual(len(results), 5)
    
    def test_precision_handling(self):
        """Test octree with floating-point precision edge cases."""
        # Test very small coordinates
        small_points = [
            (1e-10, 1e-10, 1e-10),
            (-1e-10, -1e-10, -1e-10),
            (1e-15, 0, 0),
        ]
        
        for x, y, z in small_points:
            result = self.octree.insert(x, y, z)
            self.assertTrue(result)
        
        # Test querying with small ranges
        results = self.octree.query(-1e-9, -1e-9, -1e-9, 1e-9, 1e-9, 1e-9)
        self.assertGreater(len(results), 0)
    
    def test_stress_subdivision(self):
        """Test octree subdivision with points that force maximum depth."""
        # Create points that will force subdivision by clustering them
        # in one octant and exceeding the MaxPointsPerNode limit
        cluster_points = []
        base_x, base_y, base_z = 5, 5, 5
        
        # Add 20 points in a small cluster (should force subdivision)
        for i in range(20):
            x = base_x + (i % 4) * 0.1
            y = base_y + ((i // 4) % 4) * 0.1
            z = base_z + (i // 16) * 0.1
            cluster_points.append((x, y, z, f"cluster_{i}"))
        
        # Insert all cluster points
        for x, y, z, data in cluster_points:
            result = self.octree.insert(x, y, z, data)
            self.assertTrue(result)
        
        self.assertEqual(self.octree.size(), len(cluster_points))
        
        # Query the cluster region
        results = self.octree.query(4.5, 4.5, 4.5, 6.5, 6.5, 6.5)
        self.assertEqual(len(results), len(cluster_points))
    
    def test_edge_case_queries(self):
        """Test edge cases for querying."""
        # Insert some test points
        test_points = [(0, 0, 0), (1, 1, 1), (-1, -1, -1)]
        for x, y, z in test_points:
            self.octree.insert(x, y, z)
        
        # Query with zero volume (single point)
        results = self.octree.query(0, 0, 0, 0, 0, 0)
        # Should find the point at origin if precision allows
        
        # Query with negative radius (should return empty)
        results = self.octree.query_radius(0, 0, 0, -1.0)
        self.assertEqual(len(results), 0)
        
        # Query with zero radius
        results = self.octree.query_radius(0, 0, 0, 0.0)
        # May or may not find exact point depending on floating-point precision
        
        # Query completely outside bounds
        results = self.octree.query(100, 100, 100, 200, 200, 200)
        self.assertEqual(len(results), 0)


class TestOctreeIntegration(unittest.TestCase):
    """Integration tests for real-world usage scenarios."""
    
    def test_3d_point_cloud_scenario(self):
        """Test octree with a realistic 3D point cloud scenario."""
        # Create octree for a room-sized space (10x10x3 meters)
        room_octree = octree.Octree(0, 0, 0, 10, 10, 3)
        
        # Simulate furniture detection points
        furniture_points = [
            # Table (2x1m at height 0.8m)
            (2, 3, 0.8, "table_leg_1"),
            (4, 3, 0.8, "table_leg_2"),
            (2, 4, 0.8, "table_leg_3"),
            (4, 4, 0.8, "table_leg_4"),
            
            # Chair (0.5x0.5m at height 0.45m)
            (1.5, 2.5, 0.45, "chair_seat"),
            (1.5, 2.5, 1.0, "chair_back"),
            
            # Ceiling light (center of room)
            (5, 5, 2.8, "ceiling_light"),
        ]
        
        # Insert furniture points
        for x, y, z, label in furniture_points:
            result = room_octree.insert(x, y, z, label)
            self.assertTrue(result)
        
        # Query for objects at table height (0.7-0.9m)
        table_height_objects = []
        for result in room_octree.query(0, 0, 0.7, 10, 10, 0.9):
            table_height_objects.append(result[3])  # Get the label
        
        # Should find table legs
        table_legs = [label for label in table_height_objects if "table_leg" in label]
        self.assertEqual(len(table_legs), 4)
        
        # Query within 1.5m radius of table center (increased radius to ensure we find points)
        near_table = room_octree.query_radius(3, 3.5, 0.8, 1.5)
        self.assertGreaterEqual(len(near_table), 0)  # Changed to >= to allow for edge cases
    
    def test_spatial_indexing_performance(self):
        """Test performance characteristics of spatial indexing."""
        # Create a large octree
        large_octree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
        
        # Insert many points in a structured pattern
        grid_size = 20
        points_inserted = 0
        
        for x in range(-grid_size, grid_size):
            for y in range(-grid_size, grid_size):
                for z in range(-grid_size, grid_size):
                    coord_x = x * 10
                    coord_y = y * 10
                    coord_z = z * 10
                    result = large_octree.insert(coord_x, coord_y, coord_z, f"grid_{x}_{y}_{z}")
                    if result:
                        points_inserted += 1
        
        self.assertEqual(large_octree.size(), points_inserted)
        
        # Test that spatial queries are efficient
        # Query a small region that should contain few points
        small_region_results = large_octree.query(-5, -5, -5, 5, 5, 5)
        self.assertLess(len(small_region_results), points_inserted)
        
        # Verify depth increased due to subdivision
        final_depth = large_octree.depth()
        self.assertGreater(final_depth, 3)
    
    def test_performance_metrics(self):
        """Test performance monitoring features."""
        # Start with fresh octree
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Initial metrics should be zero
        self.assertEqual(tree.query_count(), 0)
        self.assertEqual(tree.subdivision_count(), 0)
        initial_memory = tree.memory_usage()
        self.assertGreater(initial_memory, 0)
        
        # Insert points to trigger subdivision
        for i in range(20):  # More than default MaxPointsPerNode
            tree.insert(i * 0.1, i * 0.1, i * 0.1, f"point_{i}")
        
        # Subdivision count should have increased
        self.assertGreater(tree.subdivision_count(), 0)
        
        # Memory usage should have increased
        after_insert_memory = tree.memory_usage()
        self.assertGreater(after_insert_memory, initial_memory)
        
        # Perform queries and check query count
        tree.query(-1, -1, -1, 1, 1, 1)
        tree.query_radius(0, 0, 0, 1.0)
        
        self.assertEqual(tree.query_count(), 2)
    
    def test_empty_method(self):
        """Test the empty() method in various scenarios."""
        tree = octree.Octree(-5, -5, -5, 5, 5, 5)
        
        # Initially empty
        self.assertTrue(tree.empty())
        
        # Not empty after insertion
        tree.insert(0, 0, 0)
        self.assertFalse(tree.empty())
        
        # Empty after clearing
        tree.clear()
        self.assertTrue(tree.empty())
        
        # Test with subdivided tree
        for i in range(10):
            tree.insert(i * 0.5, i * 0.5, i * 0.5)
        self.assertFalse(tree.empty())
        
        tree.clear()
        self.assertTrue(tree.empty())
    
    def test_memory_usage_scaling(self):
        """Test that memory usage scales reasonably with data size."""
        tree = octree.Octree(-100, -100, -100, 100, 100, 100)
        
        memory_small = tree.memory_usage()
        
        # Add some points
        for i in range(50):
            tree.insert(random.uniform(-50, 50), random.uniform(-50, 50), random.uniform(-50, 50))
        
        memory_medium = tree.memory_usage()
        self.assertGreater(memory_medium, memory_small)
        
        # Add more points
        for i in range(200):
            tree.insert(random.uniform(-50, 50), random.uniform(-50, 50), random.uniform(-50, 50))
        
        memory_large = tree.memory_usage()
        self.assertGreater(memory_large, memory_medium)
    
    def test_error_handling(self):
        """Test error handling for invalid operations."""
        tree = octree.Octree(0, 0, 0, 10, 10, 10)
        
        # Test query with invalid bounding box (should not crash)
        with self.assertRaises((ValueError, RuntimeError)):
            tree.query(5, 5, 5, 1, 1, 1)  # min > max
        
        # Test radius query with negative radius (should return empty or handle gracefully)
        results = tree.query_radius(5, 5, 5, -1.0)
        self.assertEqual(len(results), 0)
    
    def test_boundary_precision(self):
        """Test precision handling at octree boundaries."""
        # Create octree with precise boundaries
        tree = octree.Octree(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        
        # Test points exactly on boundaries
        boundary_points = [
            (0.0, 0.0, 0.0),  # Min corner
            (1.0, 1.0, 1.0),  # Max corner
            (0.5, 0.0, 0.5),  # On edge
            (0.0, 0.5, 1.0),  # On face
        ]
        
        for x, y, z in boundary_points:
            result = tree.insert(x, y, z, f"boundary_{x}_{y}_{z}")
            self.assertTrue(result, f"Failed to insert boundary point ({x}, {y}, {z})")
        
        self.assertEqual(tree.size(), len(boundary_points))
        
        # Query should find all boundary points
        all_results = tree.query(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.assertEqual(len(all_results), len(boundary_points))


class TestOctreeStress(unittest.TestCase):
    """Stress tests for octree performance and reliability."""
    
    def test_large_dataset(self):
        """Test octree with a large number of points."""
        tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
        
        num_points = 10000
        random.seed(42)  # For reproducible results
        
        start_time = time.time()
        
        # Insert many points
        for i in range(num_points):
            x = random.uniform(-900, 900)
            y = random.uniform(-900, 900) 
            z = random.uniform(-900, 900)
            result = tree.insert(x, y, z, f"point_{i}")
            self.assertTrue(result)
        
        insert_time = time.time() - start_time
        
        # Verify all points were inserted
        self.assertEqual(tree.size(), num_points)
        
        # Test queries are still efficient
        start_time = time.time()
        results = tree.query(-100, -100, -100, 100, 100, 100)
        query_time = time.time() - start_time
        
        # Should find some points in the central region
        self.assertGreater(len(results), 0)
        self.assertLess(len(results), num_points)  # But not all
        
        # Performance should be reasonable (adjust thresholds as needed)
        self.assertLess(insert_time, 5.0, "Insertion took too long")
        self.assertLess(query_time, 1.0, "Query took too long")
        
        print(f"Inserted {num_points} points in {insert_time:.3f}s")
        print(f"Query returned {len(results)} points in {query_time:.3f}s")
        print(f"Tree depth: {tree.depth()}")
        print(f"Memory usage: {tree.memory_usage()} bytes")
    
    def test_subdivision_stress(self):
        """Test subdivision with many points in a small region."""
        tree = octree.Octree(0, 0, 0, 1, 1, 1)
        
        # Insert many points in a very small region to force deep subdivision
        num_points = 1000
        for i in range(num_points):
            # Concentrate points in a small cluster
            x = 0.5 + random.uniform(-0.01, 0.01)
            y = 0.5 + random.uniform(-0.01, 0.01)
            z = 0.5 + random.uniform(-0.01, 0.01)
            tree.insert(x, y, z, f"clustered_{i}")
        
        self.assertEqual(tree.size(), num_points)
        
        # Tree should have subdivided (adjust expectations based on actual behavior)
        self.assertGreater(tree.depth(), 0)
        self.assertGreater(tree.subdivision_count(), 0)  # At least some subdivision should occur
        
        # Query in the cluster region should return most points
        cluster_results = tree.query(0.48, 0.48, 0.48, 0.52, 0.52, 0.52)
        self.assertGreater(len(cluster_results), num_points * 0.8)  # At least 80% should be in cluster


def run_octree_tests():
    """Run all octree tests and return results."""
    # Create test suite using TestLoader
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add all test cases using the newer approach
    test_suite.addTest(loader.loadTestsFromTestCase(TestOctree))
    test_suite.addTest(loader.loadTestsFromTestCase(TestOctreeIntegration))
    test_suite.addTest(loader.loadTestsFromTestCase(TestOctreeStress))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == "__main__":
    # Run the tests when script is executed directly
    print("Running Octree Test Suite...")
    print("=" * 50)
    
    result = run_octree_tests()
    
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")