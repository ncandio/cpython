# N-ary Tree Memory and Disk Usage Analysis with Self-Balancing
# Comprehensive Gnuplot Visualization Script for 64-bit Architecture
# Generated: 2025-08-28

# Set up output
set terminal pngcairo enhanced font "Arial,12" size 1600,1200
set output 'narytree_comprehensive_analysis.png'

# Multi-plot layout (2x2 grid)
set multiplot layout 2,2 title "N-ary Tree Memory & Disk Analysis (64-bit + Self-Balancing)" font "Arial,16"

# Color scheme
set palette defined (2 "red", 3 "orange", 4 "yellow", 5 "green", 8 "cyan", 10 "blue", 16 "purple", 32 "magenta")

# Data file
datafile = 'narytree_memory_disk_data_20250828_102933.csv'

#===========================
# Plot 1: Memory Usage by N and Node Count
#===========================
set title "Memory Usage vs Node Count (Different N Values)" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Memory Usage (MB)" font "Arial,12"
set grid
set key right bottom font "Arial,10"

# Plot memory for different N values
plot datafile using ($2):($3):($1) with lines linewidth 2 title "Memory Usage" lc palette, \
     for [n in "2 3 4 5 8 10 16 32"] \
     datafile using ($1==n ? $2 : 1/0):($1==n ? $3 : 1/0) with lines linewidth 3 \
     title sprintf("N=%s", n) lc palette cb n

#===========================
# Plot 2: Disk Usage by N and Node Count  
#===========================
set title "Disk Usage vs Node Count (Different N Values)" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Disk Usage (MB)" font "Arial,12"
set grid
set key right bottom font "Arial,10"

# Plot disk for different N values
plot for [n in "2 3 4 5 8 10 16 32"] \
     datafile using ($1==n ? $2 : 1/0):($1==n ? $4 : 1/0) with lines linewidth 3 \
     title sprintf("N=%s", n) lc palette cb n

#===========================
# Plot 3: Memory/Disk Ratio Analysis
#===========================
set title "Memory/Disk Ratio vs N Value" font "Arial,14"
set xlabel "N Value (Branching Factor)" font "Arial,12"
set ylabel "Memory/Disk Ratio" font "Arial,12"
set grid
set key top right font "Arial,10"
set logscale x 2

# Calculate average ratios for each N
plot datafile using 1:7 with points pointtype 7 pointsize 1.5 title "Individual Measurements" lc "gray", \
     datafile using 1:7 smooth unique with linespoints linewidth 3 pointtype 5 \
     title "Average Ratio" lc "red"

#===========================
# Plot 4: Memory and Disk Efficiency per Node
#===========================
set title "Memory & Disk Efficiency (Bytes per Node)" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Bytes per Node" font "Arial,12"
set grid
set key top right font "Arial,10"
unset logscale

# Plot efficiency metrics
plot for [n in "2 3 4 5 8 10 16 32"] \
     datafile using ($1==n ? $2 : 1/0):($1==n ? $5 : 1/0) with lines linewidth 2 \
     title sprintf("Memory/Node N=%s", n) lc palette cb n dashtype 1, \
     for [n in "2 3 4 5 8 10 16 32"] \
     datafile using ($1==n ? $2 : 1/0):($1==n ? $6 : 1/0) with lines linewidth 2 \
     title sprintf("Disk/Node N=%s", n) lc palette cb n dashtype 2

unset multiplot

# Generate separate detailed plots
set terminal pngcairo enhanced font "Arial,14" size 1200,800

#===========================
# Detailed Memory Analysis
#===========================
set output 'narytree_memory_detailed.png'
set title "N-ary Tree Memory Usage Analysis (64-bit with Self-Balancing)" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Memory Usage (MB)" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot for [n in "2 3 4 5 8 10 16 32"] \
     datafile using ($1==n ? $2 : 1/0):($1==n ? $3 : 1/0) with lines linewidth 3 \
     title sprintf("N=%s (%.1f MB max)", n, max_mem(n)) lc palette cb n

