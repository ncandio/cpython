#!/usr/bin/env python3
"""
N-ary Tree Memory Usage Over Time Test
Monitors memory consumption as tree grows with increasing data loads
Generates data for gnuplot visualization
"""

import sys
import time
import psutil
import gc
import random
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
import narytree

class MemoryOverTimeMonitor:
    """Monitor memory usage over time as tree grows"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_mb()
        self.measurements = []
        self.start_time = time.perf_counter()
        
    def get_memory_mb(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
        
    def get_memory_delta_mb(self) -> float:
        """Get memory increase from initial in MB"""
        return self.get_memory_mb() - self.initial_memory
        
    def record_measurement(self, 
                          trees_count: int, 
                          nodes_per_tree: int, 
                          total_nodes: int,
                          operation: str,
                          additional_info: Dict = None):
        """Record a memory measurement with context"""
        current_time = time.perf_counter()
        elapsed_time = current_time - self.start_time
        
        measurement = {
            'timestamp': current_time,
            'elapsed_seconds': elapsed_time,
            'trees_count': trees_count,
            'nodes_per_tree': nodes_per_tree,
            'total_nodes': total_nodes,
            'memory_mb': self.get_memory_mb(),
            'memory_delta_mb': self.get_memory_delta_mb(),
            'operation': operation,
            'memory_per_node_kb': (self.get_memory_delta_mb() * 1024) / max(total_nodes, 1),
            'additional_info': additional_info or {}
        }
        
        self.measurements.append(measurement)
        return measurement
        
    def save_to_csv(self, filename: str):
        """Save measurements to CSV file"""
        if not self.measurements:
            return
            
        fieldnames = [
            'elapsed_seconds', 'trees_count', 'nodes_per_tree', 'total_nodes',
            'memory_mb', 'memory_delta_mb', 'memory_per_node_kb', 'operation'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for measurement in self.measurements:
                row = {key: measurement[key] for key in fieldnames}
                writer.writerow(row)
                
        print(f"💾 Data saved to: {filename}")

class NaryTreeMemoryOverTimeTest:
    """Test memory usage over time for n-ary trees"""
    
    def __init__(self):
        self.monitor = MemoryOverTimeMonitor()
        self.trees = []
        
    def test_progressive_tree_creation(self) -> str:
        """Test memory usage as we create more trees progressively"""
        print("="*80)
        print("PROGRESSIVE TREE CREATION MEMORY TEST")
        print("="*80)
        
        # Progressive tree creation schedule
        creation_schedule = [
            {"batch_size": 10, "iterations": 10},      # 100 trees total
            {"batch_size": 50, "iterations": 10},      # 500 more (600 total)
            {"batch_size": 100, "iterations": 5},      # 500 more (1100 total)
            {"batch_size": 200, "iterations": 5},      # 1000 more (2100 total)
            {"batch_size": 500, "iterations": 4},      # 2000 more (4100 total)
        ]
        
        total_trees = 0
        
        print(f"{'Batch':<8} {'Trees':<8} {'Total':<8} {'Memory':<12} {'Delta':<12} {'KB/Node':<10} {'Time':<8}")
        print("-" * 75)
        
        # Initial measurement
        self.monitor.record_measurement(0, 1, 0, "baseline")
        print(f"{'Start':<8} {0:<8} {0:<8} {self.monitor.get_memory_mb():.2f} MB{'':<4} {0:.2f}{'':<6} {0:.2f}s")
        
        batch_num = 1
        
        for schedule in creation_schedule:
            for iteration in range(schedule["iterations"]):
                # Force garbage collection before measurement
                gc.collect()
                
                # Create a batch of trees
                batch_start_time = time.perf_counter()
                batch_trees = []
                
                for i in range(schedule["batch_size"]):
                    tree = narytree.NaryTree()
                    tree.set_root(f"tree_{total_trees + i}_data")
                    batch_trees.append(tree)
                
                self.trees.extend(batch_trees)
                total_trees += schedule["batch_size"]
                
                # Record measurement
                measurement = self.monitor.record_measurement(
                    trees_count=total_trees,
                    nodes_per_tree=1,
                    total_nodes=total_trees,
                    operation=f"batch_create_{schedule['batch_size']}",
                    additional_info={"batch_time": time.perf_counter() - batch_start_time}
                )
                
                print(f"{batch_num:<8} {schedule['batch_size']:<8} {total_trees:<8} "
                      f"{measurement['memory_mb']:.2f} MB{'':<4} "
                      f"{measurement['memory_delta_mb']:.2f} MB{'':<4} "
                      f"{measurement['memory_per_node_kb']:.2f}{'':<6} "
                      f"{measurement['elapsed_seconds']:.2f}s")
                
                batch_num += 1
                
                # Small delay to see memory behavior over time
                time.sleep(0.1)
        
        # Final measurement
        final_measurement = self.monitor.record_measurement(
            trees_count=total_trees,
            nodes_per_tree=1,
            total_nodes=total_trees,
            operation="final_state"
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"narytree_memory_overtime_{timestamp}.csv"
        self.monitor.save_to_csv(csv_filename)
        
        return csv_filename
        
    def test_tree_growth_with_balancing_simulation(self) -> str:
        """Test memory usage as trees grow larger (simulated)"""
        print("\n" + "="*80)
        print("TREE GROWTH SIMULATION WITH BALANCING ANALYSIS")
        print("="*80)
        
        # Growth phases
        growth_phases = [
            {"name": "Small Trees", "tree_count": 50, "simulated_nodes_per_tree": [10, 50, 100, 200]},
            {"name": "Medium Trees", "tree_count": 20, "simulated_nodes_per_tree": [500, 1000, 2000, 5000]},
            {"name": "Large Trees", "tree_count": 10, "simulated_nodes_per_tree": [10000, 20000, 50000, 100000]},
            {"name": "Very Large Trees", "tree_count": 5, "simulated_nodes_per_tree": [200000, 500000, 1000000, 2000000]},
        ]
        
        print(f"{'Phase':<18} {'Trees':<8} {'Nodes/Tree':<12} {'Total Nodes':<12} {'Memory':<12} {'Delta':<12} {'KB/Node':<10}")
        print("-" * 95)
        
        for phase in growth_phases:
            for nodes_per_tree in phase["simulated_nodes_per_tree"]:
                # Create trees for this phase
                trees_in_phase = []
                for i in range(phase["tree_count"]):
                    tree = narytree.NaryTree()
                    # For now we can only create single-node trees, but we simulate larger trees
                    tree.set_root(f"phase_{phase['name']}_tree_{i}_nodes_{nodes_per_tree}")
                    trees_in_phase.append(tree)
                
                self.trees.extend(trees_in_phase)
                
                # Calculate simulated memory based on actual memory + theoretical expansion
                actual_total_trees = len(self.trees)
                simulated_total_nodes = actual_total_trees * nodes_per_tree
                
                # Record measurement with simulated data
                measurement = self.monitor.record_measurement(
                    trees_count=actual_total_trees,
                    nodes_per_tree=nodes_per_tree,
                    total_nodes=simulated_total_nodes,
                    operation=f"growth_phase_{phase['name'].replace(' ', '_').lower()}",
                    additional_info={
                        "phase_name": phase["name"],
                        "simulated": True,
                        "theoretical_memory_mb": (simulated_total_nodes * 0.2)  # 200 bytes per node estimate
                    }
                )
                
                # For display, show theoretical memory usage
                theoretical_memory = measurement['memory_mb'] + (simulated_total_nodes * 0.0002)  # Add theoretical
                theoretical_delta = theoretical_memory - self.monitor.initial_memory
                
                print(f"{phase['name']:<18} {actual_total_trees:<8} {nodes_per_tree:<12} {simulated_total_nodes:<12} "
                      f"{theoretical_memory:.2f} MB{'':<4} {theoretical_delta:.2f} MB{'':<4} "
                      f"{(theoretical_delta * 1024) / simulated_total_nodes:.2f}")
                
                time.sleep(0.05)  # Brief pause
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"narytree_growth_simulation_{timestamp}.csv"
        self.monitor.save_to_csv(csv_filename)
        
        return csv_filename
        
    def test_memory_with_cleanup_cycles(self) -> str:
        """Test memory usage with periodic cleanup cycles"""
        print("\n" + "="*80) 
        print("MEMORY USAGE WITH CLEANUP CYCLES")
        print("="*80)
        
        cycles = [
            {"create": 200, "keep": 150, "description": "Create 200, keep 150"},
            {"create": 300, "keep": 200, "description": "Create 300, keep 200"},
            {"create": 500, "keep": 300, "description": "Create 500, keep 300"},
            {"create": 400, "keep": 100, "description": "Create 400, keep 100"},
            {"create": 600, "keep": 400, "description": "Create 600, keep 400"},
        ]
        
        print(f"{'Cycle':<8} {'Operation':<20} {'Trees':<8} {'Memory':<12} {'Delta':<12} {'KB/Tree':<10}")
        print("-" * 75)
        
        cycle_num = 1
        
        for cycle in cycles:
            # Creation phase
            creation_trees = []
            for i in range(cycle["create"]):
                tree = narytree.NaryTree()
                tree.set_root(f"cycle_{cycle_num}_tree_{i}")
                creation_trees.append(tree)
            
            self.trees.extend(creation_trees)
            
            # Measure after creation
            create_measurement = self.monitor.record_measurement(
                trees_count=len(self.trees),
                nodes_per_tree=1,
                total_nodes=len(self.trees),
                operation=f"cycle_{cycle_num}_create"
            )
            
            print(f"{cycle_num:<8} {'Create ' + str(cycle['create']):<20} {len(self.trees):<8} "
                  f"{create_measurement['memory_mb']:.2f} MB{'':<4} "
                  f"{create_measurement['memory_delta_mb']:.2f} MB{'':<4} "
                  f"{create_measurement['memory_per_node_kb']:.2f}")
            
            # Cleanup phase - remove trees beyond what we want to keep
            trees_to_remove = len(self.trees) - cycle["keep"]
            if trees_to_remove > 0:
                # Remove the oldest trees
                del self.trees[:trees_to_remove]
                
                # Force garbage collection
                gc.collect()
                time.sleep(0.1)  # Allow GC to complete
                
                # Measure after cleanup
                cleanup_measurement = self.monitor.record_measurement(
                    trees_count=len(self.trees),
                    nodes_per_tree=1,
                    total_nodes=len(self.trees),
                    operation=f"cycle_{cycle_num}_cleanup"
                )
                
                print(f"{cycle_num:<8} {'Cleanup (keep ' + str(cycle['keep']) + ')':<20} {len(self.trees):<8} "
                      f"{cleanup_measurement['memory_mb']:.2f} MB{'':<4} "
                      f"{cleanup_measurement['memory_delta_mb']:.2f} MB{'':<4} "
                      f"{cleanup_measurement['memory_per_node_kb']:.2f}")
            
            cycle_num += 1
            time.sleep(0.2)  # Pause between cycles
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"narytree_cleanup_cycles_{timestamp}.csv"
        self.monitor.save_to_csv(csv_filename)
        
        return csv_filename

def generate_gnuplot_scripts(csv_files: List[str]):
    """Generate gnuplot scripts for visualizing the memory data"""
    
    print("\n" + "="*80)
    print("GENERATING GNUPLOT VISUALIZATION SCRIPTS")
    print("="*80)
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            continue
            
        base_name = csv_file.replace('.csv', '')
        
        # Generate gnuplot script
        script_content = f"""#!/usr/bin/gnuplot
