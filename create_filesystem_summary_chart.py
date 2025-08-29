#!/usr/bin/env python3
"""
Create final summary visualization for filesystem comparison
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Read the comparison data
df = pd.read_csv('filesystem_comparison_i7_16gb_20250829_123852.csv')

# Create figure with subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Filesystem Comparison: Intel i7 16GB System\nMemory & Disk Usage Analysis', fontsize=16, fontweight='bold')

# Colors for each filesystem
colors = {'ext4': '#2E8B57', 'ZFS': '#FF4500', 'Btrfs': '#4169E1', 'N-ary Tree FS': '#8A2BE2'}

# Plot 1: Memory Usage Comparison
ax1.loglog(df['entries'], df['ext4_memory_mb'], 'o-', color=colors['ext4'], linewidth=2, markersize=6, label='ext4')
ax1.loglog(df['entries'], df['zfs_memory_mb'], 's-', color=colors['ZFS'], linewidth=2, markersize=6, label='ZFS')
ax1.loglog(df['entries'], df['btrfs_memory_mb'], '^-', color=colors['Btrfs'], linewidth=2, markersize=6, label='Btrfs')
ax1.loglog(df['entries'], df['narytree_memory_mb'], 'd-', color=colors['N-ary Tree FS'], linewidth=2, markersize=6, label='N-ary Tree FS')

ax1.set_xlabel('Number of Files')
ax1.set_ylabel('Memory Usage (MB)')
ax1.set_title('Memory Usage Comparison (Log Scale)')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot 2: Disk Usage Comparison
ax2.semilogx(df['entries'], df['ext4_disk_mb']/1024, 'o-', color=colors['ext4'], linewidth=2, markersize=6, label='ext4')
ax2.semilogx(df['entries'], df['zfs_disk_mb']/1024, 's-', color=colors['ZFS'], linewidth=2, markersize=6, label='ZFS')  
ax2.semilogx(df['entries'], df['btrfs_disk_mb']/1024, '^-', color=colors['Btrfs'], linewidth=2, markersize=6, label='Btrfs')
ax2.semilogx(df['entries'], df['narytree_disk_mb']/1024, 'd-', color=colors['N-ary Tree FS'], linewidth=2, markersize=6, label='N-ary Tree FS')

ax2.set_xlabel('Number of Files')
ax2.set_ylabel('Disk Usage (GB)')
ax2.set_title('Disk Usage Comparison')
ax2.grid(True, alpha=0.3)
ax2.legend()

# Plot 3: RAM Usage Percentage
ax3.semilogx(df['entries'], df['ext4_ram_percent'], 'o-', color=colors['ext4'], linewidth=2, markersize=6, label='ext4')
ax3.semilogx(df['entries'], df['zfs_ram_percent'], 's-', color=colors['ZFS'], linewidth=2, markersize=6, label='ZFS')
ax3.semilogx(df['entries'], df['btrfs_ram_percent'], '^-', color=colors['Btrfs'], linewidth=2, markersize=6, label='Btrfs')
ax3.semilogx(df['entries'], df['narytree_ram_percent'], 'd-', color=colors['N-ary Tree FS'], linewidth=2, markersize=6, label='N-ary Tree FS')

# Add warning threshold
ax3.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='10% RAM Limit')
ax3.axhline(y=50, color='orange', linestyle='--', alpha=0.7, label='50% RAM Limit')

ax3.set_xlabel('Number of Files')
ax3.set_ylabel('RAM Usage (%)')
ax3.set_title('RAM Usage Percentage (16GB System)')
ax3.set_ylim(0, 50)
ax3.grid(True, alpha=0.3)
ax3.legend()

# Plot 4: Summary Bar Chart (1M files)
filesystems = ['ext4', 'ZFS', 'Btrfs', 'N-ary FS']
memory_1m = [66.95, 7232.8, 46.06, 59.8]  # MB
disk_1m = [109.8, 141.3, 152.4, 134.5]    # GB (converted from MB)

x = np.arange(len(filesystems))
width = 0.35

bars1 = ax4.bar(x - width/2, memory_1m, width, label='Memory (MB)', color=['#2E8B57', '#FF4500', '#4169E1', '#8A2BE2'], alpha=0.8)
ax4_twin = ax4.twinx()
bars2 = ax4_twin.bar(x + width/2, disk_1m, width, label='Disk (GB)', color=['#2E8B57', '#FF4500', '#4169E1', '#8A2BE2'], alpha=0.6)

ax4.set_xlabel('Filesystem')
ax4.set_ylabel('Memory Usage (MB)', color='black')
ax4_twin.set_ylabel('Disk Usage (GB)', color='gray')
ax4.set_title('Memory vs Disk Usage (1M Files)')
ax4.set_xticks(x)
ax4.set_xticklabels(filesystems)

# Add value labels on bars
for i, (mem, disk) in enumerate(zip(memory_1m, disk_1m)):
    if mem > 1000:
        ax4.text(i - width/2, mem + 100, f'{mem:.0f}MB', ha='center', va='bottom', fontsize=10)
    else:
        ax4.text(i - width/2, mem + 5, f'{mem:.0f}MB', ha='center', va='bottom', fontsize=10)
    ax4_twin.text(i + width/2, disk + 2, f'{disk:.0f}GB', ha='center', va='bottom', fontsize=10)

ax4.legend(loc='upper left')
ax4_twin.legend(loc='upper right')
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('filesystem_complete_comparison_summary.png', dpi=300, bbox_inches='tight')
plt.close()

print("Generated filesystem_complete_comparison_summary.png")

# Create efficiency comparison chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Memory Efficiency per Entry
ax1.bar(filesystems, [27, 25, 42, 57], color=['#2E8B57', '#FF4500', '#4169E1', '#8A2BE2'], alpha=0.8)
ax1.set_ylabel('Bytes per Entry')
ax1.set_title('Memory Efficiency\n(Lower = Better)')
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, val in enumerate([27, 25, 42, 57]):
    ax1.text(i, val + 1, f'{val}B', ha='center', va='bottom', fontweight='bold')

# Storage Efficiency Percentage  
efficiencies = [93.3, 72.4, 67.2, 76.2]
ax2.bar(filesystems, efficiencies, color=['#2E8B57', '#FF4500', '#4169E1', '#8A2BE2'], alpha=0.8)
ax2.set_ylabel('Storage Efficiency (%)')
ax2.set_title('Disk Storage Efficiency\n(Higher = Better)')
ax2.set_ylim(60, 100)
ax2.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, val in enumerate(efficiencies):
    ax2.text(i, val + 0.5, f'{val}%', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('filesystem_efficiency_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

print("Generated filesystem_efficiency_comparison.png")