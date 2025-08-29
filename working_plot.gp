# Working Octree Analysis Plot
set terminal png size 1000,700
set output 'octree_analysis_working.png'

# Configure the plot
set title "Octree Depth vs Memory Usage Analysis"
set xlabel "Tree Depth"
set ylabel "Memory Usage (bytes)"
set grid
set key outside right

# Set appropriate ranges based on our data
set xrange [0:15]
set yrange [1000:2000000]
set logscale y

# Plot with different colors for each strategy
plot 'octree_depth_memory_analysis_20250824_005644.csv' using 5:6 skip 1 with points pt 7 ps 1.0 lc rgb 'blue' title 'All Points'

# Save the plot
print "Plot saved as octree_analysis_working.png"