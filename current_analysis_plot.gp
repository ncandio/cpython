# Current Octree Analysis Plot
set terminal png size 1200,800 font 'Arial,14'
set output 'octree_depth_memory_current.png'

set multiplot layout 2,2 title "Octree Depth vs Memory Analysis - Complete Results" font 'Arial,18'

# Plot 1: Main Depth vs Memory scatter plot
set title "Tree Depth vs Memory Usage"
set xlabel "Tree Depth"
set ylabel "Memory Usage (bytes)"
set grid
set logscale y
plot 'depth_memory_current.txt' using 1:2 with points pt 7 ps 1.5 lc rgb 'red' title 'Data Points',\
     'depth_memory_current.txt' using 1:2 smooth csplines with lines lw 2 lc rgb 'blue' title 'Trend'

# Plot 2: Memory efficiency
unset logscale y
set title "Memory Efficiency vs Depth"
set xlabel "Tree Depth"
set ylabel "Memory per Point (bytes/point)"
plot 'depth_efficiency_current.txt' using 1:2 with points pt 5 ps 1.5 lc rgb 'green' title 'Efficiency',\
     'depth_efficiency_current.txt' using 1:2 smooth bezier with lines lw 2 lc rgb 'orange' title 'Efficiency Trend'

# Plot 3: Memory distribution histogram
set title "Memory Usage Distribution"
set xlabel "Memory Usage (KB)"
set ylabel "Frequency"
set style data histograms
set style histogram cluster gap 1
set style fill solid 0.7
# Convert bytes to KB and create histogram
plot '< awk "{print $2/1024}" depth_memory_current.txt | sort -n | uniq -c' using 2:1 with boxes lc rgb 'purple' title 'Memory Distribution'

# Plot 4: Depth distribution
set title "Tree Depth Distribution"
set xlabel "Tree Depth"
set ylabel "Frequency"
plot '< awk "{print $1}" depth_memory_current.txt | sort -n | uniq -c' using 2:1 with boxes lc rgb 'navy' title 'Depth Distribution'

unset multiplot
print "Generated comprehensive analysis plot: octree_depth_memory_current.png"