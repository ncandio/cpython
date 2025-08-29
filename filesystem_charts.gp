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

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:3 title 'ext4' with linespoints lc rgb '#2E8B57', \
     '' using 1:5 title 'ZFS' with linespoints lc rgb '#FF4500', \
     '' using 1:7 title 'Btrfs' with linespoints lc rgb '#4169E1', \
     '' using 1:9 title 'N-ary Tree FS' with linespoints lc rgb '#8A2BE2'

# Disk Usage Chart
unset logscale y
set title "Disk Usage Comparison" font "Arial,14" 
set ylabel "Disk Usage (MB)"

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:4 title 'ext4' with linespoints lc rgb '#2E8B57', \
     '' using 1:6 title 'ZFS' with linespoints lc rgb '#FF4500', \
     '' using 1:8 title 'Btrfs' with linespoints lc rgb '#4169E1', \
     '' using 1:10 title 'N-ary Tree FS' with linespoints lc rgb '#8A2BE2'

# RAM Percentage Chart
set title "RAM Usage % (16GB System)" font "Arial,14"
set ylabel "RAM Usage (%)"
set yrange [0:50]

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:11 title 'ext4' with linespoints lc rgb '#2E8B57', \
     '' using 1:13 title 'ZFS' with linespoints lc rgb '#FF4500', \
     '' using 1:15 title 'Btrfs' with linespoints lc rgb '#4169E1', \
     '' using 1:17 title 'N-ary Tree FS' with linespoints lc rgb '#8A2BE2'

# Efficiency Comparison
set title "Memory vs Disk (1M Files)" font "Arial,14"
set xlabel "Memory (MB)"
set ylabel "Disk (GB)"
unset logscale xy
set xrange [0:8000]
set yrange [100:160]

plot 67 using (67):(109.8) with points pt 7 ps 3 lc rgb '#2E8B57' title 'ext4', \
     7233 using (7233):(141.3) with points pt 5 ps 3 lc rgb '#FF4500' title 'ZFS', \
     46 using (46):(152.4) with points pt 9 ps 3 lc rgb '#4169E1' title 'Btrfs', \
     60 using (60):(134.5) with points pt 11 ps 3 lc rgb '#8A2BE2' title 'N-ary FS'

unset multiplot