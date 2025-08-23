"""Performance tests for the octree module.

This module provides performance benchmarking and timing tests
to ensure the octree implementation meets performance expectations.
"""

import unittest
import time
import random
import statistics
import sys
from test import support

try:
    import octree
except ImportError:
    octree = None


@unittest.skipIf(octree is None, "octree module not available")
class OctreePerformanceTest(unittest.TestCase):
    """Performance benchmarks for octree operations."""
    
    def setUp(self):
        """Set up performance test fixtures."""
        random.seed(42)  # For reproducible results
        self.performance_data = {}

    def time_operation(self, operation, *args, **kwargs):
        """Time an operation and return the result and elapsed time."""
        start_time = time.perf_counter()
        result = operation(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time

    @support.requires_resource('cpu')
    def test_insertion_performance(self):
        """Benchmark point insertion performance."""
        tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
        
        # Test insertion performance with different batch sizes
        batch_sizes = [100, 500, 1000, 2000]
        insertion_times = []
        
        print(f"\n{'Batch Size':>10} {'Time (s)':>10} {'Points/sec':>12} {'Cumulative':>12}")
        print("-" * 50)
        
        total_points = 0
        cumulative_time = 0
        
        for batch_size in batch_sizes:
            points = []
            for _ in range(batch_size):
                x = random.uniform(-900, 900)
                y = random.uniform(-900, 900) 
                z = random.uniform(-900, 900)
                points.append((x, y, z, f"perf_point_{total_points + len(points)}"))
            
            # Time the batch insertion
            start_time = time.perf_counter()
            for x, y, z, data in points:
                tree.insert(x, y, z, data)
            end_time = time.perf_counter()
            
            batch_time = end_time - start_time
            cumulative_time += batch_time
            total_points += batch_size
            insertion_times.append(batch_time)
            
            points_per_sec = batch_size / batch_time if batch_time > 0 else float('inf')
            cumulative_rate = total_points / cumulative_time if cumulative_time > 0 else float('inf')
            
            print(f"{batch_size:>10} {batch_time:>10.4f} {points_per_sec:>12.0f} {cumulative_rate:>12.0f}")
        
        # Performance assertions (adjust thresholds as needed)
        avg_time_per_1000 = statistics.mean(insertion_times) * (1000 / statistics.mean(batch_sizes))
        self.assertLess(avg_time_per_1000, 1.0, "Should insert 1000 points in under 1 second")
        
        # Verify all points were inserted
        self.assertEqual(tree.size(), total_points)

    @support.requires_resource('cpu')
    def test_query_performance(self):
        """Benchmark query performance."""
        tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
        
        # Pre-populate tree with points
        num_points = 10000
        print(f"\nPre-populating tree with {num_points} points...")
        
        for i in range(num_points):
            x = random.uniform(-900, 900)
            y = random.uniform(-900, 900)
            z = random.uniform(-900, 900)
            tree.insert(x, y, z, f"query_test_point_{i}")
        
        # Test different query sizes
        query_tests = [
            ("Small region", (-50, -50, -50, 50, 50, 50)),
            ("Medium region", (-200, -200, -200, 200, 200, 200)),
            ("Large region", (-500, -500, -500, 500, 500, 500)),
            ("Full tree", (-1000, -1000, -1000, 1000, 1000, 1000)),
        ]
        
        print(f"\n{'Query Type':>15} {'Time (ms)':>10} {'Results':>8} {'Rate (q/s)':>12}")
        print("-" * 50)
        
        for query_name, bounds in query_tests:
            # Warm up
            tree.query(*bounds)
            
            # Time multiple queries for accuracy
            num_queries = 100
            start_time = time.perf_counter()
            
            total_results = 0
            for _ in range(num_queries):
                results = tree.query(*bounds)
                total_results += len(results)
            
            end_time = time.perf_counter()
            
            total_time = end_time - start_time
            avg_time_ms = (total_time / num_queries) * 1000
            queries_per_sec = num_queries / total_time if total_time > 0 else float('inf')
            avg_results = total_results // num_queries
            
            print(f"{query_name:>15} {avg_time_ms:>10.3f} {avg_results:>8} {queries_per_sec:>12.0f}")
        
        # Performance assertion
        small_region_time = None
        for query_name, bounds in query_tests:
            if query_name == "Small region":
                _, time_taken = self.time_operation(tree.query, *bounds)
                small_region_time = time_taken
                break
        
        if small_region_time:
            self.assertLess(small_region_time, 0.001, "Small region query should take under 1ms")

    @support.requires_resource('cpu') 
    def test_radius_query_performance(self):
        """Benchmark radius query performance."""
        tree = octree.Octree(-500, -500, -500, 500, 500, 500)
        
        # Pre-populate
        num_points = 5000
        for i in range(num_points):
            x = random.uniform(-400, 400)
            y = random.uniform(-400, 400)
            z = random.uniform(-400, 400) 
            tree.insert(x, y, z, f"radius_point_{i}")
        
        # Test different radius sizes
        radius_tests = [
            ("Small radius", 25),
            ("Medium radius", 100),
            ("Large radius", 300),
        ]
        
        print(f"\n{'Radius Type':>15} {'Radius':>8} {'Time (ms)':>10} {'Results':>8}")
        print("-" * 50)
        
        for radius_name, radius in radius_tests:
            center_x, center_y, center_z = 0, 0, 0
            
            # Time the query
            start_time = time.perf_counter()
            results = tree.query_radius(center_x, center_y, center_z, radius)
            end_time = time.perf_counter()
            
            time_ms = (end_time - start_time) * 1000
            
            print(f"{radius_name:>15} {radius:>8} {time_ms:>10.3f} {len(results):>8}")
            
            # Verify results are actually within radius
            for x, y, z, data in results:
                distance = ((x - center_x)**2 + (y - center_y)**2 + (z - center_z)**2)**0.5
                self.assertLessEqual(distance, radius + 1e-10, "Result should be within radius")

    @support.requires_resource('cpu')
    def test_subdivision_performance(self):
        """Test subdivision performance with different point distributions."""
        distributions = [
            ("Uniform", self._generate_uniform_points),
            ("Clustered", self._generate_clustered_points),
            ("Grid", self._generate_grid_points),
        ]
        
        print(f"\n{'Distribution':>12} {'Points':>8} {'Insert(s)':>10} {'Depth':>6} {'Subdivisions':>12} {'Memory(KB)':>12}")
        print("-" * 75)
        
        for dist_name, point_generator in distributions:
            tree = octree.Octree(-100, -100, -100, 100, 100, 100)
            
            # Generate points
            points = point_generator(2000)
            
            # Time insertion
            start_time = time.perf_counter()
            for x, y, z in points:
                tree.insert(x, y, z, f"{dist_name.lower()}_point")
            end_time = time.perf_counter()
            
            insert_time = end_time - start_time
            memory_kb = tree.memory_usage() / 1024
            
            print(f"{dist_name:>12} {len(points):>8} {insert_time:>10.4f} {tree.depth():>6} "
                  f"{tree.subdivision_count():>12} {memory_kb:>12.1f}")
            
            # Verify all points were inserted
            self.assertEqual(tree.size(), len(points))

    @support.requires_resource('cpu')
    def test_memory_efficiency(self):
        """Test memory efficiency of the octree."""
        tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
        
        point_counts = [100, 500, 1000, 2000, 5000]
        
        print(f"\n{'Points':>8} {'Memory (KB)':>12} {'Bytes/Point':>12} {'Depth':>6}")
        print("-" * 45)
        
        for count in point_counts:
            # Clear and repopulate
            tree.clear()
            
            for i in range(count):
                x = random.uniform(-900, 900)
                y = random.uniform(-900, 900)
                z = random.uniform(-900, 900)
                tree.insert(x, y, z, f"mem_point_{i}")
            
            memory_bytes = tree.memory_usage()
            memory_kb = memory_bytes / 1024
            bytes_per_point = memory_bytes / count if count > 0 else 0
            
            print(f"{count:>8} {memory_kb:>12.2f} {bytes_per_point:>12.1f} {tree.depth():>6}")
            
            # Memory should scale reasonably
            self.assertLess(bytes_per_point, 1000, "Should use less than 1KB per point")

    def _generate_uniform_points(self, count):
        """Generate uniformly distributed points."""
        points = []
        for _ in range(count):
            x = random.uniform(-80, 80)
            y = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            points.append((x, y, z))
        return points

    def _generate_clustered_points(self, count):
        """Generate clustered points around centers."""
        points = []
        centers = [(30, 30, 30), (-30, -30, -30), (30, -30, 30), (-30, 30, -30)]
        
        for _ in range(count):
            center = random.choice(centers)
            x = center[0] + random.gauss(0, 10)
            y = center[1] + random.gauss(0, 10)
            z = center[2] + random.gauss(0, 10)
            # Clamp to bounds
            x = max(-80, min(80, x))
            y = max(-80, min(80, y))
            z = max(-80, min(80, z))
            points.append((x, y, z))
        return points

    def _generate_grid_points(self, count):
        """Generate grid-arranged points."""
        points = []
        grid_size = int(count**(1/3)) + 1
        spacing = 160 / grid_size  # Fit in -80 to 80 range
        
        generated = 0
        for i in range(grid_size):
            if generated >= count:
                break
            for j in range(grid_size):
                if generated >= count:
                    break
                for k in range(grid_size):
                    if generated >= count:
                        break
                    x = -80 + i * spacing
                    y = -80 + j * spacing
                    z = -80 + k * spacing
                    points.append((x, y, z))
                    generated += 1
        
        return points[:count]


@unittest.skipIf(octree is None, "octree module not available")
class OctreeScalabilityTest(unittest.TestCase):
    """Test octree scalability with varying data sizes."""
    
    @support.requires_resource('cpu')
    @support.requires_resource('memory')
    def test_scalability_analysis(self):
        """Analyze performance scaling with data size."""
        data_sizes = [1000, 2000, 5000, 10000]
        results = []
        
        print(f"\n{'Points':>8} {'Insert(s)':>10} {'Query(ms)':>10} {'Memory(MB)':>12} {'Depth':>6}")
        print("-" * 60)
        
        for size in data_sizes:
            tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
            
            # Generate points
            points = []
            for i in range(size):
                x = random.uniform(-900, 900)
                y = random.uniform(-900, 900)
                z = random.uniform(-900, 900)
                points.append((x, y, z, f"scale_point_{i}"))
            
            # Time insertion
            start_time = time.perf_counter()
            for x, y, z, data in points:
                tree.insert(x, y, z, data)
            insert_time = time.perf_counter() - start_time
            
            # Time a representative query
            start_time = time.perf_counter()
            query_results = tree.query(-100, -100, -100, 100, 100, 100)
            query_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
            
            memory_mb = tree.memory_usage() / (1024 * 1024)
            
            print(f"{size:>8} {insert_time:>10.4f} {query_time:>10.3f} {memory_mb:>12.2f} {tree.depth():>6}")
            
            results.append({
                'size': size,
                'insert_time': insert_time,
                'query_time': query_time,
                'memory_mb': memory_mb,
                'depth': tree.depth()
            })
            
            # Verify correctness
            self.assertEqual(tree.size(), size)
        
        # Analyze scaling characteristics
        if len(results) >= 2:
            # Insert time should scale roughly O(n log n)
            first, last = results[0], results[-1]
            size_ratio = last['size'] / first['size']
            time_ratio = last['insert_time'] / first['insert_time']
            
            # Time ratio should be less than size_ratio^2 (better than O(n^2))
            self.assertLess(time_ratio, size_ratio**2, 
                          f"Insertion scaling worse than O(n^2): {time_ratio} vs {size_ratio**2}")


if __name__ == '__main__':
    # Enable performance test output
    if '-v' not in sys.argv:
        sys.argv.append('-v')
    
    unittest.main(verbosity=2)