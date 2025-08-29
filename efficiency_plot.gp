# Octree Memory Efficiency Plot
set terminal png size 1000,700 font 'Arial,12'
set output 'octree_memory_efficiency.png'

set title "Octree: Memory Efficiency vs Tree Depth" font 'Arial,16'
set xlabel "Tree Depth" font 'Arial,14'
set ylabel "Memory per Point (bytes/point)" font 'Arial,14'
set grid
set key outside right

# Plot efficiency data
plot 'depth_efficiency_data.txt' using 1:2 with points pt 5 ps 1.5 lc rgb 'green' title 'Memory Efficiency',\
     'depth_efficiency_data.txt' using 1:2 smooth bezier with lines lw 2 lc rgb 'orange' title 'Efficiency Trend'

print "Successfully created octree_memory_efficiency.png"