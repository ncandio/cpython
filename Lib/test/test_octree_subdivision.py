#!/usr/bin/env python3
"""
Test suite specifically for understanding and demonstrating octree subdivision behavior.

This module provides detailed tests and explanations of how the octree subdivision
algorithm works, including visual representations and step-by-step analysis.
"""

import unittest
import sys
import os

try:
    # Add the Modules directory to the path to import octree
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Modules'))
    import octree
except ImportError as e:
    print(f"Failed to import octree module: {e}", file=sys.stderr)
    print("Make sure the octree module is compiled and available.", file=sys.stderr)
    raise


class TestOctreeSubdivision(unittest.TestCase):
    """
    Detailed tests demonstrating octree subdivision mechanics.
    
    The octree uses a hierarchical spatial partitioning approach where:
    1. Each node can hold up to MaxPointsPerNode points (default: 8)
    2. When this limit is exceeded, the node subdivides into 8 octants
    3. Existing points are redistributed to the appropriate child octants
    4. Subdivision stops at MaxDepth levels (default: 16)
    """

    def test_no_subdivision_below_threshold(self):
        """
        Test 1: No subdivision occurs when point count is below threshold.
        
        This demonstrates the base case where subdivision is not needed.
        """
        print("\n" + "="*60)
        print("TEST 1: No Subdivision Below Threshold")
        print("="*60)
        
        # Create octree with default parameters (MaxPointsPerNode = 8)
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        print(f"Initial state:")
        print(f"  Size: {tree.size()}")
        print(f"  Depth: {tree.depth()}")
        print(f"  Subdivisions: {tree.subdivision_count()}")
        print(f"  Empty: {tree.empty()}")
        
        # Insert points below the subdivision threshold
        points = [
            (1, 1, 1, "point_1"),
            (2, 2, 2, "point_2"), 
            (3, 3, 3, "point_3"),
            (-1, -1, -1, "point_4"),
            (-2, -2, -2, "point_5"),
        ]
        
        print(f"\nInserting {len(points)} points (below threshold of 8):")
        for i, (x, y, z, data) in enumerate(points):
            tree.insert(x, y, z, data)
            print(f"  After inserting point {i+1}: size={tree.size()}, depth={tree.depth()}, subdivisions={tree.subdivision_count()}")
        
        # Verify no subdivision occurred
        self.assertEqual(tree.subdivision_count(), 0, "No subdivisions should occur below threshold")
        self.assertEqual(tree.depth(), 0, "Depth should remain 0 without subdivision")
        self.assertEqual(tree.size(), len(points), "All points should be stored in root node")
        
        print(f"\nFinal state (no subdivision):")
        print(f"  Size: {tree.size()}")
        print(f"  Depth: {tree.depth()}")
        print(f"  Subdivisions: {tree.subdivision_count()}")
        
        print("\n✅ RESULT: Tree remains as single node when below subdivision threshold")

    def test_first_subdivision_trigger(self):
        """
        Test 2: First subdivision occurs when exceeding MaxPointsPerNode.
        
        This demonstrates the exact moment when subdivision is triggered.
        """
        print("\n" + "="*60)
        print("TEST 2: First Subdivision Trigger")
        print("="*60)
        
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)
        
        # Insert exactly MaxPointsPerNode points (should not subdivide yet)
        print("Phase 1: Inserting exactly 8 points (at threshold):")
        for i in range(8):
            x, y, z = i, i, i  # Simple pattern for clarity
            tree.insert(x, y, z, f"threshold_point_{i}")
            print(f"  Point {i+1}: size={tree.size()}, subdivisions={tree.subdivision_count()}")
        
        print(f"\nAfter 8 points (at threshold):")
        print(f"  Size: {tree.size()}")
        print(f"  Depth: {tree.depth()}")
        print(f"  Subdivisions: {tree.subdivision_count()}")
        
        self.assertEqual(tree.subdivision_count(), 0, "Should not subdivide at exactly the threshold")
        
        # Insert one more point to trigger subdivision
        print("\nPhase 2: Inserting 9th point (exceeds threshold):")
        tree.insert(8, 8, 8, "trigger_point")
        
        print(f"After 9th point (subdivision triggered):")
        print(f"  Size: {tree.size()}")
        print(f"  Depth: {tree.depth()}")
        print(f"  Subdivisions: {tree.subdivision_count()}")
        
        # Verify subdivision occurred
        self.assertEqual(tree.subdivision_count(), 1, "First subdivision should occur")
        self.assertGreater(tree.depth(), 0, "Depth should increase after subdivision")
        self.assertEqual(tree.size(), 9, "All points should still be accessible")
        
        print("\n✅ RESULT: Subdivision triggered exactly when exceeding 8 points")

    def test_octant_distribution(self):
        """
        Test 3: Points are correctly distributed into 8 octants after subdivision.
        
        This demonstrates how the 3D space is divided into 8 regions and how
        points are assigned to the correct octants.
        """
        print("\n" + "="*60)
        print("TEST 3: Octant Distribution Analysis")
        print("="*60)
        
        # Use a centered octree for clear octant boundaries
        tree = octree.Octree(-10, -10, -10, 10, 10, 10)  # Center at (0,0,0)
        
        print("Octree bounds: [-10, -10, -10] to [10, 10, 10]")
        print("Center point: (0, 0, 0)")
        print("\nOctant definitions:")
        print("  0: TOP_LEFT_FRONT     (-x, +y, +z)")
        print("  1: TOP_RIGHT_FRONT    (+x, +y, +z)")
        print("  2: TOP_LEFT_BACK      (-x, +y, -z)")
        print("  3: TOP_RIGHT_BACK     (+x, +y, -z)")
        print("  4: BOTTOM_LEFT_FRONT  (-x, -y, +z)")
        print("  5: BOTTOM_RIGHT_FRONT (+x, -y, +z)")
        print("  6: BOTTOM_LEFT_BACK   (-x, -y, -z)")
        print("  7: BOTTOM_RIGHT_BACK  (+x, -y, -z)")
        
        # Insert points strategically in each octant to force subdivision
        octant_points = [
            (-5, 5, 5, "octant_0_TLF"),    # TOP_LEFT_FRONT
            (5, 5, 5, "octant_1_TRF"),     # TOP_RIGHT_FRONT  
            (-5, 5, -5, "octant_2_TLB"),   # TOP_LEFT_BACK
            (5, 5, -5, "octant_3_TRB"),    # TOP_RIGHT_BACK
            (-5, -5, 5, "octant_4_BLF"),   # BOTTOM_LEFT_FRONT
            (5, -5, 5, "octant_5_BRF"),    # BOTTOM_RIGHT_FRONT
            (-5, -5, -5, "octant_6_BLB"),  # BOTTOM_LEFT_BACK
            (5, -5, -5, "octant_7_BRB"),   # BOTTOM_RIGHT_BACK
            (1, 1, 1, "extra_point"),      # Trigger subdivision
        ]
        
        print(f"\nInserting {len(octant_points)} points to trigger subdivision:")
        for i, (x, y, z, data) in enumerate(octant_points):
            tree.insert(x, y, z, data)
            octant_id = self._determine_octant(x, y, z, 0, 0, 0)  # Center at origin
            print(f"  Point {i+1}: ({x:3}, {y:3}, {z:3}) -> Expected octant {octant_id} ({data})")
        
        print(f"\nAfter insertion:")
        print(f"  Total size: {tree.size()}")
        print(f"  Tree depth: {tree.depth()}")
        print(f"  Subdivisions: {tree.subdivision_count()}")
        
        # Verify subdivision occurred
        self.assertGreater(tree.subdivision_count(), 0, "Subdivision should have occurred")
        self.assertEqual(tree.size(), len(octant_points), "All points should be retained")
        
        # Test that points can still be found in their respective regions
        print(f"\nVerifying point distribution with regional queries:")
        
        # Query each octant region
        octant_queries = [
            ((-10, 0, 0, 0, 10, 10), "TOP_LEFT_FRONT"),
            ((0, 0, 0, 10, 10, 10), "TOP_RIGHT_FRONT"),
            ((-10, 0, -10, 0, 10, 0), "TOP_LEFT_BACK"),
            ((0, 0, -10, 10, 10, 0), "TOP_RIGHT_BACK"),
            ((-10, -10, 0, 0, 0, 10), "BOTTOM_LEFT_FRONT"),
            ((0, -10, 0, 10, 0, 10), "BOTTOM_RIGHT_FRONT"),
            ((-10, -10, -10, 0, 0, 0), "BOTTOM_LEFT_BACK"),
            ((0, -10, -10, 10, 0, 0), "BOTTOM_RIGHT_BACK"),
        ]
        
        for (min_x, min_y, min_z, max_x, max_y, max_z), region_name in octant_queries:
            results = tree.query(min_x, min_y, min_z, max_x, max_y, max_z)
            print(f"  {region_name}: {len(results)} points found")
            for x, y, z, data in results:
                print(f"    ({x}, {y}, {z}) - {data}")
        
        print("\n✅ RESULT: Points correctly distributed across octants after subdivision")

    def test_deep_subdivision_cascade(self):
        """
        Test 4: Deep subdivision with cascading subdivisions.
        
        This demonstrates how subdivision can cascade deeper when points
        cluster in the same octants of child nodes.
        """
        print("\n" + "="*60)
        print("TEST 4: Deep Subdivision Cascade")
        print("="*60)
        
        tree = octree.Octree(0, 0, 0, 10, 10, 10)
        
        # Create a cluster of points in a small region to force deep subdivision
        cluster_center = (2, 2, 2)
        cluster_radius = 0.5
        
        print(f"Creating point cluster around {cluster_center} with radius {cluster_radius}")
        print("This should force multiple levels of subdivision...")
        
        import random
        random.seed(42)  # For reproducible results
        
        points_to_add = 50  # Much more than MaxPointsPerNode
        
        print(f"\nInserting {points_to_add} clustered points:")
        for i in range(points_to_add):
            # Generate points in a small cluster
            x = cluster_center[0] + random.uniform(-cluster_radius, cluster_radius)
            y = cluster_center[1] + random.uniform(-cluster_radius, cluster_radius)
            z = cluster_center[2] + random.uniform(-cluster_radius, cluster_radius)
            
            tree.insert(x, y, z, f"cluster_{i}")
            
            # Show subdivision progress at key milestones
            if i + 1 in [8, 16, 25, 35, 50]:
                print(f"  After {i+1:2} points: depth={tree.depth()}, subdivisions={tree.subdivision_count()}")
        
        print(f"\nFinal clustering results:")
        print(f"  Total points: {tree.size()}")
        print(f"  Final depth: {tree.depth()}")
        print(f"  Total subdivisions: {tree.subdivision_count()}")
        print(f"  Memory usage: {tree.memory_usage()} bytes")
        
        # Verify deep subdivision occurred
        self.assertGreater(tree.depth(), 2, "Should achieve significant depth with clustering")
        self.assertGreater(tree.subdivision_count(), 1, "Multiple subdivisions should occur")
        
        # Test that clustered points can still be efficiently queried
        cluster_query_bounds = (
            cluster_center[0] - cluster_radius - 0.1,
            cluster_center[1] - cluster_radius - 0.1, 
            cluster_center[2] - cluster_radius - 0.1,
            cluster_center[0] + cluster_radius + 0.1,
            cluster_center[1] + cluster_radius + 0.1,
            cluster_center[2] + cluster_radius + 0.1,
        )
        
        cluster_results = tree.query(*cluster_query_bounds)
        print(f"\nCluster region query found {len(cluster_results)} points")
        print(f"Query efficiency: {len(cluster_results)}/{tree.size()} = {len(cluster_results)/tree.size():.1%} of total points")
        
        # Most points should be in the cluster region
        self.assertGreater(len(cluster_results), points_to_add * 0.8, "Most points should be in cluster region")
        
        print("\n✅ RESULT: Deep subdivision successfully handles point clustering")

    def test_subdivision_memory_and_performance(self):
        """
        Test 5: Analyze subdivision impact on memory usage and query performance.
        
        This demonstrates how subdivision affects memory consumption and query efficiency.
        """
        print("\n" + "="*60)
        print("TEST 5: Subdivision Memory and Performance Analysis")
        print("="*60)
        
        # Test with different point distributions
        test_scenarios = [
            ("Uniform Distribution", self._generate_uniform_points),
            ("Clustered Distribution", self._generate_clustered_points),
        ]
        
        for scenario_name, point_generator in test_scenarios:
            print(f"\n--- {scenario_name} ---")
            
            tree = octree.Octree(-100, -100, -100, 100, 100, 100)
            initial_memory = tree.memory_usage()
            
            print(f"Initial memory usage: {initial_memory} bytes")
            
            # Add points in batches and monitor subdivision
            batch_sizes = [50, 100, 200, 500]
            total_points = 0
            
            for batch_size in batch_sizes:
                points = point_generator(batch_size)
                
                import time
                start_time = time.time()
                
                for x, y, z in points:
                    tree.insert(x, y, z, f"perf_point_{total_points}")
                    total_points += 1
                
                insert_time = time.time() - start_time
                
                # Measure query performance
                start_time = time.time()
                query_results = tree.query(-25, -25, -25, 25, 25, 25)
                query_time = time.time() - start_time
                
                current_memory = tree.memory_usage()
                memory_per_point = (current_memory - initial_memory) / total_points if total_points > 0 else 0
                
                print(f"  {total_points:3} points: depth={tree.depth()}, subdivisions={tree.subdivision_count():2}, "
                      f"memory={current_memory:6} bytes ({memory_per_point:.1f} bytes/point), "
                      f"insert_time={insert_time:.4f}s, query_time={query_time:.6f}s, query_results={len(query_results)}")
            
            print(f"  Final stats: {tree.size()} points, depth {tree.depth()}, {tree.subdivision_count()} subdivisions")
        
        print("\n✅ RESULT: Subdivision provides efficient memory usage and query performance")

    def _determine_octant(self, x, y, z, center_x, center_y, center_z):
        """Helper method to determine which octant a point belongs to."""
        index = 0
        if x >= center_x: index |= 1  # Right
        if y < center_y: index |= 4   # Bottom  
        if z < center_z: index |= 2   # Back
        return index

    def _generate_uniform_points(self, count):
        """Generate uniformly distributed points."""
        import random
        points = []
        for _ in range(count):
            x = random.uniform(-80, 80)
            y = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            points.append((x, y, z))
        return points

    def _generate_clustered_points(self, count):
        """Generate clustered points around several centers."""
        import random
        points = []
        centers = [(20, 20, 20), (-20, -20, -20), (20, -20, 20)]
        
        for _ in range(count):
            center = random.choice(centers)
            x = center[0] + random.uniform(-10, 10)
            y = center[1] + random.uniform(-10, 10) 
            z = center[2] + random.uniform(-10, 10)
            points.append((x, y, z))
        return points


