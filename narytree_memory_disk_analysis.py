#!/usr/bin/env python3
"""
N-ary Tree Memory and Disk Analysis with Self-Balancing
Analyzes memory and disk usage patterns for different N values (branching factors)
with 64-bit architecture word size considerations
"""

import sys
import math
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any

def calculate_node_memory_64bit(n_children: int, data_size_bytes: int = 8) -> int:
    """
    Calculate memory usage per node on 64-bit architecture
    
    Node structure on 64-bit:
    - data: 8 bytes (pointer to PyObject*)
    - children vector: 24 bytes (std::vector overhead) + n_children * 8 bytes (pointers)
    - parent pointer: 8 bytes
    - Additional overhead: ~16 bytes (alignment, vtable, etc.)
    """
    base_node_size = 8 + 24 + 8 + 16  # 56 bytes base
    children_pointers = n_children * 8
    return base_node_size + children_pointers + data_size_bytes

def calculate_tree_memory(total_nodes: int, avg_children: float, data_size_bytes: int = 8) -> Dict[str, int]:
    """Calculate total tree memory usage"""
    node_memory = calculate_node_memory_64bit(int(avg_children), data_size_bytes)
    
    # Additional overhead for balanced tree structures
    balancing_overhead = total_nodes * 16  # ~16 bytes per node for balancing metadata
    
    # Vector reallocations and fragmentation (~15% overhead)
    fragmentation_overhead = int((node_memory * total_nodes) * 0.15)
    
    total_memory = (node_memory * total_nodes) + balancing_overhead + fragmentation_overhead
    
    return {
        'node_memory_per_node': node_memory,
        'total_node_memory': node_memory * total_nodes,
        'balancing_overhead': balancing_overhead,
        'fragmentation_overhead': fragmentation_overhead,
        'total_memory_bytes': total_memory,
        'total_memory_mb': total_memory / (1024 * 1024)
    }

def calculate_disk_usage(total_nodes: int, n_value: int, data_size_bytes: int = 8) -> Dict[str, int]:
    """
    Calculate disk usage for tree serialization
    Accounts for tree structure metadata and serialization overhead
    """
    # Basic serialization: node_id + data + parent_id + children_count + children_ids
    per_node_disk = (
        8 +  # node_id (64-bit)
        data_size_bytes +  # actual data
        8 +  # parent_id
        4 +  # children_count (32-bit)
        n_value * 8  # children_ids (64-bit each)
    )
    
    # Tree metadata (depth, total_nodes, balancing_info, etc.)
    tree_metadata = 256  # bytes
    
    # Serialization overhead (JSON/binary format overhead ~20%)
    base_size = per_node_disk * total_nodes + tree_metadata
    serialization_overhead = int(base_size * 0.20)
    
    total_disk = base_size + serialization_overhead
    
    return {
        'per_node_disk_bytes': per_node_disk,
        'tree_metadata_bytes': tree_metadata,
        'serialization_overhead': serialization_overhead,
        'total_disk_bytes': total_disk,
        'total_disk_kb': total_disk / 1024,
        'total_disk_mb': total_disk / (1024 * 1024)
    }

def calculate_optimal_depth(total_nodes: int, n_value: int) -> int:
    """Calculate optimal depth for balanced n-ary tree"""
    if total_nodes <= 1:
        return 1
    return max(1, int(math.log(total_nodes) / math.log(n_value)) + 1)

