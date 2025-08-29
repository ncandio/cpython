# N-ary Tree Memory and Disk Usage Analysis with Self-Balancing
# Comprehensive Gnuplot Visualization Script for 64-bit Architecture

# Set up output
set terminal pngcairo enhanced font "Arial,12" size 1600,1200
set output 'narytree_comprehensive_analysis.png'

# Multi-plot layout (2x2 grid)
set multiplot layout 2,2 title "N-ary Tree Memory & Disk Analysis (64-bit + Self-Balancing)" font "Arial,16"

# Data file
datafile = 'narytree_memory_disk_data_20250828_102933.csv'

#===========================
# Plot 1: Memory Usage by N and Node Count
#===========================
set title "Memory Usage vs Node Count" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Memory Usage (MB)" font "Arial,12"
set grid
set key right bottom font "Arial,10"

plot datafile using ($1==2 ? $2 : 1/0):($1==2 ? $3 : 1/0) with lines linewidth 3 title "N=2" lc "red", \
     datafile using ($1==3 ? $2 : 1/0):($1==3 ? $3 : 1/0) with lines linewidth 3 title "N=3" lc "orange", \
     datafile using ($1==4 ? $2 : 1/0):($1==4 ? $3 : 1/0) with lines linewidth 3 title "N=4" lc "yellow", \
     datafile using ($1==5 ? $2 : 1/0):($1==5 ? $3 : 1/0) with lines linewidth 3 title "N=5" lc "green", \
     datafile using ($1==8 ? $2 : 1/0):($1==8 ? $3 : 1/0) with lines linewidth 3 title "N=8" lc "cyan", \
     datafile using ($1==10 ? $2 : 1/0):($1==10 ? $3 : 1/0) with lines linewidth 3 title "N=10" lc "blue", \
     datafile using ($1==16 ? $2 : 1/0):($1==16 ? $3 : 1/0) with lines linewidth 3 title "N=16" lc "purple", \
     datafile using ($1==32 ? $2 : 1/0):($1==32 ? $3 : 1/0) with lines linewidth 3 title "N=32" lc "magenta"

#===========================
# Plot 2: Disk Usage by N and Node Count  
#===========================
set title "Disk Usage vs Node Count" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Disk Usage (MB)" font "Arial,12"
set grid
set key right bottom font "Arial,10"

plot datafile using ($1==2 ? $2 : 1/0):($1==2 ? $4 : 1/0) with lines linewidth 3 title "N=2" lc "red", \
     datafile using ($1==3 ? $2 : 1/0):($1==3 ? $4 : 1/0) with lines linewidth 3 title "N=3" lc "orange", \
     datafile using ($1==4 ? $2 : 1/0):($1==4 ? $4 : 1/0) with lines linewidth 3 title "N=4" lc "yellow", \
     datafile using ($1==5 ? $2 : 1/0):($1==5 ? $4 : 1/0) with lines linewidth 3 title "N=5" lc "green", \
     datafile using ($1==8 ? $2 : 1/0):($1==8 ? $4 : 1/0) with lines linewidth 3 title "N=8" lc "cyan", \
     datafile using ($1==10 ? $2 : 1/0):($1==10 ? $4 : 1/0) with lines linewidth 3 title "N=10" lc "blue", \
     datafile using ($1==16 ? $2 : 1/0):($1==16 ? $4 : 1/0) with lines linewidth 3 title "N=16" lc "purple", \
     datafile using ($1==32 ? $2 : 1/0):($1==32 ? $4 : 1/0) with lines linewidth 3 title "N=32" lc "magenta"

#===========================
# Plot 3: Memory vs Disk Comparison
#===========================
set title "Memory vs Disk Usage (100K Nodes)" font "Arial,14"
set xlabel "N Value (Branching Factor)" font "Arial,12"
set ylabel "Usage (MB)" font "Arial,12"
set grid
set key top left font "Arial,10"
set xtics (2,3,4,5,8,10,16,32)

