#!/usr/bin/gnuplot
# Octree Memory Scaling Analysis
# Generated on 2025-08-24 01:22:28

set terminal png size 1400,1000 font "Arial,12"
set output "octree_memory_scaling_20250824_012228.png"

set multiplot layout 2,2 title "Octree Memory Scaling by Distribution Pattern"

# Plot 1: Total Memory Usage
set xlabel "Number of Points"
set ylabel "Total Memory (bytes)"
set title "Total Memory Usage by Pattern"
set grid
set key right bottom
set logscale y
plot "octree_memory_scaling_20250824_012228.csv" using 2:3 smooth unique title "All Patterns" lw 1 lc rgb "gray", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Random_Uniform" ? $2 : 1/0):3 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Clustered_Points" ? $2 : 1/0):3 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):3 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Grid_Distribution" ? $2 : 1/0):3 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 2: Memory Efficiency (bytes per point)
set xlabel "Number of Points"
set ylabel "Memory per Point (bytes)"
set title "Memory Efficiency by Pattern"
set grid
set key right top
unset logscale y
plot "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Random_Uniform" ? $2 : 1/0):4 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Clustered_Points" ? $2 : 1/0):4 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):4 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Grid_Distribution" ? $2 : 1/0):4 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 3: Tree Depth by Pattern
set xlabel "Number of Points"
set ylabel "Tree Depth"
set title "Tree Depth by Pattern"
set grid
set key right bottom
plot "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Random_Uniform" ? $2 : 1/0):5 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Clustered_Points" ? $2 : 1/0):5 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):5 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Grid_Distribution" ? $2 : 1/0):5 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 4: Insert Performance
set xlabel "Number of Points"
set ylabel "Insert Time (seconds)"
set title "Insert Performance by Pattern"
set grid
set key right top
set logscale y
plot "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Random_Uniform" ? $2 : 1/0):6 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Clustered_Points" ? $2 : 1/0):6 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):6 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Grid_Distribution" ? $2 : 1/0):6 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

unset multiplot
print "Memory scaling analysis saved to octree_memory_scaling_20250824_012228.png"
