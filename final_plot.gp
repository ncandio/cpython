# Final Working Octree Plot
set terminal png size 1000,700 font 'Arial,12'
set output 'octree_depth_memory_final.png'

set title "Octree: Tree Depth vs Memory Usage" font 'Arial,16'
set xlabel "Tree Depth" font 'Arial,14'
set ylabel "Memory Usage (bytes)" font 'Arial,14'
set grid
set key outside right

# Use the simple data file
plot 'depth_memory_data.txt' using 1:2 with points pt 7 ps 1.5 lc rgb 'red' title 'Depth vs Memory',\
     'depth_memory_data.txt' using 1:2 smooth csplines with lines lw 2 lc rgb 'blue' title 'Trend Line'

print "Successfully created octree_depth_memory_final.png"