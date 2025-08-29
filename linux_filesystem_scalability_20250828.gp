set terminal png size 1200,800
set output 'linux_filesystem_scalability_20250828.png'

set multiplot layout 2,1 title 'Linux Filesystem N-ary Tree Performance Analysis'

set logscale x
set grid
set xlabel 'Number of Filesystem Entries'
set ylabel 'Memory per Entry (bytes)'
set title 'Memory Efficiency: Our Implementation vs Linux B-trees'
set yrange [20:80]

plot 'linux_filesystem_scalability_20250828.csv' using 1:3 with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree (57 bytes/entry)', \
     30 with lines linestyle 2 linewidth 2 title 'Linux B-tree (avg 30 bytes/entry)', \
     40 with lines linestyle 3 linewidth 2 title 'Linux B-tree (max 40 bytes/entry)'

set ylabel 'Page Utilization (%)'
set title '4KB Page Utilization Efficiency'  
unset logscale y
set yrange [99:100]

plot 'linux_filesystem_scalability_20250828.csv' using 1:($4*100) with linespoints linewidth 3 pointsize 2 title 'Page Utilization (99.9%+)'

unset multiplot