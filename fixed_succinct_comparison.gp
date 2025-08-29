#!/usr/bin/env gnuplot
set terminal pngcairo enhanced font 'Arial,14' size 1400,1000
set output 'succinct_memory_comparison_fixed.png'

set datafile separator ","
set key outside right

set multiplot layout 2,2 title "Standard vs Succinct N-ary Tree Comparison" font 'Arial,16'

# Memory usage comparison
set title "Memory Usage: Standard vs Succinct"
set xlabel "Number of Nodes"
set ylabel "Memory Usage (MB)"
set logscale xy
set grid
plot 'succinct_vs_standard_20250829_86344.csv' using 1:2 with linespoints title 'Standard' lw 3 pt 7 ps 1.5, \
     'succinct_vs_standard_20250829_86344.csv' using 1:3 with linespoints title 'Succinct' lw 3 pt 9 ps 1.5

# Memory reduction percentage
set title "Memory Reduction Percentage"
set xlabel "Number of Nodes"
set ylabel "Memory Reduction (%)"
unset logscale y
set logscale x
set yrange [50:60]
plot 'succinct_vs_standard_20250829_86344.csv' using 1:4 with linespoints title 'Memory Savings' lw 3 pt 7 ps 1.5

# Encode/Decode time
set title "Encode/Decode Performance"
set xlabel "Number of Nodes"
set ylabel "Time (ms)"
set logscale xy
unset yrange
plot 'succinct_vs_standard_20250829_86344.csv' using 1:5 with linespoints title 'Encode Time' lw 3 pt 7 ps 1.5, \
     'succinct_vs_standard_20250829_86344.csv' using 1:6 with linespoints title 'Decode Time' lw 3 pt 9 ps 1.5

# Structure bits efficiency
set title "Structure Bits vs Theoretical (2n)"
set xlabel "Number of Nodes"
set ylabel "Structure Bits"
set logscale xy
plot 'succinct_vs_standard_20250829_86344.csv' using 1:7 with linespoints title 'Actual Bits' lw 3 pt 7 ps 1.5, \
     'succinct_vs_standard_20250829_86344.csv' using 1:($1*2) with lines title 'Theoretical (2n)' lw 3

unset multiplot