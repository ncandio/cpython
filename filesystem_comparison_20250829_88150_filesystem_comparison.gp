#!/usr/bin/env gnuplot
set terminal pngcairo enhanced font 'Arial,14' size 1600,1200
set output 'filesystem_comparison_20250829_88150_filesystem_analysis.png'

set datafile separator ","
set key outside right

set multiplot layout 2,2 title "Filesystem vs Succinct N-ary Tree Comparison" font 'Arial,18'

# Memory usage comparison
set title "Memory Usage: Filesystems vs Succinct"
set xlabel "Number of Nodes"
set ylabel "Memory Usage (KB)"
set logscale xy
set grid
plot 'filesystem_comparison_20250829_88150.csv' using 1:2 with linespoints title 'ext4' lw 3 pt 7 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:3 with linespoints title 'BTRFS' lw 3 pt 9 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:4 with linespoints title 'ZFS' lw 3 pt 11 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:5 with linespoints title 'Succinct' lw 4 pt 13 ps 2.0

# Disk usage comparison
set title "Disk Usage: Filesystems vs Succinct"
set xlabel "Number of Nodes"
set ylabel "Disk Usage (KB)"
set logscale xy
plot 'filesystem_comparison_20250829_88150.csv' using 1:6 with linespoints title 'ext4' lw 3 pt 7 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:7 with linespoints title 'BTRFS' lw 3 pt 9 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:8 with linespoints title 'ZFS' lw 3 pt 11 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:9 with linespoints title 'Succinct' lw 4 pt 13 ps 2.0

# Memory efficiency comparison
set title "Memory Efficiency: Succinct vs Filesystems"
set xlabel "Number of Nodes"
set ylabel "Memory Reduction vs ext4 (%)"
unset logscale y
set logscale x
plot 'filesystem_comparison_20250829_88150.csv' using 1:(($2-$5)/$2*100) with linespoints title 'vs ext4' lw 3 pt 7 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:(($3-$5)/$3*100) with linespoints title 'vs BTRFS' lw 3 pt 9 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:(($4-$5)/$4*100) with linespoints title 'vs ZFS' lw 3 pt 11 ps 1.5

# Disk efficiency comparison
set title "Disk Efficiency: Succinct vs Filesystems"
set xlabel "Number of Nodes"
set ylabel "Disk Reduction vs ext4 (%)"
plot 'filesystem_comparison_20250829_88150.csv' using 1:(($6-$9)/$6*100) with linespoints title 'vs ext4' lw 3 pt 7 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:(($7-$9)/$7*100) with linespoints title 'vs BTRFS' lw 3 pt 9 ps 1.5, \
     'filesystem_comparison_20250829_88150.csv' using 1:(($8-$9)/$8*100) with linespoints title 'vs ZFS' lw 3 pt 11 ps 1.5

unset multiplot
