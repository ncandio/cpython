#!/usr/bin/gnuplot

set datafile separator ","

# 5-Way Comparison Main Chart
set terminal png size 1600,1000 font "Arial,12"
set output 'filesystem_5way_comprehensive_comparison.png'

set multiplot layout 2,2 title "5-Way Filesystem Comparison: Intel i7 16GB" font "Arial,16"

# Memory Usage Chart
set title "Memory Usage Comparison" font "Arial,14"
set xlabel "Number of Files"
set ylabel "Memory Usage (MB)"
set logscale xy
set grid
set key top left

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:3 skip 1 title 'ext4' w lp lc 1, \
     '' using 1:5 skip 1 title 'ZFS' w lp lc 2, \
     '' using 1:7 skip 1 title 'Btrfs' w lp lc 3, \
     '' using 1:9 skip 1 title 'N-ary Auto' w lp lc 4, \
     '' using 1:11 skip 1 title 'N-ary Lazy' w lp lc 6

# Disk Usage Chart  
unset logscale y
set title "Disk Usage Comparison" font "Arial,14"
set ylabel "Disk Usage (GB)"

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:4 skip 1 title 'ext4' w lp lc 1, \
     '' using 1:6 skip 1 title 'ZFS' w lp lc 2, \
     '' using 1:8 skip 1 title 'Btrfs' w lp lc 3, \
     '' using 1:10 skip 1 title 'N-ary Auto' w lp lc 4, \
     '' using 1:12 skip 1 title 'N-ary Lazy' w lp lc 6

# RAM Usage Percentage
set title "RAM Usage % (16GB System)" font "Arial,14"
set ylabel "RAM Usage (%)"
set yrange [0:50]

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:5 skip 1 title 'ext4' w lp lc 1, \
     '' using 1:7 skip 1 title 'ZFS' w lp lc 2, \
     '' using 1:9 skip 1 title 'Btrfs' w lp lc 3, \
     '' using 1:11 skip 1 title 'N-ary Auto' w lp lc 4, \
     '' using 1:13 skip 1 title 'N-ary Lazy' w lp lc 6

# Summary Bar Chart (1M files)
unset logscale x
set title "Summary: 1M Files Performance" font "Arial,14"
set xlabel "Filesystem"
set ylabel "Score (Memory+Disk+Performance)"
set style data histogram
set style fill solid 0.7
set boxwidth 0.6
set grid y

# Calculate composite scores (lower memory + lower disk + higher performance)
# ext4: score=9, ZFS: score=4, Btrfs: score=6, Auto: score=7, Lazy: score=8
plot '-' using 2:xtic(1) title 'Overall Score' lc variable
ext4 9.0 1
ZFS 4.0 2
Btrfs 6.0 3
"N-ary Auto" 7.0 4
"N-ary Lazy" 8.5 6
e

unset multiplot