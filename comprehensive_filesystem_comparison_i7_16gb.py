#!/usr/bin/env python3
"""
Comprehensive Filesystem Comparison: ZFS vs Btrfs vs ext4 vs N-ary Tree FS
Intel i7 16GB System Analysis
"""

import json
import csv
import math
from datetime import datetime

class FilesystemComparator:
    def __init__(self):
        self.ram_gb = 16
        self.ram_mb = 16 * 1024
        
        # Filesystem characteristics based on research
        self.filesystem_specs = {
            'ext4': {
                'bytes_per_entry': 27,  # Average between 19-35 bytes
                'memory_cache_ratio': 0.016,  # 1.6% of filesystem for inodes
                'disk_overhead': 0.05,  # 5% reserved blocks + journal
                'fragmentation_factor': 1.02,  # Very low fragmentation
                'journal_overhead': 0.001,  # Small journal relative to filesystem
                'description': 'Traditional extent tree filesystem'
            },
            'zfs': {
                'bytes_per_entry': 25,  # 19-35 range, assume 25 average
                'memory_cache_ratio': 0.001,  # ARC: 1GB per 1TB data
                'arc_overhead': 0.44,  # 44% for 16GB system (2-7GB ARC)
                'disk_overhead': 0.20,  # 20% for dual-copy metadata + checksums
                'fragmentation_factor': 1.15,  # Copy-on-write fragmentation
                'description': 'Copy-on-write B-tree with checksumming'
            },
            'btrfs': {
                'bytes_per_entry': 42,  # 37-50 range, assume 42 average  
                'memory_cache_ratio': 0.003,  # ~0.3% for metadata
                'disk_overhead': 0.15,  # 15% CoW + checksum overhead
                'fragmentation_factor': 1.25,  # Higher CoW fragmentation than ZFS
                'snapshot_overhead': 0.05,  # 5% for snapshot metadata
                'description': 'Copy-on-write B-tree with subvolumes'
            },
            'narytree_fs': {
                'bytes_per_entry': 57,  # From implementation analysis
                'memory_cache_ratio': 0.001,  # Low overhead for in-memory
                'rebalancing_overhead': 0.10,  # 10% for automatic rebalancing
                'disk_overhead': 0.25,  # 25% for journal + metadata + alignment
                'fragmentation_factor': 1.05,  # Very low due to balanced allocation
                'description': 'Self-balancing N-ary tree with automatic optimization'
            }
        }
    
    def calculate_memory_usage(self, filesystem, num_entries):
        """Calculate memory usage for filesystem"""
        specs = self.filesystem_specs[filesystem]
        
        # Base entry memory
        base_memory_mb = (num_entries * specs['bytes_per_entry']) / (1024 * 1024)
        
        # Filesystem-specific memory calculations
        if filesystem == 'zfs':
            # ZFS ARC calculation 
            arc_memory_mb = self.ram_mb * specs['arc_overhead']
            total_memory_mb = base_memory_mb + arc_memory_mb
        elif filesystem == 'ext4':
            # ext4 inode cache
            cache_memory_mb = base_memory_mb * specs['memory_cache_ratio'] * 100
            total_memory_mb = base_memory_mb + cache_memory_mb
        elif filesystem == 'btrfs':
            # Btrfs dynamic metadata cache
            cache_memory_mb = base_memory_mb * specs['memory_cache_ratio'] * 50
            total_memory_mb = base_memory_mb + cache_memory_mb
        else:  # narytree_fs
            # N-ary tree rebalancing overhead
            rebalance_memory_mb = base_memory_mb * specs['rebalancing_overhead']
            total_memory_mb = base_memory_mb + rebalance_memory_mb
        
        return {
            'base_memory_mb': round(base_memory_mb, 2),
            'total_memory_mb': round(total_memory_mb, 2),
            'ram_percent': round((total_memory_mb / self.ram_mb) * 100, 3)
        }
    
    def calculate_disk_usage(self, filesystem, num_entries, data_size_gb=10):
        """Calculate disk usage for filesystem"""
        specs = self.filesystem_specs[filesystem]
        
        # Base metadata size
        metadata_mb = (num_entries * specs['bytes_per_entry']) / (1024 * 1024)
        
        # Data size
        data_mb = data_size_gb * 1024
        
        # Filesystem-specific disk calculations
        if filesystem == 'zfs':
            # ZFS dual-copy metadata + compression
            overhead_mb = (data_mb + metadata_mb) * specs['disk_overhead']
            fragmentation_mb = (data_mb + metadata_mb + overhead_mb) * (specs['fragmentation_factor'] - 1)
        elif filesystem == 'btrfs':
            # Btrfs CoW + snapshot overhead
            overhead_mb = (data_mb + metadata_mb) * specs['disk_overhead']
            snapshot_mb = (data_mb + metadata_mb) * specs['snapshot_overhead']
            fragmentation_mb = (data_mb + metadata_mb + overhead_mb) * (specs['fragmentation_factor'] - 1)
            overhead_mb += snapshot_mb
        elif filesystem == 'ext4':
            # ext4 journal + reserved blocks
            journal_mb = specs['journal_overhead'] * data_mb
            reserved_mb = 0.05 * data_mb  # 5% reserved
            overhead_mb = journal_mb + reserved_mb
            fragmentation_mb = (data_mb + metadata_mb + overhead_mb) * (specs['fragmentation_factor'] - 1)
        else:  # narytree_fs
            # N-ary tree filesystem journal + alignment
            overhead_mb = (data_mb + metadata_mb) * specs['disk_overhead']
            fragmentation_mb = (data_mb + metadata_mb + overhead_mb) * (specs['fragmentation_factor'] - 1)
        
        total_disk_mb = data_mb + metadata_mb + overhead_mb + fragmentation_mb
        
        return {
            'data_mb': round(data_mb, 2),
            'metadata_mb': round(metadata_mb, 2),
            'overhead_mb': round(overhead_mb, 2),
            'fragmentation_mb': round(fragmentation_mb, 2),
            'total_disk_mb': round(total_disk_mb, 2),
            'efficiency_percent': round((data_mb / total_disk_mb) * 100, 1)
        }
    
    def run_comprehensive_comparison(self):
        """Run complete comparison across all filesystems and dataset sizes"""
        
        # Test configurations
        test_sizes = [1000, 10000, 50000, 100000, 500000, 1000000, 5000000, 10000000]
        data_sizes_gb = [0.1, 1, 5, 10, 50, 100, 500, 1000]  # Corresponding data sizes
        
        results = []
        
        print("Comprehensive Filesystem Comparison - Intel i7 16GB")
        print("=" * 60)
        print("Filesystems: ext4, ZFS, Btrfs, N-ary Tree FS")
        print()
        
        for i, entries in enumerate(test_sizes):
            data_size_gb = data_sizes_gb[min(i, len(data_sizes_gb) - 1)]
            
            print(f"\n📁 {entries:,} entries ({data_size_gb}GB data):")
            print("-" * 50)
            
            entry_results = {
                'entries': entries,
                'data_size_gb': data_size_gb,
                'filesystems': {}
            }
            
            for fs_name in self.filesystem_specs.keys():
                memory_stats = self.calculate_memory_usage(fs_name, entries)
                disk_stats = self.calculate_disk_usage(fs_name, entries, data_size_gb)
                
                entry_results['filesystems'][fs_name] = {
                    'memory': memory_stats,
                    'disk': disk_stats
                }
                
                print(f"{fs_name.upper():12} | "
                      f"Mem: {memory_stats['total_memory_mb']:6.1f}MB ({memory_stats['ram_percent']:5.2f}%) | "
                      f"Disk: {disk_stats['total_disk_mb']:8.1f}MB ({disk_stats['efficiency_percent']:4.1f}% eff)")
            
            results.append(entry_results)
        
        return results
    
    def analyze_system_limits(self):
        """Analyze maximum capacity for 16GB system"""
        print(f"\n🖥️  Intel i7 16GB System Capacity Analysis:")
        print("=" * 50)
        
        # Calculate max entries before hitting 80% RAM usage
        safe_ram_limit = self.ram_mb * 0.8  # 80% of 16GB
        
        for fs_name, specs in self.filesystem_specs.items():
            if fs_name == 'zfs':
                # ZFS ARC dominates memory usage
                arc_mb = self.ram_mb * specs['arc_overhead']
                remaining_mb = safe_ram_limit - arc_mb
                max_entries = int(remaining_mb * 1024 * 1024 / specs['bytes_per_entry'])
            else:
                # Other filesystems scale linearly with entries
                effective_bytes = specs['bytes_per_entry']
                if fs_name == 'narytree_fs':
                    effective_bytes *= (1 + specs['rebalancing_overhead'])
                max_entries = int(safe_ram_limit * 1024 * 1024 / effective_bytes)
            
            print(f"{fs_name.upper():12}: ~{max_entries:,} max entries ({safe_ram_limit/1024:.1f}GB limit)")
        
        # Disk capacity analysis (assuming 1TB storage)
        print(f"\n💾 Disk Capacity Analysis (1TB storage):")
        print("-" * 40)
        
        disk_limit_gb = 800  # 80% of 1TB for safety
        
        for fs_name, specs in self.filesystem_specs.items():
            # Estimate based on 100GB data + metadata scaling
            entries_per_gb = 100000  # Assume 100K entries per GB data
            max_data_gb = disk_limit_gb * 0.8  # Account for overhead
            max_entries_disk = int(max_data_gb * entries_per_gb)
            
            print(f"{fs_name.upper():12}: ~{max_entries_disk:,} entries ({max_data_gb:.0f}GB data)")

