#!/usr/bin/gnuplot
# Octree Depth vs Memory Analysis
# Generated on 2025-08-24 01:22:28

set terminal png size 1200,800 font "Arial,12"
set output "octree_depth_memory_20250824_012228.png"

set multiplot layout 2,2 title "Octree Depth vs Memory Usage Analysis"

# Plot 1: Memory vs Depth
set xlabel "Tree Depth"
set ylabel "Memory Usage (bytes)"
set title "Memory Growth with Depth"
set grid
set key right bottom
plot "octree_depth_memory_20250824_012228.csv" using 2:4 with linespoints lw 3 pt 7 ps 1.5 lc rgb "blue" title "Total Memory"

# Plot 2: Memory per point vs Depth
set xlabel "Tree Depth"
set ylabel "Memory per Point (bytes)"
set title "Memory Efficiency vs Depth"
set grid
plot "octree_depth_memory_20250824_012228.csv" using 2:5 with linespoints lw 3 pt 9 ps 1.5 lc rgb "red" title "Bytes per Point"

# Plot 3: Points vs Depth (showing data density)
set xlabel "Tree Depth"
set ylabel "Number of Points"
set title "Point Count vs Depth"
set grid
plot "octree_depth_memory_20250824_012228.csv" using 2:3 with linespoints lw 3 pt 11 ps 1.5 lc rgb "green" title "Points"

# Plot 4: Memory scaling factor
set xlabel "Tree Depth"
set ylabel "Memory Scaling Factor"
set title "Memory Growth Rate"
set grid
# Calculate scaling relative to depth 1
depth_1_memory = 7344  # From first data point
plot "octree_depth_memory_20250824_012228.csv" using 2:($4/depth_1_memory) with linespoints lw 3 pt 13 ps 1.5 lc rgb "purple" title "Memory Scale Factor"

unset multiplot
print "Depth vs memory analysis saved to octree_depth_memory_20250824_012228.png"
