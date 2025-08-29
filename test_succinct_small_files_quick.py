#!/usr/bin/env python3
"""
Quick test for succinct encoding benefits with small files.
Reduced scope for faster execution.
"""

import os
import subprocess
import time
import json
import random
import string
from datetime import datetime

def get_disk_usage(path):
    """Get actual disk usage in bytes"""
    try:
        result = subprocess.run(['du', '-sb', path], capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.split()[0])
        return 0
    except:
        return 0

def create_small_files_structure(base_path, num_dirs=10, files_per_dir=20):
    """Create structure with many small files"""
    
    for d in range(num_dirs):
        dir_name = f"dir_{d:03d}"
        dir_path = os.path.join(base_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        
        # Create small files (10-100 bytes each)
        for f in range(files_per_dir):
            file_name = f"file_{f:03d}.txt"
            file_path = os.path.join(dir_path, file_name)
            
            content_size = random.randint(10, 100)
            content = ''.join(random.choices(string.ascii_letters, k=content_size))
            
            with open(file_path, 'w') as file:
                file.write(content)

def run_quick_test():
    """Run quick small files test"""
    
    succinct_mount = "/tmp/succinct_mount"
    ext4_location = "/tmp/compare_succinct_mount"
    
    # Test configurations
    configs = [
        {"dirs": 5, "files": 10, "name": "tiny"},
        {"dirs": 10, "files": 20, "name": "small"},
        {"dirs": 20, "files": 30, "name": "medium"},
        {"dirs": 50, "files": 50, "name": "large"}
    ]
    
    results = []
    
    print("Quick Small Files Test: Succinct FUSE vs ext4")
    print("=" * 50)
    
    for config in configs:
        print(f"\nTesting {config['name']}: {config['dirs']} dirs, {config['files']} files/dir")
        
        # Create test directories
        succinct_test = f"{succinct_mount}/test_{config['name']}"
        ext4_test = f"{ext4_location}/test_{config['name']}"
        
        os.makedirs(succinct_test, exist_ok=True)
        os.makedirs(ext4_test, exist_ok=True)
        
        # Create structures
        start = time.time()
        create_small_files_structure(succinct_test, config['dirs'], config['files'])
        succinct_time = time.time() - start
        
        start = time.time()
        create_small_files_structure(ext4_test, config['dirs'], config['files'])
        ext4_time = time.time() - start
        
        # Measure usage
        succinct_usage = get_disk_usage(succinct_test)
        ext4_usage = get_disk_usage(ext4_test)
        
        efficiency = ((ext4_usage - succinct_usage) / ext4_usage * 100) if ext4_usage > 0 else 0
        total_files = config['dirs'] * config['files']
        
        result = {
            "config": config['name'],
            "dirs": config['dirs'],
            "files_per_dir": config['files'],
            "total_files": total_files,
            "succinct_bytes": succinct_usage,
            "ext4_bytes": ext4_usage,
            "succinct_kb": succinct_usage // 1024,
            "ext4_kb": ext4_usage // 1024,
            "efficiency_percent": round(efficiency, 2),
            "succinct_time": round(succinct_time, 3),
            "ext4_time": round(ext4_time, 3)
        }
        
        results.append(result)
        
        print(f"  Files: {total_files}")
        print(f"  Succinct: {succinct_usage:,} bytes ({succinct_usage//1024:,} KB)")
        print(f"  ext4:     {ext4_usage:,} bytes ({ext4_usage//1024:,} KB)")
        print(f"  Efficiency: {efficiency:.1f}% space saved")
        print(f"  Time - Succinct: {succinct_time:.3f}s, ext4: {ext4_time:.3f}s")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON results
    results_data = {
        "timestamp": timestamp,
        "test_type": "small_files_metadata_overhead",
        "results": results
    }
    
    json_file = f"succinct_small_files_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    # CSV for plotting
    csv_file = f"succinct_small_files_{timestamp}.csv"
    with open(csv_file, 'w') as f:
        f.write("config,total_files,succinct_kb,ext4_kb,efficiency_percent\n")
        for r in results:
            f.write(f"{r['config']},{r['total_files']},{r['succinct_kb']},{r['ext4_kb']},{r['efficiency_percent']}\n")
    
    print(f"\n" + "="*50)
    print(f"Results: {json_file}")
    print(f"Plot data: {csv_file}")
    
    return csv_file

if __name__ == "__main__":
    csv_file = run_quick_test()
    print(f"\nTo plot: gnuplot -e \"datafile='{csv_file}'\" plot_small_files.gp")