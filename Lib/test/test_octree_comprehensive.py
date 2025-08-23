"""Comprehensive test suite for the octree module.

This module provides thorough testing of the 3D Octree implementation,
following CPython testing conventions and covering all API functionality,
edge cases, and error conditions.
"""

import unittest
import math
import random
import sys
import time
import gc
import weakref
from test import support
from test.support import import_helper
import warnings

# Import the octree module with proper error handling
try:
    import octree
except ImportError as e:
    octree = import_helper.skip_if_missing('octree')


class OctreeCreationTest(unittest.TestCase):
    """Test octree creation and initialization."""

    def test_valid_creation(self):
        """Test creation with valid bounds."""
        # Basic creation
        tree = octree.Octree(0, 0, 0, 10, 10, 10)
        self.assertEqual(tree.size(), 0)
        self.assertTrue(tree.empty())
        self.assertEqual(tree.depth(), 0)
        
        # Negative bounds
        tree_neg = octree.Octree(-50, -50, -50, 50, 50, 50)
        self.assertEqual(tree_neg.size(), 0)
        self.assertTrue(tree_neg.empty())
        
        # Floating point bounds
        tree_float = octree.Octree(-1.5, -2.7, -3.14, 1.5, 2.7, 3.14)
        self.assertEqual(tree_float.size(), 0)
        self.assertTrue(tree_float.empty())

    def test_invalid_creation(self):
        """Test creation with invalid bounds raises appropriate errors."""
        # Inverted bounds should raise error
        with self.assertRaises((RuntimeError, ValueError)):
            octree.Octree(10, 0, 0, 5, 100, 100)  # min_x > max_x
            
        with self.assertRaises((RuntimeError, ValueError)):
            octree.Octree(0, 10, 0, 10, 5, 10)  # min_y > max_y
            
        with self.assertRaises((RuntimeError, ValueError)):
            octree.Octree(0, 0, 10, 10, 10, 5)  # min_z > max_z

    def test_boundary_edge_cases(self):
        """Test creation with edge case bounds."""
        # Zero-volume bounds should be handled gracefully
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                tree = octree.Octree(5, 5, 5, 5, 5, 5)
                # If it succeeds, verify basic properties
                self.assertEqual(tree.size(), 0)
            except (RuntimeError, ValueError):
                # It's also acceptable to reject zero-volume bounds
                pass


