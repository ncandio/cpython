#!/usr/bin/env python3
"""
Disk occupation comparison test between Succinct FUSE filesystem and ext4.
Tests file sizes: 1MB, 10MB, 100MB
"""

import os
import subprocess
import time
import json
from datetime import datetime

def get_disk_usage(path):
    """Get actual disk usage in bytes using du command"""
    try:
        result = subprocess.run(['du', '-sb', path], capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.split()[0])
        return 0
    except:
        return 0

def create_test_file(filepath, size_mb):
    """Create a test file with specified size in MB"""
    size_bytes = size_mb * 1024 * 1024
    with open(filepath, 'wb') as f:
        # Write in chunks to avoid memory issues
        chunk_size = 1024 * 1024  # 1MB chunks
        remaining = size_bytes
        while remaining > 0:
            write_size = min(chunk_size, remaining)
            f.write(b'A' * write_size)
            remaining -= write_size

def run_disk_test():
    """Run comprehensive disk usage comparison test"""
    
    # Test configurations
    test_sizes = [1, 10, 100]  # MB
    succinct_mount = "/tmp/succinct_mount"
    ext4_location = "/tmp/compare_succinct_mount"
    
    # Create ext4 comparison directory
    os.makedirs(ext4_location, exist_ok=True)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_sizes_mb": test_sizes,
        "succinct_location": succinct_mount,
        "ext4_location": ext4_location,
        "results": []
    }
    
    print(f"Disk Usage Comparison: Succinct FUSE vs ext4")
    print(f"Succinct mount: {succinct_mount}")
    print(f"ext4 location: {ext4_location}")
    print("-" * 60)
    
    for size_mb in test_sizes:
        print(f"\nTesting {size_mb}MB files...")
        
        # File paths
        succinct_file = f"{succinct_mount}/test_{size_mb}mb.dat"
        ext4_file = f"{ext4_location}/test_{size_mb}mb.dat"
        
        # Create files
        start_time = time.time()
        create_test_file(succinct_file, size_mb)
        succinct_create_time = time.time() - start_time
        
        start_time = time.time()
        create_test_file(ext4_file, size_mb)
        ext4_create_time = time.time() - start_time
        
        # Measure disk usage
        succinct_usage = get_disk_usage(succinct_file)
        ext4_usage = get_disk_usage(ext4_file)
        
        # Calculate efficiency
        if ext4_usage > 0:
            efficiency_percent = ((ext4_usage - succinct_usage) / ext4_usage) * 100
        else:
            efficiency_percent = 0
        
        result = {
            "size_mb": size_mb,
            "succinct_bytes": succinct_usage,
            "ext4_bytes": ext4_usage,
            "succinct_kb": succinct_usage // 1024,
            "ext4_kb": ext4_usage // 1024,
            "efficiency_percent": round(efficiency_percent, 2),
            "succinct_create_time": round(succinct_create_time, 3),
            "ext4_create_time": round(ext4_create_time, 3)
        }
        
        results["results"].append(result)
        
        print(f"  Size: {size_mb}MB")
        print(f"  Succinct: {succinct_usage:,} bytes ({succinct_usage//1024:,} KB)")
        print(f"  ext4:     {ext4_usage:,} bytes ({ext4_usage//1024:,} KB)")
        print(f"  Efficiency: {efficiency_percent:.1f}% space saved")
        print(f"  Create time - Succinct: {succinct_create_time:.3f}s, ext4: {ext4_create_time:.3f}s")
        
        # Clean up files after measurement
        try:
            os.remove(succinct_file)
            os.remove(ext4_file)
        except:
            pass
    
    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"succinct_vs_ext4_disk_test_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n" + "="*60)
    print(f"Test completed. Results saved to: {results_file}")
    
    # Summary
    total_succinct = sum(r["succinct_bytes"] for r in results["results"])
    total_ext4 = sum(r["ext4_bytes"] for r in results["results"])
    avg_efficiency = sum(r["efficiency_percent"] for r in results["results"]) / len(results["results"])
    
    print(f"\nSUMMARY:")
    print(f"Total succinct usage: {total_succinct:,} bytes ({total_succinct//1024:,} KB)")
    print(f"Total ext4 usage:     {total_ext4:,} bytes ({total_ext4//1024:,} KB)")
    print(f"Average efficiency:   {avg_efficiency:.1f}% space saved")

if __name__ == "__main__":
    run_disk_test()