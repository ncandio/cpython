# Simple Octree Depth vs Memory Plot
set terminal png size 800,600 font 'Arial,12'
set output 'octree_depth_memory_plot.png'

set title "Octree: Tree Depth vs Memory Usage" font 'Arial,14'
set xlabel "Tree Depth"
set ylabel "Memory Usage (bytes)"
set grid

# Use column 5 (depth) and column 6 (memory_bytes), skip header
plot 'octree_depth_memory_analysis_20250824_005644.csv' using 5:6 skip 1 with points pt 7 ps 1.5 lc rgb 'red' title 'Depth vs Memory'