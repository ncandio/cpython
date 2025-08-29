#!/usr/bin/gnuplot

set datafile separator ","

# 5-Way Comparison Charts
set terminal png size 1600,1000 font "Arial,12"
set output 'filesystem_5way_comprehensive_comparison.png'

set multiplot layout 2,2 title "5-Way Filesystem Comparison: Intel i7 16GB\next4 vs ZFS vs Btrfs vs N-ary Auto vs N-ary Lazy" font "Arial,16"

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

# RAM Percentage Chart
set title "RAM Usage % (16GB System)" font "Arial,14"
set ylabel "RAM Usage (%)"
set yrange [0:50]

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:5 skip 1 title 'ext4' w lp lc 1, \
     '' using 1:7 skip 1 title 'ZFS' w lp lc 2, \
     '' using 1:9 skip 1 title 'Btrfs' w lp lc 3, \
     '' using 1:11 skip 1 title 'N-ary Auto' w lp lc 4, \
     '' using 1:13 skip 1 title 'N-ary Lazy' w lp lc 6

# Performance vs Memory Scatter
unset logscale xy
set title "Memory vs Performance Trade-off" font "Arial,14"
set xlabel "Memory per Entry (bytes)"
set ylabel "Performance Score (1-10)"
set xrange [20:150]
set yrange [4:11]

# Manual plot points: ext4(27,6), ZFS(25,7), Btrfs(42,5), Auto(136,10), Lazy(105,9)
plot 27 using (27):(6) w p pt 7 ps 4 lc 1 title 'ext4', \
     25 using (25):(7) w p pt 5 ps 4 lc 2 title 'ZFS', \
     42 using (42):(5) w p pt 9 ps 4 lc 3 title 'Btrfs', \
     136 using (136):(10) w p pt 11 ps 4 lc 4 title 'N-ary Auto', \
     105 using (105):(9) w p pt 13 ps 4 lc 6 title 'N-ary Lazy'

unset multiplot