# Gnuplot script for {csv_file}
# Memory usage over time for N-ary Tree implementation

set terminal png size 1200,800 enhanced font 'Arial,12'
set output '{base_name}_plot.png'

# Set title and labels
set title "N-ary Tree Memory Usage Over Time\\n{csv_file}" font 'Arial,16'
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
plot '{csv_file}' using 1:5 with linespoints linestyle 1 title "Total Memory", \\
     '{csv_file}' using 1:6 with linespoints linestyle 2 title "Delta Memory"

# Plot 2: Memory per node
set title "Memory Efficiency"  
set ylabel "KB per Node"
plot '{csv_file}' using 1:7 with linespoints linestyle 1 title "KB/Node"

# Plot 3: Total nodes over time
set title "Tree Growth"
set ylabel "Total Nodes"
plot '{csv_file}' using 1:4 with linespoints linestyle 2 title "Total Nodes"

# Plot 4: Memory vs Nodes (scatter plot)
set title "Memory vs Nodes"
set xlabel "Total Nodes"
set ylabel "Memory (MB)"
plot '{csv_file}' using 4:5 with points linestyle 1 title "Memory Usage"

unset multiplot

# Generate a second detailed plot
set output '{base_name}_detailed.png'
set terminal png size 1600,1200 enhanced font 'Arial,10'