class OctreeInsertionTest(unittest.TestCase):
    """Test point insertion functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.tree = octree.Octree(-10, -10, -10, 10, 10, 10)

    def test_basic_insertion(self):
        """Test basic point insertion."""
        # Single point insertion
        result = self.tree.insert(0, 0, 0)
        self.assertTrue(result)
        self.assertEqual(self.tree.size(), 1)
        self.assertFalse(self.tree.empty())
        
        # Multiple point insertion
        test_points = [(1, 1, 1), (-1, -1, -1), (5, 5, 5)]
        for x, y, z in test_points:
            result = self.tree.insert(x, y, z)
            self.assertTrue(result)
        
        self.assertEqual(self.tree.size(), 4)  # 1 + 3 points

    def test_insertion_with_data(self):
        """Test point insertion with associated data."""
        test_data = [
            (0, 0, 0, "center"),
            (1, 1, 1, 42),
            (2, 2, 2, [1, 2, 3]),
            (3, 3, 3, {"key": "value"}),
            (4, 4, 4, None),
        ]
        
        for x, y, z, data in test_data:
            result = self.tree.insert(x, y, z, data)
            self.assertTrue(result)
        
        self.assertEqual(self.tree.size(), len(test_data))

    def test_boundary_insertion(self):
        """Test insertion at octree boundaries."""
        # Points exactly on boundaries
        boundary_points = [
            (-10, -10, -10),  # Min corner
            (10, 10, 10),     # Max corner
            (-10, 0, 0),      # On min x boundary
            (0, 10, 0),       # On max y boundary
            (0, 0, -10),      # On min z boundary
        ]
        
        for x, y, z in boundary_points:
            result = self.tree.insert(x, y, z)
            self.assertTrue(result, f"Failed to insert boundary point ({x}, {y}, {z})")

    def test_out_of_bounds_insertion(self):
        """Test insertion of out-of-bounds points."""
        out_of_bounds = [
            (-11, 0, 0),
            (11, 0, 0),
            (0, -11, 0),
            (0, 11, 0),
            (0, 0, -11),
            (0, 0, 11),
        ]
        
        for x, y, z in out_of_bounds:
            result = self.tree.insert(x, y, z)
            self.assertFalse(result, f"Should reject out-of-bounds point ({x}, {y}, {z})")

    def test_duplicate_insertion(self):
        """Test insertion of duplicate points."""
        # Insert same point multiple times
        point = (1, 2, 3)
        data_items = ["data_1", "data_2", "data_3"]
        
        for data in data_items:
            result = self.tree.insert(*point, data)
            self.assertTrue(result)
        
        # All duplicates should be stored
        self.assertEqual(self.tree.size(), len(data_items))


class OctreeQueryTest(unittest.TestCase):
    """Test query functionality."""

    def setUp(self):
        """Set up test fixtures with known data."""
        self.tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Insert known test points
        self.test_points = [
            (0, 0, 0, "center"),
            (2, 2, 2, "positive_small"),
            (-2, -2, -2, "negative_small"),
            (5, 5, 5, "positive_large"),
            (-5, -5, -5, "negative_large"),
            (8, 8, 8, "near_boundary"),
        ]
        
        for x, y, z, data in self.test_points:
            self.tree.insert(x, y, z, data)

    def test_bounding_box_query(self):
        """Test rectangular region queries."""
        # Query that should include center and small points
        results = self.tree.query(-3, -3, -3, 3, 3, 3)
        
        # Should find center, positive_small, negative_small
        expected_count = 3
        self.assertEqual(len(results), expected_count)
        
        # Verify result format
        for point in results:
            self.assertEqual(len(point), 4)  # (x, y, z, data)
            x, y, z, data = point
            self.assertIsInstance(x, float)
            self.assertIsInstance(y, float) 
            self.assertIsInstance(z, float)

    def test_radius_query(self):
        """Test circular region queries."""
        # Query around origin with radius 3
        results = self.tree.query_radius(0, 0, 0, 3.0)
        
        # Should find points within distance 3 of origin
        for x, y, z, data in results:
            distance = math.sqrt(x*x + y*y + z*z)
            self.assertLessEqual(distance, 3.0)

    def test_empty_query_results(self):
        """Test queries that should return no results."""
        # Query empty region
        results = self.tree.query(50, 50, 50, 60, 60, 60)
        self.assertEqual(len(results), 0)
        
        # Query with zero radius
        results = self.tree.query_radius(100, 100, 100, 0.0)
        self.assertEqual(len(results), 0)

    def test_full_range_query(self):
        """Test query that should return all points."""
        results = self.tree.query(-10, -10, -10, 10, 10, 10)
        self.assertEqual(len(results), len(self.test_points))

    def test_query_parameter_validation(self):
        """Test query parameter validation."""
        # Invalid bounding box (min > max)
        with self.assertRaises((ValueError, RuntimeError)):
            self.tree.query(5, 5, 5, 1, 1, 1)
        
        # Negative radius should return empty results
        results = self.tree.query_radius(0, 0, 0, -1.0)
        self.assertEqual(len(results), 0)


class OctreeSubdivisionTest(unittest.TestCase):
    """Test octree subdivision behavior."""

    def test_subdivision_trigger(self):
        """Test that subdivision occurs when threshold is exceeded."""
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Insert points below threshold (typically 8)
        for i in range(8):
            tree.insert(i, i, i)
        
        # Should not have subdivided yet
        initial_subdivision_count = tree.subdivision_count()
        
        # Insert one more to trigger subdivision
        tree.insert(8, 8, 8)
        
        # Should have subdivided
        self.assertGreater(tree.subdivision_count(), initial_subdivision_count)
        self.assertGreater(tree.depth(), 0)

    def test_deep_subdivision(self):
        """Test subdivision with clustered points."""
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Insert many points in a small cluster
        random.seed(42)  # For reproducible tests
        cluster_center = (2, 2, 2)
        
        for i in range(50):
            x = cluster_center[0] + random.uniform(-0.5, 0.5)
            y = cluster_center[1] + random.uniform(-0.5, 0.5)
            z = cluster_center[2] + random.uniform(-0.5, 0.5)
            tree.insert(x, y, z, f"cluster_{i}")
        
        # Should have achieved significant depth
        self.assertGreater(tree.depth(), 1)
        self.assertGreater(tree.subdivision_count(), 0)
        
        # All points should still be queryable
        self.assertEqual(tree.size(), 50)


class OctreePropertiesTest(unittest.TestCase):
    """Test octree property methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.tree = octree.Octree(-10, -10, -10, 10, 10, 10)

    def test_empty_tree_properties(self):
        """Test properties of empty tree."""
        self.assertEqual(self.tree.size(), 0)
        self.assertTrue(self.tree.empty())
        self.assertEqual(self.tree.depth(), 0)
        self.assertEqual(self.tree.query_count(), 0)
        self.assertEqual(self.tree.subdivision_count(), 0)
        self.assertGreater(self.tree.memory_usage(), 0)

    def test_properties_after_insertion(self):
        """Test properties after adding points."""
        # Add some points
        for i in range(10):
            self.tree.insert(i, i, i)
        
        self.assertEqual(self.tree.size(), 10)
        self.assertFalse(self.tree.empty())
        self.assertGreater(self.tree.memory_usage(), 0)

    def test_query_count_tracking(self):
        """Test that query count is properly tracked."""
        initial_count = self.tree.query_count()
        
        # Perform queries
        self.tree.query(-1, -1, -1, 1, 1, 1)
        self.tree.query_radius(0, 0, 0, 1.0)
        
        self.assertEqual(self.tree.query_count(), initial_count + 2)

    def test_clear_functionality(self):
        """Test clearing the tree."""
        # Add points
        for i in range(5):
            self.tree.insert(i, i, i)
        
        self.assertFalse(self.tree.empty())
        
        # Clear
        self.tree.clear()
        
        # Should be empty
        self.assertTrue(self.tree.empty())
        self.assertEqual(self.tree.size(), 0)
        
        # Should be able to insert after clearing
        result = self.tree.insert(0, 0, 0)
        self.assertTrue(result)


