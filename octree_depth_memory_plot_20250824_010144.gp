# Gnuplot script for Octree Depth vs Memory Analysis
# Generated automatically from test data
# Data file: octree_depth_memory_analysis_20250824_010144.csv

set terminal pngcairo enhanced color size 1200,900 font 'Arial,12'
set output 'octree_depth_memory_analysis.png'

# Set up the plot
set title "Octree Depth vs Memory Usage Analysis" font 'Arial,16'
set xlabel "Tree Depth" font 'Arial,14'
set ylabel "Memory Usage (bytes)" font 'Arial,14'

# Configure grid and style
set grid xtics ytics mxtics mytics
set key top left
set logscale y

# Define colors and point styles for each strategy
set style line 1 lc rgb '#e41a1c' pt 7 ps 1.5  # Clustered - red circles
set style line 2 lc rgb '#377eb8' pt 5 ps 1.5  # Linear - blue squares
set style line 3 lc rgb '#4daf4a' pt 9 ps 1.5  # Controlled - green triangles
set style line 4 lc rgb '#984ea3' pt 11 ps 1.5 # Density - purple diamonds

# Plot data by strategy
plot 'octree_depth_memory_analysis_20250824_010144.csv' using ($5):($6) every ::1 title 'All Points' with points pt 6 ps 0.8 lc rgb 'gray', \
     '<(grep "Clustered" octree_depth_memory_analysis_20250824_010144.csv)' using 5:6 title 'Clustered Strategy' with points ls 1, \
     '<(grep "Linear" octree_depth_memory_analysis_20250824_010144.csv)' using 5:6 title 'Linear Strategy' with points ls 2, \
     '<(grep "Controlled" octree_depth_memory_analysis_20250824_010144.csv)' using 5:6 title 'Controlled Strategy' with points ls 3, \
     '<(grep "Density" octree_depth_memory_analysis_20250824_010144.csv)' using 5:6 title 'Density Strategy' with points ls 4

# Add trend line for clustered data (highest correlation)
f(x) = a*x + b
fit f(x) '<(grep "Clustered" octree_depth_memory_analysis_20250824_010144.csv)' using 5:(log($6)) via a, b
set samples 100
replot exp(f(x)) title sprintf('Clustered Trend: log(memory) = %.2fx + %.2f', a, b) with lines lw 2 lc rgb '#e41a1c' dt 2

# Create second plot: Memory per Point vs Depth
set output 'octree_memory_efficiency.png'
set title "Octree Memory Efficiency vs Depth" font 'Arial,16'
set ylabel "Memory per Point (bytes/point)" font 'Arial,14'
set nologscale y

plot 'octree_depth_memory_analysis_20250824_010144.csv' using ($5):($8) every ::1 title 'All Points' with points pt 6 ps 0.8 lc rgb 'gray', \
     '<(grep "Clustered" octree_depth_memory_analysis_20250824_010144.csv)' using 5:8 title 'Clustered Strategy' with points ls 1, \
     '<(grep "Linear" octree_depth_memory_analysis_20250824_010144.csv)' using 5:8 title 'Linear Strategy' with points ls 2, \
     '<(grep "Controlled" octree_depth_memory_analysis_20250824_010144.csv)' using 5:8 title 'Controlled Strategy' with points ls 3, \
     '<(grep "Density" octree_depth_memory_analysis_20250824_010144.csv)' using 5:8 title 'Density Strategy' with points ls 4

# Create third plot: 3D surface plot showing depth, points, and memory
set output 'octree_3d_analysis.png'
set title "3D Analysis: Depth, Points, Memory" font 'Arial,16'
set xlabel "Tree Depth" font 'Arial,14'
set ylabel "Number of Points" font 'Arial,14' 
set zlabel "Memory (bytes)" font 'Arial,14' rotate by 90

set dgrid3d 10,10
set hidden3d
set pm3d

splot 'octree_depth_memory_analysis_20250824_010144.csv' using 5:4:6 every ::1 title 'Memory Usage' with points pt 7 ps 1.5

# Create histogram of depth distribution
set output 'octree_depth_distribution.png'
set title "Distribution of Achieved Tree Depths" font 'Arial,16'
set xlabel "Tree Depth" font 'Arial,14'
set ylabel "Frequency" font 'Arial,14'

set style data histograms
set style histogram cluster gap 1
set style fill solid 0.7
set boxwidth 0.8

# Prepare data for histogram
set table 'depth_histogram.dat'
plot 'octree_depth_memory_analysis_20250824_010144.csv' using 5:(1.0) every ::1 smooth frequency
unset table

plot 'depth_histogram.dat' using 1:2 title 'Depth Distribution' lc rgb '#377eb8'

print ""
print "📊 Generated visualization files:"
print "  • octree_depth_memory_analysis.png - Main depth vs memory scatter plot"
print "  • octree_memory_efficiency.png - Memory efficiency analysis"
print "  • octree_3d_analysis.png - 3D surface plot"
print "  • octree_depth_distribution.png - Depth distribution histogram"
print ""
print "📋 Data Analysis Summary:"
print "📊 Statistical Analysis:"\nprint ""\nprint "Clustered Strategy:"\nprint "  Average Depth: 8.4"\nprint "  Maximum Depth: 14"\nprint "  Average Memory: 172,195 bytes"\nprint "  Maximum Memory: 349,488 bytes"\nprint ""\nprint "Linear Strategy:"\nprint "  Average Depth: 8.9"\nprint "  Maximum Depth: 14"\nprint "  Average Memory: 64,368 bytes"\nprint "  Maximum Memory: 100,656 bytes"\nprint ""\nprint "Controlled Strategy:"\nprint "  Average Depth: 1.5"\nprint "  Maximum Depth: 4"\nprint "  Average Memory: 17,712 bytes"\nprint "  Maximum Memory: 86,832 bytes"\nprint ""\nprint "Density Strategy:"\nprint "  Average Depth: 2.5"\nprint "  Maximum Depth: 4"\nprint "  Average Memory: 298,685 bytes"\nprint "  Maximum Memory: 1,762,992 bytes"\nprint ""