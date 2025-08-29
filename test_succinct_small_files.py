#!/usr/bin/env python3
"""
Test succinct encoding benefits with many small files and complex directory structures.
This test focuses on metadata overhead where succinct encoding should excel.
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

def get_directory_count(path):
    """Count total directories"""
    count = 0
    for root, dirs, files in os.walk(path):
        count += len(dirs)
    return count

def get_file_count(path):
    """Count total files"""
    count = 0
    for root, dirs, files in os.walk(path):
        count += len(files)
    return count

def create_complex_structure(base_path, num_levels=4, files_per_dir=20, dirs_per_level=5):
    """Create complex directory structure with many small files"""
    
    def random_content(size_bytes):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size_bytes))
    
    def create_level(current_path, level):
        if level >= num_levels:
            return
        
        # Create directories at this level
        for d in range(dirs_per_level):
            dir_name = f"dir_L{level}_{d:03d}"
            dir_path = os.path.join(current_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            
            # Create files in this directory
            for f in range(files_per_dir):
                file_name = f"file_{f:03d}.txt"
                file_path = os.path.join(dir_path, file_name)
                
                # Small files: 10-500 bytes
                content_size = random.randint(10, 500)
                content = random_content(content_size)
                
                with open(file_path, 'w') as file:
                    file.write(content)
            
            # Recurse to next level
            create_level(dir_path, level + 1)
    
    create_level(base_path, 0)

def run_small_files_test():
    """Run test comparing small files overhead"""
    
    succinct_mount = "/tmp/succinct_mount"
    ext4_location = "/tmp/compare_succinct_mount"
    
    # Test configurations: varying numbers of small files
    test_configs = [
        {"files_per_dir": 10, "levels": 3, "dirs_per_level": 3, "name": "small"},
        {"files_per_dir": 20, "levels": 3, "dirs_per_level": 4, "name": "medium"},
        {"files_per_dir": 30, "levels": 4, "dirs_per_level": 3, "name": "large"},
        {"files_per_dir": 50, "levels": 4, "dirs_per_level": 4, "name": "xlarge"}
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "small_files_complex_structure",
        "succinct_location": succinct_mount,
        "ext4_location": ext4_location,
        "configurations": test_configs,
        "results": []
    }
    
    print("Small Files & Complex Structure Test: Succinct FUSE vs ext4")
    print("=" * 70)
    
    for config in test_configs:
        print(f"\nTesting configuration: {config['name']}")
        print(f"  Levels: {config['levels']}, Dirs per level: {config['dirs_per_level']}")
        print(f"  Files per dir: {config['files_per_dir']}")
        
        # Create test directories
        succinct_test_dir = f"{succinct_mount}/test_{config['name']}"
        ext4_test_dir = f"{ext4_location}/test_{config['name']}"
        
        os.makedirs(succinct_test_dir, exist_ok=True)
        os.makedirs(ext4_test_dir, exist_ok=True)
        
        # Create structures
        print("  Creating succinct structure...")
        start_time = time.time()
        create_complex_structure(
            succinct_test_dir, 
            config['levels'], 
            config['files_per_dir'], 
            config['dirs_per_level']
        )
        succinct_create_time = time.time() - start_time
        
        print("  Creating ext4 structure...")
        start_time = time.time()
        create_complex_structure(
            ext4_test_dir, 
            config['levels'], 
            config['files_per_dir'], 
            config['dirs_per_level']
        )
        ext4_create_time = time.time() - start_time
        
        # Measure usage
        succinct_usage = get_disk_usage(succinct_test_dir)
        ext4_usage = get_disk_usage(ext4_test_dir)
        
        # Count files and directories
        succinct_file_count = get_file_count(succinct_test_dir)
        succinct_dir_count = get_directory_count(succinct_test_dir)
        ext4_file_count = get_file_count(ext4_test_dir)
        ext4_dir_count = get_directory_count(ext4_test_dir)
        
        # Calculate efficiency
        if ext4_usage > 0:
            efficiency_percent = ((ext4_usage - succinct_usage) / ext4_usage) * 100
        else:
            efficiency_percent = 0
        
        result = {
            "config_name": config['name'],
            "levels": config['levels'],
            "dirs_per_level": config['dirs_per_level'],
            "files_per_dir": config['files_per_dir'],
            "succinct_bytes": succinct_usage,
            "ext4_bytes": ext4_usage,
            "succinct_kb": succinct_usage // 1024,
            "ext4_kb": ext4_usage // 1024,
            "efficiency_percent": round(efficiency_percent, 2),
            "succinct_file_count": succinct_file_count,
            "ext4_file_count": ext4_file_count,
            "succinct_dir_count": succinct_dir_count,
            "ext4_dir_count": ext4_dir_count,
            "succinct_create_time": round(succinct_create_time, 3),
            "ext4_create_time": round(ext4_create_time, 3)
        }
        
        results["results"].append(result)
        
        print(f"  Results:")
        print(f"    Files created: {succinct_file_count}")
        print(f"    Directories created: {succinct_dir_count}")
        print(f"    Succinct: {succinct_usage:,} bytes ({succinct_usage//1024:,} KB)")
        print(f"    ext4:     {ext4_usage:,} bytes ({ext4_usage//1024:,} KB)")
        print(f"    Efficiency: {efficiency_percent:.1f}% space saved")
        print(f"    Create time - Succinct: {succinct_create_time:.3f}s, ext4: {ext4_create_time:.3f}s")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"succinct_small_files_test_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create CSV for gnuplot
    csv_file = f"succinct_small_files_test_{timestamp}.csv"
    with open(csv_file, 'w') as f:
        f.write("config,file_count,succinct_kb,ext4_kb,efficiency_percent\n")
        for r in results["results"]:
            f.write(f"{r['config_name']},{r['succinct_file_count']},{r['succinct_kb']},{r['ext4_kb']},{r['efficiency_percent']}\n")
    
    print(f"\n" + "="*70)
    print(f"Test completed!")
    print(f"Results saved to: {results_file}")
    print(f"CSV data saved to: {csv_file}")
    
    # Overall summary
    total_succinct = sum(r["succinct_bytes"] for r in results["results"])
    total_ext4 = sum(r["ext4_bytes"] for r in results["results"])
    avg_efficiency = sum(r["efficiency_percent"] for r in results["results"]) / len(results["results"])
    total_files = sum(r["succinct_file_count"] for r in results["results"])
    total_dirs = sum(r["succinct_dir_count"] for r in results["results"])
    
    print(f"\nOVERALL SUMMARY:")
    print(f"Total files created: {total_files}")
    print(f"Total directories created: {total_dirs}")
    print(f"Total succinct usage: {total_succinct:,} bytes ({total_succinct//1024:,} KB)")
    print(f"Total ext4 usage:     {total_ext4:,} bytes ({total_ext4//1024:,} KB)")
    print(f"Average efficiency:   {avg_efficiency:.1f}% space saved")
    
    return csv_file

if __name__ == "__main__":
    csv_file = run_small_files_test()
    print(f"\nGenerate graph with: gnuplot -e \"datafile='{csv_file}'\" plot_script.gp")