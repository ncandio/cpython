#!/usr/bin/gnuplot

set datafile separator ","

# Working 5-way charts
set terminal png size 1600,1200 font "Arial,12"
set output 'filesystem_5way_comprehensive_comparison.png'

set multiplot layout 2,2 title "5-Way Filesystem Comparison: Intel i7 16GB\nIncluding N-ary Lazy Balancing Analysis" font "Arial,16"

# Memory Chart
set title "Memory Usage (MB)" font "Arial,14"
set xlabel "Number of Files"
set ylabel "Memory Usage (MB)"
set logscale xy
set grid
set key top left

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:3 skip 1 title 'ext4' w lp lc 1, \
     '' using 1:11 skip 1 title 'N-ary Lazy' w lp lc 6, \
     '' using 1:7 skip 1 title 'Btrfs' w lp lc 3, \
     '' using 1:9 skip 1 title 'N-ary Auto' w lp lc 4, \
     '' using 1:5 skip 1 title 'ZFS' w lp lc 2

# Disk Chart
unset logscale y
set title "Disk Usage (GB)" font "Arial,14"
set ylabel "Disk Usage (GB)"

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:4 skip 1 title 'ext4' w lp lc 1, \
     '' using 1:12 skip 1 title 'N-ary Lazy' w lp lc 6, \
     '' using 1:6 skip 1 title 'ZFS' w lp lc 2, \
     '' using 1:10 skip 1 title 'N-ary Auto' w lp lc 4, \
     '' using 1:8 skip 1 title 'Btrfs' w lp lc 3

# RAM Percentage
set title "RAM % Usage" font "Arial,14"  
set ylabel "RAM Usage (%)"
set yrange [0:50]

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:5 skip 1 title 'ext4' w lp lc 1, \
     '' using 1:13 skip 1 title 'N-ary Lazy' w lp lc 6, \
     '' using 1:9 skip 1 title 'Btrfs' w lp lc 3, \
     '' using 1:11 skip 1 title 'N-ary Auto' w lp lc 4, \
     '' using 1:7 skip 1 title 'ZFS' w lp lc 2

# Summary efficiency table
unset logscale xy
set title "Efficiency Summary (1M Files)" font "Arial,14"
set xlabel "Memory per Entry (bytes)"
set ylabel "Disk Efficiency (%)"
set xrange [20:140]
set yrange [65:95]

plot 27 w p pt 7 ps 4 lc 1 title 'ext4', \
     105 w p pt 13 ps 4 lc 6 title 'N-ary Lazy', \
     42 w p pt 9 ps 4 lc 3 title 'Btrfs', \
     136 w p pt 11 ps 4 lc 4 title 'N-ary Auto', \
     25 w p pt 5 ps 4 lc 2 title 'ZFS'

unset multiplot