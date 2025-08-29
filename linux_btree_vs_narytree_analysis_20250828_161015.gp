
# Linux B-tree vs N-ary Tree Comprehensive Analysis
# System: Intel(R) Core(TM) i5-8350U CPU @ 1.70GHz (x86_64)
# Memory: 7.7GB RAM
# Generated: 2025-08-28 16:11:15

set terminal png size 1600,1200 font "Arial,12"
set output 'linux_btree_vs_narytree_analysis_20250828_161015.png'

set multiplot layout 3,2 title "Linux B-tree vs N-ary Tree: Intel i5 Performance Analysis (7.7GB RAM)" font "Arial,16"

# Plot 1: Memory Usage Comparison
set logscale x
set grid
set xlabel 'Number of Entries'
set ylabel 'Total Memory Usage (MB)'
set title 'Memory Usage: Linux B-tree vs N-ary Tree'
set key top left

plot 'linux_btree_vs_narytree_20250828_161015.csv' using 1:($2/1024/1024) with linespoints linewidth 3 pointsize 2 title 'Linux B-tree', \
     'linux_btree_vs_narytree_20250828_161015.csv' using 1:($6/1024/1024) with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree'

# Plot 2: Memory Efficiency (bytes per entry)
set ylabel 'Memory per Entry (bytes)'
set title 'Memory Efficiency Comparison'
set yrange [15:65]

plot 'linux_btree_vs_narytree_20250828_161015.csv' using 1:3 with linespoints linewidth 3 pointsize 2 title 'Linux B-tree (19-35 bytes)', \
     'linux_btree_vs_narytree_20250828_161015.csv' using 1:7 with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree (57 bytes)'

# Plot 3: Search Performance
set ylabel 'Search Time (microseconds)'
set title 'Search Performance Comparison'
set yrange [0:20]

plot 'linux_btree_vs_narytree_20250828_161015.csv' using 1:4 with linespoints linewidth 3 pointsize 2 title 'Linux B-tree', \
     'linux_btree_vs_narytree_20250828_161015.csv' using 1:8 with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree'

# Plot 4: Memory Efficiency Ratio
unset logscale x
set xlabel 'Number of Entries'
set ylabel 'Efficiency Ratio (B-tree/N-ary)'
set title 'Memory Efficiency Ratio (< 1.0 = N-ary better)'
set yrange [0:2]

plot 'linux_btree_vs_narytree_20250828_161015.csv' using 1:10 with linespoints linewidth 3 pointsize 2 title 'Memory Efficiency Ratio', \
     1.0 with lines linewidth 2 linetype 2 title 'Break-even line'

# Plot 5: Performance Scaling
set logscale x
set xlabel 'Number of Entries'
set ylabel 'Insert Time per Entry (microseconds)'
set title 'Insert Performance Scaling'

plot 'linux_btree_vs_narytree_20250828_161015.csv' using 1:5 with linespoints linewidth 3 pointsize 2 title 'Linux B-tree', \
     'linux_btree_vs_narytree_20250828_161015.csv' using 1:9 with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree'

# Plot 6: System Resource Usage Projection
unset logscale x
set xlabel 'Number of Entries'
set ylabel 'Memory Usage (% of 7.7GB RAM)'
set title 'Memory Usage as % of Available RAM'
set yrange [0:10]

total_memory_bytes = 7.7 * 1024 * 1024 * 1024
plot 'linux_btree_vs_narytree_20250828_161015.csv' using 1:(($2/total_memory_bytes)*100) with linespoints linewidth 3 pointsize 2 title 'Linux B-tree', \
     'linux_btree_vs_narytree_20250828_161015.csv' using 1:(($6/total_memory_bytes)*100) with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree'

unset multiplot

# Generate summary statistics
set terminal png size 800,600
set output 'summary_comparison_20250828_161015.png'

set grid
set xlabel 'Implementation'
set ylabel 'Average Memory per Entry (bytes)'
set title 'Memory Efficiency Summary: Linux B-tree vs N-ary Tree'
set xrange [-0.5:1.5]
set yrange [0:70]
set boxwidth 0.3

# Calculate averages (approximate)
set style fill solid 0.7
plot '-' using 1:2 with boxes title 'Average Memory per Entry', \
     '-' using 1:2:3 with errorbars title 'Range'
0 25 
1 57
e
0 25 15
1 57 2  
e
