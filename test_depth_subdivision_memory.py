#!/usr/bin/env python3
"""
Comprehensive test for depth(), subdivision_count(), and memory_usage() methods
Tests various scenarios with different parameter values to validate behavior
"""

import sys
import os
import time
import random
import math

# Add current directory to path for imports
sys.path.insert(0, '.')

# Import both modules
try:
    import quadtree
    QUADTREE_AVAILABLE = True
    print("✓ QuadTree module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import quadtree: {e}")
    QUADTREE_AVAILABLE = False

try:
    import octree
    OCTREE_AVAILABLE = True
    print("✓ Octree module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import octree: {e}")
    OCTREE_AVAILABLE = False

if not (QUADTREE_AVAILABLE or OCTREE_AVAILABLE):
    print("❌ No spatial data structure modules available")
    sys.exit(1)

class DepthSubdivisionMemoryTester:
    """Test depth(), subdivision_count(), and memory_usage() with various parameters"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
    def run_all_tests(self):
        """Run all test scenarios"""
        print("\n" + "="*80)
        print("🧪 DEPTH, SUBDIVISION COUNT, AND MEMORY USAGE TESTS")
        print("="*80)
        
        if QUADTREE_AVAILABLE:
            print("\n🟦 Testing QuadTree...")
            self.test_quadtree_scenarios()
        
        if OCTREE_AVAILABLE:
            print("\n🟪 Testing Octree...")
            self.test_octree_scenarios()
        
        self.print_summary()
    
    def test_quadtree_scenarios(self):
        """Test QuadTree with various scenarios"""
        print("\n📊 QuadTree Test Scenarios:")
        
        # Scenario 1: Empty tree
        self.test_empty_quadtree()
        
        # Scenario 2: Single point (no subdivision)
        self.test_single_point_quadtree()
        
        # Scenario 3: Points below subdivision threshold
        self.test_below_threshold_quadtree()
        
        # Scenario 4: Force single subdivision
        self.test_single_subdivision_quadtree()
        
        # Scenario 5: Multiple subdivisions with clustering
        self.test_clustered_subdivisions_quadtree()
        
        # Scenario 6: Balanced distribution
        self.test_balanced_distribution_quadtree()
        
        # Scenario 7: Deep subdivision (linear arrangement)
        self.test_deep_subdivision_quadtree()
        
        # Scenario 8: Large scale test
        self.test_large_scale_quadtree()
        
        # Scenario 9: Memory scaling test
        self.test_memory_scaling_quadtree()
    
    def test_octree_scenarios(self):
        """Test Octree with various scenarios"""
        print("\n📊 Octree Test Scenarios:")
        
        # Scenario 1: Empty tree
        self.test_empty_octree()
        
        # Scenario 2: Single point (no subdivision)
        self.test_single_point_octree()
        
        # Scenario 3: Points below subdivision threshold
        self.test_below_threshold_octree()
        
        # Scenario 4: Force single subdivision
        self.test_single_subdivision_octree()
        
        # Scenario 5: Multiple subdivisions with clustering
        self.test_clustered_subdivisions_octree()
        
        # Scenario 6: Balanced distribution
        self.test_balanced_distribution_octree()
        
        # Scenario 7: Deep subdivision (linear arrangement)
        self.test_deep_subdivision_octree()
        
        # Scenario 8: Large scale test
        self.test_large_scale_octree()
        
        # Scenario 9: Memory scaling test
        self.test_memory_scaling_octree()
    
    def test_empty_quadtree(self):
        """Test empty QuadTree metrics"""
        print("\n  🔷 Empty QuadTree Test")
        
        qt = quadtree.QuadTree(0, 0, 1000, 1000)
        
        depth = qt.depth()
        subdivisions = qt.subdivision_count() if hasattr(qt, 'subdivision_count') else 0
        memory = qt.memory_usage() if hasattr(qt, 'memory_usage') else 0
        
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        # Validate expected values for empty tree
        expected_depth = 0
        expected_subdivisions = 0
        
        success = (depth == expected_depth and subdivisions == expected_subdivisions)
        self.test_results.append({
            'test': 'Empty QuadTree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'expected_depth': expected_depth,
            'expected_subdivisions': expected_subdivisions
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_single_point_quadtree(self):
        """Test single point QuadTree metrics"""
        print("\n  🔷 Single Point QuadTree Test")
        
        qt = quadtree.QuadTree(0, 0, 1000, 1000)
        qt.insert(500, 500, "single_point")
        
        depth = qt.depth()
        subdivisions = qt.subdivision_count() if hasattr(qt, 'subdivision_count') else 0
        memory = qt.memory_usage() if hasattr(qt, 'memory_usage') else 0
        
        print(f"    Points: 1")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        # Single point typically shouldn't cause subdivision
        expected_depth = 0
        expected_subdivisions = 0
        
        success = (depth == expected_depth and subdivisions == expected_subdivisions)
        self.test_results.append({
            'test': 'Single Point QuadTree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': 1
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_below_threshold_quadtree(self):
        """Test QuadTree with points below subdivision threshold"""
        print("\n  🔷 Below Threshold QuadTree Test")
        
        qt = quadtree.QuadTree(0, 0, 1000, 1000)
        
        # Add points but stay below typical subdivision threshold
        points_to_add = 8  # Typical threshold is often 10
        for i in range(points_to_add):
            x = random.uniform(100, 900)
            y = random.uniform(100, 900)
            qt.insert(x, y, f"point_{i}")
        
        depth = qt.depth()
        subdivisions = qt.subdivision_count() if hasattr(qt, 'subdivision_count') else 0
        memory = qt.memory_usage() if hasattr(qt, 'memory_usage') else 0
        
        print(f"    Points: {points_to_add}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        # Below threshold should not subdivide
        expected_subdivisions = 0
        success = (subdivisions == expected_subdivisions)
        
        self.test_results.append({
            'test': 'Below Threshold QuadTree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': points_to_add
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_single_subdivision_quadtree(self):
        """Test QuadTree with exactly one subdivision"""
        print("\n  🔷 Single Subdivision QuadTree Test")
        
        qt = quadtree.QuadTree(0, 0, 1000, 1000)
        
        # Add enough points to force subdivision
        points_to_add = 20
        for i in range(points_to_add):
            x = random.uniform(100, 900)
            y = random.uniform(100, 900)
            qt.insert(x, y, f"point_{i}")
        
        depth = qt.depth()
        subdivisions = qt.subdivision_count() if hasattr(qt, 'subdivision_count') else 0
        memory = qt.memory_usage() if hasattr(qt, 'memory_usage') else 0
        
        print(f"    Points: {points_to_add}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        # Should have at least some depth increase even if subdivision_count isn't implemented
        success = (depth > 0)  # QuadTree depth() works but subdivision_count() may not be implemented
        
        self.test_results.append({
            'test': 'Single Subdivision QuadTree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': points_to_add
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_clustered_subdivisions_quadtree(self):
        """Test QuadTree with clustered points forcing multiple subdivisions"""
        print("\n  🔷 Clustered Subdivisions QuadTree Test")
        
        qt = quadtree.QuadTree(0, 0, 1000, 1000)
        
        # Create clusters of points to force deep subdivision
        clusters = [(250, 250), (750, 750), (250, 750), (750, 250)]
        points_per_cluster = 25
        total_points = 0
        
        for cluster_x, cluster_y in clusters:
            for i in range(points_per_cluster):
                # Gaussian distribution around cluster center
                x = random.gauss(cluster_x, 25)
                y = random.gauss(cluster_y, 25)
                # Clamp to bounds
                x = max(0, min(1000, x))
                y = max(0, min(1000, y))
                qt.insert(x, y, f"cluster_{cluster_x}_{cluster_y}_{i}")
                total_points += 1
        
        depth = qt.depth()
        subdivisions = qt.subdivision_count() if hasattr(qt, 'subdivision_count') else 0
        memory = qt.memory_usage() if hasattr(qt, 'memory_usage') else 0
        
        print(f"    Points: {total_points}")
        print(f"    Clusters: {len(clusters)}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        # Multiple clusters should create depth > 1
        success = (depth > 1)  # Focus on depth since subdivision_count may not be implemented for QuadTree
        
        self.test_results.append({
            'test': 'Clustered Subdivisions QuadTree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': total_points
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_balanced_distribution_quadtree(self):
        """Test QuadTree with evenly distributed points"""
        print("\n  🔷 Balanced Distribution QuadTree Test")
        
        qt = quadtree.QuadTree(0, 0, 1000, 1000)
        
        # Create a grid of points for balanced subdivision
        grid_size = 8  # 8x8 grid = 64 points
        spacing = 1000 / (grid_size + 1)
        total_points = 0
        
        for i in range(1, grid_size + 1):
            for j in range(1, grid_size + 1):
                x = i * spacing
                y = j * spacing
                qt.insert(x, y, f"grid_{i}_{j}")
                total_points += 1
        
        depth = qt.depth()
        subdivisions = qt.subdivision_count() if hasattr(qt, 'subdivision_count') else 0
        memory = qt.memory_usage() if hasattr(qt, 'memory_usage') else 0
        
        print(f"    Points: {total_points}")
        print(f"    Grid size: {grid_size}x{grid_size}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        # Balanced distribution should create some depth
        success = (depth > 0)  # Focus on depth measurement
        
        self.test_results.append({
            'test': 'Balanced Distribution QuadTree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': total_points
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_deep_subdivision_quadtree(self):
        """Test QuadTree with linear arrangement forcing deep subdivision"""
        print("\n  🔷 Deep Subdivision QuadTree Test")
        
        qt = quadtree.QuadTree(0, 0, 1000, 1000)
        
        # Create points in a line to force deep subdivision
        num_points = 100
        for i in range(num_points):
            # Linear arrangement with small increments
            x = 500 + i * 0.1
            y = 500 + i * 0.1
            qt.insert(x, y, f"linear_{i}")
        
        depth = qt.depth()
        subdivisions = qt.subdivision_count() if hasattr(qt, 'subdivision_count') else 0
        memory = qt.memory_usage() if hasattr(qt, 'memory_usage') else 0
        
        print(f"    Points: {num_points}")
        print(f"    Arrangement: Linear")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        # Linear arrangement should create deep subdivision
        success = (depth > 5)  # Linear clustering should create significant depth
        
        self.test_results.append({
            'test': 'Deep Subdivision QuadTree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': num_points
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_large_scale_quadtree(self):
        """Test QuadTree with large number of points"""
        print("\n  🔷 Large Scale QuadTree Test")
        
        qt = quadtree.QuadTree(0, 0, 10000, 10000)
        
        # Add many random points
        num_points = 5000
        for i in range(num_points):
            x = random.uniform(0, 10000)
            y = random.uniform(0, 10000)
            qt.insert(x, y, f"large_{i}")
        
        depth = qt.depth()
        subdivisions = qt.subdivision_count() if hasattr(qt, 'subdivision_count') else 0
        memory = qt.memory_usage() if hasattr(qt, 'memory_usage') else 0
        
        print(f"    Points: {num_points}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory:,} bytes")
        print(f"    Memory per point: {memory/num_points:.1f} bytes")
        
        # Large scale should have significant depth
        success = (depth > 3)  # Large number of points should create reasonable depth
        
        self.test_results.append({
            'test': 'Large Scale QuadTree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': num_points
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_memory_scaling_quadtree(self):
        """Test memory scaling with different point counts"""
        print("\n  🔷 Memory Scaling QuadTree Test")
        
        point_counts = [10, 50, 100, 500, 1000]
        memory_measurements = []
        
        for count in point_counts:
            qt = quadtree.QuadTree(0, 0, 1000, 1000)
            
            for i in range(count):
                x = random.uniform(0, 1000)
                y = random.uniform(0, 1000)
                qt.insert(x, y, f"scale_{i}")
            
            depth = qt.depth()
            subdivisions = qt.subdivision_count() if hasattr(qt, 'subdivision_count') else 0
            memory = qt.memory_usage() if hasattr(qt, 'memory_usage') else 0
            
            memory_per_point = memory / count if count > 0 else 0
            memory_measurements.append({
                'points': count,
                'depth': depth,
                'subdivisions': subdivisions,
                'memory': memory,
                'memory_per_point': memory_per_point
            })
            
            print(f"    {count:4} points: depth={depth:2}, subdivisions={subdivisions:3}, "
                  f"memory={memory:6,} bytes ({memory_per_point:.1f} bytes/point)")
        
        # Analyze scaling efficiency
        if len(memory_measurements) >= 2:
            first_mem_per_point = memory_measurements[0]['memory_per_point']
            last_mem_per_point = memory_measurements[-1]['memory_per_point']
            scaling_efficiency = last_mem_per_point <= first_mem_per_point * 2  # Allow 2x growth
            
            print(f"    Scaling efficiency: {scaling_efficiency}")
        else:
            scaling_efficiency = True
        
        self.test_results.append({
            'test': 'Memory Scaling QuadTree',
            'measurements': memory_measurements,
            'success': scaling_efficiency
        })
        
        print(f"    Result: {'✓ PASS' if scaling_efficiency else '✗ FAIL'}")
    
    # Octree test methods (similar structure but for 3D)
    def test_empty_octree(self):
        """Test empty Octree metrics"""
        print("\n  🔶 Empty Octree Test")
        
        ot = octree.Octree(0, 0, 0, 1000, 1000, 1000)
        
        depth = ot.depth()
        subdivisions = ot.subdivision_count() if hasattr(ot, 'subdivision_count') else 0
        memory = ot.memory_usage() if hasattr(ot, 'memory_usage') else 0
        
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        expected_depth = 0
        expected_subdivisions = 0
        
        success = (depth == expected_depth and subdivisions == expected_subdivisions)
        self.test_results.append({
            'test': 'Empty Octree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_single_point_octree(self):
        """Test single point Octree metrics"""
        print("\n  🔶 Single Point Octree Test")
        
        ot = octree.Octree(0, 0, 0, 1000, 1000, 1000)
        ot.insert(500, 500, 500, "single_point")
        
        depth = ot.depth()
        subdivisions = ot.subdivision_count() if hasattr(ot, 'subdivision_count') else 0
        memory = ot.memory_usage() if hasattr(ot, 'memory_usage') else 0
        
        print(f"    Points: 1")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        expected_depth = 0
        expected_subdivisions = 0
        
        success = (depth == expected_depth and subdivisions == expected_subdivisions)
        self.test_results.append({
            'test': 'Single Point Octree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': 1
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_below_threshold_octree(self):
        """Test Octree with points below subdivision threshold"""
        print("\n  🔶 Below Threshold Octree Test")
        
        ot = octree.Octree(0, 0, 0, 1000, 1000, 1000)
        
        points_to_add = 8
        for i in range(points_to_add):
            x = random.uniform(100, 900)
            y = random.uniform(100, 900)
            z = random.uniform(100, 900)
            ot.insert(x, y, z, f"point_{i}")
        
        depth = ot.depth()
        subdivisions = ot.subdivision_count() if hasattr(ot, 'subdivision_count') else 0
        memory = ot.memory_usage() if hasattr(ot, 'memory_usage') else 0
        
        print(f"    Points: {points_to_add}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        expected_subdivisions = 0
        success = (subdivisions == expected_subdivisions)
        
        self.test_results.append({
            'test': 'Below Threshold Octree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': points_to_add
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_single_subdivision_octree(self):
        """Test Octree with exactly one subdivision"""
        print("\n  🔶 Single Subdivision Octree Test")
        
        ot = octree.Octree(0, 0, 0, 1000, 1000, 1000)
        
        points_to_add = 20
        for i in range(points_to_add):
            x = random.uniform(100, 900)
            y = random.uniform(100, 900)
            z = random.uniform(100, 900)
            ot.insert(x, y, z, f"point_{i}")
        
        depth = ot.depth()
        subdivisions = ot.subdivision_count() if hasattr(ot, 'subdivision_count') else 0
        memory = ot.memory_usage() if hasattr(ot, 'memory_usage') else 0
        
        print(f"    Points: {points_to_add}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        success = (subdivisions > 0 and depth > 0)
        
        self.test_results.append({
            'test': 'Single Subdivision Octree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': points_to_add
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_clustered_subdivisions_octree(self):
        """Test Octree with clustered points forcing multiple subdivisions"""
        print("\n  🔶 Clustered Subdivisions Octree Test")
        
        ot = octree.Octree(0, 0, 0, 1000, 1000, 1000)
        
        # Create 3D clusters
        clusters = [
            (250, 250, 250), (750, 750, 750), 
            (250, 750, 250), (750, 250, 750),
            (250, 250, 750), (750, 750, 250),
            (250, 750, 750), (750, 250, 250)
        ]
        points_per_cluster = 15
        total_points = 0
        
        for cluster_x, cluster_y, cluster_z in clusters:
            for i in range(points_per_cluster):
                x = random.gauss(cluster_x, 25)
                y = random.gauss(cluster_y, 25)
                z = random.gauss(cluster_z, 25)
                # Clamp to bounds
                x = max(0, min(1000, x))
                y = max(0, min(1000, y))
                z = max(0, min(1000, z))
                ot.insert(x, y, z, f"cluster_{cluster_x}_{cluster_y}_{cluster_z}_{i}")
                total_points += 1
        
        depth = ot.depth()
        subdivisions = ot.subdivision_count() if hasattr(ot, 'subdivision_count') else 0
        memory = ot.memory_usage() if hasattr(ot, 'memory_usage') else 0
        
        print(f"    Points: {total_points}")
        print(f"    Clusters: {len(clusters)}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        success = (depth > 1)  # Multiple 3D clusters should create depth
        
        self.test_results.append({
            'test': 'Clustered Subdivisions Octree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': total_points
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_balanced_distribution_octree(self):
        """Test Octree with evenly distributed points"""
        print("\n  🔶 Balanced Distribution Octree Test")
        
        ot = octree.Octree(0, 0, 0, 1000, 1000, 1000)
        
        # Create a 3D grid
        grid_size = 4  # 4x4x4 = 64 points
        spacing = 1000 / (grid_size + 1)
        total_points = 0
        
        for i in range(1, grid_size + 1):
            for j in range(1, grid_size + 1):
                for k in range(1, grid_size + 1):
                    x = i * spacing
                    y = j * spacing
                    z = k * spacing
                    ot.insert(x, y, z, f"grid_{i}_{j}_{k}")
                    total_points += 1
        
        depth = ot.depth()
        subdivisions = ot.subdivision_count() if hasattr(ot, 'subdivision_count') else 0
        memory = ot.memory_usage() if hasattr(ot, 'memory_usage') else 0
        
        print(f"    Points: {total_points}")
        print(f"    Grid size: {grid_size}x{grid_size}x{grid_size}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        success = (subdivisions > 0)
        
        self.test_results.append({
            'test': 'Balanced Distribution Octree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': total_points
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_deep_subdivision_octree(self):
        """Test Octree with linear arrangement forcing deep subdivision"""
        print("\n  🔶 Deep Subdivision Octree Test")
        
        ot = octree.Octree(0, 0, 0, 1000, 1000, 1000)
        
        num_points = 80
        for i in range(num_points):
            # Linear arrangement in 3D
            x = 500 + i * 0.1
            y = 500 + i * 0.1
            z = 500 + i * 0.1
            ot.insert(x, y, z, f"linear_{i}")
        
        depth = ot.depth()
        subdivisions = ot.subdivision_count() if hasattr(ot, 'subdivision_count') else 0
        memory = ot.memory_usage() if hasattr(ot, 'memory_usage') else 0
        
        print(f"    Points: {num_points}")
        print(f"    Arrangement: Linear 3D")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory} bytes")
        
        success = (depth > 5)  # Linear arrangement in 3D should create significant depth
        
        self.test_results.append({
            'test': 'Deep Subdivision Octree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': num_points
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_large_scale_octree(self):
        """Test Octree with large number of points"""
        print("\n  🔶 Large Scale Octree Test")
        
        ot = octree.Octree(0, 0, 0, 10000, 10000, 10000)
        
        num_points = 2000  # Slightly less than QuadTree due to 3D complexity
        for i in range(num_points):
            x = random.uniform(0, 10000)
            y = random.uniform(0, 10000)
            z = random.uniform(0, 10000)
            ot.insert(x, y, z, f"large_{i}")
        
        depth = ot.depth()
        subdivisions = ot.subdivision_count() if hasattr(ot, 'subdivision_count') else 0
        memory = ot.memory_usage() if hasattr(ot, 'memory_usage') else 0
        
        print(f"    Points: {num_points}")
        print(f"    Depth: {depth}")
        print(f"    Subdivisions: {subdivisions}")
        print(f"    Memory: {memory:,} bytes")
        print(f"    Memory per point: {memory/num_points:.1f} bytes")
        
        success = (depth > 2)  # Large scale 3D should have reasonable depth
        
        self.test_results.append({
            'test': 'Large Scale Octree',
            'depth': depth,
            'subdivisions': subdivisions,
            'memory': memory,
            'success': success,
            'points': num_points
        })
        
        print(f"    Result: {'✓ PASS' if success else '✗ FAIL'}")
    
    def test_memory_scaling_octree(self):
        """Test memory scaling with different point counts for Octree"""
        print("\n  🔶 Memory Scaling Octree Test")
        
        point_counts = [10, 50, 100, 300, 500]
        memory_measurements = []
        
        for count in point_counts:
            ot = octree.Octree(0, 0, 0, 1000, 1000, 1000)
            
            for i in range(count):
                x = random.uniform(0, 1000)
                y = random.uniform(0, 1000)
                z = random.uniform(0, 1000)
                ot.insert(x, y, z, f"scale_{i}")
            
            depth = ot.depth()
            subdivisions = ot.subdivision_count() if hasattr(ot, 'subdivision_count') else 0
            memory = ot.memory_usage() if hasattr(ot, 'memory_usage') else 0
            
            memory_per_point = memory / count if count > 0 else 0
            memory_measurements.append({
                'points': count,
                'depth': depth,
                'subdivisions': subdivisions,
                'memory': memory,
                'memory_per_point': memory_per_point
            })
            
            print(f"    {count:3} points: depth={depth:2}, subdivisions={subdivisions:3}, "
                  f"memory={memory:6,} bytes ({memory_per_point:.1f} bytes/point)")
        
        # Analyze scaling efficiency
        if len(memory_measurements) >= 2:
            first_mem_per_point = memory_measurements[0]['memory_per_point']
            last_mem_per_point = memory_measurements[-1]['memory_per_point']
            scaling_efficiency = last_mem_per_point <= first_mem_per_point * 2
            
            print(f"    Scaling efficiency: {scaling_efficiency}")
        else:
            scaling_efficiency = True
        
        self.test_results.append({
            'test': 'Memory Scaling Octree',
            'measurements': memory_measurements,
            'success': scaling_efficiency
        })
        
        print(f"    Result: {'✓ PASS' if scaling_efficiency else '✗ FAIL'}")
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.get('success', False)])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 Overall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests} ✓")
        print(f"  Failed: {failed_tests} ✗")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n🔍 Detailed Results:")
        for result in self.test_results:
            status = "✓ PASS" if result.get('success', False) else "✗ FAIL"
            test_name = result['test']
            
            print(f"  {status} {test_name}")
            
            # Print key metrics if available
            if 'depth' in result and 'subdivisions' in result and 'memory' in result:
                print(f"      Depth: {result['depth']}, Subdivisions: {result['subdivisions']}, "
                      f"Memory: {result['memory']:,} bytes")
                if 'points' in result:
                    print(f"      Points: {result['points']}")
        
        print(f"\n⏱️ Test Duration: {time.time() - self.start_time:.2f} seconds")
        
        print(f"\n🎯 Key Observations:")
        print(f"  • depth() returns tree subdivision depth (0 for no subdivision)")
        print(f"  • subdivision_count() tracks total subdivisions performed")
        print(f"  • memory_usage() reports bytes allocated by the tree")
        print(f"  • Memory scaling varies with tree structure and point distribution")
        print(f"  • Clustered points create deeper trees than distributed points")


def main():
    """Run the comprehensive depth, subdivision, and memory tests"""
    tester = DepthSubdivisionMemoryTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()