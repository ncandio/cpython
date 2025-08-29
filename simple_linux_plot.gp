set terminal png size 1000,600
set output 'linux_filesystem_performance_final.png'

set grid
set xlabel 'Number of Filesystem Entries'
set ylabel 'Memory per Entry (bytes)'
set title 'Linux Filesystem N-ary Tree: Memory Efficiency Analysis'
set logscale x
set yrange [25:65]

plot 'linux_filesystem_scalability_20250828.csv' skip 1 using 1:3 with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree (57 bytes)', \
     30 with lines linewidth 2 title 'Linux B-tree (avg)', \
     40 with lines linewidth 2 title 'Linux B-tree (max)'