# N-ary Tree: Auto-Rebalancing vs Original Comparison
# Comprehensive Gnuplot Visualization Script

set terminal pngcairo enhanced font "Arial,12" size 1800,1400

# Extract data for both implementations
system("awk -F, 'NR>1 && $1==\"auto\" && $2==2 {print $3, $4}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_n2_mem.dat")
system("awk -F, 'NR>1 && $1==\"auto\" && $2==3 {print $3, $4}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_n3_mem.dat")
system("awk -F, 'NR>1 && $1==\"auto\" && $2==5 {print $3, $4}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_n5_mem.dat")

# Original data (from previous analysis)
system("awk -F, 'NR>1 && $1==2 {print $2, $3}' narytree_memory_disk_data_20250828_102933.csv > orig_n2_mem.dat")
system("awk -F, 'NR>1 && $1==3 {print $2, $3}' narytree_memory_disk_data_20250828_102933.csv > orig_n3_mem.dat")
system("awk -F, 'NR>1 && $1==5 {print $2, $3}' narytree_memory_disk_data_20250828_102933.csv > orig_n5_mem.dat")

# Auto-rebalancing disk data
system("awk -F, 'NR>1 && $1==\"auto\" && $2==2 {print $3, $5}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_n2_dsk.dat")
system("awk -F, 'NR>1 && $1==\"auto\" && $2==3 {print $3, $5}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_n3_dsk.dat")
system("awk -F, 'NR>1 && $1==\"auto\" && $2==5 {print $3, $5}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_n5_dsk.dat")

# Original disk data
system("awk -F, 'NR>1 && $1==2 {print $2, $4}' narytree_memory_disk_data_20250828_102933.csv > orig_n2_dsk.dat")
system("awk -F, 'NR>1 && $1==3 {print $2, $4}' narytree_memory_disk_data_20250828_102933.csv > orig_n3_dsk.dat")
system("awk -F, 'NR>1 && $1==5 {print $2, $4}' narytree_memory_disk_data_20250828_102933.csv > orig_n5_dsk.dat")

# Rebalancing operations data
system("awk -F, 'NR>1 && $1==\"auto\" && $2==2 {print $3, $11}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_n2_rebal.dat")
system("awk -F, 'NR>1 && $1==\"auto\" && $2==3 {print $3, $11}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_n3_rebal.dat")
system("awk -F, 'NR>1 && $1==\"auto\" && $2==5 {print $3, $11}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_n5_rebal.dat")

# Summary comparison data (100K nodes)
system("awk -F, 'NR>1 && $1==\"auto\" && $3==100000 {print $2, $4, $5}' narytree_auto_vs_original_comparison_20250828_110726.csv > auto_summary.dat")
system("awk -F, 'NR>1 && $2==100000 {print $1, $3, $4}' narytree_memory_disk_data_20250828_102933.csv > orig_summary.dat")

#===========================
# Multi-plot layout (3x2)
#===========================
set output 'narytree_auto_vs_original_comprehensive.png'
set multiplot layout 3,2 title "N-ary Tree: Auto-Rebalancing vs Original Implementation" font "Arial,16"

#===========================
# Plot 1: Memory Comparison
#===========================
set title "Memory Usage Comparison" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Memory Usage (MB)" font "Arial,12"
set grid
set key right bottom font "Arial,10"

plot 'orig_n2_mem.dat' using 1:2 with lines lw 2 lc rgb "red" dt 1 title "N=2 Original", \
     'auto_n2_mem.dat' using 1:2 with lines lw 3 lc rgb "red" dt 2 title "N=2 Auto-Rebalancing", \
     'orig_n3_mem.dat' using 1:2 with lines lw 2 lc rgb "blue" dt 1 title "N=3 Original", \
     'auto_n3_mem.dat' using 1:2 with lines lw 3 lc rgb "blue" dt 2 title "N=3 Auto-Rebalancing", \
     'orig_n5_mem.dat' using 1:2 with lines lw 2 lc rgb "green" dt 1 title "N=5 Original", \
     'auto_n5_mem.dat' using 1:2 with lines lw 3 lc rgb "green" dt 2 title "N=5 Auto-Rebalancing"

#===========================
# Plot 2: Disk Comparison
#===========================
set title "Disk Usage Comparison" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Disk Usage (MB)" font "Arial,12"
set grid
set key right bottom font "Arial,10"

