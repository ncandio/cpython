#!/usr/bin/gnuplot

set terminal png size 1600,1200 font "Arial,12"
set output 'comprehensive_filesystem_comparison_i7_16gb.png'

set datafile separator ","

set multiplot layout 2,2 title "Filesystem Comparison: Intel i7 16GB System\nMemory & Disk Usage Analysis" font "Arial,16"

# Memory Usage Chart
set title "Memory Usage Comparison" font "Arial,14"
set xlabel "Number of Files"
set ylabel "Memory Usage (MB)"
set logscale xy
set grid
set key top left

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:3 skip 1 title 'ext4' w lp lc rgb '#2E8B57', \
     '' using 1:5 skip 1 title 'ZFS' w lp lc rgb '#FF4500', \
     '' using 1:7 skip 1 title 'Btrfs' w lp lc rgb '#4169E1', \
     '' using 1:9 skip 1 title 'N-ary Tree FS' w lp lc rgb '#8A2BE2'

# Disk Usage Chart
unset logscale y
set title "Disk Usage Comparison" font "Arial,14"
set ylabel "Disk Usage (MB)"

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:4 skip 1 title 'ext4' w lp lc rgb '#2E8B57', \
     '' using 1:6 skip 1 title 'ZFS' w lp lc rgb '#FF4500', \
     '' using 1:8 skip 1 title 'Btrfs' w lp lc rgb '#4169E1', \
     '' using 1:10 skip 1 title 'N-ary Tree FS' w lp lc rgb '#8A2BE2'

# RAM Percentage Chart
set title "RAM Usage % (16GB System)" font "Arial,14"
set ylabel "RAM Usage (%)"
set yrange [0:50]

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:11 skip 1 title 'ext4' w lp lc rgb '#2E8B57', \
     '' using 1:13 skip 1 title 'ZFS' w lp lc rgb '#FF4500', \
     '' using 1:15 skip 1 title 'Btrfs' w lp lc rgb '#4169E1', \
     '' using 1:17 skip 1 title 'N-ary Tree FS' w lp lc rgb '#8A2BE2'

# Summary Efficiency Chart
unset logscale xy
set title "Storage Efficiency Summary" font "Arial,14"
set xlabel "Filesystem"
set ylabel "Usage (MB)"
unset grid
set style data histogram
set style histogram cluster gap 1
set style fill solid 0.7
set boxwidth 0.8
set xtics rotate by -45
set key top left

# Use 1M files data (row 7)
plot newhistogram "Memory (MB)", \
     'filesystem_comparison_i7_16gb_20250829_123852.csv' using 3:xtic(sprintf("ext4\n%.0f",$3)) every ::6::6 lc rgb '#2E8B57', \
     '' using 5:xtic(sprintf("ZFS\n%.0f",$5)) every ::6::6 lc rgb '#FF4500', \
     '' using 7:xtic(sprintf("Btrfs\n%.0f",$7)) every ::6::6 lc rgb '#4169E1', \
     '' using 9:xtic(sprintf("N-ary\n%.0f",$9)) every ::6::6 lc rgb '#8A2BE2'

unset multiplot