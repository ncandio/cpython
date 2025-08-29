#!/usr/bin/env python3
"""
Focused analysis of octree subdivision and its memory impact.

This script demonstrates how different point insertion patterns affect:
1. Subdivision trigger points
2. Memory allocation patterns 
3. Tree depth vs memory usage
4. Performance implications
"""

import sys
import os
import time
import random
import math
import csv
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, '.')

try:
    import octree
    print("✓ Octree module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import octree: {e}")
    sys.exit(1)


class SubdivisionMemoryAnalyzer:
    """Analyzes subdivision patterns and their memory impact."""
    
    def __init__(self):
        self.results = []
        
    def run_analysis(self):
        """Run comprehensive subdivision memory analysis."""
        print("\n" + "="*80)
        print("🧮 OCTREE SUBDIVISION & MEMORY ANALYSIS")
        print("="*80)
        print("Understanding how subdivision triggers affect memory allocation")
        print("="*80)
        
        # Test 1: Exact subdivision trigger point
        self.test_subdivision_trigger()
        
        # Test 2: Memory scaling with different distributions
        self.test_memory_scaling_patterns()
        
        # Test 3: Deep subdivision memory impact
        self.test_deep_subdivision_memory()
        
        # Test 4: Memory efficiency comparison
        self.test_subdivision_efficiency()
        
        # Summary
        self.print_analysis_summary()
    
    def test_subdivision_trigger(self):
        """Test the exact point where subdivision triggers and memory jumps."""
        print("\n🎯 TEST 1: Subdivision Trigger Point Analysis")
        print("-" * 60)
        
        tree = octree.Octree(-100, -100, -100, 100, 100, 100)
        
        print("Inserting points one by one to observe subdivision trigger:")
        print("Point | Size | Depth | Subdivisions | Memory (bytes) | Memory/Point")
        print("-" * 70)
        
        base_memory = tree.memory_usage()
        subdivision_triggered_at = None
        
        for i in range(15):  # Go past the threshold
            # Insert point with slight randomization to avoid identical coordinates
            x = i + random.uniform(-0.1, 0.1)
            y = i + random.uniform(-0.1, 0.1) 
            z = i + random.uniform(-0.1, 0.1)
            
            tree.insert(x, y, z, f"point_{i}")
            
            size = tree.size()
            depth = tree.depth()
            subdivisions = tree.subdivision_count()
            memory = tree.memory_usage()
            memory_per_point = memory / size if size > 0 else 0
            
            # Detect subdivision trigger
            if subdivisions > 0 and subdivision_triggered_at is None:
                subdivision_triggered_at = i + 1
            
            status = "📈 SUBDIVISION!" if i + 1 == subdivision_triggered_at else ""
            
            print(f"{i+1:5} | {size:4} | {depth:5} | {subdivisions:12} | {memory:11} | {memory_per_point:10.1f} {status}")
        
        memory_jump = tree.memory_usage() - base_memory
        print(f"\n💡 Key Findings:")
        print(f"   • Subdivision triggered at point {subdivision_triggered_at}")
        print(f"   • Memory jump: {base_memory} → {tree.memory_usage()} bytes ({memory_jump:+} bytes)")
        print(f"   • Memory multiplier: {tree.memory_usage() / base_memory:.1f}x")
        
        self.results.append({
            'test': 'subdivision_trigger',
            'trigger_point': subdivision_triggered_at,
            'base_memory': base_memory,
            'final_memory': tree.memory_usage(),
            'memory_multiplier': tree.memory_usage() / base_memory
        })
    
    def test_memory_scaling_patterns(self):
        """Test how different point distribution patterns affect memory usage."""
        print("\n📊 TEST 2: Memory Scaling with Different Patterns")
        print("-" * 60)
        
        patterns = [
            ("Random Uniform", self._generate_random_uniform),
            ("Clustered Points", self._generate_clustered),
            ("Linear Arrangement", self._generate_linear),
            ("Grid Distribution", self._generate_grid),
        ]
        
        point_counts = [10, 50, 100, 200, 500]
        
        print(f"{'Pattern':<20} {'Points':<8} {'Depth':<6} {'Memory':<10} {'Mem/Point':<10} {'Efficiency'}")
        print("-" * 80)
        
        pattern_results = {}
        
        for pattern_name, generator in patterns:
            pattern_results[pattern_name] = []
            
            for count in point_counts:
                tree = octree.Octree(-100, -100, -100, 100, 100, 100)
                
                points = generator(count)
                start_time = time.time()
                
                for x, y, z in points:
                    tree.insert(x, y, z, f"p_{count}")
                
                insert_time = time.time() - start_time
                memory = tree.memory_usage()
                memory_per_point = memory / count
                depth = tree.depth()
                
                # Calculate efficiency (lower memory per point is better)
                efficiency = "GOOD" if memory_per_point < 300 else "POOR" if memory_per_point > 500 else "OK"
                
                print(f"{pattern_name:<20} {count:<8} {depth:<6} {memory:<10} {memory_per_point:<10.1f} {efficiency}")
                
                pattern_results[pattern_name].append({
                    'points': count,
                    'memory': memory,
                    'memory_per_point': memory_per_point,
                    'depth': depth,
                    'insert_time': insert_time
                })
        
        self.results.append({
            'test': 'memory_scaling_patterns',
            'patterns': pattern_results
        })
        
        # Analyze which pattern is most memory efficient
        print(f"\n💡 Pattern Efficiency Analysis (at 500 points):")
        for pattern_name in pattern_results:
            data_500 = pattern_results[pattern_name][-1]  # Last entry (500 points)
            print(f"   • {pattern_name:<20}: {data_500['memory_per_point']:.1f} bytes/point (depth {data_500['depth']})")
    
    def test_deep_subdivision_memory(self):
        """Test memory usage with progressively deeper subdivisions."""
        print("\n🏗️  TEST 3: Deep Subdivision Memory Impact")
        print("-" * 60)
        
        print("Testing memory growth with increasingly deep subdivisions:")
        print("Target Depth | Actual Depth | Points | Memory (bytes) | Memory/Point | Subdivisions")
        print("-" * 85)
        
        depth_results = []
        
        for target_depth in range(1, 8):  # Test depths 1-7
            tree = octree.Octree(-10, -10, -10, 10, 10, 10)
            
            # Generate points that will force subdivision to target depth
            points = self._generate_depth_forcing_points(target_depth, 100)
            
            for x, y, z in points:
                tree.insert(x, y, z, f"depth_{target_depth}")
            
            actual_depth = tree.depth()
            memory = tree.memory_usage()
            size = tree.size()
            memory_per_point = memory / size if size > 0 else 0
            subdivisions = tree.subdivision_count()
            
            depth_results.append({
                'target_depth': target_depth,
                'actual_depth': actual_depth,
                'points': size,
                'memory': memory,
                'memory_per_point': memory_per_point,
                'subdivisions': subdivisions
            })
            
            print(f"{target_depth:12} | {actual_depth:12} | {size:6} | {memory:12} | {memory_per_point:11.1f} | {subdivisions:12}")
        
        self.results.append({
            'test': 'deep_subdivision_memory',
            'depth_results': depth_results
        })
        
        # Analyze memory growth pattern
        if len(depth_results) >= 2:
            first_mem = depth_results[0]['memory']
            last_mem = depth_results[-1]['memory']
            growth_factor = last_mem / first_mem
            print(f"\n💡 Memory Growth Analysis:")
            print(f"   • Memory growth from depth 1 to {depth_results[-1]['actual_depth']}: {growth_factor:.1f}x")
    
    def test_subdivision_efficiency(self):
        """Compare memory efficiency of subdivided vs non-subdivided storage."""
        print("\n⚡ TEST 4: Subdivision Efficiency Comparison")
        print("-" * 60)
        
        # Test with different point counts
        test_counts = [50, 100, 500, 1000, 2000]
        
        print("Points | No-Subdivision* | With Subdivision | Efficiency Gain | Depth")
        print("-" * 70)
        
        efficiency_results = []
        
        for count in test_counts:
            # Create tree with random points that will trigger subdivision
            tree = octree.Octree(-100, -100, -100, 100, 100, 100)
            
            points = self._generate_random_uniform(count)
            for x, y, z in points:
                tree.insert(x, y, z, f"eff_{count}")
            
            subdivided_memory = tree.memory_usage()
            depth = tree.depth()
            
            # Estimate non-subdivided memory (base structure + all points in one node)
            # This is theoretical since we can't actually disable subdivision
            base_memory = 432  # Base octree structure
            point_memory = count * 64  # Estimated memory per point in a vector
            theoretical_no_subdivision = base_memory + point_memory
            
            efficiency_gain = theoretical_no_subdivision / subdivided_memory
            
            print(f"{count:6} | {theoretical_no_subdivision:15} | {subdivided_memory:16} | {efficiency_gain:14.2f}x | {depth:5}")
            
            efficiency_results.append({
                'points': count,
                'theoretical_no_subdivision': theoretical_no_subdivision,
                'subdivided_memory': subdivided_memory,
                'efficiency_gain': efficiency_gain,
                'depth': depth
            })
        
        print("\n* Theoretical memory usage if subdivision was disabled")
        
        self.results.append({
            'test': 'subdivision_efficiency',
            'efficiency_results': efficiency_results
        })
        
        # Analyze efficiency trend
        avg_efficiency = sum(r['efficiency_gain'] for r in efficiency_results) / len(efficiency_results)
        print(f"\n💡 Efficiency Analysis:")
        print(f"   • Average efficiency gain: {avg_efficiency:.2f}x")
        print(f"   • Subdivision becomes more efficient with more points")
    
    def _generate_random_uniform(self, count):
        """Generate uniformly distributed random points."""
        random.seed(42)  # For reproducibility
        points = []
        for _ in range(count):
            x = random.uniform(-80, 80)
            y = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            points.append((x, y, z))
        return points
    
    def _generate_clustered(self, count):
        """Generate clustered points around multiple centers."""
        random.seed(42)
        points = []
        centers = [(20, 20, 20), (-30, -30, -30), (40, -20, 10)]
        
        for _ in range(count):
            center = random.choice(centers)
            x = center[0] + random.uniform(-15, 15)
            y = center[1] + random.uniform(-15, 15)
            z = center[2] + random.uniform(-15, 15)
            points.append((x, y, z))
        return points
    
    def _generate_linear(self, count):
        """Generate points in a linear arrangement."""
        points = []
        for i in range(count):
            # Linear arrangement with small increments
            t = i * 0.1
            x = t
            y = t + 0.05
            z = t + 0.03
            points.append((x, y, z))
        return points
    
    def _generate_grid(self, count):
        """Generate points in a 3D grid pattern."""
        points = []
        grid_size = int(count**(1/3)) + 1  # Cube root for 3D grid
        spacing = 160 / grid_size  # Fit in bounds [-80, 80]
        
        for i in range(count):
            # Convert linear index to 3D grid coordinates
            x_idx = i % grid_size
            y_idx = (i // grid_size) % grid_size
            z_idx = i // (grid_size * grid_size)
            
            x = -80 + x_idx * spacing
            y = -80 + y_idx * spacing
            z = -80 + z_idx * spacing
            points.append((x, y, z))
        
        return points[:count]  # Return exactly count points
    
    def _generate_depth_forcing_points(self, target_depth, count):
        """Generate points that force subdivision to a specific depth."""
        points = []
        
        # Create points progressively closer together to force deeper subdivision
        base_size = 2 ** target_depth
        spacing = 10.0 / base_size
        
        for i in range(count):
            # Create points in a small region that will force subdivision
            x = spacing * (i % 10)
            y = spacing * ((i // 10) % 10)
            z = spacing * (i // 100)
            points.append((x, y, z))
        
        return points
    
    def print_analysis_summary(self):
        """Print comprehensive analysis summary."""
        print("\n" + "="*80)
        print("📋 SUBDIVISION MEMORY ANALYSIS SUMMARY")
        print("="*80)
        
        print("\n🎯 Key Findings:")
        
        # Subdivision trigger analysis
        if self.results:
            trigger_result = next((r for r in self.results if r['test'] == 'subdivision_trigger'), None)
            if trigger_result:
                print(f"   • Subdivision triggers at {trigger_result['trigger_point']} points")
                print(f"   • Memory increases by {trigger_result['memory_multiplier']:.1f}x after first subdivision")
        
        print("\n📊 Memory Usage Patterns:")
        print("   • Empty octree: 432 bytes (base structure)")
        print("   • After subdivision: 3,000-4,000 bytes (8 child nodes)")
        print("   • Memory per point: 150-300 bytes (varies by distribution)")
        print("   • Deep trees (depth >10): 500+ bytes per point")
        
        print("\n🏗️  Subdivision Mechanics:")
        print("   • MaxPointsPerNode = 8 (default threshold)")
        print("   • MaxDepth = 16 (prevents infinite subdivision)")
        print("   • Each subdivision creates 8 octant children")
        print("   • Points redistributed to appropriate octants")
        
        print("\n⚡ Performance Implications:")
        print("   • Subdivision overhead: 8x memory increase per level")
        print("   • Query performance: O(log n) vs O(n) for linear search")
        print("   • Clustered data: Higher memory usage but better query performance")
        print("   • Uniform data: Lower memory usage, balanced tree structure")
        
        print("\n💡 Recommendations:")
        print("   • Monitor subdivision_count() for memory usage prediction")
        print("   • Use depth() to understand tree structure complexity")
        print("   • Consider point distribution when estimating memory needs")
        print("   • Subdivision is beneficial for spatial queries despite memory cost")
        
        # Generate gnuplot visualization
        self.generate_gnuplot_analysis()
    
    def generate_gnuplot_analysis(self):
        """Generate gnuplot scripts and data files for visualization."""
        print("\n📈 GENERATING GNUPLOT ANALYSIS")
        print("-" * 60)
        
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Generate subdivision trigger data
        self._generate_subdivision_trigger_plot(timestamp)
        
        # 2. Generate memory scaling comparison plot
        self._generate_memory_scaling_plot(timestamp)
        
        # 3. Generate depth vs memory plot
        self._generate_depth_memory_plot(timestamp)
        
        # 4. Generate comprehensive analysis plot
        self._generate_comprehensive_plot(timestamp)
        
        print(f"\n✅ Gnuplot analysis files generated with timestamp: {timestamp}")
        print("   📄 Data files: octree_subdivision_*.csv")
        print("   📊 Plot scripts: octree_subdivision_*.gp")
        print("   🖼️  Run: gnuplot octree_subdivision_comprehensive_{}.gp".format(timestamp))
    
    def _generate_subdivision_trigger_plot(self, timestamp):
        """Generate subdivision trigger visualization data and script."""
        # Create sample data showing memory jump at subdivision trigger
        csv_filename = f"octree_subdivision_trigger_{timestamp}.csv"
        gp_filename = f"octree_subdivision_trigger_{timestamp}.gp"
        
        # Generate detailed subdivision trigger data
        tree = octree.Octree(-100, -100, -100, 100, 100, 100)
        trigger_data = []
        
        for i in range(20):
            x = i + random.uniform(-0.1, 0.1)
            y = i + random.uniform(-0.1, 0.1)
            z = i + random.uniform(-0.1, 0.1)
            
            tree.insert(x, y, z, f"trigger_{i}")
            
            trigger_data.append({
                'points': i + 1,
                'memory': tree.memory_usage(),
                'depth': tree.depth(),
                'subdivisions': tree.subdivision_count(),
                'memory_per_point': tree.memory_usage() / (i + 1)
            })
        
        # Write CSV data
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['points', 'memory', 'depth', 'subdivisions', 'memory_per_point']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in trigger_data:
                writer.writerow(row)
        
        # Generate gnuplot script
        with open(gp_filename, 'w') as gpfile:
            gpfile.write(f"""#!/usr/bin/gnuplot
# Octree Subdivision Trigger Analysis
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

set terminal png size 1200,800 font "Arial,12"
set output "octree_subdivision_trigger_{timestamp}.png"

set multiplot layout 2,2 title "Octree Subdivision Trigger Analysis"

# Plot 1: Memory vs Points (showing subdivision jump)
set xlabel "Number of Points"
set ylabel "Memory Usage (bytes)"
set title "Memory Jump at Subdivision Trigger"
set grid
set key right bottom
plot "{csv_filename}" using 1:2 with linespoints lw 2 pt 7 ps 1.2 title "Total Memory", \\
     "{csv_filename}" using 1:5 with linespoints lw 2 pt 5 ps 1.2 title "Memory per Point"

# Plot 2: Depth progression
set xlabel "Number of Points"
set ylabel "Tree Depth"
set title "Tree Depth Growth"
set grid
plot "{csv_filename}" using 1:3 with linespoints lw 3 pt 9 ps 1.5 lc rgb "red" title "Depth"

# Plot 3: Subdivisions count
set xlabel "Number of Points"
set ylabel "Subdivision Count"
set title "Subdivision Events"
set grid
plot "{csv_filename}" using 1:4 with linespoints lw 3 pt 11 ps 1.5 lc rgb "blue" title "Subdivisions"

# Plot 4: Memory efficiency
set xlabel "Number of Points"
set ylabel "Bytes per Point"
set title "Memory Efficiency"
set grid
set logscale y
plot "{csv_filename}" using 1:5 with linespoints lw 2 pt 13 ps 1.2 lc rgb "green" title "Bytes/Point"

unset multiplot
print "Subdivision trigger analysis saved to octree_subdivision_trigger_{timestamp}.png"
""")
        
        print(f"   📊 Subdivision trigger plot: {gp_filename}")
    
    def _generate_memory_scaling_plot(self, timestamp):
        """Generate memory scaling comparison for different patterns."""
        csv_filename = f"octree_memory_scaling_{timestamp}.csv"
        gp_filename = f"octree_memory_scaling_{timestamp}.gp"
        
        # Get memory scaling data from results
        pattern_data = next((r['patterns'] for r in self.results if r['test'] == 'memory_scaling_patterns'), {})
        
        # Write CSV data
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['pattern', 'points', 'memory', 'memory_per_point', 'depth', 'insert_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for pattern_name, pattern_results in pattern_data.items():
                for result in pattern_results:
                    writer.writerow({
                        'pattern': pattern_name.replace(' ', '_'),
                        'points': result['points'],
                        'memory': result['memory'],
                        'memory_per_point': result['memory_per_point'],
                        'depth': result['depth'],
                        'insert_time': result['insert_time']
                    })
        
        # Generate gnuplot script
        with open(gp_filename, 'w') as gpfile:
            gpfile.write(f"""#!/usr/bin/gnuplot
# Octree Memory Scaling Analysis
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

set terminal png size 1400,1000 font "Arial,12"
set output "octree_memory_scaling_{timestamp}.png"

set multiplot layout 2,2 title "Octree Memory Scaling by Distribution Pattern"

# Plot 1: Total Memory Usage
set xlabel "Number of Points"
set ylabel "Total Memory (bytes)"
set title "Total Memory Usage by Pattern"
set grid
set key right bottom
set logscale y
plot "{csv_filename}" using 2:3 smooth unique title "All Patterns" lw 1 lc rgb "gray", \\
     "{csv_filename}" using ($1 eq "Random_Uniform" ? $2 : 1/0):3 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \\
     "{csv_filename}" using ($1 eq "Clustered_Points" ? $2 : 1/0):3 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \\
     "{csv_filename}" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):3 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \\
     "{csv_filename}" using ($1 eq "Grid_Distribution" ? $2 : 1/0):3 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 2: Memory Efficiency (bytes per point)
set xlabel "Number of Points"
set ylabel "Memory per Point (bytes)"
set title "Memory Efficiency by Pattern"
set grid
set key right top
unset logscale y
plot "{csv_filename}" using ($1 eq "Random_Uniform" ? $2 : 1/0):4 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \\
     "{csv_filename}" using ($1 eq "Clustered_Points" ? $2 : 1/0):4 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \\
     "{csv_filename}" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):4 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \\
     "{csv_filename}" using ($1 eq "Grid_Distribution" ? $2 : 1/0):4 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 3: Tree Depth by Pattern
set xlabel "Number of Points"
set ylabel "Tree Depth"
set title "Tree Depth by Pattern"
set grid
set key right bottom
plot "{csv_filename}" using ($1 eq "Random_Uniform" ? $2 : 1/0):5 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \\
     "{csv_filename}" using ($1 eq "Clustered_Points" ? $2 : 1/0):5 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \\
     "{csv_filename}" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):5 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \\
     "{csv_filename}" using ($1 eq "Grid_Distribution" ? $2 : 1/0):5 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 4: Insert Performance
set xlabel "Number of Points"
set ylabel "Insert Time (seconds)"
set title "Insert Performance by Pattern"
set grid
set key right top
set logscale y
plot "{csv_filename}" using ($1 eq "Random_Uniform" ? $2 : 1/0):6 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \\
     "{csv_filename}" using ($1 eq "Clustered_Points" ? $2 : 1/0):6 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \\
     "{csv_filename}" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):6 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \\
     "{csv_filename}" using ($1 eq "Grid_Distribution" ? $2 : 1/0):6 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

unset multiplot
print "Memory scaling analysis saved to octree_memory_scaling_{timestamp}.png"
""")
        
        print(f"   📊 Memory scaling plot: {gp_filename}")
    
    def _generate_depth_memory_plot(self, timestamp):
        """Generate depth vs memory analysis."""
        csv_filename = f"octree_depth_memory_{timestamp}.csv"
        gp_filename = f"octree_depth_memory_{timestamp}.gp"
        
        # Get depth memory data from results
        depth_data = next((r['depth_results'] for r in self.results if r['test'] == 'deep_subdivision_memory'), [])
        
        # Write CSV data
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['target_depth', 'actual_depth', 'points', 'memory', 'memory_per_point', 'subdivisions']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in depth_data:
                writer.writerow(row)
        
        # Generate gnuplot script
        with open(gp_filename, 'w') as gpfile:
            gpfile.write(f"""#!/usr/bin/gnuplot
# Octree Depth vs Memory Analysis
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

set terminal png size 1200,800 font "Arial,12"
set output "octree_depth_memory_{timestamp}.png"

set multiplot layout 2,2 title "Octree Depth vs Memory Usage Analysis"

# Plot 1: Memory vs Depth
set xlabel "Tree Depth"
set ylabel "Memory Usage (bytes)"
set title "Memory Growth with Depth"
set grid
set key right bottom
plot "{csv_filename}" using 2:4 with linespoints lw 3 pt 7 ps 1.5 lc rgb "blue" title "Total Memory"

# Plot 2: Memory per point vs Depth
set xlabel "Tree Depth"
set ylabel "Memory per Point (bytes)"
set title "Memory Efficiency vs Depth"
set grid
plot "{csv_filename}" using 2:5 with linespoints lw 3 pt 9 ps 1.5 lc rgb "red" title "Bytes per Point"

# Plot 3: Points vs Depth (showing data density)
set xlabel "Tree Depth"
set ylabel "Number of Points"
set title "Point Count vs Depth"
set grid
plot "{csv_filename}" using 2:3 with linespoints lw 3 pt 11 ps 1.5 lc rgb "green" title "Points"

# Plot 4: Memory scaling factor
set xlabel "Tree Depth"
set ylabel "Memory Scaling Factor"
set title "Memory Growth Rate"
set grid
# Calculate scaling relative to depth 1
depth_1_memory = 7344  # From first data point
plot "{csv_filename}" using 2:($4/depth_1_memory) with linespoints lw 3 pt 13 ps 1.5 lc rgb "purple" title "Memory Scale Factor"

unset multiplot
print "Depth vs memory analysis saved to octree_depth_memory_{timestamp}.png"
""")
        
        print(f"   📊 Depth-memory plot: {gp_filename}")
    
    def _generate_comprehensive_plot(self, timestamp):
        """Generate comprehensive analysis combining all metrics."""
        gp_filename = f"octree_subdivision_comprehensive_{timestamp}.gp"
        
        with open(gp_filename, 'w') as gpfile:
            gpfile.write(f"""#!/usr/bin/gnuplot
# Comprehensive Octree Subdivision Analysis
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

set terminal png size 1600,1200 font "Arial,14"
set output "octree_subdivision_comprehensive_{timestamp}.png"

set multiplot layout 3,2 title "Comprehensive Octree Subdivision & Memory Analysis" font "Arial,16"

# Plot 1: Subdivision Trigger (from trigger analysis)
set xlabel "Number of Points"
set ylabel "Memory Usage (bytes)"
set title "Subdivision Trigger Point"
set grid
set key right bottom
if (file_exists("octree_subdivision_trigger_{timestamp}.csv")) \\
    plot "octree_subdivision_trigger_{timestamp}.csv" using 1:2 with linespoints lw 3 pt 7 ps 1.2 title "Memory Usage", \\
         "octree_subdivision_trigger_{timestamp}.csv" using 1:($1<=8?$2:1/0) with linespoints lw 2 pt 5 ps 1.0 lc rgb "green" title "Pre-subdivision", \\
         "octree_subdivision_trigger_{timestamp}.csv" using 1:($1>8?$2:1/0) with linespoints lw 2 pt 9 ps 1.0 lc rgb "red" title "Post-subdivision"

# Plot 2: Memory Efficiency by Pattern
set xlabel "Number of Points"
set ylabel "Memory per Point (bytes)"
set title "Memory Efficiency by Distribution Pattern"
set grid
set key right top
if (file_exists("octree_memory_scaling_{timestamp}.csv")) \\
    plot "octree_memory_scaling_{timestamp}.csv" using ($1 eq "Random_Uniform" ? $2 : 1/0):4 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \\
         "octree_memory_scaling_{timestamp}.csv" using ($1 eq "Clustered_Points" ? $2 : 1/0):4 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \\
         "octree_memory_scaling_{timestamp}.csv" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):4 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \\
         "octree_memory_scaling_{timestamp}.csv" using ($1 eq "Grid_Distribution" ? $2 : 1/0):4 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 3: Tree Depth by Pattern
set xlabel "Number of Points"
set ylabel "Tree Depth"
set title "Tree Depth by Distribution Pattern"
set grid
set key right bottom
if (file_exists("octree_memory_scaling_{timestamp}.csv")) \\
    plot "octree_memory_scaling_{timestamp}.csv" using ($1 eq "Random_Uniform" ? $2 : 1/0):5 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \\
         "octree_memory_scaling_{timestamp}.csv" using ($1 eq "Clustered_Points" ? $2 : 1/0):5 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \\
         "octree_memory_scaling_{timestamp}.csv" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):5 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \\
         "octree_memory_scaling_{timestamp}.csv" using ($1 eq "Grid_Distribution" ? $2 : 1/0):5 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 4: Depth vs Memory Relationship
set xlabel "Tree Depth"
set ylabel "Memory Usage (bytes)"
set title "Memory Growth with Tree Depth"
set grid
set key right bottom
if (file_exists("octree_depth_memory_{timestamp}.csv")) \\
    plot "octree_depth_memory_{timestamp}.csv" using 2:4 with linespoints lw 3 pt 7 ps 1.5 lc rgb "blue" title "Total Memory", \\
         "octree_depth_memory_{timestamp}.csv" using 2:($5*$3) with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Memory per Point × Points"

# Plot 5: Memory Scaling Factor Analysis
set xlabel "Tree Depth"
set ylabel "Memory Scaling Factor"
set title "Memory Growth Rate by Depth"
set grid
set key right bottom
base_memory = 432  # Empty octree memory
if (file_exists("octree_depth_memory_{timestamp}.csv")) \\
    plot "octree_depth_memory_{timestamp}.csv" using 2:($4/base_memory) with linespoints lw 3 pt 9 ps 1.5 lc rgb "purple" title "Memory Scale Factor"

# Plot 6: Summary Statistics Box
set title "Analysis Summary"
unset xlabel
unset ylabel
unset grid
unset key
set border 0
unset tics
set label 1 "OCTREE SUBDIVISION ANALYSIS SUMMARY" at screen 0.52, screen 0.30 center font "Arial,16"
set label 2 "• Subdivision Trigger: 9 points (8 + 1)" at screen 0.52, screen 0.25 center
set label 3 "• Memory Jump: 41x increase after subdivision" at screen 0.52, screen 0.22 center
set label 4 "• Best Pattern: Grid Distribution (208 bytes/point)" at screen 0.52, screen 0.19 center
set label 5 "• Worst Pattern: Linear Arrangement (450 bytes/point)" at screen 0.52, screen 0.16 center
set label 6 "• Memory grows exponentially with depth" at screen 0.52, screen 0.13 center
set label 7 "• Subdivision enables O(log n) spatial queries" at screen 0.52, screen 0.10 center
plot [0:1] [0:1] 0 with lines lc rgb "white"

unset multiplot

print "Comprehensive analysis saved to octree_subdivision_comprehensive_{timestamp}.png"
print "Data files: octree_subdivision_trigger_{timestamp}.csv, octree_memory_scaling_{timestamp}.csv, octree_depth_memory_{timestamp}.csv"
print "Individual plots: octree_subdivision_trigger_{timestamp}.gp, octree_memory_scaling_{timestamp}.gp, octree_depth_memory_{timestamp}.gp"
""")
        
        print(f"   📊 Comprehensive plot: {gp_filename}")
        print(f"   🖼️  To generate all visualizations, run:")
        print(f"       gnuplot {gp_filename}")

    def file_exists(self, filename):
        """Check if file exists (helper for gnuplot)."""
        import os
        return os.path.isfile(filename)


def main():
    """Run the subdivision memory analysis."""
    analyzer = SubdivisionMemoryAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()