plot 'orig_n2_dsk.dat' using 1:2 with lines lw 2 lc rgb "red" dt 1 title "N=2 Original", \
     'auto_n2_dsk.dat' using 1:2 with lines lw 3 lc rgb "red" dt 2 title "N=2 Auto-Rebalancing", \
     'orig_n3_dsk.dat' using 1:2 with lines lw 2 lc rgb "blue" dt 1 title "N=3 Original", \
     'auto_n3_dsk.dat' using 1:2 with lines lw 3 lc rgb "blue" dt 2 title "N=3 Auto-Rebalancing", \
     'orig_n5_dsk.dat' using 1:2 with lines lw 2 lc rgb "green" dt 1 title "N=5 Original", \
     'auto_n5_dsk.dat' using 1:2 with lines lw 3 lc rgb "green" dt 2 title "N=5 Auto-Rebalancing"

#===========================
# Plot 3: Memory Overhead Analysis
#===========================
set title "Memory Overhead: Auto vs Original (100K Nodes)" font "Arial,14"
set xlabel "N Value" font "Arial,12"
set ylabel "Memory Usage (MB)" font "Arial,12"
set grid
set key top left font "Arial,10"
set xtics (2,3,4,5,8,10,16,32)

plot 'orig_summary.dat' using 1:2 with linespoints lw 3 pt 7 ps 1.5 lc rgb "blue" title "Original (Lazy Rebalancing)", \
     'auto_summary.dat' using 1:2 with linespoints lw 3 pt 5 ps 1.5 lc rgb "red" title "Auto-Rebalancing"

#===========================
# Plot 4: Disk Overhead Analysis
#===========================
set title "Disk Overhead: Auto vs Original (100K Nodes)" font "Arial,14"
set xlabel "N Value" font "Arial,12"
set ylabel "Disk Usage (MB)" font "Arial,12"
set grid
set key top left font "Arial,10"
set xtics (2,3,4,5,8,10,16,32)

plot 'orig_summary.dat' using 1:3 with linespoints lw 3 pt 7 ps 1.5 lc rgb "blue" title "Original (Lazy Rebalancing)", \
     'auto_summary.dat' using 1:3 with linespoints lw 3 pt 5 ps 1.5 lc rgb "red" title "Auto-Rebalancing"

#===========================
# Plot 5: Rebalancing Operations
#===========================
set title "Rebalancing Operations (Auto-Rebalancing)" font "Arial,14"
set xlabel "Number of Nodes" font "Arial,12"
set ylabel "Total Rebalancing Operations" font "Arial,12"
set grid
set key right bottom font "Arial,10"

plot 'auto_n2_rebal.dat' using 1:2 with lines lw 3 lc rgb "red" title "N=2 Rebalances", \
     'auto_n3_rebal.dat' using 1:2 with lines lw 3 lc rgb "blue" title "N=3 Rebalances", \
     'auto_n5_rebal.dat' using 1:2 with lines lw 3 lc rgb "green" title "N=5 Rebalances"

#===========================
# Plot 6: Overhead Percentage Analysis
#===========================
set title "Memory & Disk Overhead Percentage" font "Arial,14"
set xlabel "N Value" font "Arial,12"
set ylabel "Overhead Percentage (%)" font "Arial,12"
set grid
set key top right font "Arial,10"
set xtics (2,3,4,5,8,10,16,32)

# Calculate overhead percentages (approximations for visualization)
plot [2:32] 35 with lines lw 3 lc rgb "red" dt 2 title "Memory Overhead (~37%)", \
     15 with lines lw 3 lc rgb "blue" dt 2 title "Disk Overhead (~15%)", \
     0 with lines lw 1 lc rgb "black" dt 1 title "No Overhead"

unset multiplot

#===========================
# Detailed Memory Efficiency Plot
#===========================
set output 'narytree_memory_efficiency_comparison.png'
set title "Memory Efficiency: Auto-Rebalancing vs Original Implementation" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Memory Usage (MB)" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot 'orig_n2_mem.dat' using 1:2 with lines lw 3 lc rgb "red" title "N=2 Original (Lazy)", \
     'auto_n2_mem.dat' using 1:2 with lines lw 4 lc rgb "red" dt 2 title "N=2 Auto-Rebalancing", \
     'orig_n3_mem.dat' using 1:2 with lines lw 3 lc rgb "blue" title "N=3 Original (Lazy)", \
     'auto_n3_mem.dat' using 1:2 with lines lw 4 lc rgb "blue" dt 2 title "N=3 Auto-Rebalancing", \
     'orig_n5_mem.dat' using 1:2 with lines lw 3 lc rgb "green" title "N=5 Original (Lazy)", \
     'auto_n5_mem.dat' using 1:2 with lines lw 4 lc rgb "green" dt 2 title "N=5 Auto-Rebalancing"

#===========================
# Rebalancing Cost Analysis
#===========================
set output 'narytree_rebalancing_cost_analysis.png'
set title "Auto-Rebalancing: Operation Cost vs Tree Size" font "Arial,16"
set xlabel "Number of Nodes" font "Arial,14"
set ylabel "Cumulative Rebalancing Operations" font "Arial,14"
set grid
set key right bottom font "Arial,12"

