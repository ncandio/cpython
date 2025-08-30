#!/usr/bin/env python3
"""
Comprehensive filesystem performance comparison:
- ext4 (traditional Linux filesystem)  
- Btrfs (modern copy-on-write filesystem)
- VFS/tmpfs (in-memory filesystem)
- Enhanced N-ary Tree FUSE (our succinct implementation)
"""

import os
import subprocess
import time
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

class FilesystemBenchmark:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_configurations": [],
            "filesystem_results": {}
        }
        
    def setup_test_locations(self):
        """Setup test locations for different filesystems"""
        locations = {}
        
        # ext4 - use /tmp (usually ext4 on most systems)
        locations['ext4'] = "/tmp/fs_benchmark_ext4"
        
        # Btrfs - create if available, otherwise skip
        btrfs_path = "/tmp/fs_benchmark_btrfs"
        locations['btrfs'] = btrfs_path
        
        # VFS/tmpfs - create tmpfs mount
        tmpfs_path = "/tmp/fs_benchmark_tmpfs"
        locations['tmpfs'] = tmpfs_path
        
        # Enhanced N-ary Tree FUSE
        locations['narytree_fuse'] = "/tmp/succinct_mount"
        
        # Create directories
        for name, path in locations.items():
            if name != 'narytree_fuse':  # FUSE mount already exists
                os.makedirs(path, exist_ok=True)
        
        return locations
        
    def setup_tmpfs(self, mount_point, size_mb=512):
        """Setup tmpfs mount"""
        try:
            # Check if already mounted
            result = subprocess.run(['findmnt', mount_point], capture_output=True)
            if result.returncode != 0:
                # Mount tmpfs
                subprocess.run(['sudo', 'mkdir', '-p', mount_point], check=True)
                subprocess.run(['sudo', 'mount', '-t', 'tmpfs', '-o', f'size={size_mb}M', 
                              'tmpfs', mount_point], check=True, input='nico\n', text=True)
                subprocess.run(['sudo', 'chmod', '777', mount_point], check=True, input='nico\n', text=True)
            return True
        except subprocess.CalledProcessError:
            print(f"Warning: Could not setup tmpfs at {mount_point}")
            return False
    
    def cleanup_tmpfs(self, mount_point):
        """Cleanup tmpfs mount"""
        try:
            subprocess.run(['sudo', 'umount', mount_point], check=True, input='nico\n', text=True)
            subprocess.run(['sudo', 'rmdir', mount_point], check=True, input='nico\n', text=True)
        except subprocess.CalledProcessError:
            pass
    
    def get_disk_usage(self, path):
        """Get disk usage in bytes"""
        try:
            result = subprocess.run(['du', '-sb', path], capture_output=True, text=True)
            if result.returncode == 0:
                return int(result.stdout.split()[0])
        except:
            pass
        return 0
    
    def get_filesystem_info(self, path):
        """Get filesystem type and mount info"""
        try:
            result = subprocess.run(['df', '-T', path], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    fields = lines[1].split()
                    return {
                        'filesystem': fields[0],
                        'type': fields[1],
                        'total_kb': int(fields[2]),
                        'used_kb': int(fields[3]),
                        'available_kb': int(fields[4]),
                        'use_percent': fields[5],
                        'mount': fields[6]
                    }
        except:
            pass
        return {}
    
    def create_test_files(self, base_path, test_config):
        """Create test files according to configuration"""
        files_created = 0
        dirs_created = 0
        start_time = time.time()
        
        try:
            for d in range(test_config['num_dirs']):
                dir_path = os.path.join(base_path, f"testdir_{d:04d}")
                os.makedirs(dir_path, exist_ok=True)
                dirs_created += 1
                
                for f in range(test_config['files_per_dir']):
                    file_path = os.path.join(dir_path, f"file_{f:04d}.txt")
                    content = 'A' * test_config['file_size_bytes']
                    
                    with open(file_path, 'w') as file:
                        file.write(content)
                    files_created += 1
                    
        except Exception as e:
            print(f"Error creating files: {e}")
        
        creation_time = time.time() - start_time
        return files_created, dirs_created, creation_time
    
    def read_test_files(self, base_path, test_config):
        """Read all test files and measure performance"""
        files_read = 0
        bytes_read = 0
        start_time = time.time()
        
        try:
            for d in range(test_config['num_dirs']):
                dir_path = os.path.join(base_path, f"testdir_{d:04d}")
                if not os.path.exists(dir_path):
                    continue
                    
                for f in range(test_config['files_per_dir']):
                    file_path = os.path.join(dir_path, f"file_{f:04d}.txt")
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as file:
                            content = file.read()
                            bytes_read += len(content)
                        files_read += 1
                        
        except Exception as e:
            print(f"Error reading files: {e}")
        
        read_time = time.time() - start_time
        return files_read, bytes_read, read_time
    
    def cleanup_test_files(self, base_path):
        """Remove all test files"""
        start_time = time.time()
        try:
            if os.path.exists(base_path):
                shutil.rmtree(base_path)
                os.makedirs(base_path, exist_ok=True)
        except Exception as e:
            print(f"Error cleaning up: {e}")
        
        cleanup_time = time.time() - start_time
        return cleanup_time
    
    def benchmark_filesystem(self, fs_name, fs_path, test_configs):
        """Benchmark a specific filesystem"""
        print(f"\nBenchmarking {fs_name} at {fs_path}")
        print("-" * 50)
        
        fs_info = self.get_filesystem_info(fs_path)
        results = {
            'filesystem_info': fs_info,
            'test_results': []
        }
        
        for config in test_configs:
            print(f"  Test: {config['name']} ({config['num_dirs']} dirs, {config['files_per_dir']} files/dir)")
            
            test_path = os.path.join(fs_path, f"test_{config['name']}")
            os.makedirs(test_path, exist_ok=True)
            
            # Create files
            files_created, dirs_created, create_time = self.create_test_files(test_path, config)
            
            # Measure disk usage
            disk_usage = self.get_disk_usage(test_path)
            
            # Read files  
            files_read, bytes_read, read_time = self.read_test_files(test_path, config)
            
            # Cleanup
            cleanup_time = self.cleanup_test_files(test_path)
            
            # Calculate metrics
            total_files = config['num_dirs'] * config['files_per_dir']
            create_throughput = files_created / create_time if create_time > 0 else 0
            read_throughput = files_read / read_time if read_time > 0 else 0
            bytes_per_file = bytes_read / files_read if files_read > 0 else 0
            
            test_result = {
                'config': config,
                'files_created': files_created,
                'dirs_created': dirs_created,
                'files_read': files_read,
                'bytes_read': bytes_read,
                'disk_usage_bytes': disk_usage,
                'create_time_sec': create_time,
                'read_time_sec': read_time,
                'cleanup_time_sec': cleanup_time,
                'create_throughput_files_sec': create_throughput,
                'read_throughput_files_sec': read_throughput,
                'bytes_per_file': bytes_per_file,
                'efficiency_bytes_per_file': disk_usage / total_files if total_files > 0 else 0
            }
            
            results['test_results'].append(test_result)
            
            print(f"    Created: {files_created} files in {create_time:.3f}s ({create_throughput:.1f} files/sec)")
            print(f"    Read: {files_read} files in {read_time:.3f}s ({read_throughput:.1f} files/sec)")
            print(f"    Disk usage: {disk_usage / 1024:.1f} KB ({disk_usage / total_files:.1f} bytes/file)")
        
        return results
    
    def run_comprehensive_benchmark(self):
        """Run comprehensive filesystem benchmark"""
        print("Comprehensive Filesystem Performance Comparison")
        print("=" * 60)
        
        # Test configurations
        test_configs = [
            {
                'name': 'small_files',
                'num_dirs': 10,
                'files_per_dir': 50,
                'file_size_bytes': 100,
                'description': 'Many small files (100 bytes each)'
            },
            {
                'name': 'medium_files',
                'num_dirs': 20,
                'files_per_dir': 25,
                'file_size_bytes': 1024,
                'description': 'Medium files (1KB each)'
            },
            {
                'name': 'large_files',
                'num_dirs': 5,
                'files_per_dir': 10,
                'file_size_bytes': 10240,
                'description': 'Larger files (10KB each)'
            }
        ]
        
        self.results['test_configurations'] = test_configs
        
        # Setup filesystem locations
        locations = self.setup_test_locations()
        
        # Setup tmpfs
        tmpfs_available = self.setup_tmpfs(locations['tmpfs'])
        
        # Test filesystems
        filesystems_to_test = ['ext4']
        
        # Check for Btrfs availability
        try:
            result = subprocess.run(['which', 'btrfs'], capture_output=True)
            if result.returncode == 0:
                filesystems_to_test.append('btrfs')
        except:
            pass
        
        if tmpfs_available:
            filesystems_to_test.append('tmpfs')
        
        # Check if FUSE mount exists
        if os.path.exists(locations['narytree_fuse']) and os.path.ismount(locations['narytree_fuse']):
            filesystems_to_test.append('narytree_fuse')
        else:
            print("Warning: N-ary tree FUSE filesystem not mounted at", locations['narytree_fuse'])
        
        # Run benchmarks
        for fs_name in filesystems_to_test:
            if fs_name in locations:
                self.results['filesystem_results'][fs_name] = self.benchmark_filesystem(
                    fs_name, locations[fs_name], test_configs
                )
        
        # Cleanup
        if tmpfs_available:
            self.cleanup_tmpfs(locations['tmpfs'])
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"filesystem_comprehensive_benchmark_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate CSV for plotting
        csv_file = f"filesystem_benchmark_{timestamp}.csv"
        self.generate_csv(csv_file)
        
        print(f"\n" + "=" * 60)
        print(f"Benchmark completed!")
        print(f"Results saved to: {results_file}")
        print(f"Plot data saved to: {csv_file}")
        
        return csv_file, results_file
    
    def generate_csv(self, csv_file):
        """Generate CSV file for gnuplot"""
        with open(csv_file, 'w') as f:
            f.write("filesystem,test_name,files_created,create_time,read_time,disk_usage_kb,create_throughput,read_throughput,efficiency_bytes_per_file\n")
            
            for fs_name, fs_results in self.results['filesystem_results'].items():
                for test_result in fs_results['test_results']:
                    config = test_result['config']
                    f.write(f"{fs_name},{config['name']},{test_result['files_created']},")
                    f.write(f"{test_result['create_time_sec']},{test_result['read_time_sec']},")
                    f.write(f"{test_result['disk_usage_bytes']/1024},{test_result['create_throughput_files_sec']},")
                    f.write(f"{test_result['read_throughput_files_sec']},{test_result['efficiency_bytes_per_file']}\n")

if __name__ == "__main__":
    benchmark = FilesystemBenchmark()
    csv_file, json_file = benchmark.run_comprehensive_benchmark()
    print(f"\nTo create plots: gnuplot -e \"datafile='{csv_file}'\" filesystem_comparison.gp")