plot datafile using ($2==100000 ? $1 : 1/0):($2==100000 ? $3 : 1/0) with linespoints \
     linewidth 3 pointtype 7 pointsize 1.5 title "Memory Usage" lc "blue", \
     datafile using ($2==100000 ? $1 : 1/0):($2==100000 ? $4 : 1/0) with linespoints \
     linewidth 3 pointtype 5 pointsize 1.5 title "Disk Usage" lc "red"

#===========================
# Plot 4: Memory/Disk Efficiency Ratio
#===========================
set title "Memory/Disk Ratio vs N Value" font "Arial,14"
set xlabel "N Value (Branching Factor)" font "Arial,12"
set ylabel "Memory/Disk Ratio" font "Arial,12"
set grid
set key top right font "Arial,10"
set xtics (2,3,4,5,8,10,16,32)

plot datafile using ($2==100000 ? $1 : 1/0):($2==100000 ? $7 : 1/0) with linespoints \
     linewidth 3 pointtype 9 pointsize 1.5 title "Ratio (100K nodes)" lc "green", \
     1 with lines linewidth 2 dashtype 2 title "Equal Memory/Disk" lc "black"

unset multiplot

# Generate detailed analysis plot
set terminal pngcairo enhanced font "Arial,14" size 1400,900
set output 'narytree_memory_scaling_analysis.png'
set title "N-ary Tree Scaling Analysis: Memory & Disk vs Node Count" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Usage (MB)" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot datafile using ($1==2 ? $2 : 1/0):($1==2 ? $3 : 1/0) with lines linewidth 2 title "N=2 Memory" lc "red" dashtype 1, \
     datafile using ($1==2 ? $2 : 1/0):($1==2 ? $4 : 1/0) with lines linewidth 2 title "N=2 Disk" lc "red" dashtype 2, \
     datafile using ($1==3 ? $2 : 1/0):($1==3 ? $3 : 1/0) with lines linewidth 2 title "N=3 Memory" lc "blue" dashtype 1, \
     datafile using ($1==3 ? $2 : 1/0):($1==3 ? $4 : 1/0) with lines linewidth 2 title "N=3 Disk" lc "blue" dashtype 2, \
     datafile using ($1==5 ? $2 : 1/0):($1==5 ? $3 : 1/0) with lines linewidth 2 title "N=5 Memory" lc "green" dashtype 1, \
     datafile using ($1==5 ? $2 : 1/0):($1==5 ? $4 : 1/0) with lines linewidth 2 title "N=5 Disk" lc "green" dashtype 2, \
     datafile using ($1==16 ? $2 : 1/0):($1==16 ? $3 : 1/0) with lines linewidth 2 title "N=16 Memory" lc "purple" dashtype 1, \
     datafile using ($1==16 ? $2 : 1/0):($1==16 ? $4 : 1/0) with lines linewidth 2 title "N=16 Disk" lc "purple" dashtype 2

# Generate balancing overhead analysis
set output 'narytree_balancing_overhead.png'
set title "Self-Balancing Overhead Analysis" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Balancing Overhead (MB)" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot datafile using ($1==2 ? $2 : 1/0):($1==2 ? $9 : 1/0) with lines linewidth 3 title "N=2" lc "red", \
     datafile using ($1==3 ? $2 : 1/0):($1==3 ? $9 : 1/0) with lines linewidth 3 title "N=3" lc "orange", \
     datafile using ($1==5 ? $2 : 1/0):($1==5 ? $9 : 1/0) with lines linewidth 3 title "N=5" lc "green", \
     datafile using ($1==8 ? $2 : 1/0):($1==8 ? $9 : 1/0) with lines linewidth 3 title "N=8" lc "cyan", \
     datafile using ($1==16 ? $2 : 1/0):($1==16 ? $9 : 1/0) with lines linewidth 3 title "N=16" lc "purple", \
     datafile using ($1==32 ? $2 : 1/0):($1==32 ? $9 : 1/0) with lines linewidth 3 title "N=32" lc "magenta"

print "🎯 Gnuplot visualization completed successfully!"