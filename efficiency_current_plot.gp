# Current Memory Efficiency Analysis
set terminal png size 1000,700 font 'Arial,12'
set output 'octree_efficiency_current.png'

set title "Octree: Memory Efficiency vs Tree Depth (Latest Results)" font 'Arial,16'
set xlabel "Tree Depth" font 'Arial,14'
set ylabel "Memory per Point (bytes/point)" font 'Arial,14'
set grid
set key outside right

# Efficiency plot
plot 'depth_efficiency_current.txt' using 1:2 with points pt 5 ps 1.5 lc rgb 'green' title 'Memory Efficiency',\
     'depth_efficiency_current.txt' using 1:2 smooth bezier with lines lw 2 lc rgb 'orange' title 'Efficiency Trend'

print "Successfully created octree_efficiency_current.png"