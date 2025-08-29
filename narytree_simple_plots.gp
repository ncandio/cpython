# N-ary Tree Memory and Disk Usage Analysis
# Simple and effective visualization

set terminal pngcairo enhanced font "Arial,12" size 1600,1200
set output 'narytree_comprehensive_analysis.png'

# Multi-plot layout (2x2 grid)
set multiplot layout 2,2 title "N-ary Tree Memory & Disk Analysis (64-bit + Self-Balancing)" font "Arial,16"

# Data file
datafile = 'narytree_memory_disk_data_20250828_102933.csv'

#===========================
# Plot 1: Memory Usage vs Node Count
#===========================
set title "Memory Usage vs Node Count" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Memory Usage (MB)" font "Arial,12"
set grid
set key right bottom font "Arial,10"

plot for [n in "2 3 4 5 8 10 16 32"] \
     sprintf("< awk -F, 'NR>1 && $1==%s {print $2, $3}' %s", n, datafile) \
     using 1:2 with lines linewidth 3 title sprintf("N=%s", n)

#===========================
# Plot 2: Disk Usage vs Node Count
#===========================
set title "Disk Usage vs Node Count" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Disk Usage (MB)" font "Arial,12"
set grid
set key right bottom font "Arial,10"

plot for [n in "2 3 4 5 8 10 16 32"] \
     sprintf("< awk -F, 'NR>1 && $1==%s {print $2, $4}' %s", n, datafile) \
     using 1:2 with lines linewidth 3 title sprintf("N=%s", n)

#===========================
# Plot 3: Memory vs Disk at 100K nodes
#===========================
set title "Memory vs Disk Usage (100K Nodes)" font "Arial,14"
set xlabel "N Value (Branching Factor)" font "Arial,12"
set ylabel "Usage (MB)" font "Arial,12"
set grid
set key top left font "Arial,10"
set xtics (2,3,4,5,8,10,16,32)

plot "< awk -F, 'NR>1 && $2==100000 {print $1, $3}' narytree_memory_disk_data_20250828_102933.csv" \
     using 1:2 with linespoints linewidth 3 pointtype 7 pointsize 1.5 title "Memory" lc "blue", \
     "< awk -F, 'NR>1 && $2==100000 {print $1, $4}' narytree_memory_disk_data_20250828_102933.csv" \
     using 1:2 with linespoints linewidth 3 pointtype 5 pointsize 1.5 title "Disk" lc "red"

#===========================
# Plot 4: Memory/Disk Ratio
#===========================
set title "Memory/Disk Ratio vs N Value" font "Arial,14"
set xlabel "N Value" font "Arial,12"
set ylabel "Memory/Disk Ratio" font "Arial,12"
set grid
set key top right font "Arial,10"

plot "< awk -F, 'NR>1 && $2==100000 {print $1, $7}' narytree_memory_disk_data_20250828_102933.csv" \
     using 1:2 with linespoints linewidth 3 pointtype 9 pointsize 1.5 title "Ratio" lc "green", \
     1 with lines linewidth 2 dashtype 2 title "Equal (Ratio=1)" lc "black"

unset multiplot

# Single detailed plot for memory scaling
set output 'narytree_memory_scaling.png'
set title "Memory Scaling by N Value" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Memory Usage (MB)" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot for [n in "2 3 5 8 16 32"] \
     sprintf("< awk -F, 'NR>1 && $1==%s {print $2, $3}' %s", n, datafile) \
     using 1:2 with lines linewidth 3 title sprintf("N=%s", n)

# Disk scaling plot
set output 'narytree_disk_scaling.png'
set title "Disk Usage Scaling by N Value" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Disk Usage (MB)" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot for [n in "2 3 5 8 16 32"] \
     sprintf("< awk -F, 'NR>1 && $1==%s {print $2, $4}' %s", n, datafile) \
     using 1:2 with lines linewidth 3 title sprintf("N=%s", n)

# Balancing overhead
set output 'narytree_balancing_overhead.png'
set title "Self-Balancing Overhead by N Value" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Balancing Overhead (MB)" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot for [n in "2 3 5 8 16 32"] \
     sprintf("< awk -F, 'NR>1 && $1==%s {print $2, $9}' %s", n, datafile) \
     using 1:2 with lines linewidth 3 title sprintf("N=%s", n)

print "📊 Visualization completed!"
print "Generated files:"
print "- narytree_comprehensive_analysis.png (4-panel overview)"
print "- narytree_memory_scaling.png (memory scaling)"
print "- narytree_disk_scaling.png (disk scaling)"
print "- narytree_balancing_overhead.png (balancing overhead)"