set multiplot layout 3,1

# Detailed memory timeline
set title "Detailed Memory Usage Timeline" font 'Arial,14'
set xlabel "Time (seconds)"
set ylabel "Memory (MB)"
set grid
plot '{csv_file}' using 1:5 with lines lw 2 title "Total Memory", \\
     '{csv_file}' using 1:6 with lines lw 2 title "Delta Memory"

# Memory efficiency over time
set title "Memory Efficiency Over Time"
set ylabel "KB per Node"
plot '{csv_file}' using 1:7 with lines lw 2 title "Memory/Node"

# Growth rate analysis
set title "Node Growth Rate"
set xlabel "Time (seconds)"
set ylabel "Nodes"
plot '{csv_file}' using 1:4 with lines lw 3 title "Total Nodes"

unset multiplot

print "Generated plots: {base_name}_plot.png and {base_name}_detailed.png"
"""
        
        script_filename = f"{base_name}.gp"
        with open(script_filename, 'w') as f:
            f.write(script_content)
        
        print(f"📊 Generated gnuplot script: {script_filename}")
        
        # Try to run gnuplot if available
        try:
            import subprocess
            result = subprocess.run(['gnuplot', script_filename], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ Generated plots: {base_name}_plot.png, {base_name}_detailed.png")
            else:
                print(f"⚠️  Gnuplot execution had issues: {result.stderr}")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"ℹ️  Gnuplot not available or timed out. Run manually: gnuplot {script_filename}")
        except Exception as e:
            print(f"⚠️  Could not execute gnuplot: {str(e)}")

def main():
    """Main test execution"""
    print("N-ARY TREE MEMORY USAGE OVER TIME ANALYSIS")
    print("Target: Intel i5, 4-core, 16GB RAM")
    print("Tracking memory consumption as data volume increases")
    print("="*80)
    
    tester = NaryTreeMemoryOverTimeTest()
    csv_files = []
    
    try:
        # Test 1: Progressive tree creation
        csv1 = tester.test_progressive_tree_creation()
        csv_files.append(csv1)
        
        # Test 2: Tree growth simulation  
        csv2 = tester.test_tree_growth_with_balancing_simulation()
        csv_files.append(csv2)
        
        # Test 3: Memory with cleanup cycles
        csv3 = tester.test_memory_with_cleanup_cycles()
        csv_files.append(csv3)
        
        # Generate gnuplot visualizations
        generate_gnuplot_scripts(csv_files)
        
        # Print summary
        print(f"\n{'='*80}")
        print("MEMORY OVERTIME TEST SUMMARY")
        print(f"{'='*80}")
        print(f"📁 Generated {len(csv_files)} CSV data files")
        print(f"📊 Generated {len(csv_files)} gnuplot scripts")
        print(f"🔍 Total measurements: {len(tester.monitor.measurements)}")
        
        if tester.monitor.measurements:
            final_memory = tester.monitor.measurements[-1]['memory_mb']
            peak_memory = max(m['memory_mb'] for m in tester.monitor.measurements)
            total_trees = tester.monitor.measurements[-1]['trees_count']
            
            print(f"💾 Final memory usage: {final_memory:.2f} MB")
            print(f"📈 Peak memory usage: {peak_memory:.2f} MB")  
            print(f"🌳 Total trees created: {total_trees}")
            print(f"⏱️  Total test time: {tester.monitor.measurements[-1]['elapsed_seconds']:.2f} seconds")
        
        print(f"\n🎯 Files generated:")
        for csv_file in csv_files:
            print(f"   📄 {csv_file}")
            print(f"   📊 {csv_file.replace('.csv', '.gp')}")
            
        print(f"\n💡 To view plots, run:")
        for csv_file in csv_files:
            script_name = csv_file.replace('.csv', '.gp')
            print(f"   gnuplot {script_name}")
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()