#!/usr/bin/gnuplot

set terminal png size 1400,1000 font "Arial,12"
set output 'comprehensive_filesystem_comparison_i7_16gb.png'

set multiplot layout 2,2 title "Filesystem Comparison: Intel i7 16GB System" font "Arial,16"

# Memory Usage Chart
set title "Memory Usage Comparison" font "Arial,14"
set xlabel "Number of Files"
set ylabel "Memory Usage (MB)"
set logscale xy
set grid
set key top left

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:3 title 'ext4' w lp lc 1, \
     '' using 1:5 title 'ZFS' w lp lc 2, \
     '' using 1:7 title 'Btrfs' w lp lc 3, \
     '' using 1:9 title 'N-ary Tree FS' w lp lc 4

# Disk Usage Chart
unset logscale y
set title "Disk Usage Comparison" font "Arial,14"
set ylabel "Disk Usage (MB)"

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:4 title 'ext4' w lp lc 1, \
     '' using 1:6 title 'ZFS' w lp lc 2, \
     '' using 1:8 title 'Btrfs' w lp lc 3, \
     '' using 1:10 title 'N-ary Tree FS' w lp lc 4

# RAM Percentage Chart  
set title "RAM Usage % (16GB System)" font "Arial,14"
set ylabel "RAM Usage (%)"
set yrange [0:50]

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:11 title 'ext4' w lp lc 1, \
     '' using 1:13 title 'ZFS' w lp lc 2, \
     '' using 1:15 title 'Btrfs' w lp lc 3, \
     '' using 1:17 title 'N-ary Tree FS' w lp lc 4

# Summary Chart - Memory vs Disk at 1M files
unset logscale xy
set title "Memory vs Disk Usage (1M Files)" font "Arial,14"
set xlabel "Memory Usage (MB)"
set ylabel "Disk Usage (GB)"
set xrange [0:8000]
set yrange [100:160]

plot 67 using (67):(109.8) w p pt 7 ps 3 lc 1 title 'ext4', \
     7233 using (7233):(141.3) w p pt 5 ps 3 lc 2 title 'ZFS', \
     46 using (46):(152.4) w p pt 9 ps 3 lc 3 title 'Btrfs', \
     60 using (60):(134.5) w p pt 11 ps 3 lc 4 title 'N-ary FS'

unset multiplot