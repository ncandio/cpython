#!/usr/bin/gnuplot
# Simple test of progressive data

set terminal png size 1200,800
set output 'analysis_results/simple_progressive_test.png'
set title "Simple Progressive Test"
set xlabel "Total Words"
set ylabel "Memory (MB)"
set grid

# Test with specific file path
plot 'analysis_results/progressive_test_20250827_213928/progressive_memory_disk_20250827_213928.csv' every ::1 using 5:6 with linespoints title "Memory Usage"