#!/usr/bin/gnuplot
# Complete Octree Subdivision & Memory Analysis
set terminal png size 1600,1200 font "Arial,12"
set output "octree_subdivision_complete_analysis.png"
set datafile separator ","

set multiplot layout 3,2 title "Octree Subdivision & Memory Analysis" font "Arial,16"

# Plot 1: Memory Jump at Subdivision Trigger
set xlabel "Number of Points"
set ylabel "Memory Usage (bytes)"
set title "Memory Jump at Subdivision Trigger (9 points)"
set grid
set key right top
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:2 skip 1 with linespoints lw 3 pt 7 ps 1.2 lc rgb "blue" title "Total Memory", \
     "octree_subdivision_trigger_20250824_012228.csv" using 1:($1<=8?$2:1/0) skip 1 with linespoints lw 2 pt 5 ps 1.0 lc rgb "green" title "Pre-subdivision", \
     "octree_subdivision_trigger_20250824_012228.csv" using 1:($1>8?$2:1/0) skip 1 with linespoints lw 2 pt 9 ps 1.0 lc rgb "red" title "Post-subdivision"

# Plot 2: Memory Efficiency
set xlabel "Number of Points"
set ylabel "Bytes per Point"
set title "Memory Efficiency (Bytes per Point)"
set grid
set key right top
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:5 skip 1 with linespoints lw 2 pt 7 ps 1.2 lc rgb "purple" title "Memory per Point"

# Plot 3: Tree Depth Growth
set xlabel "Number of Points"
set ylabel "Tree Depth"
set title "Tree Depth Growth"
set grid
set key right bottom
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:3 skip 1 with linespoints lw 3 pt 9 ps 1.5 lc rgb "red" title "Tree Depth"

# Plot 4: Memory Scaling by Pattern  
set xlabel "Number of Points"
set ylabel "Memory per Point (bytes)"
set title "Memory Efficiency by Distribution Pattern"
set grid
set key right top
plot "octree_memory_scaling_20250824_012228.csv" using 2:4 skip 1 with lines lw 2 lc rgb "gray" title "All Patterns"

# Plot 5: Memory vs Depth
set xlabel "Tree Depth"
set ylabel "Memory Usage (bytes)"
set title "Memory Growth with Tree Depth"
set grid
set key right bottom
plot "octree_depth_memory_20250824_012228.csv" using 2:4 skip 1 with linespoints lw 3 pt 7 ps 1.5 lc rgb "blue" title "Total Memory"

# Plot 6: Summary Text
set title "Key Findings"
unset xlabel
unset ylabel
unset grid
unset key
set border 0
unset tics
set label 1 "OCTREE SUBDIVISION ANALYSIS SUMMARY" at screen 0.52, screen 0.35 center font "Arial,14,bold"
set label 2 "• Subdivision triggers at 9 points (MaxPointsPerNode = 8)" at screen 0.52, screen 0.30 center
set label 3 "• Memory jumps 41x after subdivision (432 → 17,712 bytes)" at screen 0.52, screen 0.27 center
set label 4 "• Best pattern: Grid Distribution (208 bytes/point)" at screen 0.52, screen 0.24 center
set label 5 "• Worst pattern: Linear Arrangement (450 bytes/point)" at screen 0.52, screen 0.21 center  
set label 6 "• Each subdivision creates 8 child octants" at screen 0.52, screen 0.18 center
set label 7 "• Memory grows exponentially with tree depth" at screen 0.52, screen 0.15 center
set label 8 "• Trade-off: Memory cost vs O(log n) query performance" at screen 0.52, screen 0.12 center
plot [0:1] [0:1] 1/0 notitle

unset multiplot
print "Complete octree analysis saved to octree_subdivision_complete_analysis.png"