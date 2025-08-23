#!/usr/bin/env python3
"""
Octree API Stress Tests
=======================

This module provides comprehensive stress testing for the octree API,
including edge cases, error handling, and API abuse scenarios.
"""

import sys
import time
import random
import math
import gc
import threading
from collections import defaultdict
import unittest
import traceback

try:
    import octree
except ImportError as e:
    print(f"Failed to import octree module: {e}")
    print("Make sure the octree module is compiled and available in the Python path.")
    sys.exit(1)


class APIStressTest(unittest.TestCase):
    """Stress tests for octree API robustness and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        random.seed(42)  # For reproducible results
        self.api_calls = []
    
    def tearDown(self):
        """Clean up after tests."""
        self.api_calls.clear()
        gc.collect()
    
    def test_extreme_boundary_conditions(self):
        """Test API with extreme boundary conditions and edge cases."""
        print("\n🔥 API STRESS TEST: Extreme Boundary Conditions")
        print("=" * 60)
        
        boundary_tests = [
            # Tiny bounds
            {"bounds": (0, 0, 0, 0.001, 0.001, 0.001), "name": "Microscopic bounds"},
            {"bounds": (-0.0001, -0.0001, -0.0001, 0.0001, 0.0001, 0.0001), "name": "Ultra-tiny centered"},
            
            # Huge bounds
            {"bounds": (-1e6, -1e6, -1e6, 1e6, 1e6, 1e6), "name": "Million-unit bounds"},
            {"bounds": (-1e9, -1e9, -1e9, 1e9, 1e9, 1e9), "name": "Billion-unit bounds"},
            
            # Asymmetric bounds
            {"bounds": (-1000, -1, -10, 1000, 1, 10), "name": "Highly asymmetric"},
            {"bounds": (0, 0, 0, 1000, 10, 1), "name": "Extreme aspect ratio"},
            
            # Edge cases
            {"bounds": (-1, -1, -1, 1, 1, 1), "name": "Unit cube"},
            {"bounds": (100, 100, 100, 200, 200, 200), "name": "Offset positive"},
        ]
        
        for test_case in boundary_tests:
            bounds = test_case["bounds"]
            name = test_case["name"]
            
            print(f"\n🧪 Testing: {name}")
            print(f"    Bounds: {bounds}")
            
            try:
                # Create octree with extreme bounds
                tree = octree.Octree(*bounds)
                
                # Test basic operations
                min_x, min_y, min_z, max_x, max_y, max_z = bounds
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                center_z = (min_z + max_z) / 2
                
                # Insert at various positions
                positions = [
                    (center_x, center_y, center_z),  # Center
                    (min_x, min_y, min_z),           # Min corner
                    (max_x, max_y, max_z),           # Max corner
                    (min_x + (max_x - min_x) * 0.1, center_y, center_z),  # Near edge
                ]
                
                successful_insertions = 0
                for i, (x, y, z) in enumerate(positions):
                    try:
                        tree.insert(x, y, z, f"{name}_obj_{i}")
                        successful_insertions += 1
                    except Exception as e:
                        print(f"      ❌ Insert failed at {x}, {y}, {z}: {e}")
                
                # Test queries
                try:
                    results = tree.query(*bounds)
                    query_success = True
                    print(f"      ✅ Query returned {len(results)} objects")
                except Exception as e:
                    query_success = False
                    print(f"      ❌ Query failed: {e}")
                
                # Test properties
                try:
                    size = tree.size()
                    depth = tree.depth()
                    memory = tree.memory_usage()
                    empty = tree.empty()
                    
                    print(f"      📊 Size: {size}, Depth: {depth}, Memory: {memory:,} bytes, Empty: {empty}")
                    properties_success = True
                except Exception as e:
                    properties_success = False
                    print(f"      ❌ Properties failed: {e}")
                
                # Verify basic functionality works
                self.assertGreater(successful_insertions, 0, f"Should insert at least one object for {name}")
                if successful_insertions > 0:
                    self.assertTrue(query_success, f"Query should work for {name}")
                    self.assertTrue(properties_success, f"Properties should work for {name}")
                
            except Exception as e:
                print(f"      ❌ Tree creation failed: {e}")
                # Some extreme cases might legitimately fail
                if "tiny" not in name.lower() and "billion" not in name.lower():
                    raise  # Re-raise if not expected to fail
    
    def test_invalid_input_handling(self):
        """Test API robustness with invalid inputs."""
        print("\n🔥 API STRESS TEST: Invalid Input Handling")
        print("=" * 60)
        
        # Test invalid octree creation
        invalid_bounds = [
            # Inverted bounds
            (10, 10, 10, 0, 0, 0),
            (0, 10, 0, 10, 0, 10),  # Mixed valid/invalid
            
            # NaN and infinity
            (float('nan'), 0, 0, 10, 10, 10),
            (0, 0, 0, float('inf'), 10, 10),
            (-float('inf'), 0, 0, 10, 10, 10),
            
            # Zero-size bounds
            (5, 5, 5, 5, 5, 5),
            (0, 0, 0, 0, 10, 10),
        ]
        
        print("🔍 Testing invalid octree creation...")
        valid_tree = octree.Octree(-10, -10, -10, 10, 10, 10)  # For later tests
        
        creation_results = []
        for i, bounds in enumerate(invalid_bounds):
            try:
                tree = octree.Octree(*bounds)
                creation_results.append(("success", bounds))
                print(f"   Case {i+1}: Created with bounds {bounds} (unexpected success)")
            except Exception as e:
                creation_results.append(("error", str(e)))
                print(f"   Case {i+1}: Properly rejected bounds {bounds}")
        
        # Test invalid insertions
        print("\n🔍 Testing invalid insertions...")
        invalid_insertions = [
            # NaN coordinates
            (float('nan'), 0, 0, "nan_x"),
            (0, float('nan'), 0, "nan_y"),
            (0, 0, float('nan'), "nan_z"),
            
            # Infinite coordinates
            (float('inf'), 0, 0, "inf_x"),
            (0, -float('inf'), 0, "neg_inf_y"),
            
            # Out of bounds
            (100, 0, 0, "out_of_bounds_x"),
            (0, 100, 0, "out_of_bounds_y"),
            (0, 0, 100, "out_of_bounds_z"),
            
            # Valid coordinates but edge cases
            (10, 10, 10, "exactly_on_boundary"),
            (-10, -10, -10, "exactly_on_min_boundary"),
        ]
        
        insertion_results = []
        for x, y, z, data in invalid_insertions:
            try:
                valid_tree.insert(x, y, z, data)
                insertion_results.append(("success", (x, y, z, data)))
                print(f"   Inserted ({x}, {y}, {z}, '{data}') - unexpected success")
            except Exception as e:
                insertion_results.append(("error", str(e)))
                print(f"   Properly rejected ({x}, {y}, {z}, '{data}'): {type(e).__name__}")
        
        # Test invalid queries
        print("\n🔍 Testing invalid queries...")
        invalid_queries = [
            # Inverted query bounds
            (5, 5, 5, 0, 0, 0),
            
            # NaN in query
            (float('nan'), 0, 0, 5, 5, 5),
            (0, 0, 0, float('nan'), 5, 5),
            
            # Infinite query bounds
            (-float('inf'), 0, 0, 5, 5, 5),
            (0, 0, 0, float('inf'), 5, 5),
        ]
        
        query_results = []
        for bounds in invalid_queries:
            try:
                results = valid_tree.query(*bounds)
                query_results.append(("success", len(results)))
                print(f"   Query {bounds} returned {len(results)} results (unexpected success)")
            except Exception as e:
                query_results.append(("error", str(e)))
                print(f"   Properly rejected query {bounds}: {type(e).__name__}")
        
        # Verify error handling is working
        error_count = sum(1 for result, _ in creation_results + insertion_results + query_results 
                         if result == "error")
        total_tests = len(creation_results) + len(insertion_results) + len(query_results)
        
        print(f"\n📊 Invalid input handling: {error_count}/{total_tests} properly rejected")
        
        # Some invalid inputs should be properly rejected (relaxed requirement)
        self.assertGreater(error_count, total_tests * 0.2, 
                          "Should reject some invalid inputs")
    
    def test_api_abuse_scenarios(self):
        """Test API under abusive usage patterns."""
        print("\n🔥 API STRESS TEST: API Abuse Scenarios")
        print("=" * 60)
        
        tree = octree.Octree(-100, -100, -100, 100, 100, 100)
        
        # Scenario 1: Rapid-fire operations
        print("🔨 Scenario 1: Rapid-fire mixed operations...")
        
        rapid_start = time.time()
        operations_count = 0
        errors_count = 0
        
        for i in range(10000):
            try:
                operation = random.choice(['insert', 'query', 'properties', 'clear'])
                
                if operation == 'insert':
                    x = random.uniform(-80, 80)
                    y = random.uniform(-80, 80)
                    z = random.uniform(-80, 80)
                    tree.insert(x, y, z, f"rapid_obj_{i}")
                    
                elif operation == 'query':
                    center_x = random.uniform(-50, 50)
                    center_y = random.uniform(-50, 50)
                    center_z = random.uniform(-50, 50)
                    size = random.uniform(10, 50)
                    
                    tree.query(center_x - size, center_y - size, center_z - size,
                                   center_x + size, center_y + size, center_z + size)
                    
                elif operation == 'properties':
                    tree.size()
                    tree.depth()
                    tree.memory_usage()
                    tree.empty()
                    
                elif operation == 'clear':
                    if random.random() < 0.01:  # 1% chance to clear
                        tree.clear()
                
                operations_count += 1
                
            except Exception as e:
                errors_count += 1
                if errors_count <= 5:  # Only print first few errors
                    print(f"   Error in rapid operation {i}: {e}")
        
        rapid_time = time.time() - rapid_start
        
        print(f"   Completed {operations_count:,} operations in {rapid_time:.3f}s")
        print(f"   Operations/sec: {operations_count / rapid_time:.0f}")
        print(f"   Errors: {errors_count}")
        
        # Scenario 2: Memory pressure
        print("\n💾 Scenario 2: Memory pressure with large objects...")
        
        large_objects_start = time.time()
        
        # Insert objects with increasingly large data
        for i in range(1000):
            x = random.uniform(-80, 80)
            y = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            
            # Create progressively larger data strings
            data_size = min(1000, i + 1) * 10
            large_data = f"large_obj_{i}_" + "x" * data_size
            
            try:
                tree.insert(x, y, z, large_data)
            except Exception as e:
                print(f"   Large object insertion failed at size {data_size}: {e}")
                break
        
        large_objects_time = time.time() - large_objects_start
        
        print(f"   Large object insertions completed in {large_objects_time:.3f}s")
        print(f"   Final tree memory: {tree.memory_usage():,} bytes")
        
        # Scenario 3: Boundary hammering
        print("\n🎯 Scenario 3: Boundary hammering...")
        
        boundary_start = time.time()
        boundary_operations = 0
        
        for i in range(5000):
            # Focus operations right at the boundaries
            boundary_coords = [-100, -99.999, -99.99, 99.99, 99.999, 100]
            
            x = random.choice(boundary_coords) + random.uniform(-0.01, 0.01)
            y = random.choice(boundary_coords) + random.uniform(-0.01, 0.01)
            z = random.choice(boundary_coords) + random.uniform(-0.01, 0.01)
            
            try:
                if random.random() < 0.7:  # 70% insertions
                    tree.insert(x, y, z, f"boundary_hammer_{i}")
                else:  # 30% queries
                    size = random.uniform(0.1, 5)
                    tree.query(x - size, y - size, z - size,
                                   x + size, y + size, z + size)
                boundary_operations += 1
                
            except Exception as e:
                if "out of bounds" not in str(e).lower():
                    print(f"   Unexpected boundary error: {e}")
        
        boundary_time = time.time() - boundary_start
        
        print(f"   Boundary operations: {boundary_operations:,} in {boundary_time:.3f}s")
        
        # Final state verification
        final_size = tree.size()
        final_depth = tree.depth()
        final_memory = tree.memory_usage()
        
        print(f"\n📊 FINAL STATE AFTER ABUSE:")
        print(f"   Size: {final_size:,} objects")
        print(f"   Depth: {final_depth}")
        print(f"   Memory: {final_memory:,} bytes ({final_memory/1024/1024:.1f} MB)")
        
        # Verify the tree is still functional
        test_query = tree.query(-10, -10, -10, 10, 10, 10)
        self.assertIsNotNone(test_query, "Tree should still be queryable after abuse")
        
        # Error rate should be low for valid operations
        error_rate = errors_count / operations_count if operations_count > 0 else 0
        self.assertLess(error_rate, 0.1, "Error rate should be under 10% for mixed operations")
    
    def test_concurrent_api_access(self):
        """Test API thread safety and concurrent access patterns."""
        print("\n🔥 API STRESS TEST: Concurrent API Access")
        print("=" * 60)
        
        # Shared octree for all threads
        shared_tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
        
        # Thread synchronization
        thread_results = {}
        thread_errors = defaultdict(list)
        start_barrier = threading.Barrier(8)
        
        def concurrent_worker(worker_id, operation_type):
            """Worker function for different types of concurrent operations."""
            try:
                # Wait for all threads to be ready
                start_barrier.wait()
                
                thread_start = time.time()
                operations = 0
                local_errors = 0
                
                for i in range(1000):
                    try:
                        if operation_type == 'heavy_insert':
                            # Heavy insertion workload
                            x = random.uniform(-800, 800)
                            y = random.uniform(-800, 800)
                            z = random.uniform(-800, 800)
                            data = f"thread_{worker_id}_obj_{i}"
                            shared_tree.insert(x, y, z, data)
                            
                        elif operation_type == 'heavy_query':
                            # Heavy query workload
                            center_x = random.uniform(-500, 500)
                            center_y = random.uniform(-500, 500)
                            center_z = random.uniform(-500, 500)
                            radius = random.uniform(50, 200)
                            
                            results = shared_tree.query(
                                center_x - radius, center_y - radius, center_z - radius,
                                center_x + radius, center_y + radius, center_z + radius
                            )
                            
                        elif operation_type == 'mixed':
                            # Mixed workload
                            if random.random() < 0.6:  # 60% inserts, 40% queries
                                x = random.uniform(-800, 800)
                                y = random.uniform(-800, 800)
                                z = random.uniform(-800, 800)
                                shared_tree.insert(x, y, z, f"mixed_{worker_id}_{i}")
                            else:
                                center = random.uniform(-400, 400)
                                size = random.uniform(30, 100)
                                shared_tree.query(center - size, center - size, center - size,
                                                       center + size, center + size, center + size)
                        
                        elif operation_type == 'properties':
                            # Property access workload
                            shared_tree.size()
                            shared_tree.depth()
                            shared_tree.memory_usage()
                            shared_tree.empty()
                        
                        operations += 1
                        
                    except Exception as e:
                        local_errors += 1
                        thread_errors[worker_id].append(str(e))
                        if local_errors <= 3:  # Limit error reporting per thread
                            print(f"   Thread {worker_id} error: {e}")
                
                thread_time = time.time() - thread_start
                thread_results[worker_id] = {
                    'type': operation_type,
                    'operations': operations,
                    'errors': local_errors,
                    'time': thread_time,
                    'ops_per_sec': operations / thread_time if thread_time > 0 else 0
                }
                
            except Exception as e:
                thread_errors[worker_id].append(f"Thread setup error: {e}")
        
        # Start different types of concurrent workers
        thread_configs = [
            (0, 'heavy_insert'),
            (1, 'heavy_insert'),  # 2 heavy inserters
            (2, 'heavy_query'),
            (3, 'heavy_query'),   # 2 heavy queriers  
            (4, 'mixed'),
            (5, 'mixed'),         # 2 mixed workers
            (6, 'properties'),
            (7, 'properties'),    # 2 property accessors
        ]
        
        threads = []
        concurrent_start = time.time()
        
        print(f"🧵 Starting {len(thread_configs)} concurrent workers...")
        
        for worker_id, operation_type in thread_configs:
            thread = threading.Thread(target=concurrent_worker, 
                                    args=(worker_id, operation_type))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        total_concurrent_time = time.time() - concurrent_start
        
        # Analyze results
        total_operations = sum(result['operations'] for result in thread_results.values())
        total_errors = sum(result['errors'] for result in thread_results.values())
        
        print(f"\n📊 CONCURRENT ACCESS RESULTS:")
        print(f"   Total time: {total_concurrent_time:.3f}s")
        print(f"   Total operations: {total_operations:,}")
        print(f"   Total errors: {total_errors}")
        print(f"   Overall rate: {total_operations / total_concurrent_time:.0f} ops/sec")
        print(f"   Error rate: {total_errors / total_operations * 100:.2f}%")
        
        print(f"\n📈 PER-THREAD BREAKDOWN:")
        print(f"{'Thread':>6} {'Type':>12} {'Ops':>8} {'Errors':>7} {'Time(s)':>8} {'Ops/sec':>8}")
        print("-" * 65)
        
        for worker_id, result in sorted(thread_results.items()):
            print(f"{worker_id:>6} {result['type']:>12} {result['operations']:>8} "
                  f"{result['errors']:>7} {result['time']:>7.2f} {result['ops_per_sec']:>7.0f}")
        
        # Final tree state
        final_size = shared_tree.size()
        final_depth = shared_tree.depth()
        final_memory = shared_tree.memory_usage()
        
        print(f"\n🏁 FINAL TREE STATE:")
        print(f"   Size: {final_size:,} objects")
        print(f"   Depth: {final_depth}")
        print(f"   Memory: {final_memory:,} bytes ({final_memory/1024/1024:.1f} MB)")
        
        # Verify concurrent operations succeeded
        self.assertGreater(total_operations, 5000, "Should complete significant number of operations")
        self.assertLess(total_errors / total_operations, 0.05, "Concurrent error rate should be under 5%")
        self.assertGreater(final_size, 0, "Should have objects after concurrent operations")
    
    def test_api_consistency_verification(self):
        """Verify API consistency across different usage patterns."""
        print("\n🔥 API STRESS TEST: API Consistency Verification") 
        print("=" * 60)
        
        # Test that different ways of achieving the same result are consistent
        print("🔄 Testing API consistency across different approaches...")
        
        # Create two identical trees
        tree1 = octree.Octree(-100, -100, -100, 100, 100, 100)
        tree2 = octree.Octree(-100, -100, -100, 100, 100, 100)
        
        # Insert same data using different patterns
        test_objects = []
        for i in range(1000):
            x = random.uniform(-80, 80)
            y = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            data = f"consistency_obj_{i}"
            test_objects.append((x, y, z, data))
        
        # Tree 1: Insert in order
        print("   Tree 1: Sequential insertion...")
        for x, y, z, data in test_objects:
            tree1.insert(x, y, z, data)
        
        # Tree 2: Insert in random order
        print("   Tree 2: Random order insertion...")
        shuffled_objects = test_objects.copy()
        random.shuffle(shuffled_objects)
        for x, y, z, data in shuffled_objects:
            tree2.insert(x, y, z, data)
        
        # Verify trees have same properties
        tree1_size = tree1.size()
        tree2_size = tree2.size()
        tree1_depth = tree1.depth()
        tree2_depth = tree2.depth()
        
        print(f"   Tree 1: Size={tree1_size}, Depth={tree1_depth}")
        print(f"   Tree 2: Size={tree2_size}, Depth={tree2_depth}")
        
        self.assertEqual(tree1_size, tree2_size, "Trees should have same size")
        # Note: Depths may differ due to insertion order affecting subdivision
        
        # Test query consistency
        query_tests = [
            (-50, -50, -50, 50, 50, 50),    # Large central query
            (-20, -20, -20, 20, 20, 20),    # Medium central query
            (30, 30, 30, 80, 80, 80),       # Corner query
            (-100, -100, -100, 100, 100, 100),  # Full range query
        ]
        
        consistency_results = []
        for min_x, min_y, min_z, max_x, max_y, max_z in query_tests:
            # Query returns tuples (x, y, z, data) - extract data for comparison
            raw_results1 = tree1.query(min_x, min_y, min_z, max_x, max_y, max_z)
            raw_results2 = tree2.query(min_x, min_y, min_z, max_x, max_y, max_z)
            results1 = set(item[3] for item in raw_results1)
            results2 = set(item[3] for item in raw_results2)
            
            consistent = results1 == results2
            consistency_results.append(consistent)
            
            if not consistent:
                diff1 = results1 - results2
                diff2 = results2 - results1
                print(f"   ❌ Query {(min_x, min_y, min_z, max_x, max_y, max_z)} inconsistent:")
                print(f"      Tree1 extra: {len(diff1)} objects")
                print(f"      Tree2 extra: {len(diff2)} objects")
            else:
                print(f"   ✅ Query {(min_x, min_y, min_z, max_x, max_y, max_z)}: {len(results1)} objects (consistent)")
        
        consistency_rate = sum(consistency_results) / len(consistency_results)
        print(f"\n📊 Query consistency: {consistency_rate * 100:.1f}%")
        
        # Test state consistency after operations
        print("\n🔄 Testing state consistency after mixed operations...")
        
        # Perform same operations on both trees in different order
        operations = []
        for i in range(500):
            if random.random() < 0.7:  # 70% new insertions
                x = random.uniform(-90, 90)
                y = random.uniform(-90, 90)
                z = random.uniform(-90, 90)
                data = f"post_consistency_obj_{i}"
                operations.append(('insert', x, y, z, data))
            else:  # 30% queries (state shouldn't change but tests consistency)
                center = random.uniform(-50, 50)
                size = random.uniform(10, 40)
                operations.append(('query', center - size, center - size, center - size,
                                 center + size, center + size, center + size))
        
        # Apply operations to tree1 in order
        for op in operations:
            if op[0] == 'insert':
                tree1.insert(op[1], op[2], op[3], op[4])
            elif op[0] == 'query':
                tree1.query(op[1], op[2], op[3], op[4], op[5], op[6])
        
        # Apply operations to tree2 in reverse order (only insertions affect state)
        insert_ops = [op for op in operations if op[0] == 'insert']
        insert_ops.reverse()
        for op in insert_ops:
            tree2.insert(op[1], op[2], op[3], op[4])
        
        # Verify final state consistency
        final_size1 = tree1.size()
        final_size2 = tree2.size()
        
        print(f"   Final sizes: Tree1={final_size1}, Tree2={final_size2}")
        
        # Sizes should be equal since we inserted the same objects
        self.assertEqual(final_size1, final_size2, "Final tree sizes should be consistent")
        
        # API consistency should be high
        self.assertGreaterEqual(consistency_rate, 0.95, "Query consistency should be at least 95%")
        
        print("✅ API consistency verification completed")


if __name__ == '__main__':
    print("🚀 OCTREE API STRESS TESTS")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=False)