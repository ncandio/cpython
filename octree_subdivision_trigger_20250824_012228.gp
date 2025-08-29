#!/usr/bin/gnuplot
# Octree Subdivision Trigger Analysis
# Generated on 2025-08-24 01:22:28

set terminal png size 1200,800 font "Arial,12"
set output "octree_subdivision_trigger_20250824_012228.png"

set multiplot layout 2,2 title "Octree Subdivision Trigger Analysis"

# Plot 1: Memory vs Points (showing subdivision jump)
set xlabel "Number of Points"
set ylabel "Memory Usage (bytes)"
set title "Memory Jump at Subdivision Trigger"
set grid
set key right bottom
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:2 with linespoints lw 2 pt 7 ps 1.2 title "Total Memory", \
     "octree_subdivision_trigger_20250824_012228.csv" using 1:5 with linespoints lw 2 pt 5 ps 1.2 title "Memory per Point"

# Plot 2: Depth progression
set xlabel "Number of Points"
set ylabel "Tree Depth"
set title "Tree Depth Growth"
set grid
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:3 with linespoints lw 3 pt 9 ps 1.5 lc rgb "red" title "Depth"

# Plot 3: Subdivisions count
set xlabel "Number of Points"
set ylabel "Subdivision Count"
set title "Subdivision Events"
set grid
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:4 with linespoints lw 3 pt 11 ps 1.5 lc rgb "blue" title "Subdivisions"

# Plot 4: Memory efficiency
set xlabel "Number of Points"
set ylabel "Bytes per Point"
set title "Memory Efficiency"
set grid
set logscale y
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:5 with linespoints lw 2 pt 13 ps 1.2 lc rgb "green" title "Bytes/Point"

unset multiplot
print "Subdivision trigger analysis saved to octree_subdivision_trigger_20250824_012228.png"
