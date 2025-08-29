#!/usr/bin/gnuplot
# Octree Depth vs Data Capacity Analysis
set terminal png size 1400,1000 font "Arial,12"
set output "octree_depth_capacity_20250824_015353.png"
set datafile separator ","

set multiplot layout 2,2 title "Octree Depth vs Data Capacity Analysis"

# Plot 1: Points vs Actual Depth Achieved
set xlabel "Number of Points"
set ylabel "Actual Tree Depth"
set title "Data Points vs Achieved Tree Depth"
set grid
set logscale x
plot "octree_depth_capacity_20250824_015353.csv" using 2:3 skip 1 with points pt 7 ps 1.5 lc rgb "blue" title "Actual Depth"

# Plot 2: Memory Usage vs Points
set xlabel "Number of Points" 
set ylabel "Memory Usage (MB)"
set title "Memory Usage vs Data Points"
set grid
set logscale x
set logscale y
plot "octree_depth_capacity_20250824_015353.csv" using 2:4 skip 1 with linespoints lw 2 pt 7 ps 1.2 lc rgb "red" title "Memory Usage"

# Plot 3: Memory Efficiency
set xlabel "Tree Depth"
set ylabel "Memory per Point (bytes)"
set title "Memory Efficiency by Tree Depth"
set grid
unset logscale x
unset logscale y
plot "octree_depth_capacity_20250824_015353.csv" using 3:5 skip 1 with points pt 9 ps 1.5 lc rgb "green" title "Memory per Point"

# Plot 4: Theoretical vs Practical Capacity
set xlabel "Tree Depth"
set ylabel "Data Points"
set title "Theoretical vs Practical Capacity"
set grid
set logscale y
plot "octree_depth_capacity_20250824_015353.csv" using 1:6 skip 1 with linespoints lw 3 pt 7 ps 1.2 lc rgb "orange" title "Theoretical Max", \
     "octree_depth_capacity_20250824_015353.csv" using 3:2 skip 1 with points pt 9 ps 1.5 lc rgb "blue" title "Practical Achieved"

unset multiplot
print "Depth vs capacity analysis saved to octree_depth_capacity_20250824_015353.png"
