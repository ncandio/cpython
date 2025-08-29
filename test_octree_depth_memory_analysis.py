#!/usr/bin/env python3
"""
Focused Octree Depth vs Memory Usage Analysis
Tests relationship between depth() and memory_usage() with increasing tree depths
Produces CSV data for analysis and visualization
"""

import sys
import os
import time
import random
import csv
from datetime import datetime

# Add current directory to path
sys.path.insert(0, '.')

try:
    import octree
    print("✓ Octree module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import octree: {e}")
    sys.exit(1)

class OctreeDepthMemoryAnalyzer:
    """Analyze relationship between Octree depth and memory usage"""
    
    def __init__(self):
        self.results = []
        self.csv_filename = f"octree_depth_memory_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
    def run_analysis(self):
        """Run comprehensive depth vs memory analysis"""
        print("\n" + "="*80)
        print("🧠 OCTREE DEPTH vs MEMORY USAGE ANALYSIS")
        print("="*80)
        
        # Strategy 1: Force increasing depths with clustered points
        print("\n📊 Strategy 1: Clustered Points (Force Deep Subdivision)")
        self.test_clustered_depth_progression()
        
        # Strategy 2: Linear point arrangement for consistent depth increase
        print("\n📊 Strategy 2: Linear Arrangement (Predictable Depth)")
        self.test_linear_depth_progression()
        
        # Strategy 3: Recursive subdivision with controlled point placement
        print("\n📊 Strategy 3: Controlled Recursive Subdivision")
        self.test_controlled_depth_progression()
        
        # Strategy 4: Point density scaling
        print("\n📊 Strategy 4: Point Density Scaling")
        self.test_density_scaling()
        
        # Generate and display CSV
        self.save_to_csv()
        self.display_csv_analysis()
        
    def test_clustered_depth_progression(self):
        """Test depth progression using increasingly tight clusters"""
        print("  Testing clustered point arrangements...")
        
        base_size = 1000
        cluster_tightness_factors = [100, 50, 25, 10, 5, 2, 1, 0.5, 0.25, 0.1]
        
        for i, tightness in enumerate(cluster_tightness_factors):
            ot = octree.Octree(0, 0, 0, base_size, base_size, base_size)
            
            # Create tight cluster of points
            num_points = 50 + i * 10  # Increase point count slightly each iteration
            center_x, center_y, center_z = base_size/2, base_size/2, base_size/2
            
            for j in range(num_points):
                # Gaussian distribution with decreasing standard deviation
                x = random.gauss(center_x, tightness)
                y = random.gauss(center_y, tightness)
                z = random.gauss(center_z, tightness)
                
                # Clamp to bounds
                x = max(0, min(base_size, x))
                y = max(0, min(base_size, y))
                z = max(0, min(base_size, z))
                
                ot.insert(x, y, z, f"cluster_tight_{tightness}_{j}")
            
            depth = ot.depth()
            memory = ot.memory_usage()
            subdivisions = ot.subdivision_count()
            
            self.results.append({
                'strategy': 'Clustered',
                'iteration': i + 1,
                'parameter': f'tightness_{tightness}',
                'num_points': num_points,
                'depth': depth,
                'memory_bytes': memory,
                'subdivisions': subdivisions,
                'memory_per_point': memory / num_points if num_points > 0 else 0
            })
            
            print(f"    Iteration {i+1:2d}: Tightness={tightness:5.2f}, Points={num_points:2d}, "
                  f"Depth={depth:2d}, Memory={memory:6,} bytes")
    
    def test_linear_depth_progression(self):
        """Test depth using linear point arrangements with decreasing increments"""
        print("  Testing linear point arrangements...")
        
        base_size = 1000
        increments = [10, 5, 2, 1, 0.5, 0.25, 0.1, 0.05, 0.025, 0.01]
        
        for i, increment in enumerate(increments):
            ot = octree.Octree(0, 0, 0, base_size, base_size, base_size)
            
            # Create linear arrangement with decreasing spacing
            num_points = 60 + i * 5
            start_x, start_y, start_z = base_size/2, base_size/2, base_size/2
            
            for j in range(num_points):
                # Linear progression in 3D diagonal
                x = start_x + j * increment
                y = start_y + j * increment  
                z = start_z + j * increment
                
                # Wrap around if exceeding bounds
                x = x % base_size
                y = y % base_size
                z = z % base_size
                
                ot.insert(x, y, z, f"linear_{increment}_{j}")
            
            depth = ot.depth()
            memory = ot.memory_usage()
            subdivisions = ot.subdivision_count()
            
            self.results.append({
                'strategy': 'Linear',
                'iteration': i + 1,
                'parameter': f'increment_{increment}',
                'num_points': num_points,
                'depth': depth,
                'memory_bytes': memory,
                'subdivisions': subdivisions,
                'memory_per_point': memory / num_points if num_points > 0 else 0
            })
            
            print(f"    Iteration {i+1:2d}: Increment={increment:6.3f}, Points={num_points:2d}, "
                  f"Depth={depth:2d}, Memory={memory:6,} bytes")
    
    def test_controlled_depth_progression(self):
        """Test depth using controlled recursive subdivision patterns"""
        print("  Testing controlled recursive subdivision...")
        
        base_size = 1000
        subdivision_levels = list(range(1, 11))  # Target depths 1-10
        
        for target_depth in subdivision_levels:
            ot = octree.Octree(0, 0, 0, base_size, base_size, base_size)
            
            # Place points to force specific depth
            # Strategy: place points in nested octants
            self._place_points_for_target_depth(ot, target_depth, base_size)
            
            actual_depth = ot.depth()
            memory = ot.memory_usage()
            subdivisions = ot.subdivision_count()
            num_points = ot.size()
            
            self.results.append({
                'strategy': 'Controlled',
                'iteration': target_depth,
                'parameter': f'target_depth_{target_depth}',
                'num_points': num_points,
                'depth': actual_depth,
                'memory_bytes': memory,
                'subdivisions': subdivisions,
                'memory_per_point': memory / num_points if num_points > 0 else 0
            })
            
            print(f"    Target Depth {target_depth:2d}: Actual={actual_depth:2d}, Points={num_points:2d}, "
                  f"Memory={memory:6,} bytes")
    
    def _place_points_for_target_depth(self, octree_obj, target_depth, size):
        """Place points strategically to achieve target depth"""
        # Start at center and work outward in nested pattern
        center = size / 2
        
        # Base points to ensure some subdivision
        base_points = max(12, target_depth * 8)  # Ensure enough points for subdivision
        
        for i in range(base_points):
            # Create nested subdivision pattern
            depth_factor = min(i // 8, target_depth - 1)  # Which depth level
            subdivision_size = size / (2 ** depth_factor) / 4  # Size of subdivision
            
            # Octant selection (8 octants per level)
            octant = i % 8
            
            # Calculate octant offsets
            x_offset = (octant & 1) * subdivision_size - subdivision_size/2
            y_offset = ((octant >> 1) & 1) * subdivision_size - subdivision_size/2  
            z_offset = ((octant >> 2) & 1) * subdivision_size - subdivision_size/2
            
            # Place point in specific octant at specific depth
            x = center + x_offset + random.uniform(-subdivision_size/8, subdivision_size/8)
            y = center + y_offset + random.uniform(-subdivision_size/8, subdivision_size/8)
            z = center + z_offset + random.uniform(-subdivision_size/8, subdivision_size/8)
            
            # Ensure bounds
            x = max(0, min(size-1, x))
            y = max(0, min(size-1, y))  
            z = max(0, min(size-1, z))
            
            octree_obj.insert(x, y, z, f"controlled_{target_depth}_{i}")
    
    def test_density_scaling(self):
        """Test how point density affects depth and memory"""
        print("  Testing point density scaling...")
        
        base_size = 1000
        densities = [10, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400]  # Points
        
        for i, num_points in enumerate(densities):
            ot = octree.Octree(0, 0, 0, base_size, base_size, base_size)
            
            # Random distribution with increasing density
            for j in range(num_points):
                x = random.uniform(0, base_size)
                y = random.uniform(0, base_size) 
                z = random.uniform(0, base_size)
                
                ot.insert(x, y, z, f"density_{num_points}_{j}")
            
            depth = ot.depth()
            memory = ot.memory_usage()
            subdivisions = ot.subdivision_count()
            
            self.results.append({
                'strategy': 'Density',
                'iteration': i + 1,
                'parameter': f'points_{num_points}',
                'num_points': num_points,
                'depth': depth,
                'memory_bytes': memory,
                'subdivisions': subdivisions,
                'memory_per_point': memory / num_points if num_points > 0 else 0
            })
            
            print(f"    Density {i+1:2d}: Points={num_points:4d}, Depth={depth:2d}, "
                  f"Memory={memory:7,} bytes ({memory/num_points:.1f} bytes/point)")
    
    def save_to_csv(self):
        """Save results to CSV file"""
        print(f"\n💾 Saving results to {self.csv_filename}...")
        
        with open(self.csv_filename, 'w', newline='') as csvfile:
            fieldnames = [
                'strategy', 'iteration', 'parameter', 'num_points', 
                'depth', 'memory_bytes', 'subdivisions', 'memory_per_point'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
        
        print(f"✓ Saved {len(self.results)} data points to CSV")
    
    def display_csv_analysis(self):
        """Display CSV content and analysis"""
        print(f"\n" + "="*80)
        print("📈 DEPTH vs MEMORY ANALYSIS RESULTS")
        print("="*80)
        
        # Display CSV content
        print(f"\n📄 CSV File Content ({self.csv_filename}):")
        print("-" * 100)
        
        # Print header
        header = "Strategy,Iter,Parameter,Points,Depth,Memory(bytes),Subdivisions,Mem/Point"
        print(header)
        print("-" * 100)
        
        # Print data rows
        for result in self.results:
            row = f"{result['strategy']:<9},{result['iteration']:>4},{result['parameter']:<20},"
            row += f"{result['num_points']:>6},{result['depth']:>5},{result['memory_bytes']:>12},"
            row += f"{result['subdivisions']:>11},{result['memory_per_point']:>8.1f}"
            print(row)
        
        # Analysis by strategy
        print(f"\n📊 Analysis by Strategy:")
        print("-" * 80)
        
        strategies = {}
        for result in self.results:
            strategy = result['strategy']
            if strategy not in strategies:
                strategies[strategy] = {
                    'count': 0,
                    'max_depth': 0,
                    'max_memory': 0,
                    'total_points': 0,
                    'total_memory': 0,
                    'depth_memory_pairs': []
                }
            
            s = strategies[strategy]
            s['count'] += 1
            s['max_depth'] = max(s['max_depth'], result['depth'])
            s['max_memory'] = max(s['max_memory'], result['memory_bytes'])
            s['total_points'] += result['num_points']
            s['total_memory'] += result['memory_bytes']
            s['depth_memory_pairs'].append((result['depth'], result['memory_bytes']))
        
        for strategy, stats in strategies.items():
            print(f"\n{strategy} Strategy:")
            print(f"  Tests: {stats['count']}")
            print(f"  Max Depth Achieved: {stats['max_depth']}")
            print(f"  Max Memory Used: {stats['max_memory']:,} bytes")
            print(f"  Avg Points per Test: {stats['total_points'] / stats['count']:.1f}")
            print(f"  Avg Memory per Test: {stats['total_memory'] / stats['count']:,.0f} bytes")
            
            # Depth-Memory correlation analysis
            depths = [pair[0] for pair in stats['depth_memory_pairs']]
            memories = [pair[1] for pair in stats['depth_memory_pairs']]
            
            if len(depths) > 1:
                # Simple correlation coefficient
                mean_depth = sum(depths) / len(depths)
                mean_memory = sum(memories) / len(memories)
                
                numerator = sum((d - mean_depth) * (m - mean_memory) 
                               for d, m in zip(depths, memories))
                
                depth_var = sum((d - mean_depth)**2 for d in depths)
                memory_var = sum((m - mean_memory)**2 for m in memories)
                
                if depth_var > 0 and memory_var > 0:
                    correlation = numerator / (depth_var * memory_var)**0.5
                    print(f"  Depth-Memory Correlation: {correlation:.3f}")
        
        # Overall insights
        print(f"\n🎯 Key Insights:")
        all_depths = [r['depth'] for r in self.results]
        all_memories = [r['memory_bytes'] for r in self.results]
        
        print(f"  • Depth Range: {min(all_depths)} to {max(all_depths)}")
        print(f"  • Memory Range: {min(all_memories):,} to {max(all_memories):,} bytes")
        
        # Memory growth patterns
        depth_memory_map = {}
        for result in self.results:
            depth = result['depth']
            memory = result['memory_bytes']
            if depth not in depth_memory_map:
                depth_memory_map[depth] = []
            depth_memory_map[depth].append(memory)
        
        print(f"\n📈 Memory Usage by Depth Level:")
        for depth in sorted(depth_memory_map.keys()):
            memories = depth_memory_map[depth]
            avg_memory = sum(memories) / len(memories)
            min_memory = min(memories)
            max_memory = max(memories)
            print(f"  Depth {depth:2d}: Avg={avg_memory:8.0f} bytes, "
                  f"Range=[{min_memory:6,} - {max_memory:7,}] bytes, Samples={len(memories)}")
        
        # Memory efficiency analysis
        print(f"\n⚡ Memory Efficiency Analysis:")
        
        # Find most memory-efficient configurations
        efficient_configs = sorted(self.results, key=lambda x: x['memory_per_point'])[:5]
        print(f"  Most Memory Efficient (bytes per point):")
        for i, config in enumerate(efficient_configs, 1):
            print(f"    {i}. {config['strategy']:>9} - {config['memory_per_point']:6.1f} bytes/point "
                  f"(Depth: {config['depth']}, Points: {config['num_points']})")
        
        # Find deepest trees
        deepest_configs = sorted(self.results, key=lambda x: x['depth'], reverse=True)[:5]
        print(f"\n  Deepest Trees Achieved:")
        for i, config in enumerate(deepest_configs, 1):
            print(f"    {i}. {config['strategy']:>9} - Depth {config['depth']} "
                  f"({config['memory_bytes']:,} bytes, {config['num_points']} points)")
        
        print(f"\n📄 Complete data saved to: {self.csv_filename}")
        print(f"   Use Excel, Google Sheets, or Python/R to create visualizations")
        
        # Generate gnuplot visualization
        self.generate_gnuplot_demo()
    
    def generate_gnuplot_demo(self):
        """Generate gnuplot scripts and execute them to create visualizations"""
        print(f"\n📈 GNUPLOT VISUALIZATION DEMO")
        print("="*80)
        
        # Create gnuplot script for depth vs memory scatter plot
        gnuplot_script = f"octree_depth_memory_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gp"
        
        with open(gnuplot_script, 'w') as f:
            f.write(f"""# Gnuplot script for Octree Depth vs Memory Analysis
# Generated automatically from test data
# Data file: {self.csv_filename}

set terminal pngcairo enhanced color size 1200,900 font 'Arial,12'
set output 'octree_depth_memory_analysis.png'

# Set up the plot
set title "Octree Depth vs Memory Usage Analysis" font 'Arial,16'
set xlabel "Tree Depth" font 'Arial,14'
set ylabel "Memory Usage (bytes)" font 'Arial,14'

# Configure grid and style
set grid xtics ytics mxtics mytics
set key top left
set logscale y

# Define colors and point styles for each strategy
set style line 1 lc rgb '#e41a1c' pt 7 ps 1.5  # Clustered - red circles
set style line 2 lc rgb '#377eb8' pt 5 ps 1.5  # Linear - blue squares
set style line 3 lc rgb '#4daf4a' pt 9 ps 1.5  # Controlled - green triangles
set style line 4 lc rgb '#984ea3' pt 11 ps 1.5 # Density - purple diamonds

# Plot data by strategy
plot '{self.csv_filename}' using ($5):($6) every ::1 title 'All Points' with points pt 6 ps 0.8 lc rgb 'gray', \\
     '<(grep "Clustered" {self.csv_filename})' using 5:6 title 'Clustered Strategy' with points ls 1, \\
     '<(grep "Linear" {self.csv_filename})' using 5:6 title 'Linear Strategy' with points ls 2, \\
     '<(grep "Controlled" {self.csv_filename})' using 5:6 title 'Controlled Strategy' with points ls 3, \\
     '<(grep "Density" {self.csv_filename})' using 5:6 title 'Density Strategy' with points ls 4

# Add trend line for clustered data (highest correlation)
f(x) = a*x + b
fit f(x) '<(grep "Clustered" {self.csv_filename})' using 5:(log($6)) via a, b
set samples 100
replot exp(f(x)) title sprintf('Clustered Trend: log(memory) = %.2fx + %.2f', a, b) with lines lw 2 lc rgb '#e41a1c' dt 2

# Create second plot: Memory per Point vs Depth
set output 'octree_memory_efficiency.png'
set title "Octree Memory Efficiency vs Depth" font 'Arial,16'
set ylabel "Memory per Point (bytes/point)" font 'Arial,14'
set nologscale y

plot '{self.csv_filename}' using ($5):($8) every ::1 title 'All Points' with points pt 6 ps 0.8 lc rgb 'gray', \\
     '<(grep "Clustered" {self.csv_filename})' using 5:8 title 'Clustered Strategy' with points ls 1, \\
     '<(grep "Linear" {self.csv_filename})' using 5:8 title 'Linear Strategy' with points ls 2, \\
     '<(grep "Controlled" {self.csv_filename})' using 5:8 title 'Controlled Strategy' with points ls 3, \\
     '<(grep "Density" {self.csv_filename})' using 5:8 title 'Density Strategy' with points ls 4

# Create third plot: 3D surface plot showing depth, points, and memory
set output 'octree_3d_analysis.png'
set title "3D Analysis: Depth, Points, Memory" font 'Arial,16'
set xlabel "Tree Depth" font 'Arial,14'
set ylabel "Number of Points" font 'Arial,14' 
set zlabel "Memory (bytes)" font 'Arial,14' rotate by 90

set dgrid3d 10,10
set hidden3d
set pm3d

splot '{self.csv_filename}' using 5:4:6 every ::1 title 'Memory Usage' with points pt 7 ps 1.5

# Create histogram of depth distribution
set output 'octree_depth_distribution.png'
set title "Distribution of Achieved Tree Depths" font 'Arial,16'
set xlabel "Tree Depth" font 'Arial,14'
set ylabel "Frequency" font 'Arial,14'

set style data histograms
set style histogram cluster gap 1
set style fill solid 0.7
set boxwidth 0.8

# Prepare data for histogram
set table 'depth_histogram.dat'
plot '{self.csv_filename}' using 5:(1.0) every ::1 smooth frequency
unset table

plot 'depth_histogram.dat' using 1:2 title 'Depth Distribution' lc rgb '#377eb8'

print ""
print "📊 Generated visualization files:"
print "  • octree_depth_memory_analysis.png - Main depth vs memory scatter plot"
print "  • octree_memory_efficiency.png - Memory efficiency analysis"
print "  • octree_3d_analysis.png - 3D surface plot"
print "  • octree_depth_distribution.png - Depth distribution histogram"
print ""
print "📋 Data Analysis Summary:"
""")
            
            # Add statistical analysis to gnuplot output
            f.write(self._generate_gnuplot_statistics())
        
        print(f"✓ Created gnuplot script: {gnuplot_script}")
        
        # Try to execute gnuplot
        try:
            import subprocess
            result = subprocess.run(['gnuplot', gnuplot_script], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Gnuplot executed successfully!")
                print("📊 Generated visualization files:")
                print("  • octree_depth_memory_analysis.png - Main depth vs memory scatter plot")
                print("  • octree_memory_efficiency.png - Memory efficiency analysis") 
                print("  • octree_3d_analysis.png - 3D surface plot")
                print("  • octree_depth_distribution.png - Depth distribution histogram")
                
                # Display some example gnuplot commands for manual execution
                self._show_manual_gnuplot_commands()
                
            else:
                print("⚠️ Gnuplot execution failed. You can run it manually:")
                print(f"   gnuplot {gnuplot_script}")
                print(f"   Error: {result.stderr}")
                self._show_manual_gnuplot_commands()
                
        except FileNotFoundError:
            print("⚠️ Gnuplot not found. Install it with:")
            print("   sudo apt-get install gnuplot  # Ubuntu/Debian")
            print("   brew install gnuplot          # macOS") 
            print("   yum install gnuplot           # RHEL/CentOS")
            print(f"\nThen run: gnuplot {gnuplot_script}")
            self._show_manual_gnuplot_commands()
            
        except Exception as e:
            print(f"⚠️ Error running gnuplot: {e}")
            print(f"You can run it manually: gnuplot {gnuplot_script}")
            self._show_manual_gnuplot_commands()
    
    def _generate_gnuplot_statistics(self):
        """Generate statistical analysis for gnuplot output"""
        stats = []
        
        # Group by strategy for analysis
        strategies = {}
        for result in self.results:
            strategy = result['strategy']
            if strategy not in strategies:
                strategies[strategy] = {'depths': [], 'memories': []}
            strategies[strategy]['depths'].append(result['depth'])
            strategies[strategy]['memories'].append(result['memory_bytes'])
        
        stats.append('print "📊 Statistical Analysis:"')
        stats.append('print ""')
        
        for strategy, data in strategies.items():
            depths = data['depths']
            memories = data['memories']
            
            avg_depth = sum(depths) / len(depths)
            max_depth = max(depths)
            avg_memory = sum(memories) / len(memories)
            max_memory = max(memories)
            
            stats.append(f'print "{strategy} Strategy:"')
            stats.append(f'print "  Average Depth: {avg_depth:.1f}"')
            stats.append(f'print "  Maximum Depth: {max_depth}"')
            stats.append(f'print "  Average Memory: {avg_memory:,.0f} bytes"')
            stats.append(f'print "  Maximum Memory: {max_memory:,} bytes"')
            stats.append('print ""')
        
        return '\\n'.join(stats)
    
    def _show_manual_gnuplot_commands(self):
        """Show manual gnuplot commands for users"""
        print(f"\n🔧 Manual Gnuplot Commands:")
        print(f"If you have gnuplot installed, you can create plots manually:")
        print(f"")
        
        # Basic scatter plot
        print(f"1. Basic Depth vs Memory scatter plot:")
        print(f"   gnuplot -e \"set terminal png; set output 'depth_memory.png'; "
              f"set title 'Depth vs Memory'; set xlabel 'Depth'; set ylabel 'Memory (bytes)'; "
              f"plot '{self.csv_filename}' using 5:6 every ::1 with points pt 7\"")
        print(f"")
        
        # Memory efficiency plot
        print(f"2. Memory efficiency plot:")
        print(f"   gnuplot -e \"set terminal png; set output 'efficiency.png'; "
              f"set title 'Memory Efficiency'; set xlabel 'Depth'; set ylabel 'Bytes per Point'; "
              f"plot '{self.csv_filename}' using 5:8 every ::1 with points pt 7\"")
        print(f"")
        
        # Strategy comparison
        print(f"3. Strategy comparison:")
        print(f"   gnuplot -e \"set terminal png; set output 'strategies.png'; "
              f"set title 'Strategy Comparison'; set xlabel 'Depth'; set ylabel 'Memory'; "
              f"plot '{self.csv_filename}' using 5:6 every ::1 title 'All' with points\"")
        print(f"")
        
        print(f"📖 Gnuplot Tutorial:")
        print(f"   Data columns in {self.csv_filename}:")
        print(f"   Column 1: strategy")
        print(f"   Column 2: iteration") 
        print(f"   Column 3: parameter")
        print(f"   Column 4: num_points")
        print(f"   Column 5: depth")
        print(f"   Column 6: memory_bytes")
        print(f"   Column 7: subdivisions")
        print(f"   Column 8: memory_per_point")


def main():
    """Run the Octree depth vs memory analysis"""
    print("🔬 Octree Depth vs Memory Usage Analysis")
    print("Generating comprehensive data for depth/memory relationship study")
    
    analyzer = OctreeDepthMemoryAnalyzer()
    analyzer.run_analysis()
    
    print(f"\n🎉 Analysis Complete!")
    print(f"📊 Results saved to CSV for further analysis and visualization")


if __name__ == "__main__":
    main()