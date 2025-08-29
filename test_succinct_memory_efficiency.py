#!/usr/bin/env python3

import sys
import os
import json
import time
from datetime import datetime

# Add the build directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Modules'))

try:
    import narytree
except ImportError as e:
    print(f"Failed to import narytree: {e}")
    print("Make sure to build the module first with: python setup_narytree.py build_ext --inplace")
    sys.exit(1)

def build_test_tree(size):
    """Build a test N-ary tree with specified number of nodes"""
    tree = narytree.NaryTree()
    tree.set_root(f"root_0")
    
    nodes_queue = [tree.root()]
    nodes_created = 1
    
    while nodes_created < size and nodes_queue:
        current_node = nodes_queue.pop(0)
        
        # Add 2-4 children per node (typical N-ary tree usage)
        children_count = min(3, size - nodes_created)
        for i in range(children_count):
            if nodes_created >= size:
                break
            child = current_node.add_child(f"node_{nodes_created}")
            nodes_queue.append(child)
            nodes_created += 1
    
    return tree

def measure_memory_efficiency():
    """Compare memory usage: standard vs succinct representation"""
    test_sizes = [100, 1000, 10000, 50000, 100000]
    results = []
    
    print("Testing Succinct N-ary Tree Memory Efficiency")
    print("=" * 60)
    
    for size in test_sizes:
        print(f"\nTesting with {size:,} nodes...")
        
        # Build test tree
        start_time = time.time()
        tree = build_test_tree(size)
        build_time = time.time() - start_time
        
        # Get standard memory stats
        standard_stats = tree.get_memory_stats()
        
        # Encode to succinct representation
        start_time = time.time()
        succinct_encoding = tree.encode_succinct()
        encode_time = time.time() - start_time
        
        # Decode back to verify correctness
        start_time = time.time()
        decoded_tree = narytree.NaryTree.decode_succinct(succinct_encoding)
        decode_time = time.time() - start_time
        
        # Verify tree integrity
        original_size = tree.size()
        decoded_size = decoded_tree.size()
        integrity_check = original_size == decoded_size
        
        # Calculate memory efficiency
        succinct_memory = succinct_encoding['memory_usage']
        standard_memory = standard_stats['total_estimated_bytes']
        memory_reduction = (standard_memory - succinct_memory) / standard_memory * 100
        
        result = {
            'nodes': size,
            'standard_memory_bytes': standard_memory,
            'succinct_memory_bytes': succinct_memory,
            'memory_reduction_percent': memory_reduction,
            'standard_bytes_per_node': standard_memory / size,
            'succinct_bytes_per_node': succinct_memory / size,
            'encode_time_seconds': encode_time,
            'decode_time_seconds': decode_time,
            'build_time_seconds': build_time,
            'integrity_check_passed': integrity_check,
            'structure_bits_count': len(succinct_encoding['structure_bits']) * 8,
            'theoretical_minimum_bits': 2 * size + 1
        }
        
        results.append(result)
        
        print(f"  Standard: {standard_memory:,} bytes ({standard_memory/size:.1f} bytes/node)")
        print(f"  Succinct: {succinct_memory:,} bytes ({succinct_memory/size:.1f} bytes/node)")
        print(f"  Reduction: {memory_reduction:.1f}% memory saved")
        print(f"  Encoding: {encode_time*1000:.2f}ms, Decoding: {decode_time*1000:.2f}ms")
        print(f"  Integrity: {'✓' if integrity_check else '✗'}")
    
    return results

def generate_report(results):
    """Generate comprehensive analysis report"""
    
    print("\n" + "=" * 80)
    print("SUCCINCT N-ARY TREE MEMORY EFFICIENCY ANALYSIS")
    print("=" * 80)
    
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Architecture: 64-bit")
    print(f"Implementation: Left-Child Right-Sibling with 2n+1 bit encoding")
    
    print(f"\n{'Nodes':<10} {'Standard':<12} {'Succinct':<12} {'Reduction':<12} {'Encode':<10} {'Decode':<10}")
    print(f"{'':<10} {'(MB)':<12} {'(MB)':<12} {'(%)':<12} {'(ms)':<10} {'(ms)':<10}")
    print("-" * 80)
    
    for r in results:
        standard_mb = r['standard_memory_bytes'] / (1024 * 1024)
        succinct_mb = r['succinct_memory_bytes'] / (1024 * 1024)
        
        print(f"{r['nodes']:<10,} {standard_mb:<12.3f} {succinct_mb:<12.3f} {r['memory_reduction_percent']:<12.1f} "
              f"{r['encode_time_seconds']*1000:<10.2f} {r['decode_time_seconds']*1000:<10.2f}")
    
    # Calculate efficiency metrics
    avg_reduction = sum(r['memory_reduction_percent'] for r in results) / len(results)
    max_reduction = max(r['memory_reduction_percent'] for r in results)
    
    print(f"\nEFFICIENCY SUMMARY:")
    print(f"Average memory reduction: {avg_reduction:.1f}%")
    print(f"Maximum memory reduction: {max_reduction:.1f}%")
    
    # Theoretical analysis
    largest_test = results[-1]
    theoretical_bits = largest_test['theoretical_minimum_bits']
    actual_bits = largest_test['structure_bits_count']
    theoretical_bytes = theoretical_bits / 8 + largest_test['nodes'] * 8  # 8 bytes per PyObject*
    
    print(f"\nTHEORETICAL ANALYSIS (100K nodes):")
    print(f"Theoretical minimum: {theoretical_bytes:,} bytes ({theoretical_bytes/largest_test['nodes']:.1f} bytes/node)")
    print(f"Our implementation: {largest_test['succinct_memory_bytes']:,} bytes ({largest_test['succinct_bytes_per_node']:.1f} bytes/node)")
    print(f"Efficiency vs theoretical: {theoretical_bytes/largest_test['succinct_memory_bytes']*100:.1f}%")
    
    return results

if __name__ == "__main__":
    try:
        results = measure_memory_efficiency()
        final_results = generate_report(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"succinct_narytree_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(final_results, f, indent=2)
        
        print(f"\nDetailed results saved to: {filename}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()