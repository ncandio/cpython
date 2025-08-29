#!/usr/bin/gnuplot

set datafile separator ","

# 5-Way Filesystem Comparison with Lazy Balancing
set terminal png size 1600,1200 font "Arial,12"
set output 'filesystem_5way_comprehensive_comparison.png'

set multiplot layout 2,2 title "5-Way Filesystem Comparison: Intel i7 16GB\next4 vs ZFS vs Btrfs vs N-ary Auto vs N-ary Lazy" font "Arial,16"

# Memory Usage Chart
set title "Memory Usage Comparison" font "Arial,14"
set xlabel "Number of Files"
set ylabel "Memory Usage (MB)"
set logscale xy
set grid
set key top left

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:3 skip 1 title 'ext4' w lp lw 2 lc rgb '#2E8B57', \
     '' using 1:5 skip 1 title 'ZFS' w lp lw 2 lc rgb '#FF4500', \
     '' using 1:7 skip 1 title 'Btrfs' w lp lw 2 lc rgb '#4169E1', \
     '' using 1:9 skip 1 title 'N-ary Auto' w lp lw 2 lc rgb '#8A2BE2', \
     '' using 1:11 skip 1 title 'N-ary Lazy' w lp lw 2 lc rgb '#FF1493'

# Disk Usage Chart
unset logscale y
set title "Disk Usage Comparison" font "Arial,14"
set ylabel "Disk Usage (GB)"

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:4 skip 1 title 'ext4' w lp lw 2 lc rgb '#2E8B57', \
     '' using 1:6 skip 1 title 'ZFS' w lp lw 2 lc rgb '#FF4500', \
     '' using 1:8 skip 1 title 'Btrfs' w lp lw 2 lc rgb '#4169E1', \
     '' using 1:10 skip 1 title 'N-ary Auto' w lp lw 2 lc rgb '#8A2BE2', \
     '' using 1:12 skip 1 title 'N-ary Lazy' w lp lw 2 lc rgb '#FF1493'

# Rebalancing Operations Chart
set title "Rebalancing Operations (1M Files)" font "Arial,14"
set ylabel "Rebalancing Operations"
set xlabel "Filesystem"
unset logscale xy
set style data histogram
set style histogram cluster gap 1
set style fill solid 0.8
set boxwidth 0.8
set grid y

# Use 1M files data (row 7: ext4=0, zfs=0, btrfs=0, auto=210000, lazy=10000)
plot '-' using 2:xtic(1) title 'Rebalancing Operations' lc variable
ext4 0 1
ZFS 0 2  
Btrfs 0 3
"N-ary Auto" 210000 4
"N-ary Lazy" 10000 5
e

# RAM Usage Percentage
set title "RAM Usage % (16GB System)" font "Arial,14"
set ylabel "RAM Usage (%)"
set xlabel "Number of Files"
set logscale x
unset logscale y
set yrange [0:50]
set grid
set key top left
unset style

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:5 skip 1 title 'ext4' w lp lw 2 lc rgb '#2E8B57', \
     '' using 1:7 skip 1 title 'ZFS' w lp lw 2 lc rgb '#FF4500', \
     '' using 1:9 skip 1 title 'Btrfs' w lp lw 2 lc rgb '#4169E1', \
     '' using 1:11 skip 1 title 'N-ary Auto' w lp lw 2 lc rgb '#8A2BE2', \
     '' using 1:13 skip 1 title 'N-ary Lazy' w lp lw 2 lc rgb '#FF1493'

unset multiplot

# Create detailed memory efficiency chart
set terminal png size 1400,800 font "Arial,12"
set output 'filesystem_memory_efficiency_5way.png'

set title "Memory Efficiency: 5-Way Comparison\n(Lower = Better Memory Usage)" font "Arial,16"
set xlabel "Number of Files" font "Arial,14"
set ylabel "Memory Usage (MB)" font "Arial,14"
set logscale xy
set grid
set key top left

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:3 skip 1 title 'ext4 (27 B/entry)' w lp lw 3 lc rgb '#2E8B57', \
     '' using 1:11 skip 1 title 'N-ary Lazy (105 B/entry)' w lp lw 3 lc rgb '#FF1493', \
     '' using 1:7 skip 1 title 'Btrfs (42 B/entry)' w lp lw 3 lc rgb '#4169E1', \
     '' using 1:9 skip 1 title 'N-ary Auto (136 B/entry)' w lp lw 3 lc rgb '#8A2BE2', \
     '' using 1:5 skip 1 title 'ZFS (25 B/entry + ARC)' w lp lw 3 lc rgb '#FF4500'

# Create performance vs efficiency scatter plot
set terminal png size 1200,800 font "Arial,12"  
set output 'filesystem_performance_efficiency_matrix.png'

set title "Performance vs Memory Efficiency Matrix\n(1M Files on Intel i7 16GB)" font "Arial,16"
set xlabel "Memory Usage (MB)" font "Arial,14"
set ylabel "Performance Guarantee Score" font "Arial,14"
unset logscale xy
set grid

# Performance scores: ext4=6, ZFS=7, Btrfs=5, Auto=10, Lazy=9
# Memory usage: ext4=67, ZFS=7233, Btrfs=46, Auto=156, Lazy=105

plot 67 using (67):(6) w p pt 7 ps 4 lc rgb '#2E8B57' title 'ext4', \
     7233 using (7233):(7) w p pt 5 ps 4 lc rgb '#FF4500' title 'ZFS', \
     46 using (46):(5) w p pt 9 ps 4 lc rgb '#4169E1' title 'Btrfs', \
     156 using (156):(10) w p pt 11 ps 4 lc rgb '#8A2BE2' title 'N-ary Auto', \
     105 using (105):(9) w p pt 13 ps 4 lc rgb '#FF1493' title 'N-ary Lazy'