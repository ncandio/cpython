set terminal png size 1200,900 font "Arial,12"
set output 'linux_btree_vs_narytree_final_comparison.png'

set multiplot layout 2,2 title "Linux B-tree vs N-ary Tree: Intel i5-8350U Performance Comparison"

# Memory per entry comparison
set logscale x
set grid
set xlabel 'Number of Entries'
set ylabel 'Memory per Entry (bytes)'
set title 'Memory Efficiency: B-tree vs N-ary Tree'
set key top right

plot 'linux_btree_vs_narytree_20250828_161015.csv' skip 1 using 1:3 with linespoints linewidth 3 pointsize 2 title 'Linux B-tree (19-35 bytes)', \
     'linux_btree_vs_narytree_20250828_161015.csv' skip 1 using 1:7 with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree (57 bytes)'

# Total memory usage comparison  
set ylabel 'Total Memory Usage (MB)'
set title 'Total Memory Requirements'

plot 'linux_btree_vs_narytree_20250828_161015.csv' skip 1 using 1:($2/1048576) with linespoints linewidth 3 pointsize 2 title 'Linux B-tree', \
     'linux_btree_vs_narytree_20250828_161015.csv' skip 1 using 1:($6/1048576) with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree'

# Memory efficiency ratio
unset logscale x
set xlabel 'Number of Entries'
set ylabel 'Efficiency Ratio (B-tree/N-ary)'
set title 'Memory Efficiency Ratio'
set yrange [0:1.2]

plot 'linux_btree_vs_narytree_20250828_161015.csv' skip 1 using 1:10 with linespoints linewidth 3 pointsize 2 title 'Memory Efficiency Ratio', \
     1.0 with lines linewidth 2 linetype 0 title 'Break-even (1.0)'

# System memory usage percentage (for 8GB system)
set logscale x
set ylabel 'Memory Usage (% of 8GB RAM)'
set title 'System Memory Usage (Intel i5 8GB RAM)'
set yrange [0:5]

plot 'linux_btree_vs_narytree_20250828_161015.csv' skip 1 using 1:(($2/(8*1024*1024*1024))*100) with linespoints linewidth 3 pointsize 2 title 'Linux B-tree', \
     'linux_btree_vs_narytree_20250828_161015.csv' skip 1 using 1:(($6/(8*1024*1024*1024))*100) with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree'

unset multiplot