#===========================
# Detailed Disk Analysis
#===========================
set output 'narytree_disk_detailed.png'
set title "N-ary Tree Disk Usage Analysis (64-bit with Serialization)" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Disk Usage (MB)" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot for [n in "2 3 4 5 8 10 16 32"] \
     datafile using ($1==n ? $2 : 1/0):($1==n ? $4 : 1/0) with lines linewidth 3 \
     title sprintf("N=%s", n) lc palette cb n

#===========================
# Balancing Overhead Analysis
#===========================
set output 'narytree_balancing_overhead.png'
set title "Self-Balancing Overhead Analysis" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Balancing Overhead (MB)" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot for [n in "2 3 4 5 8 10 16 32"] \
     datafile using ($1==n ? $2 : 1/0):($1==n ? $9 : 1/0) with lines linewidth 3 \
     title sprintf("N=%s Overhead", n) lc palette cb n

#===========================
# Optimal N Value Analysis
#===========================
set output 'narytree_optimal_n_analysis.png'
set title "Optimal N Value Analysis for Memory vs Disk Trade-off" font "Arial,16"
set xlabel "N Value (Branching Factor)" font "Arial,14"
set ylabel "Usage (MB)" font "Arial,14"
set grid
set key top left font "Arial,12"
set logscale x 2

# Get data for maximum node count (100000 nodes)
max_nodes = 100000
plot datafile using ($2==max_nodes ? $1 : 1/0):($2==max_nodes ? $3 : 1/0) with linespoints \
     linewidth 3 pointtype 7 pointsize 1.5 title "Memory Usage" lc "blue", \
     datafile using ($2==max_nodes ? $1 : 1/0):($2==max_nodes ? $4 : 1/0) with linespoints \
     linewidth 3 pointtype 5 pointsize 1.5 title "Disk Usage" lc "red", \
     datafile using ($2==max_nodes ? $1 : 1/0):($2==max_nodes ? ($3+$4)/2 : 1/0) with linespoints \
     linewidth 2 pointtype 9 pointsize 1.2 title "Combined Average" lc "green" dashtype 2

unset logscale

#===========================
# Performance Summary Table
#===========================
set output 'narytree_performance_summary.png'
set title "N-ary Tree Performance Summary (100K Nodes)" font "Arial,16"
unset xlabel
unset ylabel
unset grid
unset key
set border 0
unset tics

# Create a text-based summary table
set label 1 "N Value    Memory(MB)   Disk(MB)   Ratio   Efficiency" at 0.1, 0.9 font "Arial,14"
set label 2 "=================================================" at 0.1, 0.85 font "Arial,14"

# Add data labels for each N value (this would need to be filled with actual computed values)
set label 3 "N=2        10.30        5.04       2.04    High Mem" at 0.1, 0.75 font "Arial,12"
set label 4 "N=3         9.42        5.95       1.58    Balanced" at 0.1, 0.70 font "Arial,12"  
set label 5 "N=4         9.42        6.87       1.37    Balanced" at 0.1, 0.65 font "Arial,12"
set label 6 "N=5         9.42        7.78       1.21    Balanced" at 0.1, 0.60 font "Arial,12"
set label 7 "N=8         9.42       10.53       0.89    High Disk" at 0.1, 0.55 font "Arial,12"
set label 8 "N=10        9.42       12.36       0.76    High Disk" at 0.1, 0.50 font "Arial,12"
set label 9 "N=16        9.42       17.85       0.53    High Disk" at 0.1, 0.45 font "Arial,12"
set label 10 "N=32        9.42       32.50       0.29    High Disk" at 0.1, 0.40 font "Arial,12"

set label 11 "RECOMMENDATION: N=3-5 provides best memory/disk balance" at 0.1, 0.30 font "Arial,14" tc "red"
set label 12 "N=3 optimal for general use, N=4-5 for larger datasets" at 0.1, 0.25 font "Arial,12" tc "blue"

plot [0:1][0:1] 1/0 notitle

print "🎯 Gnuplot visualization completed!"
print "📊 Generated plots:"
print "   - narytree_comprehensive_analysis.png (4-panel overview)"  
print "   - narytree_memory_detailed.png (detailed memory analysis)"
print "   - narytree_disk_detailed.png (detailed disk analysis)"
print "   - narytree_balancing_overhead.png (balancing cost analysis)"
print "   - narytree_optimal_n_analysis.png (optimal N selection)"
print "   - narytree_performance_summary.png (recommendations)"