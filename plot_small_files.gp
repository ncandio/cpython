#!/usr/bin/gnuplot
# Gnuplot script for succinct vs ext4 small files comparison

set terminal png enhanced size 1200,800 font 'Arial,12'
set output 'succinct_vs_ext4_small_files.png'

set title 'Succinct FUSE vs ext4: Small Files Metadata Overhead Comparison'
set xlabel 'Number of Files'
set ylabel 'Disk Usage (KB)'
set grid

# Set up multiplot layout
set multiplot layout 2,2 title 'Succinct FUSE vs ext4 Analysis'

# Plot 1: Disk usage comparison
set title 'Disk Usage Comparison'
set key top left
plot datafile using 2:3 with linespoints title 'Succinct (KB)' lw 2 pt 7 ps 1.2, \
     datafile using 2:4 with linespoints title 'ext4 (KB)' lw 2 pt 5 ps 1.2

# Plot 2: Efficiency percentage
set title 'Space Efficiency (%)'
set ylabel 'Space Saved (%)'
set key bottom right
plot datafile using 2:5 with linespoints title 'Efficiency %' lw 3 pt 9 ps 1.2 lc rgb 'red'

# Plot 3: Ratio comparison
set title 'Succinct vs ext4 Ratio'
set ylabel 'Ratio (Succinct/ext4)'
set key top right
plot datafile using 2:($3/$4) with linespoints title 'Size Ratio' lw 2 pt 11 ps 1.2 lc rgb 'green'

# Plot 4: Data table
set title 'Summary Table'
unset xlabel
unset ylabel
unset grid
set border 0
unset tics
set key off

# Create a simple data display
set label 1 "Configuration Summary:" at screen 0.55, 0.35 font ",14"
set label 2 sprintf("Data from: %s", datafile) at screen 0.55, 0.30 font ",10"
set label 3 "Succinct FUSE filesystem shows metadata" at screen 0.55, 0.25 font ",10"
set label 4 "overhead reduction for complex structures" at screen 0.55, 0.22 font ",10"

plot NaN notitle

unset multiplot