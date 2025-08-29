#!/usr/bin/gnuplot

set datafile separator ","

# Memory Usage Detail Chart
set terminal png size 1200,800 font "Arial,12"
set output 'filesystem_memory_detailed_comparison.png'

set title "Memory Usage: Filesystem Comparison (Intel i7 16GB)\nLogarithmic Scale" font "Arial,16"
set xlabel "Number of Files" font "Arial,14"
set ylabel "Memory Usage (MB)" font "Arial,14"
set logscale xy
set grid
set key top left

# Add reference lines for RAM limits
set arrow from 1000,1638 to 10000000,1638 nohead lc rgb '#FF0000' lw 2
set label "10% of 16GB" at 100000,2000 tc rgb '#FF0000'
set arrow from 1000,8192 to 10000000,8192 nohead lc rgb '#FF6600' lw 2
set label "50% of 16GB" at 100000,10000 tc rgb '#FF6600'

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:3 skip 1 title 'ext4' w lp lw 3 lc rgb '#2E8B57', \
     '' using 1:5 skip 1 title 'ZFS' w lp lw 3 lc rgb '#FF4500', \
     '' using 1:7 skip 1 title 'Btrfs' w lp lw 3 lc rgb '#4169E1', \
     '' using 1:9 skip 1 title 'N-ary Tree FS' w lp lw 3 lc rgb '#8A2BE2'

# Disk Efficiency Chart  
set terminal png size 1200,800 font "Arial,12"
set output 'filesystem_disk_efficiency_detailed.png'

unset arrow
unset label
set title "Disk Storage Efficiency\n(Lower = Better Efficiency)" font "Arial,16"
set xlabel "Number of Files" font "Arial,14"
set ylabel "Total Disk Usage (GB)" font "Arial,14"
set logscale x
unset logscale y
set grid
set key top left

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:($4/1024) skip 1 title 'ext4 (93.3% eff)' w lp lw 3 lc rgb '#2E8B57', \
     '' using 1:($10/1024) skip 1 title 'N-ary Tree FS (76.2% eff)' w lp lw 3 lc rgb '#8A2BE2', \
     '' using 1:($6/1024) skip 1 title 'ZFS (72.4% eff)' w lp lw 3 lc rgb '#FF4500', \
     '' using 1:($8/1024) skip 1 title 'Btrfs (67.2% eff)' w lp lw 3 lc rgb '#4169E1'

# RAM Usage Percentage Chart
set terminal png size 1200,600 font "Arial,12"  
set output 'filesystem_ram_usage_percentage.png'

set title "RAM Usage Percentage (16GB Intel i7 System)" font "Arial,16"
set xlabel "Number of Files" font "Arial,14"
set ylabel "RAM Usage (%)" font "Arial,14"
set logscale x
unset logscale y
set yrange [0:50]
set grid
set key top left

# Add warning threshold
set arrow from 1000,10 to 10000000,10 nohead lc rgb '#FF0000' lw 2
set label "10% Warning" at 100000,12 tc rgb '#FF0000'

plot 'filesystem_comparison_i7_16gb_20250829_123852.csv' using 1:11 skip 1 title 'ext4' w lp lw 3 lc rgb '#2E8B57', \
     '' using 1:13 skip 1 title 'ZFS' w lp lw 3 lc rgb '#FF4500', \
     '' using 1:15 skip 1 title 'Btrfs' w lp lw 3 lc rgb '#4169E1', \
     '' using 1:17 skip 1 title 'N-ary Tree FS' w lp lw 3 lc rgb '#8A2BE2'