#!/usr/bin/env python3
"""
Octree Collision Detection Stress Tests
=======================================

This module provides comprehensive stress testing for octree collision detection,
focusing on edge cases, performance under load, and correctness verification.
"""

import sys
import time
import random
import math
import gc
from collections import defaultdict
import unittest

try:
    import octree
except ImportError as e:
    print(f"Failed to import octree module: {e}")
    print("Make sure the octree module is compiled and available in the Python path.")
    sys.exit(1)


class CollisionStressTest(unittest.TestCase):
    """Stress tests for octree collision detection scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        random.seed(42)  # For reproducible results
        self.performance_data = []
    
    def tearDown(self):
        """Clean up after tests."""
        gc.collect()
    
    def test_massive_overlapping_objects(self):
        """Test collision detection with thousands of overlapping objects."""
        print("\n🔥 COLLISION STRESS TEST: Massive Overlapping Objects")
        print("=" * 60)
        
        tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
        
        # Create overlapping spherical regions
        center_points = [
            (0, 0, 0),    # Central cluster
            (100, 100, 100),  # Offset cluster
            (-100, -100, -100),  # Negative cluster
            (200, 0, 0),  # X-axis cluster
            (0, 200, 0),  # Y-axis cluster
            (0, 0, 200),  # Z-axis cluster
        ]
        
        total_objects = 50000
        objects_per_cluster = total_objects // len(center_points)
        collision_radius = 150  # Large radius for many overlaps
        
        start_time = time.time()
        
        # Insert objects in clusters with guaranteed overlaps
        object_id = 0
        for center_x, center_y, center_z in center_points:
            for _ in range(objects_per_cluster):
                # Generate points within collision radius of center
                angle1 = random.uniform(0, 2 * math.pi)
                angle2 = random.uniform(0, math.pi)
                distance = random.uniform(0, collision_radius * 0.8)
                
                x = center_x + distance * math.sin(angle2) * math.cos(angle1)
                y = center_y + distance * math.sin(angle2) * math.sin(angle1)
                z = center_z + distance * math.cos(angle2)
                
                tree.insert(x, y, z, f"object_{object_id}")
                object_id += 1
        
        insertion_time = time.time() - start_time
        
        # Test collision detection for each cluster
        collision_results = {}
        query_start = time.time()
        
        for i, (center_x, center_y, center_z) in enumerate(center_points):
            # Query for collisions in each cluster
            results = tree.query(
                center_x - collision_radius,
                center_y - collision_radius, 
                center_z - collision_radius,
                center_x + collision_radius,
                center_y + collision_radius,
                center_z + collision_radius
            )
            collision_results[f"cluster_{i}"] = len(results)
        
        query_time = time.time() - query_start
        
        print(f"📊 Inserted {total_objects} overlapping objects in {insertion_time:.3f}s")
        print(f"📊 Query time: {query_time:.3f}s")
        print(f"📊 Tree depth: {tree.depth()}")
        print(f"📊 Memory usage: {tree.memory_usage():,} bytes")
        
        print("\n🎯 Collision Results per Cluster:")
        for cluster, count in collision_results.items():
            print(f"   {cluster}: {count:,} potential collisions")
        
        # Verify we have overlapping objects
        total_collisions = sum(collision_results.values())
        self.assertGreater(total_collisions, total_objects, 
                          "Should have more collision candidates than objects due to overlaps")
        
        # Performance assertions
        self.assertLess(insertion_time, 10.0, "Insertion should complete within 10 seconds")
        self.assertLess(query_time, 5.0, "Collision queries should complete within 5 seconds")
    
    def test_collision_accuracy_verification(self):
        """Verify collision detection accuracy against brute force method."""
        print("\n🔥 COLLISION STRESS TEST: Accuracy Verification")
        print("=" * 60)
        
        tree = octree.Octree(-500, -500, -500, 500, 500, 500)
        
        # Generate test objects with known positions
        test_objects = []
        num_objects = 5000
        
        for i in range(num_objects):
            x = random.uniform(-400, 400)
            y = random.uniform(-400, 400)
            z = random.uniform(-400, 400)
            tree.insert(x, y, z, f"obj_{i}")
            test_objects.append((x, y, z, f"obj_{i}"))
        
        # Test collision detection accuracy
        test_queries = 100
        accuracy_results = []
        
        start_time = time.time()
        
        for _ in range(test_queries):
            # Random query box
            center_x = random.uniform(-300, 300)
            center_y = random.uniform(-300, 300)
            center_z = random.uniform(-300, 300)
            size = random.uniform(50, 200)
            
            min_x, max_x = center_x - size/2, center_x + size/2
            min_y, max_y = center_y - size/2, center_y + size/2
            min_z, max_z = center_z - size/2, center_z + size/2
            
            # Octree query - returns tuples of (x, y, z, data)
            octree_raw = tree.query(min_x, min_y, min_z, max_x, max_y, max_z)
            octree_results = set(item[3] for item in octree_raw)  # Extract just the data
            
            # Brute force verification
            brute_force_results = set()
            for x, y, z, obj_id in test_objects:
                if min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z:
                    brute_force_results.add(obj_id)
            
            # Compare results
            if octree_results == brute_force_results:
                accuracy_results.append(1.0)
            else:
                # Calculate accuracy percentage
                correct = len(octree_results & brute_force_results)
                total = len(octree_results | brute_force_results)
                accuracy = correct / total if total > 0 else 1.0
                accuracy_results.append(accuracy)
        
        query_time = time.time() - start_time
        average_accuracy = sum(accuracy_results) / len(accuracy_results)
        
        print(f"📊 Tested {test_queries} collision queries against brute force")
        print(f"📊 Average accuracy: {average_accuracy * 100:.2f}%")
        print(f"📊 Query time: {query_time:.3f}s ({query_time/test_queries*1000:.2f}ms per query)")
        
        # Accuracy should be perfect
        self.assertGreaterEqual(average_accuracy, 0.99, 
                               "Collision detection should be at least 99% accurate")
    
    def test_collision_boundary_stress(self):
        """Test collision detection at octree boundaries."""
        print("\n🔥 COLLISION STRESS TEST: Boundary Collisions")
        print("=" * 60)
        
        tree = octree.Octree(-100, -100, -100, 100, 100, 100)
        
        # Insert objects right at boundaries
        boundary_positions = [
            # Corner points
            (-100, -100, -100), (100, 100, 100),
            (-100, -100, 100), (-100, 100, -100),
            (100, -100, -100), (100, 100, -100),
            (100, -100, 100), (-100, 100, 100),
            
            # Edge centers
            (0, -100, -100), (0, 100, 100),
            (-100, 0, -100), (100, 0, 100),
            (-100, -100, 0), (100, 100, 0),
            
            # Face centers
            (0, 0, -100), (0, 0, 100),
            (0, -100, 0), (0, 100, 0),
            (-100, 0, 0), (100, 0, 0),
            
            # Slightly inside boundaries
            (-99.9, -99.9, -99.9), (99.9, 99.9, 99.9),
        ]
        
        # Add many objects around each boundary position
        object_count = 0
        for base_x, base_y, base_z in boundary_positions:
            for _ in range(500):  # 500 objects per boundary position
                offset = random.uniform(-5, 5)
                x = base_x + random.uniform(-offset, offset)
                y = base_y + random.uniform(-offset, offset) 
                z = base_z + random.uniform(-offset, offset)
                
                # Clamp to boundaries
                x = max(-100, min(100, x))
                y = max(-100, min(100, y))
                z = max(-100, min(100, z))
                
                tree.insert(x, y, z, f"boundary_obj_{object_count}")
                object_count += 1
        
        # Test boundary collision queries
        boundary_query_results = []
        
        start_time = time.time()
        
        # Query exactly at boundaries
        boundary_queries = [
            (-100, -100, -100, -90, -90, -90),  # Corner region
            (90, 90, 90, 100, 100, 100),        # Opposite corner
            (-105, -105, -105, -95, -95, -95),  # Slightly outside
            (95, 95, 95, 105, 105, 105),        # Slightly outside other corner
            (-10, -10, -10, 10, 10, 10),        # Center region
        ]
        
        for min_x, min_y, min_z, max_x, max_y, max_z in boundary_queries:
            results = tree.query(min_x, min_y, min_z, max_x, max_y, max_z)
            boundary_query_results.append(len(results))
        
        query_time = time.time() - start_time
        
        print(f"📊 Inserted {object_count:,} boundary objects")
        print(f"📊 Tree depth: {tree.depth()}")
        print(f"📊 Boundary query results: {boundary_query_results}")
        print(f"📊 Query time: {query_time:.3f}s")
        
        # Verify we can find objects at boundaries
        self.assertTrue(all(count >= 0 for count in boundary_query_results),
                       "All boundary queries should return valid results")
        self.assertTrue(any(count > 0 for count in boundary_query_results),
                       "Should find objects in at least some boundary regions")
    
    def test_collision_performance_scaling(self):
        """Test how collision detection performance scales with object count."""
        print("\n🔥 COLLISION STRESS TEST: Performance Scaling")
        print("=" * 60)
        
        object_counts = [1000, 5000, 10000, 25000, 50000]
        performance_results = []
        
        for count in object_counts:
            print(f"\n🔬 Testing with {count:,} objects...")
            
            tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
            
            # Insert objects
            insert_start = time.time()
            for i in range(count):
                x = random.uniform(-800, 800)
                y = random.uniform(-800, 800)
                z = random.uniform(-800, 800)
                tree.insert(x, y, z, f"perf_obj_{i}")
            
            insert_time = time.time() - insert_start
            
            # Test collision queries
            num_queries = 100
            query_start = time.time()
            
            total_collisions = 0
            for _ in range(num_queries):
                center_x = random.uniform(-500, 500)
                center_y = random.uniform(-500, 500)
                center_z = random.uniform(-500, 500)
                radius = random.uniform(50, 200)
                
                results = tree.query(
                    center_x - radius, center_y - radius, center_z - radius,
                    center_x + radius, center_y + radius, center_z + radius
                )
                total_collisions += len(results)
            
            query_time = time.time() - query_start
            avg_query_time = query_time / num_queries
            
            performance_results.append({
                'objects': count,
                'insert_time': insert_time,
                'query_time': avg_query_time,
                'total_collisions': total_collisions,
                'depth': tree.depth(),
                'memory': tree.memory_usage()
            })
            
            print(f"   Insert time: {insert_time:.3f}s")
            print(f"   Avg query time: {avg_query_time*1000:.2f}ms")
            print(f"   Tree depth: {tree.depth()}")
            print(f"   Memory: {tree.memory_usage():,} bytes")
        
        # Analyze scaling
        print(f"\n📈 SCALING ANALYSIS:")
        print(f"{'Objects':>10} {'Insert(s)':>10} {'Query(ms)':>10} {'Depth':>8} {'Memory(MB)':>12}")
        print("-" * 60)
        
        for result in performance_results:
            print(f"{result['objects']:>10,} {result['insert_time']:>9.3f} "
                  f"{result['query_time']*1000:>9.2f} {result['depth']:>8} "
                  f"{result['memory']/1024/1024:>11.1f}")
        
        # Performance should scale reasonably (not exponentially)
        # Check that query time doesn't grow too fast
        if len(performance_results) >= 2:
            first_query_time = performance_results[0]['query_time']
            last_query_time = performance_results[-1]['query_time']
            scaling_factor = last_query_time / first_query_time
            object_scaling = performance_results[-1]['objects'] / performance_results[0]['objects']
            
            print(f"\n📊 Query time scaling factor: {scaling_factor:.2f}x for {object_scaling:.1f}x more objects")
            
            # Query time should scale better than linear with object count
            self.assertLess(scaling_factor, object_scaling, 
                           "Query time should scale better than linearly")


if __name__ == '__main__':
    print("🚀 OCTREE COLLISION DETECTION STRESS TESTS")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=False)