set terminal png size 1000,700 font "Arial,12"
set output 'intel_i5_final_performance_comparison.png'

set grid
set xlabel 'Number of Entries'
set ylabel 'Memory per Entry (bytes)'
set title 'Linux B-tree vs N-ary Tree: Intel i5-8350U Performance Analysis'
set logscale x
set key top right
set xrange [800:1200000]
set yrange [15:65]

# Define data points directly
plot '-' using 1:2 with linespoints linewidth 3 pointsize 2 title 'Linux B-tree (19-35 bytes)', \
     '-' using 1:2 with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree (57 bytes)'
1000 35.0
10000 28.0
50000 24.0
100000 22.0
500000 20.0
1000000 19.0
e
1000 57.3
10000 56.9
50000 56.9
100000 56.9
500000 56.9
1000000 56.9
e