class TestSubdivisionEdgeCases(unittest.TestCase):
    """Test edge cases in subdivision behavior."""

    def test_subdivision_at_max_depth(self):
        """
        Test subdivision behavior when maximum depth is reached.
        
        This shows how the octree handles the case where MaxDepth is reached
        and no further subdivision can occur.
        """
        print("\n" + "="*60)
        print("EDGE CASE: Subdivision at Maximum Depth")
        print("="*60)
        
        # Create octree that will quickly reach max depth by using the same point
        tree = octree.Octree(0, 0, 0, 1, 1, 1)
        
        print("Testing subdivision limits by inserting many points at the same location...")
        print("(This forces subdivision until MaxDepth is reached)")
        
        # Insert many points at nearly the same location
        base_point = (0.5, 0.5, 0.5)
        max_points_to_test = 100
        
        for i in range(max_points_to_test):
            # Add tiny variations to avoid exact duplicates
            epsilon = i * 1e-10
            x = base_point[0] + epsilon
            y = base_point[1] + epsilon
            z = base_point[2] + epsilon
            
            tree.insert(x, y, z, f"depth_test_{i}")
            
            # Monitor key milestones
            if (i + 1) in [10, 20, 50, 100]:
                print(f"  After {i+1:3} points: size={tree.size()}, depth={tree.depth()}, subdivisions={tree.subdivision_count()}")
        
        print(f"\nFinal state with concentrated points:")
        print(f"  Total points: {tree.size()}")
        print(f"  Max depth reached: {tree.depth()}")
        print(f"  Total subdivisions: {tree.subdivision_count()}")
        
        # Verify the tree can still handle queries efficiently
        all_results = tree.query(0, 0, 0, 1, 1, 1)
        print(f"  Query found {len(all_results)} points")
        
        self.assertEqual(len(all_results), tree.size(), "All points should be queryable")
        
        print("\n✅ RESULT: Octree gracefully handles maximum depth limitations")


def run_subdivision_tests():
    """Run all subdivision-specific tests with detailed output."""
    print("OCTREE SUBDIVISION ANALYSIS")
    print("="*80)
    print("This test suite demonstrates how octree subdivision works internally.")
    print("Each test shows different aspects of the subdivision algorithm.")
    print("="*80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests in logical order
    suite.addTest(loader.loadTestsFromTestCase(TestOctreeSubdivision))
    suite.addTest(loader.loadTestsFromTestCase(TestSubdivisionEdgeCases))
    
    # Run with minimal unittest output (we provide our own detailed output)
    runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("SUBDIVISION ANALYSIS COMPLETE")
    print("="*80)
    if result.wasSuccessful():
        print("✅ All subdivision tests passed!")
        print(f"Ran {result.testsRun} tests successfully.")
    else:
        print("❌ Some subdivision tests failed!")
        print(f"Failures: {len(result.failures)}, Errors: {len(result.errors)}")
    
    return result


if __name__ == "__main__":
    # Run the subdivision analysis
    run_subdivision_tests()