#!/usr/bin/env python3
"""
N-ary Tree Auto-Rebalancing Memory and Disk Analysis
Analyzes memory and disk usage patterns for auto-rebalancing version
and compares with original lazy rebalancing implementation
"""

import sys
import math
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any

def calculate_auto_rebalancing_node_memory_64bit(n_children: int, data_size_bytes: int = 8) -> int:
    """
    Calculate memory usage per node on 64-bit architecture for auto-rebalancing version
    
    Node structure on 64-bit (enhanced):
    - data: 8 bytes (pointer to PyObject*)
    - children vector: 24 bytes (std::vector overhead) + n_children * 8 bytes (pointers)
    - parent pointer: 8 bytes
    - Additional overhead: ~16 bytes (alignment, vtable, etc.)
    - Auto-rebalancing metadata: ~8 bytes (operation counters, flags)
    """
    base_node_size = 8 + 24 + 8 + 16 + 8  # 64 bytes base (vs 56 in original)
    children_pointers = n_children * 8
    return base_node_size + children_pointers + data_size_bytes

def calculate_auto_tree_memory(total_nodes: int, avg_children: float, data_size_bytes: int = 8) -> Dict[str, int]:
    """Calculate total tree memory usage with auto-rebalancing overhead"""
    node_memory = calculate_auto_rebalancing_node_memory_64bit(int(avg_children), data_size_bytes)
    
    # Enhanced balancing overhead for auto-rebalancing
    balancing_overhead = total_nodes * 24  # ~24 bytes per node (more metadata)
    
    # Rebalancing operation overhead (temporary memory during rebalancing)
    rebalancing_operation_overhead = int(total_nodes * 16)  # Temporary data structures
    
    # Vector reallocations and fragmentation (~20% overhead due to frequent rebalancing)
    fragmentation_overhead = int((node_memory * total_nodes) * 0.20)
    
    total_memory = (node_memory * total_nodes) + balancing_overhead + rebalancing_operation_overhead + fragmentation_overhead
    
    return {
        'node_memory_per_node': node_memory,
        'total_node_memory': node_memory * total_nodes,
        'balancing_overhead': balancing_overhead,
        'rebalancing_operation_overhead': rebalancing_operation_overhead,
        'fragmentation_overhead': fragmentation_overhead,
        'total_memory_bytes': total_memory,
        'total_memory_mb': total_memory / (1024 * 1024)
    }

def calculate_auto_disk_usage(total_nodes: int, n_value: int, data_size_bytes: int = 8) -> Dict[str, int]:
    """
    Calculate disk usage for auto-rebalancing tree serialization
    Includes additional metadata for rebalancing statistics
    """
    # Enhanced serialization: includes rebalancing stats
    per_node_disk = (
        8 +  # node_id (64-bit)
        data_size_bytes +  # actual data
        8 +  # parent_id
        4 +  # children_count (32-bit)
        n_value * 8 +  # children_ids (64-bit each)
        8    # rebalancing metadata per node
    )
    
    # Enhanced tree metadata (depth, total_nodes, balancing_info, operation_counts, etc.)
    tree_metadata = 512  # bytes (vs 256 in original)
    
    # Serialization overhead (JSON/binary format overhead ~25% due to extra metadata)
    base_size = per_node_disk * total_nodes + tree_metadata
    serialization_overhead = int(base_size * 0.25)
    
    total_disk = base_size + serialization_overhead
    
    return {
        'per_node_disk_bytes': per_node_disk,
        'tree_metadata_bytes': tree_metadata,
        'serialization_overhead': serialization_overhead,
        'total_disk_bytes': total_disk,
        'total_disk_kb': total_disk / 1024,
        'total_disk_mb': total_disk / (1024 * 1024)
    }

def calculate_rebalancing_frequency(total_nodes: int, n_value: int) -> Dict[str, int]:
    """Calculate expected rebalancing operations for auto-rebalancing version"""
    
    # Periodic rebalancing: every 10 operations
    periodic_rebalances = total_nodes // 10
    
    # Threshold-based rebalancing (estimated)
    # More frequent for smaller N values due to deeper trees initially
    threshold_factor = {2: 0.15, 3: 0.10, 4: 0.08, 5: 0.06, 8: 0.04, 10: 0.03, 16: 0.02, 32: 0.01}
    threshold_rebalances = int(total_nodes * threshold_factor.get(n_value, 0.05))
    
    # Emergency rebalancing (rare)
    emergency_rebalances = max(0, int(total_nodes * 0.01))  # ~1% of operations
    
    total_rebalances = periodic_rebalances + threshold_rebalances + emergency_rebalances
    
    return {
        'periodic_rebalances': periodic_rebalances,
        'threshold_rebalances': threshold_rebalances,
        'emergency_rebalances': emergency_rebalances,
        'total_rebalances': total_rebalances,
        'rebalancing_percentage': (total_rebalances / total_nodes) * 100 if total_nodes > 0 else 0
    }

