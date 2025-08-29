#!/usr/bin/env gnuplot
set terminal pngcairo enhanced font 'Arial,14' size 1400,1000
set output 'disk_progressive_20250829_87740_disk_analysis.png'

set datafile separator ","
set key outside right

set multiplot layout 2,2 title "Disk Storage: Standard vs Succinct N-ary Tree" font 'Arial,16'

# Disk usage comparison
set title "Disk Usage: Standard vs Succinct"
set xlabel "Number of Nodes"
set ylabel "Disk Usage (MB)"
set logscale xy
set grid
plot 'disk_progressive_20250829_87740.csv' using 1:2 with linespoints title 'Standard Format' lw 3 pt 7 ps 1.5, \
     'disk_progressive_20250829_87740.csv' using 1:3 with linespoints title 'Succinct Format' lw 3 pt 9 ps 1.5

# Disk reduction percentage
set title "Disk Space Reduction"
set xlabel "Number of Nodes"
set ylabel "Disk Reduction (%)"
unset logscale y
set logscale x
plot 'disk_progressive_20250829_87740.csv' using 1:4 with linespoints title 'Disk Savings' lw 3 pt 7 ps 1.5

# Save/Load performance
set title "Save/Load Performance"
set xlabel "Number of Nodes"
set ylabel "Time (ms)"
set logscale xy
plot 'disk_progressive_20250829_87740.csv' using 1:5 with linespoints title 'Save Time' lw 3 pt 7 ps 1.5, \
     'disk_progressive_20250829_87740.csv' using 1:6 with linespoints title 'Load Time' lw 3 pt 9 ps 1.5

# Progressive data growth
set title "Progressive Disk Space Growth"
set xlabel "Number of Nodes"
set ylabel "Cumulative Disk Space (MB)"
set logscale xy
plot 'disk_progressive_20250829_87740.csv' using 1:($2) with linespoints title 'Standard Cumulative' lw 3 pt 7 ps 1.5, \
     'disk_progressive_20250829_87740.csv' using 1:($3) with linespoints title 'Succinct Cumulative' lw 3 pt 9 ps 1.5

unset multiplot