class OctreeStressTest(unittest.TestCase):
    """Stress tests for octree performance and reliability."""
    
    @support.requires_resource('cpu')
    def test_large_dataset(self):
        """Test with a large number of points."""
        tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
        
        num_points = 5000
        random.seed(42)
        
        # Insert many points
        for i in range(num_points):
            x = random.uniform(-900, 900)
            y = random.uniform(-900, 900) 
            z = random.uniform(-900, 900)
            result = tree.insert(x, y, z, f"point_{i}")
            self.assertTrue(result)
        
        # Verify all points were inserted
        self.assertEqual(tree.size(), num_points)
        
        # Test that queries still work efficiently
        results = tree.query(-100, -100, -100, 100, 100, 100)
        self.assertGreater(len(results), 0)
        self.assertLess(len(results), num_points)

    @support.requires_resource('cpu')
    def test_subdivision_stress(self):
        """Test subdivision with concentrated points."""
        tree = octree.Octree(0, 0, 0, 1, 1, 1)
        
        # Insert many points in a small region
        num_points = 1000
        for i in range(num_points):
            x = 0.5 + random.uniform(-0.01, 0.01)
            y = 0.5 + random.uniform(-0.01, 0.01)
            z = 0.5 + random.uniform(-0.01, 0.01)
            tree.insert(x, y, z, f"clustered_{i}")
        
        self.assertEqual(tree.size(), num_points)
        self.assertGreater(tree.subdivision_count(), 0)


