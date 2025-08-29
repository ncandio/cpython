# N-ary Tree Analysis - Compatible Version
set terminal pngcairo enhanced font "Arial,14" size 1600,900

# Extract specific data sets
system("awk -F, 'NR>1 && $1==2 {print $2, $3}' narytree_memory_disk_data_20250828_102933.csv > n2_mem.dat")
system("awk -F, 'NR>1 && $1==3 {print $2, $3}' narytree_memory_disk_data_20250828_102933.csv > n3_mem.dat") 
system("awk -F, 'NR>1 && $1==5 {print $2, $3}' narytree_memory_disk_data_20250828_102933.csv > n5_mem.dat")
system("awk -F, 'NR>1 && $1==8 {print $2, $3}' narytree_memory_disk_data_20250828_102933.csv > n8_mem.dat")
system("awk -F, 'NR>1 && $1==16 {print $2, $3}' narytree_memory_disk_data_20250828_102933.csv > n16_mem.dat")
system("awk -F, 'NR>1 && $1==32 {print $2, $3}' narytree_memory_disk_data_20250828_102933.csv > n32_mem.dat")

system("awk -F, 'NR>1 && $1==2 {print $2, $4}' narytree_memory_disk_data_20250828_102933.csv > n2_dsk.dat")
system("awk -F, 'NR>1 && $1==3 {print $2, $4}' narytree_memory_disk_data_20250828_102933.csv > n3_dsk.dat")
system("awk -F, 'NR>1 && $1==5 {print $2, $4}' narytree_memory_disk_data_20250828_102933.csv > n5_dsk.dat")
system("awk -F, 'NR>1 && $1==8 {print $2, $4}' narytree_memory_disk_data_20250828_102933.csv > n8_dsk.dat")
system("awk -F, 'NR>1 && $1==16 {print $2, $4}' narytree_memory_disk_data_20250828_102933.csv > n16_dsk.dat")
system("awk -F, 'NR>1 && $1==32 {print $2, $4}' narytree_memory_disk_data_20250828_102933.csv > n32_dsk.dat")

system("awk -F, 'NR>1 && $2==100000 {print $1, $3, $4, $7}' narytree_memory_disk_data_20250828_102933.csv > summary.dat")

# Memory Usage Plot
set output 'narytree_memory_analysis.png'
set title "N-ary Tree Memory Usage (64-bit Architecture + Self-Balancing)"
set xlabel "Number of Nodes"
set ylabel "Memory Usage (MB)"
set grid
set key right bottom

plot 'n2_mem.dat' using 1:2 with lines lw 3 lc rgb "red" title "N=2", \
     'n3_mem.dat' using 1:2 with lines lw 3 lc rgb "blue" title "N=3", \
     'n5_mem.dat' using 1:2 with lines lw 3 lc rgb "green" title "N=5", \
     'n8_mem.dat' using 1:2 with lines lw 3 lc rgb "purple" title "N=8", \
     'n16_mem.dat' using 1:2 with lines lw 3 lc rgb "orange" title "N=16", \
     'n32_mem.dat' using 1:2 with lines lw 3 lc rgb "brown" title "N=32"

# Disk Usage Plot
set output 'narytree_disk_analysis.png'
set title "N-ary Tree Disk Usage (64-bit Architecture + Serialization)"
set xlabel "Number of Nodes"
set ylabel "Disk Usage (MB)"
set grid
set key right bottom

plot 'n2_dsk.dat' using 1:2 with lines lw 3 lc rgb "red" title "N=2", \
     'n3_dsk.dat' using 1:2 with lines lw 3 lc rgb "blue" title "N=3", \
     'n5_dsk.dat' using 1:2 with lines lw 3 lc rgb "green" title "N=5", \
     'n8_dsk.dat' using 1:2 with lines lw 3 lc rgb "purple" title "N=8", \
     'n16_dsk.dat' using 1:2 with lines lw 3 lc rgb "orange" title "N=16", \
     'n32_dsk.dat' using 1:2 with lines lw 3 lc rgb "brown" title "N=32"

# Comparison at 100K nodes
set output 'narytree_comparison_100k.png'
set title "Memory vs Disk Usage at 100,000 Nodes"
set xlabel "N Value (Branching Factor)"
set ylabel "Usage (MB)"
set grid
set key top left
set xtics (2,3,4,5,8,10,16,32)

plot 'summary.dat' using 1:2 with linespoints lw 3 pt 7 ps 1.5 lc rgb "blue" title "Memory", \
     'summary.dat' using 1:3 with linespoints lw 3 pt 5 ps 1.5 lc rgb "red" title "Disk"

# Memory/Disk Ratio
set output 'narytree_ratio_analysis.png'
set title "Memory/Disk Ratio Analysis"
set xlabel "N Value"
set ylabel "Memory/Disk Ratio"
set grid
set key top right

plot 'summary.dat' using 1:4 with linespoints lw 3 pt 9 ps 1.5 lc rgb "green" title "Ratio", \
     1 with lines lw 2 dt 2 lc rgb "black" title "Equal Usage"

# Combined efficiency plot
set output 'narytree_efficiency_combined.png'
set title "N-ary Tree Efficiency Analysis (Memory + Disk)"
set xlabel "Number of Nodes"
set ylabel "Usage (MB)"
set grid
set key right bottom

plot 'n2_mem.dat' using 1:2 with lines lw 2 lc rgb "red" dt 1 title "N=2 Memory", \
     'n2_dsk.dat' using 1:2 with lines lw 2 lc rgb "red" dt 2 title "N=2 Disk", \
     'n3_mem.dat' using 1:2 with lines lw 2 lc rgb "blue" dt 1 title "N=3 Memory", \
     'n3_dsk.dat' using 1:2 with lines lw 2 lc rgb "blue" dt 2 title "N=3 Disk", \
     'n5_mem.dat' using 1:2 with lines lw 2 lc rgb "green" dt 1 title "N=5 Memory", \
     'n5_dsk.dat' using 1:2 with lines lw 2 lc rgb "green" dt 2 title "N=5 Disk"

# Clean up
system("rm -f n*_mem.dat n*_dsk.dat summary.dat")

print "Analysis complete! Generated 5 visualization files:"
print "- narytree_memory_analysis.png"
print "- narytree_disk_analysis.png" 
print "- narytree_comparison_100k.png"
print "- narytree_ratio_analysis.png"
print "- narytree_efficiency_combined.png"