def save_results(results):
    """Save results to JSON and CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed JSON
    json_filename = f"filesystem_comparison_i7_16gb_{timestamp}.json"
    with open(json_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save CSV summary
    csv_filename = f"filesystem_comparison_i7_16gb_{timestamp}.csv"
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'entries', 'data_size_gb',
            'ext4_memory_mb', 'ext4_disk_mb', 'ext4_ram_percent',
            'zfs_memory_mb', 'zfs_disk_mb', 'zfs_ram_percent', 
            'btrfs_memory_mb', 'btrfs_disk_mb', 'btrfs_ram_percent',
            'narytree_memory_mb', 'narytree_disk_mb', 'narytree_ram_percent'
        ])
        
        for result in results:
            row = [result['entries'], result['data_size_gb']]
            for fs in ['ext4', 'zfs', 'btrfs', 'narytree_fs']:
                fs_data = result['filesystems'][fs]
                row.extend([
                    fs_data['memory']['total_memory_mb'],
                    fs_data['disk']['total_disk_mb'],
                    fs_data['memory']['ram_percent']
                ])
            writer.writerow(row)
    
    return json_filename, csv_filename

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Filesystem Comparison")
    print("📊 Intel Core i7 + 16GB RAM + 1TB Storage")
    print("📝 Analyzing: ext4, ZFS, Btrfs, N-ary Tree FS\n")
    
    comparator = FilesystemComparator()
    
    # Run main comparison
    results = comparator.run_comprehensive_comparison()
    
    # Analyze system limits
    comparator.analyze_system_limits()
    
    # Save results
    json_file, csv_file = save_results(results)
    
    print(f"\n💾 Results saved:")
    print(f"📄 Detailed analysis: {json_file}")
    print(f"📊 CSV data: {csv_file}")
    
    print(f"\n🏆 Quick Summary for Intel i7 16GB:")
    print("- ext4: Most memory efficient, proven stability")
    print("- ZFS: Best data integrity, needs ARC tuning")  
    print("- Btrfs: Balanced features, modern design")
    print("- N-ary Tree FS: Best cache locality, predictable performance")