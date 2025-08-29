#!/usr/bin/gnuplot
# Gnuplot script for narytree_memory_overtime_20250827_200205.csv
# Memory usage over time for N-ary Tree implementation

set terminal png size 1200,800 enhanced font 'Arial,12'
set output 'narytree_memory_overtime_20250827_200205_plot.png'

# Set title and labels
set title "N-ary Tree Memory Usage Over Time\nnarytree_memory_overtime_20250827_200205.csv" font 'Arial,16'
set xlabel "Time (seconds)" font 'Arial,14'
set ylabel "Memory Usage (MB)" font 'Arial,14'

# Configure grid and style
set grid
set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 ps 0.5
set style line 2 lc rgb '#dd181f' lt 1 lw 2 pt 5 ps 0.5

# Set up multi-plot for different metrics
set multiplot layout 2,2 title "N-ary Tree Memory Analysis" font 'Arial,18'

# Plot 1: Memory usage over time
set title "Total Memory Usage"
set ylabel "Memory (MB)"
plot 'narytree_memory_overtime_20250827_200205.csv' using 1:5 with linespoints linestyle 1 title "Total Memory", \
     'narytree_memory_overtime_20250827_200205.csv' using 1:6 with linespoints linestyle 2 title "Delta Memory"

# Plot 2: Memory per node
set title "Memory Efficiency"  
set ylabel "KB per Node"
plot 'narytree_memory_overtime_20250827_200205.csv' using 1:7 with linespoints linestyle 1 title "KB/Node"

# Plot 3: Total nodes over time
set title "Tree Growth"
set ylabel "Total Nodes"
plot 'narytree_memory_overtime_20250827_200205.csv' using 1:4 with linespoints linestyle 2 title "Total Nodes"

# Plot 4: Memory vs Nodes (scatter plot)
set title "Memory vs Nodes"
set xlabel "Total Nodes"
set ylabel "Memory (MB)"
plot 'narytree_memory_overtime_20250827_200205.csv' using 4:5 with points linestyle 1 title "Memory Usage"

unset multiplot

# Generate a second detailed plot
set output 'narytree_memory_overtime_20250827_200205_detailed.png'
set terminal png size 1600,1200 enhanced font 'Arial,10'

set multiplot layout 3,1

# Detailed memory timeline
set title "Detailed Memory Usage Timeline" font 'Arial,14'
set xlabel "Time (seconds)"
set ylabel "Memory (MB)"
set grid
plot 'narytree_memory_overtime_20250827_200205.csv' using 1:5 with lines lw 2 title "Total Memory", \
     'narytree_memory_overtime_20250827_200205.csv' using 1:6 with lines lw 2 title "Delta Memory"

# Memory efficiency over time
set title "Memory Efficiency Over Time"
set ylabel "KB per Node"
plot 'narytree_memory_overtime_20250827_200205.csv' using 1:7 with lines lw 2 title "Memory/Node"

# Growth rate analysis
set title "Node Growth Rate"
set xlabel "Time (seconds)"
set ylabel "Nodes"
plot 'narytree_memory_overtime_20250827_200205.csv' using 1:4 with lines lw 3 title "Total Nodes"

unset multiplot

print "Generated plots: narytree_memory_overtime_20250827_200205_plot.png and narytree_memory_overtime_20250827_200205_detailed.png"
