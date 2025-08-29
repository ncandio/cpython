#!/usr/bin/gnuplot

# Simple Filesystem Comparison Visualization
set terminal png size 1400,1000 font "Arial,12"
set output 'comprehensive_filesystem_comparison_i7_16gb.png'

set multiplot layout 2,2 title "Filesystem Comparison: Intel i7 16GB System\nMemory & Disk Usage Analysis" font "Arial,16"

# Data file
datafile = 'filesystem_comparison_i7_16gb_20250829_123852.csv'

# Plot 1: Memory Usage
set title "Memory Usage Comparison" font "Arial,14"
set xlabel "Number of Files"
set ylabel "Memory Usage (MB)"
set logscale x
set logscale y
set grid
set key top left

plot datafile using 1:3 with linespoints lw 2 pt 7 title 'ext4' lc rgb '#2E8B57', \
     datafile using 1:5 with linespoints lw 2 pt 5 title 'ZFS' lc rgb '#FF4500', \
     datafile using 1:7 with linespoints lw 2 pt 9 title 'Btrfs' lc rgb '#4169E1', \
     datafile using 1:9 with linespoints lw 2 pt 11 title 'N-ary Tree FS' lc rgb '#8A2BE2'

# Plot 2: Disk Usage  
unset logscale y
set title "Disk Usage Comparison" font "Arial,14"
set xlabel "Number of Files"
set ylabel "Disk Usage (MB)"
set logscale x
set grid
set key top left

plot datafile using 1:4 with linespoints lw 2 pt 7 title 'ext4' lc rgb '#2E8B57', \
     datafile using 1:6 with linespoints lw 2 pt 5 title 'ZFS' lc rgb '#FF4500', \
     datafile using 1:8 with linespoints lw 2 pt 9 title 'Btrfs' lc rgb '#4169E1', \
     datafile using 1:10 with linespoints lw 2 pt 11 title 'N-ary Tree FS' lc rgb '#8A2BE2'

# Plot 3: RAM Percentage
set title "RAM Usage % (16GB System)" font "Arial,14"
set xlabel "Number of Files"
set ylabel "RAM Usage (%)"
set logscale x
unset logscale y
set grid
set key top left

plot datafile using 1:11 with linespoints lw 2 pt 7 title 'ext4' lc rgb '#2E8B57', \
     datafile using 1:13 with linespoints lw 2 pt 5 title 'ZFS' lc rgb '#FF4500', \
     datafile using 1:15 with linespoints lw 2 pt 9 title 'Btrfs' lc rgb '#4169E1', \
     datafile using 1:17 with linespoints lw 2 pt 11 title 'N-ary Tree FS' lc rgb '#8A2BE2'

# Plot 4: Efficiency Summary (Bar Chart)
unset logscale x
set title "Storage Efficiency (1M Files)" font "Arial,14"
set ylabel "Storage Usage (GB)"
set xlabel "Filesystem"
set style data histogram
set style histogram cluster gap 1
set style fill solid 0.8
set boxwidth 0.8
set grid y
unset key

# Manual bar chart using boxes
set xrange [-0.5:3.5]
set xtics ("ext4" 0, "ZFS" 1, "Btrfs" 2, "N-ary FS" 3)

# Memory values (convert MB to GB): ext4=0.067, ZFS=7.23, Btrfs=0.046, N-ary=0.060  
# Disk values (convert MB to GB): ext4=109.8, ZFS=141.3, Btrfs=152.4, N-ary=134.5

plot '-' using 1:2 with boxes lc rgb '#2E8B57' title 'Memory', \
     '-' using 1:2 with boxes lc rgb '#FF6B6B' title 'Disk'
0 0.067
1 7.23
2 0.046
3 0.060
e
0 109.8
1 141.3  
2 152.4
3 134.5
e

unset multiplot