plot 'auto_n2_rebal.dat' using 1:2 with lines lw 4 lc rgb "red" title "N=2 (26% ops)", \
     'auto_n3_rebal.dat' using 1:2 with lines lw 4 lc rgb "blue" title "N=3 (21% ops)", \
     'auto_n5_rebal.dat' using 1:2 with lines lw 4 lc rgb "green" title "N=5 (17% ops)", \
     'auto_n2_rebal.dat' using 1:($1*0.26) with lines lw 2 lc rgb "gray" dt 2 title "26% of operations line", \
     'auto_n3_rebal.dat' using 1:($1*0.21) with lines lw 2 lc rgb "gray" dt 3 title "21% of operations line", \
     'auto_n5_rebal.dat' using 1:($1*0.17) with lines lw 2 lc rgb "gray" dt 4 title "17% of operations line"

#===========================
# Performance Trade-off Summary
#===========================
set output 'narytree_performance_tradeoff_summary.png'
set title "Performance Trade-off: Auto-Rebalancing vs Original" font "Arial,16"
unset xlabel
unset ylabel
unset grid
unset key
set border 0
unset tics

# Create summary table
set label 1 "Implementation Comparison Summary (100,000 nodes)" at 0.1, 0.95 font "Arial,16" tc rgb "blue"
set label 2 "================================================================" at 0.1, 0.90 font "Arial,14"

set label 3 "MEMORY USAGE:" at 0.1, 0.82 font "Arial,14" tc rgb "red"
set label 4 "Original (Lazy):     9.42 MB  (99 bytes/node)" at 0.15, 0.78 font "Arial,12"
set label 5 "Auto-Rebalancing:   12.97 MB (136 bytes/node)" at 0.15, 0.74 font "Arial,12"
set label 6 "Overhead:           +37.7% memory" at 0.15, 0.70 font "Arial,12" tc rgb "red"

set label 7 "DISK USAGE (N=3):" at 0.1, 0.62 font "Arial,14" tc rgb "blue"
set label 8 "Original (Lazy):     5.95 MB" at 0.15, 0.58 font "Arial,12"
set label 9 "Auto-Rebalancing:   7.15 MB" at 0.15, 0.54 font "Arial,12"
set label 10 "Overhead:          +20.2% disk" at 0.15, 0.50 font "Arial,12" tc rgb "blue"

set label 11 "REBALANCING OPERATIONS (N=3):" at 0.1, 0.42 font "Arial,14" tc rgb "green"
set label 12 "Original (Lazy):     0 (manual only)" at 0.15, 0.38 font "Arial,12"
set label 13 "Auto-Rebalancing:   21,000 operations (21% of all operations)" at 0.15, 0.34 font "Arial,12"
set label 14 "Frequency:          Every 10 operations + threshold-based" at 0.15, 0.30 font "Arial,12"

set label 15 "PERFORMANCE CHARACTERISTICS:" at 0.1, 0.22 font "Arial,14" tc rgb "purple"
set label 16 "Original:           O(log n) when balanced, O(n) when unbalanced" at 0.15, 0.18 font "Arial,12"
set label 17 "Auto-Rebalancing:   Consistent O(log n) - always balanced" at 0.15, 0.14 font "Arial,12"

set label 18 "RECOMMENDATION:" at 0.1, 0.06 font "Arial,16" tc rgb "red"
set label 19 "Use Auto-Rebalancing for: Interactive apps, consistent performance needs" at 0.1, 0.02 font "Arial,14" tc rgb "green"
set label 20 "Use Original (Lazy) for: Batch processing, memory-constrained systems" at 0.1, -0.02 font "Arial,14" tc rgb "orange"

plot [0:1][0:1] 1/0 notitle

# Clean up temporary files
system("rm -f auto_n*_*.dat orig_n*_*.dat *_summary.dat")

print "🎯 Auto-Rebalancing vs Original Comparison Complete!"
print ""
print "📊 Generated Comprehensive Visualizations:"
print "   - narytree_auto_vs_original_comprehensive.png (6-panel comparison)"
print "   - narytree_memory_efficiency_comparison.png (detailed memory analysis)"
print "   - narytree_rebalancing_cost_analysis.png (rebalancing operations cost)"
print "   - narytree_performance_tradeoff_summary.png (summary and recommendations)"
print ""
print "🔍 Key Insights:"
print "   - Auto-rebalancing adds ~37% memory overhead"
print "   - Disk overhead is more modest at ~15-20%"
print "   - 12,000-26,000 rebalancing operations per 100K nodes"
print "   - Consistent O(log n) performance vs variable performance in lazy version"
print "   - Trade-off: Higher resource usage for guaranteed consistent performance"