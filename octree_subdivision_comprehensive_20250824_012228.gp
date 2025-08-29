#!/usr/bin/gnuplot
# Comprehensive Octree Subdivision Analysis
# Generated on 2025-08-24 01:22:28

set terminal png size 1600,1200 font "Arial,14"
set output "octree_subdivision_comprehensive_20250824_012228.png"

set multiplot layout 3,2 title "Comprehensive Octree Subdivision & Memory Analysis" font "Arial,16"

# Plot 1: Subdivision Trigger (from trigger analysis)
set xlabel "Number of Points"
set ylabel "Memory Usage (bytes)"
set title "Subdivision Trigger Point"
set grid
set key right bottom
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:2 with linespoints lw 3 pt 7 ps 1.2 title "Memory Usage", \
     "octree_subdivision_trigger_20250824_012228.csv" using 1:($1<=8?$2:1/0) with linespoints lw 2 pt 5 ps 1.0 lc rgb "green" title "Pre-subdivision", \
     "octree_subdivision_trigger_20250824_012228.csv" using 1:($1>8?$2:1/0) with linespoints lw 2 pt 9 ps 1.0 lc rgb "red" title "Post-subdivision"

# Plot 2: Memory Efficiency by Pattern
set xlabel "Number of Points"
set ylabel "Memory per Point (bytes)"
set title "Memory Efficiency by Distribution Pattern"
set grid
set key right top
plot "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Random_Uniform" ? $2 : 1/0):4 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Clustered_Points" ? $2 : 1/0):4 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):4 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Grid_Distribution" ? $2 : 1/0):4 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 3: Tree Depth by Pattern
set xlabel "Number of Points"
set ylabel "Tree Depth"
set title "Tree Depth by Distribution Pattern"
set grid
set key right bottom
plot "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Random_Uniform" ? $2 : 1/0):5 with linespoints lw 2 pt 7 ps 1.2 lc rgb "blue" title "Random Uniform", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Clustered_Points" ? $2 : 1/0):5 with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Clustered", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Linear_Arrangement" ? $2 : 1/0):5 with linespoints lw 2 pt 9 ps 1.2 lc rgb "green" title "Linear", \
     "octree_memory_scaling_20250824_012228.csv" using ($1 eq "Grid_Distribution" ? $2 : 1/0):5 with linespoints lw 2 pt 11 ps 1.2 lc rgb "orange" title "Grid"

# Plot 4: Depth vs Memory Relationship
set xlabel "Tree Depth"
set ylabel "Memory Usage (bytes)"
set title "Memory Growth with Tree Depth"
set grid
set key right bottom
plot "octree_depth_memory_20250824_012228.csv" using 2:4 with linespoints lw 3 pt 7 ps 1.5 lc rgb "blue" title "Total Memory", \
     "octree_depth_memory_20250824_012228.csv" using 2:($5*$3) with linespoints lw 2 pt 5 ps 1.2 lc rgb "red" title "Memory per Point × Points"

# Plot 5: Memory Scaling Factor Analysis
set xlabel "Tree Depth"
set ylabel "Memory Scaling Factor"
set title "Memory Growth Rate by Depth"
set grid
set key right bottom
base_memory = 432  # Empty octree memory
plot "octree_depth_memory_20250824_012228.csv" using 2:($4/base_memory) with linespoints lw 3 pt 9 ps 1.5 lc rgb "purple" title "Memory Scale Factor"

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

print "Comprehensive analysis saved to octree_subdivision_comprehensive_20250824_012228.png"
print "Data files: octree_subdivision_trigger_20250824_012228.csv, octree_memory_scaling_20250824_012228.csv, octree_depth_memory_20250824_012228.csv"
print "Individual plots: octree_subdivision_trigger_20250824_012228.gp, octree_memory_scaling_20250824_012228.gp, octree_depth_memory_20250824_012228.gp"
