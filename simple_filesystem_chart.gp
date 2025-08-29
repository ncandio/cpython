#!/usr/bin/gnuplot

set datafile separator ","

# Memory Comparison Chart
set terminal png size 1200,800 font "Arial,12"
set output 'filesystem_memory_comparison.png'

set title "Memory Usage: Filesystem Comparison\nIntel i7 16GB System" font "Arial,16"
set xlabel "Number of Files" font "Arial,14"  
set ylabel "Memory Usage (MB)" font "Arial,14"
set logscale xy
set grid

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:3 skip 1 w lp title 'ext4' lc 1 lw 2, \
     '' using 1:5 skip 1 w lp title 'ZFS' lc 2 lw 2, \
     '' using 1:7 skip 1 w lp title 'Btrfs' lc 3 lw 2, \
     '' using 1:9 skip 1 w lp title 'N-ary Tree FS' lc 4 lw 2

# Disk Comparison Chart
set terminal png size 1200,800 font "Arial,12"
set output 'filesystem_disk_comparison.png'

set title "Disk Usage: Filesystem Comparison\nIntel i7 16GB System" font "Arial,16"
set ylabel "Disk Usage (GB)"
unset logscale y

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:($4/1024) skip 1 w lp title 'ext4' lc 1 lw 2, \
     '' using 1:($6/1024) skip 1 w lp title 'ZFS' lc 2 lw 2, \
     '' using 1:($8/1024) skip 1 w lp title 'Btrfs' lc 3 lw 2, \
     '' using 1:($10/1024) skip 1 w lp title 'N-ary Tree FS' lc 4 lw 2

# RAM Usage Percentage
set terminal png size 1200,600 font "Arial,12"
set output 'filesystem_ram_percentage.png'

set title "RAM Usage Percentage\nIntel i7 16GB System" font "Arial,16" 
set ylabel "RAM Usage (%)"
set yrange [0:50]

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:11 skip 1 w lp title 'ext4' lc 1 lw 2, \
     '' using 1:13 skip 1 w lp title 'ZFS' lc 2 lw 2, \
     '' using 1:15 skip 1 w lp title 'Btrfs' lc 3 lw 2, \
     '' using 1:17 skip 1 w lp title 'N-ary Tree FS' lc 4 lw 2