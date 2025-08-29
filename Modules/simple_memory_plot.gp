#!/usr/bin/gnuplot
# Simple working plot for N-ary Tree Memory Analysis

set terminal png size 1200,800 enhanced font 'Arial,12'
set output 'narytree_memory_simple.png'

set title "N-ary Tree Memory Usage vs Tree Count" font 'Arial,16'
set xlabel "Number of Trees" font 'Arial,14'
set ylabel "Memory Usage (MB)" font 'Arial,14'
set grid
set key top left

# Plot memory usage vs tree count
plot 'narytree_memory_overtime_20250827_200205.csv' using 2:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2E8B57' title "Total Memory Usage"

print "Generated: narytree_memory_simple.png"

# Second plot: Memory over time
set output 'narytree_memory_timeline_simple.png'
set title "N-ary Tree Memory Usage Over Time" font 'Arial,16'
set xlabel "Time (seconds)" font 'Arial,14'
set ylabel "Memory Usage (MB)" font 'Arial,14'

plot 'narytree_memory_overtime_20250827_200205.csv' using 1:5 with lines lw 2 lc rgb '#DC143C' title "Memory Over Time"

print "Generated: narytree_memory_timeline_simple.png"

# Third plot: Tree growth
set output 'narytree_growth_simple.png'
set title "Tree Count Growth Over Time" font 'Arial,16'  
set xlabel "Time (seconds)" font 'Arial,14'
set ylabel "Number of Trees" font 'Arial,14'

plot 'narytree_memory_overtime_20250827_200205.csv' using 1:2 with linespoints lw 2 pt 5 ps 0.6 lc rgb '#4169E1' title "Tree Count"

print "Generated: narytree_growth_simple.png"