#!/usr/bin/gnuplot
set terminal png 
set output "test.png"
set datafile separator ","
plot "octree_subdivision_trigger_20250824_012228.csv" using 1:2 skip 1 with linespoints title "Memory"