def simulate_auto_rebalancing_tree_growth(n_value: int, max_nodes: int = 100000, step_size: int = 1000) -> List[Dict[str, Any]]:
    """
    Simulate auto-rebalancing tree growth and analyze memory/disk patterns
    """
    results = []
    
    for node_count in range(step_size, max_nodes + 1, step_size):
        # Calculate tree properties (same logic as before)
        optimal_depth = max(1, int(math.log(node_count) / math.log(n_value)) + 1)
        
        # Auto-rebalancing maintains near-optimal structure more consistently
        internal_nodes = max(0, node_count - (node_count // n_value))
        avg_children = min(n_value, node_count / max(1, internal_nodes)) if internal_nodes > 0 else 0
        
        # Memory analysis with auto-rebalancing overhead
        memory_stats = calculate_auto_tree_memory(node_count, avg_children)
        
        # Disk analysis with enhanced metadata
        disk_stats = calculate_auto_disk_usage(node_count, n_value)
        
        # Rebalancing analysis
        rebalancing_stats = calculate_rebalancing_frequency(node_count, n_value)
        
        # Memory efficiency metrics
        memory_per_node = memory_stats['total_memory_bytes'] / node_count
        disk_per_node = disk_stats['total_disk_bytes'] / node_count
        
        # Calculate memory/disk ratio
        memory_disk_ratio = memory_stats['total_memory_bytes'] / max(1, disk_stats['total_disk_bytes'])
        
        # Rebalancing overhead calculation
        rebalancing_cost_memory = memory_stats['total_memory_bytes'] * 0.15  # 15% overhead during rebalancing
        
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
            'balancing_overhead_mb': memory_stats['balancing_overhead'] / (1024 * 1024),
            'rebalancing_operation_overhead_mb': memory_stats['rebalancing_operation_overhead'] / (1024 * 1024),
            'fragmentation_overhead_mb': memory_stats['fragmentation_overhead'] / (1024 * 1024),
            'total_rebalances': rebalancing_stats['total_rebalances'],
            'rebalancing_percentage': rebalancing_stats['rebalancing_percentage'],
            'periodic_rebalances': rebalancing_stats['periodic_rebalances'],
            'threshold_rebalances': rebalancing_stats['threshold_rebalances'],
            'emergency_rebalances': rebalancing_stats['emergency_rebalances']
        }
        
        results.append(result)
    
    return results

def load_original_analysis_data(filename: str) -> Dict[str, Any]:
    """Load original (lazy rebalancing) analysis data for comparison"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Original analysis file '{filename}' not found. Will generate comparison without baseline.")
        return {}

def run_comprehensive_auto_rebalancing_analysis(n_values: List[int], max_nodes: int = 50000, step_size: int = 1000) -> Dict[str, Any]:
    """Run comprehensive analysis for auto-rebalancing version"""
    
    print("🔄 Starting Auto-Rebalancing N-ary Tree Analysis...")
    print(f"📊 Analyzing N values: {n_values}")
    print(f"📈 Node range: {step_size} to {max_nodes} (step: {step_size})")
    print(f"💻 Architecture: 64-bit")
    print(f"⚖️  Auto-rebalancing: ENABLED (explicit rebalancing at each step)")
    
    analysis_results = {}
    
    for n_value in n_values:
        print(f"\n🌳 Analyzing Auto-Rebalancing N={n_value}...")
        start_time = time.time()
        
        results = simulate_auto_rebalancing_tree_growth(n_value, max_nodes, step_size)
        
        # Calculate summary statistics
        max_memory_mb = max(r['memory_mb'] for r in results)
        max_disk_mb = max(r['disk_mb'] for r in results)
        avg_memory_per_node = sum(r['memory_per_node'] for r in results) / len(results)
        avg_disk_per_node = sum(r['disk_per_node'] for r in results) / len(results)
        avg_ratio = sum(r['memory_disk_ratio'] for r in results) / len(results)
        total_rebalances = max(r['total_rebalances'] for r in results)
        avg_rebalancing_percentage = sum(r['rebalancing_percentage'] for r in results) / len(results)
        
        summary = {
            'n_value': n_value,
            'max_memory_mb': max_memory_mb,
            'max_disk_mb': max_disk_mb,
            'avg_memory_per_node': avg_memory_per_node,
            'avg_disk_per_node': avg_disk_per_node,
            'avg_memory_disk_ratio': avg_ratio,
            'total_rebalances_at_max': total_rebalances,
            'avg_rebalancing_percentage': avg_rebalancing_percentage,
            'total_simulations': len(results),
            'analysis_time_seconds': time.time() - start_time
        }
        
        analysis_results[f'AutoRebalancing_N_{n_value}'] = {
            'summary': summary,
            'detailed_results': results
        }
        
        print(f"✅ Auto-Rebalancing N={n_value} completed in {summary['analysis_time_seconds']:.2f}s")
        print(f"   📊 Max memory: {max_memory_mb:.2f} MB")
        print(f"   💾 Max disk: {max_disk_mb:.2f} MB")
        print(f"   📈 Avg memory/node: {avg_memory_per_node:.0f} bytes")
        print(f"   🔄 Total rebalances: {total_rebalances}")
        print(f"   ⚡ Rebalancing rate: {avg_rebalancing_percentage:.1f}%")
    
    # Add metadata
    analysis_results['metadata'] = {
        'timestamp': datetime.now().isoformat(),
        'architecture': '64-bit',
        'implementation': 'auto-rebalancing',
        'max_nodes_analyzed': max_nodes,
        'step_size': step_size,
        'n_values_analyzed': n_values,
        'rebalancing_strategy': 'explicit_at_each_step',
        'rebalancing_thresholds': {
            'periodic': 'every_10_operations',
            'threshold': '1.5x_optimal_depth',
            'emergency': '2.0x_optimal_depth'
        }
    }
    
    return analysis_results

def compare_with_original_analysis(auto_results: Dict[str, Any], original_filename: str = None) -> Dict[str, Any]:
    """Compare auto-rebalancing results with original lazy rebalancing"""
    
    print(f"\n🔍 Comparing Auto-Rebalancing vs Original (Lazy) Implementation")
    print("=" * 70)
    
    comparison_results = {}
    
    # Try to load original results
    original_results = {}
    if original_filename:
        original_results = load_original_analysis_data(original_filename)
    
    # Compare each N value
    for key, auto_data in auto_results.items():
        if key.startswith('AutoRebalancing_N_'):
            n_value = auto_data['summary']['n_value']
            auto_summary = auto_data['summary']
            
            # Try to find corresponding original data
            original_key = f'N_{n_value}'
            original_summary = original_results.get(original_key, {}).get('summary', {})
            
            if original_summary:
                print(f"\n📊 N={n_value} Comparison:")
                print(f"   Memory (Auto vs Original): {auto_summary['max_memory_mb']:.2f} MB vs {original_summary.get('max_memory_mb', 0):.2f} MB")
                print(f"   Disk (Auto vs Original):   {auto_summary['max_disk_mb']:.2f} MB vs {original_summary.get('max_disk_mb', 0):.2f} MB")
                print(f"   Memory/Node (Auto vs Original): {auto_summary['avg_memory_per_node']:.0f} vs {original_summary.get('avg_memory_per_node', 0):.0f} bytes")
                print(f"   Rebalancing Operations: {auto_summary['total_rebalances_at_max']} (Auto) vs 0 (Original)")
                
                # Calculate overhead
                memory_overhead = ((auto_summary['max_memory_mb'] - original_summary.get('max_memory_mb', 0)) / 
                                 max(1, original_summary.get('max_memory_mb', 0))) * 100
                disk_overhead = ((auto_summary['max_disk_mb'] - original_summary.get('max_disk_mb', 0)) / 
                               max(1, original_summary.get('max_disk_mb', 0))) * 100
                
                comparison_results[f'N_{n_value}'] = {
                    'auto_rebalancing': auto_summary,
                    'original': original_summary,
                    'memory_overhead_percentage': memory_overhead,
                    'disk_overhead_percentage': disk_overhead,
                    'rebalancing_operations': auto_summary['total_rebalances_at_max'],
                    'rebalancing_rate': auto_summary['avg_rebalancing_percentage']
                }
                
                print(f"   📈 Memory overhead: {memory_overhead:+.1f}%")
                print(f"   💾 Disk overhead: {disk_overhead:+.1f}%")
            else:
                print(f"\n📊 N={n_value}: Original data not available for comparison")
                comparison_results[f'N_{n_value}'] = {
                    'auto_rebalancing': auto_summary,
                    'original': {},
                    'rebalancing_operations': auto_summary['total_rebalances_at_max'],
                    'rebalancing_rate': auto_summary['avg_rebalancing_percentage']
                }
    
    return comparison_results

def save_auto_rebalancing_results(results: Dict[str, Any], filename: str = None):
    """Save auto-rebalancing analysis results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"narytree_auto_rebalancing_analysis_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"💾 Auto-rebalancing results saved to: {filename}")
    return filename

def generate_auto_rebalancing_gnuplot_data(results: Dict[str, Any], comparison: Dict[str, Any]) -> str:
    """Generate data files for gnuplot visualization comparing both versions"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_filename = f"narytree_auto_vs_original_comparison_{timestamp}.csv"
    
    with open(data_filename, 'w') as f:
        # Write header
        f.write("implementation,n_value,node_count,memory_mb,disk_mb,memory_per_node,disk_per_node,")
        f.write("memory_disk_ratio,optimal_depth,balancing_overhead_mb,total_rebalances,rebalancing_percentage\n")
        
        # Write data for auto-rebalancing version
        for key, data in results.items():
            if key.startswith('AutoRebalancing_N_'):
                for result in data['detailed_results']:
                    f.write(f"auto,{result['n_value']},{result['node_count']},{result['memory_mb']:.3f},")
                    f.write(f"{result['disk_mb']:.3f},{result['memory_per_node']:.1f},")
                    f.write(f"{result['disk_per_node']:.1f},{result['memory_disk_ratio']:.3f},")
                    f.write(f"{result['optimal_depth']},{result['balancing_overhead_mb']:.3f},")
                    f.write(f"{result['total_rebalances']},{result['rebalancing_percentage']:.2f}\n")
    
    print(f"📈 Comparison gnuplot data saved to: {data_filename}")
    return data_filename

if __name__ == "__main__":
    # Configuration
    N_VALUES = [2, 3, 4, 5, 8, 10, 16, 32]  # Same N values as original analysis
    MAX_NODES = 100000  # Same scale as original
    STEP_SIZE = 2000    # Same step size as original
    
    print("🔄 N-ary Tree Auto-Rebalancing Analysis & Comparison")
    print("=" * 60)
    
    # Run auto-rebalancing analysis
    auto_results = run_comprehensive_auto_rebalancing_analysis(N_VALUES, MAX_NODES, STEP_SIZE)
    
    # Save auto-rebalancing results
    auto_filename = save_auto_rebalancing_results(auto_results)
    
    # Compare with original results (if available)
    original_filename = "narytree_memory_disk_analysis_20250828_102933.json"  # From earlier analysis
    comparison = compare_with_original_analysis(auto_results, original_filename)
    
    # Generate comparison data for gnuplot
    comparison_data_filename = generate_auto_rebalancing_gnuplot_data(auto_results, comparison)
    
    print("\n📊 Auto-Rebalancing Analysis Summary:")
    print("-" * 50)
    
    for key, data in auto_results.items():
        if key.startswith('AutoRebalancing_N_'):
            summary = data['summary']
            print(f"N={summary['n_value']:2d}: Memory={summary['max_memory_mb']:8.2f} MB, "
                  f"Disk={summary['max_disk_mb']:8.2f} MB, "
                  f"Ratio={summary['avg_memory_disk_ratio']:5.2f}, "
                  f"Rebalances={summary['total_rebalances_at_max']:4d}")
    
    print(f"\n🎯 Files Generated:")
    print(f"   📄 Auto-rebalancing results: {auto_filename}")
    print(f"   📊 Comparison data: {comparison_data_filename}")
    print(f"   🔧 Next: Generate comparison visualizations")
    
    print(f"\n🔍 Key Findings Preview:")
    if comparison:
        total_overhead_memory = sum(comp.get('memory_overhead_percentage', 0) for comp in comparison.values()) / len(comparison)
        total_overhead_disk = sum(comp.get('disk_overhead_percentage', 0) for comp in comparison.values()) / len(comparison)
        print(f"   📈 Average memory overhead: {total_overhead_memory:+.1f}%")
        print(f"   💾 Average disk overhead: {total_overhead_disk:+.1f}%")
        print(f"   🔄 Auto-rebalancing provides consistent performance at cost of {total_overhead_memory:.1f}% memory")