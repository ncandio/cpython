
set terminal png size 1000,700 font "Arial,12"
set output 'intel_i5_final_comparison.png'

set grid
set xlabel 'Number of Entries'
set ylabel 'Memory per Entry (bytes)'
set title 'Linux B-tree vs N-ary Tree: Intel i5-8350U Comparison'
set logscale x
set key top right

plot 'intel_i5_comparison_data.csv' skip 1 using 1:2 with linespoints linewidth 3 pointsize 2 title 'Linux B-tree (19-35 bytes)', \
     'intel_i5_comparison_data.csv' skip 1 using 1:3 with linespoints linewidth 3 pointsize 2 title 'Our N-ary Tree (57 bytes)'