def simulate_tree_growth(n_value: int, max_nodes: int = 100000, step_size: int = 1000) -> List[Dict[str, Any]]:
    """
    Simulate tree growth and analyze memory/disk patterns with self-balancing
    """
    results = []
    
    for node_count in range(step_size, max_nodes + 1, step_size):
        # Calculate tree properties
        optimal_depth = calculate_optimal_depth(node_count, n_value)
        
        # For balanced tree, most nodes will have close to n_value children
        # except leaves and the last level
        internal_nodes = max(0, node_count - (node_count // n_value))
        avg_children = min(n_value, node_count / max(1, internal_nodes)) if internal_nodes > 0 else 0
        
        # Memory analysis
        memory_stats = calculate_tree_memory(node_count, avg_children)
        
        # Disk analysis
        disk_stats = calculate_disk_usage(node_count, n_value)
        
        # Balancing frequency (heuristic: balance every ~log(n) operations)
        balance_frequency = max(1, int(math.log(node_count) / math.log(n_value)))
        balancing_cost_memory = memory_stats['total_memory_bytes'] * 0.1  # 10% temporary overhead
        
        # Memory efficiency metrics
        memory_per_node = memory_stats['total_memory_bytes'] / node_count
        disk_per_node = disk_stats['total_disk_bytes'] / node_count
        
        # Calculate memory/disk ratio
        memory_disk_ratio = memory_stats['total_memory_bytes'] / max(1, disk_stats['total_disk_bytes'])
        
        result = {
            'n_value': n_value,
            'node_count': node_count,
            'optimal_depth': optimal_depth,
            'avg_children': avg_children,
            'memory_bytes': memory_stats['total_memory_bytes'],
            'memory_mb': memory_stats['total_memory_mb'],
            'memory_per_node': memory_per_node,
            'disk_bytes': disk_stats['total_disk_bytes'],
            'disk_kb': disk_stats['total_disk_kb'],
            'disk_mb': disk_stats['total_disk_mb'],
            'disk_per_node': disk_per_node,
            'memory_disk_ratio': memory_disk_ratio,
            'balancing_overhead_mb': balancing_cost_memory / (1024 * 1024),
            'balance_frequency': balance_frequency,
            'fragmentation_overhead_mb': memory_stats['fragmentation_overhead'] / (1024 * 1024)
        }
        
        results.append(result)
    
    return results

def run_comprehensive_analysis(n_values: List[int], max_nodes: int = 50000, step_size: int = 1000) -> Dict[str, Any]:
    """Run comprehensive analysis for multiple N values"""
    
    print("🔍 Starting comprehensive N-ary tree memory/disk analysis...")
    print(f"📊 Analyzing N values: {n_values}")
    print(f"📈 Node range: {step_size} to {max_nodes} (step: {step_size})")
    print(f"💻 Architecture: 64-bit")
    print("⚖️  Including self-balancing overhead analysis")
    
    analysis_results = {}
    
    for n_value in n_values:
        print(f"\n🌳 Analyzing N={n_value}...")
        start_time = time.time()
        
        results = simulate_tree_growth(n_value, max_nodes, step_size)
        
        # Calculate summary statistics
        max_memory_mb = max(r['memory_mb'] for r in results)
        max_disk_mb = max(r['disk_mb'] for r in results)
        avg_memory_per_node = sum(r['memory_per_node'] for r in results) / len(results)
        avg_disk_per_node = sum(r['disk_per_node'] for r in results) / len(results)
        avg_ratio = sum(r['memory_disk_ratio'] for r in results) / len(results)
        
        summary = {
            'n_value': n_value,
            'max_memory_mb': max_memory_mb,
            'max_disk_mb': max_disk_mb,
            'avg_memory_per_node': avg_memory_per_node,
            'avg_disk_per_node': avg_disk_per_node,
            'avg_memory_disk_ratio': avg_ratio,
            'total_simulations': len(results),
            'analysis_time_seconds': time.time() - start_time
        }
        
        analysis_results[f'N_{n_value}'] = {
            'summary': summary,
            'detailed_results': results
        }
        
        print(f"✅ N={n_value} completed in {summary['analysis_time_seconds']:.2f}s")
        print(f"   📊 Max memory: {max_memory_mb:.2f} MB")
        print(f"   💾 Max disk: {max_disk_mb:.2f} MB")
        print(f"   📈 Avg memory/node: {avg_memory_per_node:.0f} bytes")
    
    # Add metadata
    analysis_results['metadata'] = {
        'timestamp': datetime.now().isoformat(),
        'architecture': '64-bit',
        'max_nodes_analyzed': max_nodes,
        'step_size': step_size,
        'n_values_analyzed': n_values,
        'includes_balancing_overhead': True,
        'word_size_bytes': 8
    }
    
    return analysis_results

def save_results(results: Dict[str, Any], filename: str = None):
    """Save analysis results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"narytree_memory_disk_analysis_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"💾 Results saved to: {filename}")
    return filename

def generate_gnuplot_data(results: Dict[str, Any]) -> str:
    """Generate data files for gnuplot visualization"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_filename = f"narytree_memory_disk_data_{timestamp}.csv"
    
    with open(data_filename, 'w') as f:
        # Write header
        f.write("n_value,node_count,memory_mb,disk_mb,memory_per_node,disk_per_node,memory_disk_ratio,optimal_depth,balancing_overhead_mb\n")
        
        # Write data for each N value
        for key, data in results.items():
            if key.startswith('N_'):
                for result in data['detailed_results']:
                    f.write(f"{result['n_value']},{result['node_count']},{result['memory_mb']:.3f},"
                           f"{result['disk_mb']:.3f},{result['memory_per_node']:.1f},"
                           f"{result['disk_per_node']:.1f},{result['memory_disk_ratio']:.3f},"
                           f"{result['optimal_depth']},{result['balancing_overhead_mb']:.3f}\n")
    
    print(f"📈 Gnuplot data saved to: {data_filename}")
    return data_filename

if __name__ == "__main__":
    # Configuration
    N_VALUES = [2, 3, 4, 5, 8, 10, 16, 32]  # Different branching factors to analyze
    MAX_NODES = 100000  # Maximum number of nodes to simulate
    STEP_SIZE = 2000    # Step size for simulation
    
    print("🚀 N-ary Tree Memory/Disk Analysis with Self-Balancing")
    print("=" * 60)
    
    # Run analysis
    results = run_comprehensive_analysis(N_VALUES, MAX_NODES, STEP_SIZE)
    
    # Save results
    json_filename = save_results(results)
    data_filename = generate_gnuplot_data(results)
    
    print("\n📊 Analysis Summary:")
    print("-" * 40)
    
    for key, data in results.items():
        if key.startswith('N_'):
            summary = data['summary']
            print(f"N={summary['n_value']:2d}: Memory={summary['max_memory_mb']:8.2f} MB, "
                  f"Disk={summary['max_disk_mb']:8.2f} MB, "
                  f"Ratio={summary['avg_memory_disk_ratio']:5.2f}")
    
    print(f"\n🎯 Files generated:")
    print(f"   📄 Full results: {json_filename}")
    print(f"   📊 Gnuplot data: {data_filename}")
    print(f"   🔧 Next: Run gnuplot visualization script")