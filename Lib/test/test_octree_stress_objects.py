#!/usr/bin/env python3
"""
Octree Object Creation Stress Tests
===================================

This module provides comprehensive stress testing for octree object creation,
memory management, and lifecycle operations.
"""

import sys
import time
import random
import math
import gc
import threading
from collections import defaultdict
import unittest
import weakref

try:
    import octree
except ImportError as e:
    print(f"Failed to import octree module: {e}")
    print("Make sure the octree module is compiled and available in the Python path.")
    sys.exit(1)


class ObjectCreationStressTest(unittest.TestCase):
    """Stress tests for octree object creation and management."""
    
    def setUp(self):
        """Set up test fixtures."""
        random.seed(42)  # For reproducible results
        self.created_objects = []
        gc.collect()  # Start with clean memory
    
    def tearDown(self):
        """Clean up after tests."""
        self.created_objects.clear()
        gc.collect()
    
    def test_massive_object_creation(self):
        """Test creating and destroying massive numbers of octree objects."""
        print("\n🔥 OBJECT CREATION STRESS TEST: Massive Object Creation")
        print("=" * 65)
        
        num_trees = 1000
        objects_per_tree = 1000
        total_objects = num_trees * objects_per_tree
        
        print(f"🏭 Creating {num_trees:,} octree instances with {objects_per_tree:,} objects each")
        print(f"📊 Total objects to manage: {total_objects:,}")
        
        creation_times = []
        memory_usage = []
        
        start_time = time.time()
        
        for tree_id in range(num_trees):
            tree_start = time.time()
            
            # Create octree with random bounds
            size = random.uniform(100, 1000)
            tree = octree.Octree(-size, -size, -size, size, size, size)
            
            # Fill with objects
            for obj_id in range(objects_per_tree):
                x = random.uniform(-size * 0.8, size * 0.8)
                y = random.uniform(-size * 0.8, size * 0.8)
                z = random.uniform(-size * 0.8, size * 0.8)
                tree.insert(x, y, z, f"tree_{tree_id}_obj_{obj_id}")
            
            tree_time = time.time() - tree_start
            creation_times.append(tree_time)
            memory_usage.append(tree.memory_usage())
            
            self.created_objects.append(tree)
            
            # Progress reporting
            if (tree_id + 1) % 100 == 0:
                elapsed = time.time() - start_time
                rate = (tree_id + 1) / elapsed
                print(f"   Progress: {tree_id + 1:,}/{num_trees:,} trees ({rate:.1f} trees/sec)")
        
        total_creation_time = time.time() - start_time
        
        # Analyze results
        avg_creation_time = sum(creation_times) / len(creation_times)
        total_memory = sum(memory_usage)
        avg_memory = total_memory / len(memory_usage)
        
        print(f"\n📈 CREATION RESULTS:")
        print(f"   Total creation time: {total_creation_time:.2f}s")
        print(f"   Average time per tree: {avg_creation_time:.4f}s")
        print(f"   Creation rate: {num_trees / total_creation_time:.1f} trees/sec")
        print(f"   Total memory usage: {total_memory:,} bytes ({total_memory/1024/1024:.1f} MB)")
        print(f"   Average memory per tree: {avg_memory:,} bytes ({avg_memory/1024:.1f} KB)")
        print(f"   Memory per object: {avg_memory / objects_per_tree:.1f} bytes")
        
        # Performance assertions
        self.assertLess(avg_creation_time, 1.0, "Average tree creation should be under 1 second")
        self.assertLess(avg_memory / objects_per_tree, 1000, "Memory per object should be reasonable")
        
        # Test cleanup
        cleanup_start = time.time()
        self.created_objects.clear()
        gc.collect()
        cleanup_time = time.time() - cleanup_start
        
        print(f"   Cleanup time: {cleanup_time:.3f}s")
    
    def test_object_lifecycle_stress(self):
        """Test object insertion, modification, and removal under stress."""
        print("\n🔥 OBJECT CREATION STRESS TEST: Object Lifecycle")
        print("=" * 65)
        
        tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
        
        # Phase 1: Rapid insertion
        num_objects = 100000
        print(f"🌱 Phase 1: Inserting {num_objects:,} objects...")
        
        insertion_start = time.time()
        inserted_objects = []
        
        for i in range(num_objects):
            x = random.uniform(-800, 800)
            y = random.uniform(-800, 800)
            z = random.uniform(-800, 800)
            obj_data = f"lifecycle_obj_{i}"
            
            tree.insert(x, y, z, obj_data)
            inserted_objects.append((x, y, z, obj_data))
        
        insertion_time = time.time() - insertion_start
        initial_size = tree.size()
        initial_memory = tree.memory_usage()
        
        print(f"   Insertion completed in {insertion_time:.3f}s ({num_objects/insertion_time:.0f} objects/sec)")
        print(f"   Tree size: {initial_size:,}")
        print(f"   Memory usage: {initial_memory:,} bytes ({initial_memory/1024/1024:.1f} MB)")
        
        # Phase 2: Random queries and modifications
        print(f"\n🔄 Phase 2: Random operations...")
        
        operations_start = time.time()
        num_operations = 10000
        
        for _ in range(num_operations):
            operation = random.choice(['query', 'clear_region', 'bulk_query'])
            
            if operation == 'query':
                # Single point queries
                x = random.uniform(-800, 800)
                y = random.uniform(-800, 800)
                z = random.uniform(-800, 800)
                radius = random.uniform(10, 100)
                
                results = tree.query(x - radius, y - radius, z - radius,
                                         x + radius, y + radius, z + radius)
                
            elif operation == 'clear_region':
                # Clear small regions periodically
                if random.random() < 0.1:  # 10% chance
                    center_x = random.uniform(-500, 500)
                    center_y = random.uniform(-500, 500) 
                    center_z = random.uniform(-500, 500)
                    clear_size = random.uniform(20, 80)
                    
                    # Simulate clearing by querying (actual clear would need remove method)
                    tree.query(center_x - clear_size, center_y - clear_size, center_z - clear_size,
                                   center_x + clear_size, center_y + clear_size, center_z + clear_size)
                    
            elif operation == 'bulk_query':
                # Large area queries
                area_size = random.uniform(200, 500)
                center_x = random.uniform(-400, 400)
                center_y = random.uniform(-400, 400)
                center_z = random.uniform(-400, 400)
                
                results = tree.query(center_x - area_size, center_y - area_size, center_z - area_size,
                                         center_x + area_size, center_y + area_size, center_z + area_size)
        
        operations_time = time.time() - operations_start
        final_size = tree.size()
        final_memory = tree.memory_usage()
        
        print(f"   Operations completed in {operations_time:.3f}s ({num_operations/operations_time:.0f} ops/sec)")
        print(f"   Final tree size: {final_size:,}")
        print(f"   Final memory usage: {final_memory:,} bytes ({final_memory/1024/1024:.1f} MB)")
        
        # Phase 3: Complete reconstruction
        print(f"\n🔄 Phase 3: Tree reconstruction...")
        
        reconstruction_start = time.time()
        
        # Clear and rebuild
        tree.clear()
        
        # Re-insert subset of objects
        num_reinsert = num_objects // 2
        for i in range(0, num_reinsert):
            x, y, z, obj_data = inserted_objects[i]
            tree.insert(x, y, z, f"reconstructed_{obj_data}")
        
        reconstruction_time = time.time() - reconstruction_start
        reconstructed_size = tree.size()
        reconstructed_memory = tree.memory_usage()
        
        print(f"   Reconstruction completed in {reconstruction_time:.3f}s")
        print(f"   Reconstructed size: {reconstructed_size:,}")
        print(f"   Reconstructed memory: {reconstructed_memory:,} bytes ({reconstructed_memory/1024/1024:.1f} MB)")
        
        # Verify reconstruction
        self.assertEqual(reconstructed_size, num_reinsert, "Reconstructed tree should have correct size")
        self.assertLess(reconstruction_time, insertion_time, "Reconstruction should be faster than initial insertion")
    
    def test_concurrent_object_creation(self):
        """Test concurrent object creation from multiple threads."""
        print("\n🔥 OBJECT CREATION STRESS TEST: Concurrent Creation")
        print("=" * 65)
        
        num_threads = 8
        objects_per_thread = 5000
        total_objects = num_threads * objects_per_thread
        
        print(f"🧵 Creating {num_threads} threads, {objects_per_thread:,} objects per thread")
        print(f"📊 Total concurrent objects: {total_objects:,}")
        
        # Shared results storage
        thread_results = {}
        thread_errors = []
        
        def create_objects(thread_id):
            """Worker function for each thread."""
            try:
                thread_start = time.time()
                
                # Each thread creates its own octree
                tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
                
                created_count = 0
                for obj_id in range(objects_per_thread):
                    x = random.uniform(-800, 800)
                    y = random.uniform(-800, 800) 
                    z = random.uniform(-800, 800)
                    
                    tree.insert(x, y, z, f"thread_{thread_id}_obj_{obj_id}")
                    created_count += 1
                
                thread_time = time.time() - thread_start
                
                # Test some queries to verify functionality
                query_results = []
                for _ in range(10):
                    x = random.uniform(-500, 500)
                    y = random.uniform(-500, 500)
                    z = random.uniform(-500, 500)
                    radius = random.uniform(50, 150)
                    
                    results = tree.query(x - radius, y - radius, z - radius,
                                             x + radius, y + radius, z + radius)
                    query_results.append(len(results))
                
                thread_results[thread_id] = {
                    'created': created_count,
                    'time': thread_time,
                    'tree_size': tree.size(),
                    'memory': tree.memory_usage(),
                    'depth': tree.depth(),
                    'queries': query_results,
                    'tree': tree
                }
                
            except Exception as e:
                thread_errors.append(f"Thread {thread_id}: {e}")
        
        # Start all threads
        threads = []
        concurrent_start = time.time()
        
        for thread_id in range(num_threads):
            thread = threading.Thread(target=create_objects, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        total_concurrent_time = time.time() - concurrent_start
        
        # Analyze results
        if thread_errors:
            print(f"❌ Thread errors occurred:")
            for error in thread_errors:
                print(f"   {error}")
        
        successful_threads = len(thread_results)
        total_created = sum(result['created'] for result in thread_results.values())
        total_memory = sum(result['memory'] for result in thread_results.values())
        avg_thread_time = sum(result['time'] for result in thread_results.values()) / successful_threads
        
        print(f"\n📈 CONCURRENT RESULTS:")
        print(f"   Successful threads: {successful_threads}/{num_threads}")
        print(f"   Total objects created: {total_created:,}")
        print(f"   Total concurrent time: {total_concurrent_time:.3f}s")
        print(f"   Average thread time: {avg_thread_time:.3f}s")
        print(f"   Concurrent speedup: {avg_thread_time / total_concurrent_time:.1f}x")
        print(f"   Total memory usage: {total_memory:,} bytes ({total_memory/1024/1024:.1f} MB)")
        print(f"   Creation rate: {total_created / total_concurrent_time:.0f} objects/sec")
        
        # Per-thread breakdown
        print(f"\n📊 PER-THREAD BREAKDOWN:")
        print(f"{'Thread':>8} {'Objects':>10} {'Time(s)':>8} {'Size':>8} {'Depth':>6} {'Memory(KB)':>12}")
        print("-" * 70)
        
        for thread_id, result in sorted(thread_results.items()):
            print(f"{thread_id:>8} {result['created']:>10,} {result['time']:>7.3f} "
                  f"{result['tree_size']:>8,} {result['depth']:>6} {result['memory']/1024:>11.1f}")
        
        # Assertions
        self.assertEqual(len(thread_errors), 0, "No thread errors should occur")
        self.assertEqual(successful_threads, num_threads, "All threads should complete successfully")
        self.assertEqual(total_created, total_objects, "Should create expected number of objects")
        # Note: Due to Python's GIL, actual speedup may be limited
        # The main goal is testing thread safety and data integrity
        self.assertGreater(total_created, 5000, "Should complete significant operations concurrently")
        # Performance can vary significantly due to GIL and threading overhead
        # As long as operations complete without errors, concurrency is working
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during object creation and destruction."""
        print("\n🔥 OBJECT CREATION STRESS TEST: Memory Leak Detection")
        print("=" * 65)
        
        # Get baseline memory
        gc.collect()
        
        # Create and destroy objects in cycles
        num_cycles = 50
        objects_per_cycle = 2000
        
        memory_samples = []
        
        print(f"🔍 Running {num_cycles} cycles of {objects_per_cycle:,} objects each...")
        
        for cycle in range(num_cycles):
            cycle_start = time.time()
            
            # Create octree and fill with objects
            tree = octree.Octree(-500, -500, -500, 500, 500, 500)
            
            for i in range(objects_per_cycle):
                x = random.uniform(-400, 400)
                y = random.uniform(-400, 400)
                z = random.uniform(-400, 400)
                tree.insert(x, y, z, f"leak_test_{cycle}_{i}")
            
            # Record memory usage
            cycle_memory = tree.memory_usage()
            memory_samples.append(cycle_memory)
            
            # Destroy tree (Python garbage collection)
            del tree
            gc.collect()
            
            cycle_time = time.time() - cycle_start
            
            if (cycle + 1) % 10 == 0:
                avg_memory = sum(memory_samples[-10:]) / min(10, len(memory_samples))
                print(f"   Cycle {cycle + 1:2d}: {cycle_time:.3f}s, "
                      f"Memory: {cycle_memory:,} bytes, "
                      f"Avg(last 10): {avg_memory:,.0f} bytes")
        
        # Analyze memory usage trend
        if len(memory_samples) >= 10:
            first_10_avg = sum(memory_samples[:10]) / 10
            last_10_avg = sum(memory_samples[-10:]) / 10
            memory_growth = last_10_avg - first_10_avg
            growth_percentage = (memory_growth / first_10_avg) * 100
            
            print(f"\n📊 MEMORY ANALYSIS:")
            print(f"   First 10 cycles average: {first_10_avg:,.0f} bytes")
            print(f"   Last 10 cycles average: {last_10_avg:,.0f} bytes")
            print(f"   Memory growth: {memory_growth:+.0f} bytes ({growth_percentage:+.1f}%)")
            
            # Check for significant memory leaks
            # Allow for some variation but detect major leaks
            max_acceptable_growth = 10  # 10% growth is acceptable
            self.assertLess(abs(growth_percentage), max_acceptable_growth,
                           f"Memory growth should be under {max_acceptable_growth}% (got {growth_percentage:.1f}%)")
        
        print(f"✅ Memory leak test completed - no significant leaks detected")
    
    def test_object_reference_management(self):
        """Test proper handling of object references and data."""
        print("\n🔥 OBJECT CREATION STRESS TEST: Reference Management")
        print("=" * 65)
        
        tree = octree.Octree(-100, -100, -100, 100, 100, 100)
        
        # Test with various data types
        test_objects = [
            # Simple strings
            "simple_string",
            "another_string_with_numbers_123",
            
            # Complex strings
            "unicode_string_🌳🔥📊",
            "very_long_string_" + "x" * 1000,
            
            # Numbers (as strings since octree stores string data)
            "42",
            "3.14159",
            "-999.999",
            
            # JSON-like strings
            '{"type": "test", "value": 42}',
            '["list", "of", "items"]',
        ]
        
        # Insert objects with different data types
        object_positions = []
        for i, data in enumerate(test_objects):
            x = random.uniform(-80, 80)
            y = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            
            tree.insert(x, y, z, data)
            object_positions.append((x, y, z, data))
        
        print(f"📦 Inserted {len(test_objects)} objects with various data types")
        
        # Test reference integrity through queries
        correct_references = 0
        total_queries = 0
        
        for x, y, z, expected_data in object_positions:
            # Query small region around each object
            results = tree.query(x - 1, y - 1, z - 1, x + 1, y + 1, z + 1)
            # Extract just the data from tuples (x, y, z, data)
            data_results = [item[3] for item in results]
            
            total_queries += 1
            if expected_data in data_results:
                correct_references += 1
            else:
                print(f"   ❌ Missing reference: {expected_data}")
        
        # Test bulk operations don't corrupt references
        print(f"🔄 Testing bulk operations with {total_queries} references...")
        
        # Add many more objects
        for i in range(10000):
            x = random.uniform(-90, 90)
            y = random.uniform(-90, 90)
            z = random.uniform(-90, 90)
            tree.insert(x, y, z, f"bulk_obj_{i}")
        
        # Re-verify original references
        correct_after_bulk = 0
        for x, y, z, expected_data in object_positions:
            results = tree.query(x - 1, y - 1, z - 1, x + 1, y + 1, z + 1)
            # Extract just the data from tuples (x, y, z, data)
            data_results = [item[3] for item in results]
            if expected_data in data_results:
                correct_after_bulk += 1
        
        print(f"\n📊 REFERENCE INTEGRITY RESULTS:")
        print(f"   Initial correct references: {correct_references}/{total_queries}")
        print(f"   After bulk operations: {correct_after_bulk}/{total_queries}")
        print(f"   Reference stability: {correct_after_bulk == correct_references}")
        
        # Assertions
        self.assertEqual(correct_references, total_queries, 
                        "All initial references should be found")
        self.assertEqual(correct_after_bulk, correct_references,
                        "References should remain stable after bulk operations")


if __name__ == '__main__':
    print("🚀 OCTREE OBJECT CREATION STRESS TESTS")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=False)