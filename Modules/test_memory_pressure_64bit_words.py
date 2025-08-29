#!/usr/bin/env python3
"""
Memory Pressure Test with 64-bit Processor Words
Tests memory limits by storing processor word-size data in n-ary trees
Pushes toward 16GB system limits while monitoring performance
"""

import sys
import time
import psutil
import gc
import random
import struct
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Generator
import narytree

class ProcessorWordGenerator:
    """Generate 64-bit processor words for testing"""
    
    def __init__(self):
        self.word_size_bits = 64
        self.word_size_bytes = 8
        self.max_word_value = 2**63 - 1  # Max signed 64-bit integer
        
    def generate_random_word(self) -> int:
        """Generate a random 64-bit word"""
        return random.randint(0, self.max_word_value)
        
    def generate_pattern_word(self, pattern_type: str, index: int) -> int:
        """Generate patterned 64-bit words for specific test scenarios"""
        if pattern_type == "sequential":
            return index % self.max_word_value
        elif pattern_type == "fibonacci":
            return self.fibonacci_64bit(index)
        elif pattern_type == "prime_like":
            return (index * 6364136223846793005 + 1442695040888963407) % self.max_word_value
        elif pattern_type == "bit_pattern":
            # Create interesting bit patterns
            return (0xAAAAAAAAAAAAAAAA if index % 2 else 0x5555555555555555) ^ (index << 8)
        else:
            return self.generate_random_word()
            
    def fibonacci_64bit(self, n: int) -> int:
        """Generate nth Fibonacci number modulo 64-bit max"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, (a + b) % self.max_word_value
        return b
        
    def word_to_bytes(self, word: int) -> bytes:
        """Convert 64-bit word to bytes"""
        return struct.pack('<Q', word)  # Little-endian unsigned 64-bit
        
    def estimate_word_memory_overhead(self) -> int:
        """Estimate Python object overhead for storing a 64-bit word"""
        # Python int object + tree node overhead
        return sys.getsizeof(self.max_word_value) + 200  # Estimated tree node overhead

class MemoryPressureMonitor:
    """Monitor memory pressure and system limits"""
    
    def __init__(self, target_memory_gb: float = 12.0):
        self.process = psutil.Process()
        self.target_memory_gb = target_memory_gb
        self.target_memory_bytes = target_memory_gb * 1024 * 1024 * 1024
        self.initial_memory = self.get_memory_bytes()
        self.measurements = []
        self.start_time = time.perf_counter()
        
        # System info
        self.total_system_memory = psutil.virtual_memory().total
        self.available_memory = psutil.virtual_memory().available
        
    def get_memory_bytes(self) -> int:
        """Get current memory usage in bytes"""
        return self.process.memory_info().rss
        
    def get_memory_gb(self) -> float:
        """Get current memory usage in GB"""
        return self.get_memory_bytes() / 1024 / 1024 / 1024
        
    def get_memory_delta_gb(self) -> float:
        """Get memory increase from initial in GB"""
        return (self.get_memory_bytes() - self.initial_memory) / 1024 / 1024 / 1024
        
    def get_available_memory_gb(self) -> float:
        """Get available system memory in GB"""
        return psutil.virtual_memory().available / 1024 / 1024 / 1024
        
    def is_approaching_limit(self, safety_margin_gb: float = 1.0) -> bool:
        """Check if we're approaching memory limits"""
        current_gb = self.get_memory_gb()
        available_gb = self.get_available_memory_gb()
        return (current_gb >= self.target_memory_gb - safety_margin_gb) or (available_gb < safety_margin_gb)
        
    def record_measurement(self, trees_count: int, words_per_tree: int, total_words: int, 
                          word_pattern: str, additional_info: Dict = None):
        """Record a memory measurement"""
        current_time = time.perf_counter()
        elapsed_time = current_time - self.start_time
        
        measurement = {
            'timestamp': current_time,
            'elapsed_seconds': elapsed_time,
            'trees_count': trees_count,
            'words_per_tree': words_per_tree,
            'total_words': total_words,
            'word_pattern': word_pattern,
            'memory_gb': self.get_memory_gb(),
            'memory_delta_gb': self.get_memory_delta_gb(),
            'available_memory_gb': self.get_available_memory_gb(),
            'memory_per_word_bytes': (self.get_memory_delta_gb() * 1024**3) / max(total_words, 1),
            'memory_pressure_percent': (self.get_memory_gb() / (self.total_system_memory / 1024**3)) * 100,
            'additional_info': additional_info or {}
        }
        
        self.measurements.append(measurement)
        return measurement
        
    def save_to_csv(self, filename: str):
        """Save measurements to CSV"""
        if not self.measurements:
            return
            
        fieldnames = [
            'elapsed_seconds', 'trees_count', 'words_per_tree', 'total_words',
            'word_pattern', 'memory_gb', 'memory_delta_gb', 'available_memory_gb',
            'memory_per_word_bytes', 'memory_pressure_percent'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for measurement in self.measurements:
                row = {key: measurement[key] for key in fieldnames}
                writer.writerow(row)

class MemoryPressureTest:
    """Memory pressure test with 64-bit words"""
    
    def __init__(self):
        self.word_generator = ProcessorWordGenerator()
        self.monitor = MemoryPressureMonitor()
        self.trees = []
        
    def test_progressive_word_loading(self) -> str:
        """Test progressive loading of 64-bit words into trees"""
        print("="*80)
        print("PROGRESSIVE 64-BIT WORD LOADING MEMORY PRESSURE TEST")
        print("="*80)
        
        print(f"Target system memory: {self.monitor.total_system_memory / 1024**3:.1f} GB")
        print(f"Available memory: {self.monitor.get_available_memory_gb():.1f} GB")
        print(f"Test memory target: {self.monitor.target_memory_gb:.1f} GB")
        print(f"64-bit word size: {self.word_generator.word_size_bytes} bytes")
        
        # Progressive loading schedule
        loading_phases = [
            {"name": "Small Words", "trees": 100, "words_per_tree": 1, "pattern": "sequential"},
            {"name": "Medium Words", "trees": 500, "words_per_tree": 1, "pattern": "random"},
            {"name": "Large Words", "trees": 1000, "words_per_tree": 1, "pattern": "fibonacci"},
            {"name": "Very Large Words", "trees": 2000, "words_per_tree": 1, "pattern": "bit_pattern"},
            {"name": "Massive Words", "trees": 5000, "words_per_tree": 1, "pattern": "prime_like"},
            {"name": "Ultra Scale", "trees": 10000, "words_per_tree": 1, "pattern": "random"},
            {"name": "Memory Pressure", "trees": 20000, "words_per_tree": 1, "pattern": "sequential"},
        ]
        
        print(f"\n{'Phase':<20} {'Trees':<8} {'Total Words':<12} {'Memory':<12} {'Delta':<12} {'Available':<12} {'Bytes/Word':<12} {'Pressure':<10}")
        print("-" * 110)
        
        # Initial measurement
        self.monitor.record_measurement(0, 0, 0, "baseline")
        
        total_trees = 0
        total_words = 0
        
        for phase in loading_phases:
            if self.monitor.is_approaching_limit():
                print(f"⚠️  Approaching memory limit, stopping before {phase['name']}")
                break
                
            phase_start_time = time.perf_counter()
            
            # Create trees with 64-bit words for this phase
            phase_trees = []
            for i in range(phase["trees"]):
                tree = narytree.NaryTree()
                
                # Generate 64-bit word based on pattern
                word = self.word_generator.generate_pattern_word(phase["pattern"], total_words + i)
                
                # Store the word in the tree
                tree.set_root(word)
                phase_trees.append(tree)
                
                # Safety check every 1000 trees
                if i > 0 and i % 1000 == 0:
                    if self.monitor.is_approaching_limit():
                        print(f"    ⚠️  Memory limit reached at {i} trees in {phase['name']}")
                        phase_trees = phase_trees[:i]
                        break
            
            self.trees.extend(phase_trees)
            total_trees += len(phase_trees)
            total_words += len(phase_trees) * phase["words_per_tree"]
            
            # Record measurement
            measurement = self.monitor.record_measurement(
                trees_count=total_trees,
                words_per_tree=phase["words_per_tree"],
                total_words=total_words,
                word_pattern=phase["pattern"],
                additional_info={
                    "phase_name": phase["name"],
                    "phase_duration": time.perf_counter() - phase_start_time,
                    "trees_in_phase": len(phase_trees)
                }
            )
            
            print(f"{phase['name']:<20} {total_trees:<8} {total_words:<12} "
                  f"{measurement['memory_gb']:.2f} GB{'':<4} "
                  f"{measurement['memory_delta_gb']:.2f} GB{'':<4} "
                  f"{measurement['available_memory_gb']:.2f} GB{'':<4} "
                  f"{measurement['memory_per_word_bytes']:.0f}{'':<8} "
                  f"{measurement['memory_pressure_percent']:.1f}%")
            
            # Force garbage collection between phases
            gc.collect()
            time.sleep(0.1)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"memory_pressure_64bit_words_{timestamp}.csv"
        self.monitor.save_to_csv(csv_filename)
        
        return csv_filename
        
    def test_memory_limit_approach(self) -> str:
        """Test approaching actual memory limits"""
        print("\n" + "="*80)
        print("MEMORY LIMIT APPROACH TEST")
        print("="*80)
        
        print("Attempting to approach system memory limits safely...")
        
        # Calculate how many trees we need for significant memory usage
        estimated_bytes_per_tree = self.word_generator.estimate_word_memory_overhead()
        target_memory_bytes = self.monitor.target_memory_bytes * 0.9  # 90% of target
        estimated_trees_needed = int(target_memory_bytes / estimated_bytes_per_tree)
        
        print(f"Estimated bytes per tree: {estimated_bytes_per_tree}")
        print(f"Target memory: {target_memory_bytes / 1024**3:.1f} GB")
        print(f"Estimated trees needed: {estimated_trees_needed:,}")
        
        # Create trees in large batches
        batch_size = 10000
        batch_count = 0
        
        print(f"\n{'Batch':<8} {'Trees':<12} {'Memory':<12} {'Delta':<12} {'Available':<12} {'Pressure':<10}")
        print("-" * 75)
        
        while not self.monitor.is_approaching_limit() and len(self.trees) < estimated_trees_needed:
            batch_start_time = time.perf_counter()
            
            # Create batch of trees
            batch_trees = []
            for i in range(min(batch_size, estimated_trees_needed - len(self.trees))):
                tree = narytree.NaryTree()
                
                # Use different word patterns for variety
                pattern_types = ["sequential", "random", "fibonacci", "bit_pattern", "prime_like"]
                pattern = pattern_types[batch_count % len(pattern_types)]
                word = self.word_generator.generate_pattern_word(pattern, len(self.trees) + i)
                
                tree.set_root(word)
                batch_trees.append(tree)
                
                # Check memory every 5000 trees within the batch
                if i > 0 and i % 5000 == 0:
                    if self.monitor.is_approaching_limit():
                        batch_trees = batch_trees[:i]
                        break
            
            self.trees.extend(batch_trees)
            batch_count += 1
            
            # Record measurement
            measurement = self.monitor.record_measurement(
                trees_count=len(self.trees),
                words_per_tree=1,
                total_words=len(self.trees),
                word_pattern="mixed",
                additional_info={
                    "batch_number": batch_count,
                    "batch_size": len(batch_trees),
                    "batch_duration": time.perf_counter() - batch_start_time
                }
            )
            
            print(f"{batch_count:<8} {len(self.trees):<12} "
                  f"{measurement['memory_gb']:.2f} GB{'':<4} "
                  f"{measurement['memory_delta_gb']:.2f} GB{'':<4} "
                  f"{measurement['available_memory_gb']:.2f} GB{'':<4} "
                  f"{measurement['memory_pressure_percent']:.1f}%")
            
            # Safety checks
            if measurement['available_memory_gb'] < 2.0:
                print("⚠️  Available memory below 2GB, stopping for safety")
                break
                
            if measurement['memory_pressure_percent'] > 85:
                print("⚠️  Memory pressure above 85%, stopping for safety")
                break
            
            # Brief pause for system stability
            time.sleep(0.5)
            gc.collect()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"memory_limit_approach_{timestamp}.csv"
        self.monitor.save_to_csv(csv_filename)
        
        return csv_filename
        
    def test_word_size_impact_analysis(self) -> str:
        """Analyze the impact of different word sizes and patterns"""
        print("\n" + "="*80)
        print("64-BIT WORD SIZE IMPACT ANALYSIS")
        print("="*80)
        
        # Test different data types to compare with 64-bit words
        test_scenarios = [
            {"name": "8-bit bytes", "data_func": lambda i: i % 256, "description": "Small integers (0-255)"},
            {"name": "32-bit ints", "data_func": lambda i: i % (2**31), "description": "32-bit integers"},
            {"name": "64-bit words", "data_func": lambda i: self.word_generator.generate_pattern_word("sequential", i), "description": "Full 64-bit integers"},
            {"name": "Strings", "data_func": lambda i: f"string_data_{i:016x}", "description": "16-char hex strings"},
            {"name": "Float64", "data_func": lambda i: float(i) * 3.14159, "description": "64-bit floats"},
        ]
        
        trees_per_scenario = 5000
        
        print(f"\n{'Data Type':<15} {'Trees':<8} {'Memory':<12} {'Delta':<12} {'Bytes/Item':<12} {'Description':<20}")
        print("-" * 90)
        
        baseline_memory = self.monitor.get_memory_gb()
        
        for scenario in test_scenarios:
            if self.monitor.is_approaching_limit():
                print(f"⚠️  Skipping {scenario['name']} - approaching memory limit")
                continue
                
            # Clear previous trees to isolate measurement
            self.trees.clear()
            gc.collect()
            time.sleep(0.2)
            
            scenario_start_memory = self.monitor.get_memory_gb()
            
            # Create trees with this data type
            scenario_trees = []
            for i in range(trees_per_scenario):
                tree = narytree.NaryTree()
                data = scenario["data_func"](i)
                tree.set_root(data)
                scenario_trees.append(tree)
                
                # Safety check
                if i > 0 and i % 2000 == 0:
                    if self.monitor.is_approaching_limit():
                        scenario_trees = scenario_trees[:i]
                        break
            
            self.trees = scenario_trees
            
            # Measure memory usage
            measurement = self.monitor.record_measurement(
                trees_count=len(scenario_trees),
                words_per_tree=1,
                total_words=len(scenario_trees),
                word_pattern=scenario["name"],
                additional_info={
                    "scenario_name": scenario["name"],
                    "data_description": scenario["description"]
                }
            )
            
            memory_for_scenario = measurement['memory_gb'] - scenario_start_memory
            bytes_per_item = (memory_for_scenario * 1024**3) / len(scenario_trees)
            
            print(f"{scenario['name']:<15} {len(scenario_trees):<8} "
                  f"{measurement['memory_gb']:.2f} GB{'':<4} "
                  f"{memory_for_scenario:.3f} GB{'':<5} "
                  f"{bytes_per_item:.0f}{'':<8} "
                  f"{scenario['description']:<20}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"word_size_impact_analysis_{timestamp}.csv"
        self.monitor.save_to_csv(csv_filename)
        
        return csv_filename

def generate_pressure_test_plots(csv_files: List[str]):
    """Generate gnuplot scripts for memory pressure visualization"""
    print("\n" + "="*80)
    print("GENERATING MEMORY PRESSURE VISUALIZATION")
    print("="*80)
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            continue
            
        base_name = csv_file.replace('.csv', '')
        
        script_content = f"""#!/usr/bin/gnuplot
# Memory Pressure Analysis Plot for {csv_file}

set terminal png size 1600,1200 enhanced font 'Arial,12'
set output '{base_name}_analysis.png'

set multiplot layout 2,2 title "Memory Pressure Analysis: 64-bit Words" font 'Arial,16'

# Plot 1: Memory usage over time
set title "Memory Usage Over Time"
set xlabel "Time (seconds)"
set ylabel "Memory (GB)"
set grid
plot '{csv_file}' using 1:6 with linespoints lw 2 pt 7 lc rgb '#2E8B57' title "Total Memory", \\
     '{csv_file}' using 1:7 with linespoints lw 2 pt 5 lc rgb '#DC143C' title "Delta Memory"

# Plot 2: Memory pressure percentage
set title "Memory Pressure"
set xlabel "Time (seconds)"
set ylabel "Memory Pressure (%)"
plot '{csv_file}' using 1:10 with linespoints lw 3 pt 9 lc rgb '#FF4500' title "Memory Pressure %"

# Plot 3: Memory efficiency
set title "Memory Efficiency"
set xlabel "Total Words"
set ylabel "Bytes per Word"
plot '{csv_file}' using 4:9 with linespoints lw 2 pt 11 lc rgb '#4169E1' title "Bytes/Word"

# Plot 4: Available memory decline
set title "Available Memory"
set xlabel "Time (seconds)"
set ylabel "Available Memory (GB)"
plot '{csv_file}' using 1:8 with linespoints lw 2 pt 13 lc rgb '#8B0000' title "Available Memory"

unset multiplot

print "Generated: {base_name}_analysis.png"
"""
        
        script_filename = f"{base_name}.gp"
        with open(script_filename, 'w') as f:
            f.write(script_content)
        
        print(f"📊 Generated: {script_filename}")
        
        # Try to execute gnuplot
        try:
            import subprocess
            result = subprocess.run(['gnuplot', script_filename], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✅ Generated plot: {base_name}_analysis.png")
            else:
                print(f"⚠️  Gnuplot issues: {result.stderr}")
        except Exception as e:
            print(f"ℹ️  Run manually: gnuplot {script_filename}")

def main():
    """Main execution function"""
    print("64-BIT PROCESSOR WORD MEMORY PRESSURE TEST")
    print("Target: Intel i5 x86_64, 16GB RAM System")
    print("Testing memory limits with processor word-size data")
    print("="*80)
    
    tester = MemoryPressureTest()
    csv_files = []
    
    try:
        # Test 1: Progressive word loading
        print("Phase 1: Progressive 64-bit word loading...")
        csv1 = tester.test_progressive_word_loading()
        csv_files.append(csv1)
        
        # Test 2: Memory limit approach (if system can handle it)
        if tester.monitor.get_available_memory_gb() > 4.0:  # Only if enough memory available
            print("Phase 2: Approaching memory limits...")
            csv2 = tester.test_memory_limit_approach()
            csv_files.append(csv2)
        else:
            print("⚠️  Skipping memory limit test - insufficient available memory")
        
        # Test 3: Word size impact analysis
        print("Phase 3: Word size impact analysis...")
        csv3 = tester.test_word_size_impact_analysis()
        csv_files.append(csv3)
        
        # Generate visualizations
        generate_pressure_test_plots(csv_files)
        
        # Final summary
        final_measurement = tester.monitor.measurements[-1] if tester.monitor.measurements else None
        
        print(f"\n{'='*80}")
        print("MEMORY PRESSURE TEST SUMMARY")
        print(f"{'='*80}")
        
        if final_measurement:
            print(f"🔍 Total measurements: {len(tester.monitor.measurements)}")
            print(f"💾 Peak memory usage: {max(m['memory_gb'] for m in tester.monitor.measurements):.2f} GB")
            print(f"📈 Max memory pressure: {max(m['memory_pressure_percent'] for m in tester.monitor.measurements):.1f}%")
            print(f"🌳 Max trees created: {max(m['trees_count'] for m in tester.monitor.measurements):,}")
            print(f"💽 Total 64-bit words: {max(m['total_words'] for m in tester.monitor.measurements):,}")
            print(f"⏱️  Total test time: {final_measurement['elapsed_seconds']:.2f} seconds")
            
            avg_bytes_per_word = sum(m['memory_per_word_bytes'] for m in tester.monitor.measurements) / len(tester.monitor.measurements)
            print(f"📊 Average bytes per 64-bit word: {avg_bytes_per_word:.0f}")
        
        print(f"\n📁 Generated files:")
        for csv_file in csv_files:
            print(f"   📄 {csv_file}")
            print(f"   📊 {csv_file.replace('.csv', '.gp')}")
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()