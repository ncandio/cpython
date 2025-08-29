#!/usr/bin/gnuplot

# Filesystem Comparison Visualization for Intel i7 16GB System
# Memory and Disk Usage Across Different Domains

set terminal png size 1400,1000 font "Arial,12"

# Set output file
set output 'comprehensive_filesystem_comparison_i7_16gb.png'

# Configure multiplot layout (2x2 grid)
set multiplot layout 2,2 title "Filesystem Comparison: Intel i7 16GB System\nMemory & Disk Usage Analysis" font "Arial,16"

# Set data file
datafile = 'filesystem_comparison_i7_16gb_20250829_123852.csv'

# Plot 1: Memory Usage Comparison (Linear Scale)
set title "Memory Usage Comparison" font "Arial,14"
set xlabel "Number of Files"
set ylabel "Memory Usage (MB)"
set logscale x
set logscale y
set grid
set key top left

plot datafile using 1:3 with linespoints lw 2 pt 7 title 'ext4' lc rgb '#2E8B57', \
     datafile using 1:5 with linespoints lw 2 pt 5 title 'ZFS' lc rgb '#FF4500', \
     datafile using 1:7 with linespoints lw 2 pt 9 title 'Btrfs' lc rgb '#4169E1', \
     datafile using 1:9 with linespoints lw 2 pt 11 title 'N-ary Tree FS' lc rgb '#8A2BE2'

# Plot 2: Disk Usage Comparison
unset logscale y
set title "Disk Usage Comparison" font "Arial,14"
set xlabel "Number of Files"  
set ylabel "Disk Usage (MB)"
set logscale x
set grid
set key top left

plot datafile using 1:4 with linespoints lw 2 pt 7 title 'ext4' lc rgb '#2E8B57', \
     datafile using 1:6 with linespoints lw 2 pt 5 title 'ZFS' lc rgb '#FF4500', \
     datafile using 1:8 with linespoints lw 2 pt 9 title 'Btrfs' lc rgb '#4169E1', \
     datafile using 1:10 with linespoints lw 2 pt 11 title 'N-ary Tree FS' lc rgb '#8A2BE2'

# Plot 3: RAM Percentage Usage
set title "RAM Usage Percentage (16GB System)" font "Arial,14"
set xlabel "Number of Files"
set ylabel "RAM Usage (%)"
set logscale x
unset logscale y
set grid
set key top left

# Add 10% RAM threshold line
set arrow from 1000,10 to 10000000,10 nohead linecolor rgb '#FF0000' linewidth 2
set label "10% RAM Threshold" at 100000,12 textcolor rgb '#FF0000'

plot datafile using 1:11 with linespoints lw 2 pt 7 title 'ext4' lc rgb '#2E8B57', \
     datafile using 1:13 with linespoints lw 2 pt 5 title 'ZFS' lc rgb '#FF4500', \
     datafile using 1:15 with linespoints lw 2 pt 9 title 'Btrfs' lc rgb '#4169E1', \
     datafile using 1:17 with linespoints lw 2 pt 11 title 'N-ary Tree FS' lc rgb '#8A2BE2'

# Plot 4: Efficiency Comparison (Memory vs Disk)
unset arrow
unset label
set title "Memory vs Disk Efficiency" font "Arial,14"
set xlabel "Memory Usage (MB)" 
set ylabel "Disk Usage (MB)"
unset logscale x
unset logscale y
set grid
set key bottom right

# Use 1M files data point for this comparison
plot datafile using 3:4 every ::5::5 with points pt 7 ps 3 title 'ext4' lc rgb '#2E8B57', \
     datafile using 5:6 every ::5::5 with points pt 5 ps 3 title 'ZFS' lc rgb '#FF4500', \
     datafile using 7:8 every ::5::5 with points pt 9 ps 3 title 'Btrfs' lc rgb '#4169E1', \
     datafile using 9:10 every ::5::5 with points pt 11 ps 3 title 'N-ary Tree FS' lc rgb '#8A2BE2'

unset multiplot

# Create separate detailed memory comparison
set terminal png size 1200,800 font "Arial,12"
set output 'filesystem_memory_comparison_detailed.png'

set title "Detailed Memory Usage: Filesystem Comparison (Intel i7 16GB)\nLogarithmic Scale Analysis" font "Arial,16"
set xlabel "Number of Files" font "Arial,14"
set ylabel "Memory Usage (MB)" font "Arial,14"
set logscale x
set logscale y
set grid
set key top left

# Add RAM capacity reference lines
set arrow from 1000,1638 to 10000000,1638 nohead linecolor rgb '#FF0000' linewidth 2
set label "10% of 16GB RAM" at 100000,2000 textcolor rgb '#FF0000'

set arrow from 1000,8192 to 10000000,8192 nohead linecolor rgb '#FF6600' linewidth 2  
set label "50% of 16GB RAM" at 100000,10000 textcolor rgb '#FF6600'

plot datafile using 1:3 with linespoints lw 3 pt 7 ps 2 title 'ext4' lc rgb '#2E8B57', \
     datafile using 1:5 with linespoints lw 3 pt 5 ps 2 title 'ZFS' lc rgb '#FF4500', \
     datafile using 1:7 with linespoints lw 3 pt 9 ps 2 title 'Btrfs' lc rgb '#4169E1', \
     datafile using 1:9 with linespoints lw 3 pt 11 ps 2 title 'N-ary Tree FS' lc rgb '#8A2BE2'

# Create disk efficiency chart
set terminal png size 1200,600 font "Arial,12"
set output 'filesystem_disk_efficiency_comparison.png'

set title "Disk Storage Efficiency Comparison\n(Lower is Better - Less Overhead)" font "Arial,16"
set xlabel "Number of Files" font "Arial,14"
set ylabel "Total Disk Usage (MB)" font "Arial,14"
set logscale x
unset logscale y
set grid
set key top left

plot datafile using 1:4 with linespoints lw 3 pt 7 ps 2 title 'ext4 (93.3% eff)' lc rgb '#2E8B57', \
     datafile using 1:10 with linespoints lw 3 pt 11 ps 2 title 'N-ary Tree FS (76.2% eff)' lc rgb '#8A2BE2', \
     datafile using 1:6 with linespoints lw 3 pt 5 ps 2 title 'ZFS (72.4% eff)' lc rgb '#FF4500', \
     datafile using 1:8 with linespoints lw 3 pt 9 ps 2 title 'Btrfs (67.2% eff)' lc rgb '#4169E1'