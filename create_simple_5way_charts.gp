#!/usr/bin/gnuplot

set datafile separator ","

# Simple 5-way comparison charts
set terminal png size 1400,1000 font "Arial,12"
set output 'filesystem_5way_comprehensive_comparison.png'

set multiplot layout 2,2 title "5-Way Filesystem Comparison: Intel i7 16GB\nMemory & Disk Analysis with Lazy Balancing" font "Arial,16"

# Memory Usage Chart
set title "Memory Usage Comparison" font "Arial,14"
set xlabel "Number of Files"
set ylabel "Memory Usage (MB)"
set logscale xy
set grid
set key top left

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:3 skip 1 title 'ext4' w lp lc rgb '#2E8B57', \
     '' using 1:5 skip 1 title 'ZFS' w lp lc rgb '#FF4500', \
     '' using 1:7 skip 1 title 'Btrfs' w lp lc rgb '#4169E1', \
     '' using 1:9 skip 1 title 'N-ary Auto' w lp lc rgb '#8A2BE2', \
     '' using 1:11 skip 1 title 'N-ary Lazy' w lp lc rgb '#FF1493'

# Disk Usage Chart
unset logscale y  
set title "Disk Usage Comparison" font "Arial,14"
set ylabel "Disk Usage (GB)"

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:4 skip 1 title 'ext4' w lp lc rgb '#2E8B57', \
     '' using 1:6 skip 1 title 'ZFS' w lp lc rgb '#FF4500', \
     '' using 1:8 skip 1 title 'Btrfs' w lp lc rgb '#4169E1', \
     '' using 1:10 skip 1 title 'N-ary Auto' w lp lc rgb '#8A2BE2', \
     '' using 1:12 skip 1 title 'N-ary Lazy' w lp lc rgb '#FF1493'

# RAM Usage Percentage
set title "RAM Usage % (16GB System)" font "Arial,14"
set ylabel "RAM Usage (%)"
set yrange [0:50]

plot 'filesystem_5way_comparison_20250829_135043.csv' using 1:5 skip 1 title 'ext4' w lp lc rgb '#2E8B57', \
     '' using 1:7 skip 1 title 'ZFS' w lp lc rgb '#FF4500', \
     '' using 1:9 skip 1 title 'Btrfs' w lp lc rgb '#4169E1', \
     '' using 1:11 skip 1 title 'N-ary Auto' w lp lc rgb '#8A2BE2', \
     '' using 1:13 skip 1 title 'N-ary Lazy' w lp lc rgb '#FF1493'

# Efficiency Summary (1M files)
unset logscale xy
set title "Efficiency Summary (1M Files)" font "Arial,14"
set xlabel "Memory Usage (MB)"
set ylabel "Disk Efficiency (%)"
set xrange [0:8000]
set yrange [65:95]

# Plot points: (memory_mb, disk_efficiency_percent)
plot 67 using (67):(93.3) w p pt 7 ps 3 lc rgb '#2E8B57' title 'ext4', \
     7233 using (7233):(72.4) w p pt 5 ps 3 lc rgb '#FF4500' title 'ZFS', \
     46 using (46):(67.2) w p pt 9 ps 3 lc rgb '#4169E1' title 'Btrfs', \
     156 using (156):(74.0) w p pt 11 ps 3 lc rgb '#8A2BE2' title 'N-ary Auto', \
     105 using (105):(79.5) w p pt 13 ps 3 lc rgb '#FF1493' title 'N-ary Lazy'

unset multiplot

# Create separate rebalancing comparison
set terminal png size 1200,600 font "Arial,12"
set output 'filesystem_rebalancing_operations_comparison.png'

set title "Rebalancing Operations: N-ary Tree Approaches\n(1M Files Scenario)" font "Arial,16"
set xlabel "Implementation"
set ylabel "Rebalancing Operations"
set style data histogram  
set style histogram cluster gap 2
set style fill solid 0.8
set boxwidth 0.6
set grid y

# Manual data for rebalancing operations
plot '-' using 2:xtic(1) title 'Rebalancing Ops' lc rgb '#8A2BE2'
"Manual" 0
"Lazy" 10000  
"Auto" 210000
e