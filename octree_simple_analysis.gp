#!/usr/bin/gnuplot
# Simple Octree Subdivision Analysis
set terminal png size 1400,800 font "Arial,12"
set output "octree_subdivision_analysis_final.png"

set multiplot layout 2,2 title "Octree Subdivision & Memory Analysis"

# Plot 1: Subdivision Trigger
set xlabel "Number of Points"
set ylabel "Memory Usage (bytes)"
set title "Memory Jump at Subdivision Trigger"
set grid
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:2 with linespoints lw 2 pt 7 title "Total Memory"

# Plot 2: Memory per Point
set xlabel "Number of Points" 
set ylabel "Bytes per Point"
set title "Memory Efficiency"
set grid
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:5 with linespoints lw 2 pt 5 title "Memory per Point"

# Plot 3: Tree Depth Growth
set xlabel "Number of Points"
set ylabel "Tree Depth"
set title "Tree Structure Growth"
set grid
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:3 with linespoints lw 2 pt 9 title "Depth"

# Plot 4: Memory vs Depth from depth analysis
set xlabel "Tree Depth"
set ylabel "Memory Usage (bytes)"
set title "Memory Growth by Depth"
set grid
plot "octree_depth_memory_20250824_012228.csv" using 2:4 with linespoints lw 3 pt 7 title "Memory vs Depth"

unset multiplot
print "Analysis complete - saved to octree_subdivision_analysis_final.png"