#!/usr/bin/env gnuplot
set terminal pngcairo enhanced font 'Arial,12' size 1400,1000
set output 'succinct_vs_standard_20250829_86344_memory_comparison.png'

set multiplot layout 2,2 title "Standard vs Succinct N-ary Tree Comparison" font 'Arial,16'

# Memory usage comparison
set title "Memory Usage: Standard vs Succinct"
set xlabel "Number of Nodes"
set ylabel "Memory Usage (MB)"
set logscale xy
set grid
plot 'succinct_vs_standard_20250829_86344.csv' using 1:2 with linespoints title 'Standard Implementation' lw 2 pt 7, \
     'succinct_vs_standard_20250829_86344.csv' using 1:3 with linespoints title 'Succinct Encoding' lw 2 pt 9

# Memory reduction percentage
set title "Memory Reduction Percentage"
set xlabel "Number of Nodes"
set ylabel "Memory Reduction (%)"
unset logscale y
set logscale x
plot 'succinct_vs_standard_20250829_86344.csv' using 1:4 with linespoints title 'Memory Savings' lw 2 pt 7

# Encode/Decode time
set title "Encode/Decode Performance"
set xlabel "Number of Nodes"
set ylabel "Time (ms)"
set logscale xy
plot 'succinct_vs_standard_20250829_86344.csv' using 1:5 with linespoints title 'Encode Time' lw 2 pt 7, \
     'succinct_vs_standard_20250829_86344.csv' using 1:6 with linespoints title 'Decode Time' lw 2 pt 9

# Structure bits vs theoretical
set title "Structure Bits vs Theoretical Minimum"
set xlabel "Number of Nodes"
set ylabel "Structure Bits"
set logscale xy
plot 'succinct_vs_standard_20250829_86344.csv' using 1:7 with linespoints title 'Actual Structure Bits' lw 2 pt 7, \
     'succinct_vs_standard_20250829_86344.csv' using 1:($1*2) with lines title 'Theoretical Minimum (2n)' lw 2

unset multiplot
