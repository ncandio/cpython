#!/usr/bin/env python3
"""
Octree Depth vs Data Capacity Analysis
Comprehensive study of how many points can be stored at different tree depths
"""

import sys
import octree
import random
import csv
from datetime import datetime

def analyze_depth_capacity():
    """Analyze data capacity at different octree depths."""
    
    print("🎯 OCTREE DEPTH vs DATA CAPACITY ANALYSIS")
    print("="*60)
    
    # Define point ranges to test for each depth target
    depth_targets = {
        1: [10, 20, 50, 64],           # Up to theoretical max
        2: [50, 100, 200, 500, 512],   # Up to theoretical max  
        3: [500, 1000, 2000, 4096],    # Up to theoretical max
        4: [1000, 5000, 10000, 32768], # Up to theoretical max
        5: [5000, 20000, 50000],       # Practical limits
        6: [10000, 50000, 100000],     # Practical limits
    }
    
    results = []
    
    print("Target | Points  | Actual | Memory (MB) | Mem/Point | Theoretical Max")
    print("Depth  | Tested  | Depth  |             | (bytes)   | Capacity")
    print("-------|---------|--------|-------------|-----------|----------------")
    
    for target_depth in sorted(depth_targets.keys()):
        point_counts = depth_targets[target_depth]
        theoretical_max = (8 ** target_depth) * 8
        
        for point_count in point_counts:
            # Test with random uniform distribution
            tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
            random.seed(42)  # Reproducible results
            
            # Add points
            for i in range(point_count):
                x = random.uniform(-900, 900)
                y = random.uniform(-900, 900)
                z = random.uniform(-900, 900)
                tree.insert(x, y, z, f"point_{i}")
            
            actual_depth = tree.depth()
            memory_mb = tree.memory_usage() / (1024 * 1024)
            memory_per_point = tree.memory_usage() / point_count
            
            # Determine if we reached target depth
            status = "✓" if actual_depth == target_depth else f"→{actual_depth}"
            
            results.append({
                'target_depth': target_depth,
                'points': point_count,
                'actual_depth': actual_depth,
                'memory_mb': memory_mb,
                'memory_per_point': memory_per_point,
                'theoretical_max': theoretical_max
            })
            
            print(f"{target_depth:6} | {point_count:7,} | {actual_depth:6} | {memory_mb:10.2f} | {memory_per_point:8.1f} | {theoretical_max:14,} {status}")
    
    # Generate summary table
    print("\n" + "="*60)
    print("📊 PRACTICAL CAPACITY BY DEPTH SUMMARY")
    print("="*60)
    
    # Group results by actual depth achieved
    depth_groups = {}
    for result in results:
        depth = result['actual_depth']
        if depth not in depth_groups:
            depth_groups[depth] = []
        depth_groups[depth].append(result)
    
    print("Depth | Points Range    | Memory Range     | Efficiency")
    print("------|-----------------|------------------|----------------")
    
    for depth in sorted(depth_groups.keys()):
        group = depth_groups[depth]
        min_points = min(r['points'] for r in group)
        max_points = max(r['points'] for r in group)
        min_memory = min(r['memory_mb'] for r in group) 
        max_memory = max(r['memory_mb'] for r in group)
        
        # Calculate average memory per point for this depth
        avg_mem_per_point = sum(r['memory_per_point'] for r in group) / len(group)
        efficiency = "GOOD" if avg_mem_per_point < 300 else "FAIR" if avg_mem_per_point < 500 else "POOR"
        
        print(f"{depth:5} | {min_points:7,}-{max_points:7,} | {min_memory:6.2f}-{max_memory:6.2f} MB | {efficiency:8} ({avg_mem_per_point:.0f} b/pt)")
    
    # Generate CSV for plotting
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"octree_depth_capacity_{timestamp}.csv"
    
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['target_depth', 'points', 'actual_depth', 'memory_mb', 'memory_per_point', 'theoretical_max']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    print(f"\n📄 Data saved to: {csv_filename}")
    
    # Generate gnuplot script
    generate_gnuplot_script(csv_filename, timestamp)
    
    return results

def generate_gnuplot_script(csv_filename, timestamp):
    """Generate gnuplot script for visualization."""
    
    gp_filename = f"octree_depth_capacity_{timestamp}.gp"
    
    with open(gp_filename, 'w') as gpfile:
        gpfile.write(f"""#!/usr/bin/gnuplot
# Octree Depth vs Data Capacity Analysis
set terminal png size 1400,1000 font "Arial,12"
set output "octree_depth_capacity_{timestamp}.png"
set datafile separator ","

set multiplot layout 2,2 title "Octree Depth vs Data Capacity Analysis"

# Plot 1: Points vs Actual Depth Achieved
set xlabel "Number of Points"
set ylabel "Actual Tree Depth"
set title "Data Points vs Achieved Tree Depth"
set grid
set logscale x
plot "{csv_filename}" using 2:3 skip 1 with points pt 7 ps 1.5 lc rgb "blue" title "Actual Depth"

# Plot 2: Memory Usage vs Points
set xlabel "Number of Points" 
set ylabel "Memory Usage (MB)"
set title "Memory Usage vs Data Points"
set grid
set logscale x
set logscale y
plot "{csv_filename}" using 2:4 skip 1 with linespoints lw 2 pt 7 ps 1.2 lc rgb "red" title "Memory Usage"

# Plot 3: Memory Efficiency
set xlabel "Tree Depth"
set ylabel "Memory per Point (bytes)"
set title "Memory Efficiency by Tree Depth"
set grid
unset logscale x
unset logscale y
plot "{csv_filename}" using 3:5 skip 1 with points pt 9 ps 1.5 lc rgb "green" title "Memory per Point"

# Plot 4: Theoretical vs Practical Capacity
set xlabel "Tree Depth"
set ylabel "Data Points"
set title "Theoretical vs Practical Capacity"
set grid
set logscale y
plot "{csv_filename}" using 1:6 skip 1 with linespoints lw 3 pt 7 ps 1.2 lc rgb "orange" title "Theoretical Max", \\
     "{csv_filename}" using 3:2 skip 1 with points pt 9 ps 1.5 lc rgb "blue" title "Practical Achieved"

unset multiplot
print "Depth vs capacity analysis saved to octree_depth_capacity_{timestamp}.png"
""")
    
    print(f"📊 Gnuplot script: {gp_filename}")
    print(f"🖼️  Run: gnuplot {gp_filename}")

if __name__ == "__main__":
    analyze_depth_capacity()