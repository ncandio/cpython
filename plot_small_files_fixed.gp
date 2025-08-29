#!/usr/bin/gnuplot
# Gnuplot script for succinct vs ext4 small files comparison

set terminal png enhanced size 1200,800 font 'Arial,12'
set output 'succinct_vs_ext4_small_files.png'

set datafile separator ","
set key autotitle columnhead

# Set up multiplot layout
set multiplot layout 2,2 title 'Succinct FUSE vs ext4: Small Files Analysis'

# Plot 1: Disk usage comparison
set title 'Disk Usage Comparison'
set xlabel 'Number of Files'
set ylabel 'Disk Usage (KB)'
set grid
set key top left
plot datafile using 2:3 with linespoints title 'Succinct (KB)' lw 2 pt 7 ps 1.2 lc rgb 'blue', \
     datafile using 2:4 with linespoints title 'ext4 (KB)' lw 2 pt 5 ps 1.2 lc rgb 'red'

# Plot 2: Efficiency percentage
set title 'Space Efficiency'
set ylabel 'Space Saved (%)'
set key bottom right
plot datafile using 2:5 with linespoints title 'Efficiency %' lw 3 pt 9 ps 1.2 lc rgb 'green'

# Plot 3: Ratio comparison
set title 'Size Ratio (Succinct/ext4)'
set ylabel 'Ratio'
set key top right
plot datafile using 2:($3/$4) with linespoints title 'Size Ratio' lw 2 pt 11 ps 1.2 lc rgb 'purple'

# Plot 4: Bar chart comparison
set title 'Direct Comparison by Configuration'
set xlabel 'Test Configuration'
set ylabel 'Disk Usage (KB)'
set style data histograms
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9
set xtic rotate by -45 scale 0
plot datafile using 3:xtic(1) title 'Succinct (KB)' lc rgb 'blue', \
     '' using 4 title 'ext4 (KB)' lc rgb 'red'

unset multiplot