class OctreeErrorHandlingTest(unittest.TestCase):
    """Test error handling and edge cases."""

    def test_invalid_query_bounds(self):
        """Test handling of invalid query parameters."""
        tree = octree.Octree(0, 0, 0, 10, 10, 10)
        
        # Invalid bounding box
        with self.assertRaises((ValueError, RuntimeError)):
            tree.query(5, 5, 5, 1, 1, 1)

    def test_precision_edge_cases(self):
        """Test with very small/large coordinate values."""
        tree = octree.Octree(-1, -1, -1, 1, 1, 1)
        
        # Very small coordinates
        small_coords = [
            (1e-10, 1e-10, 1e-10),
            (-1e-10, -1e-10, -1e-10),
        ]
        
        for x, y, z in small_coords:
            result = tree.insert(x, y, z)
            self.assertTrue(result)

    def test_nan_and_infinity_handling(self):
        """Test handling of NaN and infinity values."""
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Test with NaN (should be handled gracefully)
        try:
            result = tree.insert(float('nan'), 0, 0)
            # Implementation may accept or reject NaN
        except (ValueError, RuntimeError):
            pass  # Acceptable to reject NaN
        
        # Test with infinity (should typically be rejected as out of bounds)
        result = tree.insert(float('inf'), 0, 0)
        self.assertFalse(result)  # Should be out of bounds


class OctreeMemoryTest(unittest.TestCase):
    """Test memory management and reference counting."""

    def test_memory_usage_scaling(self):
        """Test that memory usage scales reasonably."""
        tree = octree.Octree(-100, -100, -100, 100, 100, 100)
        
        initial_memory = tree.memory_usage()
        
        # Add points and check memory growth
        for batch_size in [50, 100, 200]:
            for i in range(batch_size):
                tree.insert(
                    random.uniform(-50, 50),
                    random.uniform(-50, 50),
                    random.uniform(-50, 50)
                )
            
            current_memory = tree.memory_usage()
            self.assertGreater(current_memory, initial_memory)

    def test_data_reference_counting(self):
        """Test that Python objects are properly reference counted."""
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Create an object to track
        test_obj = [1, 2, 3]
        weak_ref = weakref.ref(test_obj)
        
        # Insert with the object as data
        tree.insert(0, 0, 0, test_obj)
        
        # Delete our reference
        del test_obj
        
        # Object should still be alive (held by octree)
        self.assertIsNotNone(weak_ref())
        
        # Clear tree
        tree.clear()
        gc.collect()
        
        # Now object should be gone
        self.assertIsNone(weak_ref())


class OctreeCompatibilityTest(unittest.TestCase):
    """Test compatibility and integration aspects."""

    def test_pickling_not_supported(self):
        """Test that octree objects handle pickling appropriately."""
        import pickle
        
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        tree.insert(1, 2, 3)
        
        # Octree objects likely don't support pickling
        with self.assertRaises((TypeError, AttributeError, pickle.PicklingError)):
            pickle.dumps(tree)

    def test_string_representation(self):
        """Test string representation of octree objects."""
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Should have some string representation
        str_repr = str(tree)
        self.assertIsInstance(str_repr, str)
        self.assertIn('octree', str_repr.lower())

    def test_type_and_attributes(self):
        """Test type information and available attributes."""
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Check type
        self.assertEqual(type(tree).__name__, 'Octree')
        
        # Check that methods exist
        methods = ['insert', 'query', 'query_radius', 'size', 'clear', 
                  'depth', 'empty', 'memory_usage', 'query_count', 
                  'subdivision_count']
        
        for method in methods:
            self.assertTrue(hasattr(tree, method))
            self.assertTrue(callable(getattr(tree, method)))


def load_tests(loader, tests, pattern):
    """Load additional tests for the octree module."""
    # This allows the test framework to discover all test cases
    return loader.loadTestsFromModule(sys.modules[__name__])


if __name__ == '__main__':
    # Run tests when executed directly
    unittest.main(verbosity=2)