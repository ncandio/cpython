#!/usr/bin/gnuplot
# Enhanced Gnuplot script for N-ary Tree Memory Analysis
# Handles real data with proper scaling and multiple visualizations

set terminal png size 1600,1200 enhanced font 'Arial,12'
set output 'narytree_complete_analysis.png'

# Set up multiplot layout
set multiplot layout 2,3 title "N-ary Tree Memory Usage Over Time Analysis" font 'Arial,16'

# Configure styles
set style line 1 lc rgb '#2E8B57' lt 1 lw 2 pt 7 ps 0.8  # Sea Green
set style line 2 lc rgb '#DC143C' lt 1 lw 2 pt 5 ps 0.8  # Crimson
set style line 3 lc rgb '#4169E1' lt 1 lw 2 pt 9 ps 0.8  # Royal Blue
set style line 4 lc rgb '#FF8C00' lt 1 lw 2 pt 11 ps 0.8 # Dark Orange

# Plot 1: Progressive Tree Creation - Memory over Time
set title "Progressive Tree Creation" font 'Arial,14'
set xlabel "Time (seconds)"
set ylabel "Memory (MB)"
set grid
plot 'narytree_memory_overtime_20250827_200205.csv' using 1:5 with linespoints linestyle 1 title "Total Memory", \
     'narytree_memory_overtime_20250827_200205.csv' using 1:6 with linespoints linestyle 2 title "Delta Memory"

# Plot 2: Tree Count vs Memory
set title "Memory Usage vs Tree Count"
set xlabel "Number of Trees"
set ylabel "Memory (MB)"
plot 'narytree_memory_overtime_20250827_200205.csv' using 2:5 with linespoints linestyle 3 title "Memory vs Trees"

# Plot 3: Growth Simulation - Theoretical Analysis
set title "Growth Simulation (Theoretical)"
set xlabel "Time (seconds)"
set ylabel "Memory (MB)"
set logscale y
plot 'narytree_growth_simulation_20250827_200206.csv' using 1:5 with linespoints linestyle 1 title "Theoretical Memory", \
     'narytree_growth_simulation_20250827_200206.csv' using 1:6 with linespoints linestyle 2 title "Theoretical Delta"

# Plot 4: Memory Efficiency Over Time
set title "Memory Efficiency"
unset logscale y
set xlabel "Time (seconds)" 
set ylabel "KB per Node"
plot 'narytree_memory_overtime_20250827_200205.csv' using 1:7 with linespoints linestyle 4 title "Actual KB/Node", \
     'narytree_growth_simulation_20250827_200206.csv' using 1:7 with linespoints linestyle 2 title "Theoretical KB/Node"

# Plot 5: Cleanup Cycles Analysis
set title "Memory with Cleanup Cycles"
set xlabel "Time (seconds)"
set ylabel "Memory (MB)"
plot 'narytree_cleanup_cycles_20250827_200207.csv' using 1:5 with linespoints linestyle 1 title "Memory", \
     'narytree_cleanup_cycles_20250827_200207.csv' using 1:6 with linespoints linestyle 2 title "Delta"

# Plot 6: Combined Tree Growth
set title "Tree Growth Comparison" 
set xlabel "Total Trees"
set ylabel "Memory (MB)"
plot 'narytree_memory_overtime_20250827_200205.csv' using 2:5 with points linestyle 1 title "Progressive Creation", \
     'narytree_cleanup_cycles_20250827_200207.csv' using 2:5 with points linestyle 2 title "With Cleanup"

unset multiplot

# Generate detailed single plots
set terminal png size 1200,800

# Detailed memory timeline
set output 'narytree_memory_timeline.png'
set title "N-ary Tree Memory Usage Timeline" font 'Arial,16'
set xlabel "Time (seconds)" font 'Arial,14'
set ylabel "Memory Usage (MB)" font 'Arial,14'
set grid
set key top left

plot 'narytree_memory_overtime_20250827_200205.csv' using 1:5 with lines lw 3 lc rgb '#2E8B57' title "Progressive Creation", \
     'narytree_cleanup_cycles_20250827_200207.csv' using 1:5 with lines lw 3 lc rgb '#DC143C' title "With Cleanup Cycles", \
     'narytree_memory_overtime_20250827_200205.csv' using 1:6 with lines lw 2 lc rgb '#4169E1' title "Delta Memory"

# Memory efficiency comparison
set output 'narytree_efficiency_analysis.png' 
set title "Memory Efficiency Analysis" font 'Arial,16'
set xlabel "Number of Trees" font 'Arial,14'
set ylabel "Memory per Tree (KB)" font 'Arial,14'
set grid

plot 'narytree_memory_overtime_20250827_200205.csv' using 2:($6*1024/$2) with linespoints lw 2 pt 7 lc rgb '#2E8B57' title "Actual Memory/Tree", \
     'narytree_cleanup_cycles_20250827_200207.csv' using 2:($6*1024/$2) with linespoints lw 2 pt 5 lc rgb '#DC143C' title "With Cleanup"

# Tree scaling analysis
set output 'narytree_scaling_analysis.png'
set title "Tree Scaling Analysis: Memory vs Tree Count" font 'Arial,16'
set xlabel "Number of Trees (log scale)" font 'Arial,14'
set ylabel "Total Memory (MB)" font 'Arial,14'
set logscale x
set grid

plot 'narytree_memory_overtime_20250827_200205.csv' using 2:5 with linespoints lw 3 pt 7 ps 1 lc rgb '#2E8B57' title "Memory Usage", \
     x*0.001 with lines lw 2 lc rgb '#808080' title "Linear Reference"

print "Generated comprehensive memory analysis plots:"
print "  narytree_complete_analysis.png - Multi-panel overview"
print "  narytree_memory_timeline.png - Detailed timeline"  
print "  narytree_efficiency_analysis.png - Efficiency metrics"
print "  narytree_scaling_analysis.png - Scaling behavior"