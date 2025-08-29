#include "Modules/nary_tree.cpp"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>
#include <iomanip>
#include <filesystem>
#include <cstdlib>

struct FilesystemBenchmarkResult {
    size_t node_count;
    size_t ext4_memory_kb;
    size_t btrfs_memory_kb; 
    size_t zfs_memory_kb;
    size_t succinct_memory_kb;
    size_t ext4_disk_kb;
    size_t btrfs_disk_kb;
    size_t zfs_disk_kb;
    size_t succinct_disk_kb;
    double creation_time_ms;
};

NaryTree<std::string> create_filesystem_tree(size_t target_nodes) {
    if (target_nodes == 0) return NaryTree<std::string>();
    
    NaryTree<std::string> tree("root_directory");
    auto* root = tree.root();
    
    std::vector<NaryTree<std::string>::Node*> current_level = {root};
    size_t nodes_created = 1;
    
    while (nodes_created < target_nodes && !current_level.empty()) {
        std::vector<NaryTree<std::string>::Node*> next_level;
        
        for (auto* node : current_level) {
            int children_to_add = std::min((int)(target_nodes - nodes_created), 4); // Average 4 files per dir
            for (int i = 0; i < children_to_add; ++i) {
                std::string name = (i % 2 == 0) ? 
                    "file_" + std::to_string(nodes_created) + ".txt" :
                    "dir_" + std::to_string(nodes_created);
                auto& child = node->add_child(name);
                next_level.push_back(&child);
                nodes_created++;
                if (nodes_created >= target_nodes) break;
            }
            if (nodes_created >= target_nodes) break;
        }
        current_level = std::move(next_level);
    }
    
    return tree;
}

// Simulate filesystem metadata overhead
size_t estimate_ext4_overhead(size_t node_count) {
    // ext4: ~256 bytes per inode + directory entry overhead
    return node_count * (256 + 32); // inode + dentry
}

size_t estimate_btrfs_overhead(size_t node_count) {
    // BTRFS: ~512 bytes per inode + B-tree overhead
    return node_count * (512 + 64); // larger inodes + btree overhead
}

size_t estimate_zfs_overhead(size_t node_count) {
    // ZFS: ~320 bytes per inode + additional metadata
    return node_count * (320 + 48); // znode + metadata
}

FilesystemBenchmarkResult benchmark_filesystem_comparison(size_t node_count) {
    std::cout << "Filesystem benchmark " << node_count << " nodes... " << std::flush;
    
    FilesystemBenchmarkResult result;
    result.node_count = node_count;
    
    // Create filesystem tree
    auto start = std::chrono::high_resolution_clock::now();
    auto tree = create_filesystem_tree(node_count);
    auto creation_duration = std::chrono::high_resolution_clock::now() - start;
    result.creation_time_ms = std::chrono::duration<double, std::milli>(creation_duration).count();
    
    // Filesystem metadata estimates (in memory)
    result.ext4_memory_kb = estimate_ext4_overhead(node_count) / 1024;
    result.btrfs_memory_kb = estimate_btrfs_overhead(node_count) / 1024;
    result.zfs_memory_kb = estimate_zfs_overhead(node_count) / 1024;
    
    // Succinct implementation memory
    auto encoding = tree.encode_succinct();
    result.succinct_memory_kb = encoding.memory_usage() / 1024;
    
    // Disk usage estimates (assume 4KB blocks)
    size_t block_size = 4096;
    result.ext4_disk_kb = ((estimate_ext4_overhead(node_count) + block_size - 1) / block_size) * block_size / 1024;
    result.btrfs_disk_kb = ((estimate_btrfs_overhead(node_count) + block_size - 1) / block_size) * block_size / 1024;
    result.zfs_disk_kb = ((estimate_zfs_overhead(node_count) + block_size - 1) / block_size) * block_size / 1024;
    result.succinct_disk_kb = ((encoding.memory_usage() + block_size - 1) / block_size) * block_size / 1024;
    
    std::cout << "Done\n";
    return result;
}

void save_filesystem_csv(const std::vector<FilesystemBenchmarkResult>& results, const std::string& filename) {
    std::ofstream file(filename);
    file << "nodes,ext4_memory_kb,btrfs_memory_kb,zfs_memory_kb,succinct_memory_kb,";
    file << "ext4_disk_kb,btrfs_disk_kb,zfs_disk_kb,succinct_disk_kb,creation_time_ms\n";
    
    for (const auto& result : results) {
        file << result.node_count << ","
             << result.ext4_memory_kb << ","
             << result.btrfs_memory_kb << ","
             << result.zfs_memory_kb << ","
             << result.succinct_memory_kb << ","
             << result.ext4_disk_kb << ","
             << result.btrfs_disk_kb << ","
             << result.zfs_disk_kb << ","
             << result.succinct_disk_kb << ","
             << result.creation_time_ms << "\n";
    }
}

void create_filesystem_gnuplot_script(const std::string& data_file, const std::string& output_base) {
    std::string script_file = output_base + "_filesystem_comparison.gp";
    std::ofstream script(script_file);
    
    script << "#!/usr/bin/env gnuplot\n";
    script << "set terminal pngcairo enhanced font 'Arial,14' size 1600,1200\n";
    script << "set output '" << output_base << "_filesystem_analysis.png'\n\n";
    script << "set datafile separator \",\"\n";
    script << "set key outside right\n\n";
    script << "set multiplot layout 2,2 title \"Filesystem vs Succinct N-ary Tree Comparison\" font 'Arial,18'\n\n";
    
    script << "# Memory usage comparison\n";
    script << "set title \"Memory Usage: Filesystems vs Succinct\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Memory Usage (KB)\"\n";
    script << "set logscale xy\n";
    script << "set grid\n";
    script << "plot '" << data_file << "' using 1:2 with linespoints title 'ext4' lw 3 pt 7 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:3 with linespoints title 'BTRFS' lw 3 pt 9 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:4 with linespoints title 'ZFS' lw 3 pt 11 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:5 with linespoints title 'Succinct' lw 4 pt 13 ps 2.0\n\n";
    
    script << "# Disk usage comparison\n";
    script << "set title \"Disk Usage: Filesystems vs Succinct\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Disk Usage (KB)\"\n";
    script << "set logscale xy\n";
    script << "plot '" << data_file << "' using 1:6 with linespoints title 'ext4' lw 3 pt 7 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:7 with linespoints title 'BTRFS' lw 3 pt 9 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:8 with linespoints title 'ZFS' lw 3 pt 11 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:9 with linespoints title 'Succinct' lw 4 pt 13 ps 2.0\n\n";
    
    script << "# Memory efficiency comparison\n";
    script << "set title \"Memory Efficiency: Succinct vs Filesystems\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Memory Reduction vs ext4 (%)\"\n";
    script << "unset logscale y\n";
    script << "set logscale x\n";
    script << "plot '" << data_file << "' using 1:(($2-$5)/$2*100) with linespoints title 'vs ext4' lw 3 pt 7 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:(($3-$5)/$3*100) with linespoints title 'vs BTRFS' lw 3 pt 9 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:(($4-$5)/$4*100) with linespoints title 'vs ZFS' lw 3 pt 11 ps 1.5\n\n";
    
    script << "# Disk efficiency comparison\n";
    script << "set title \"Disk Efficiency: Succinct vs Filesystems\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Disk Reduction vs ext4 (%)\"\n";
    script << "plot '" << data_file << "' using 1:(($6-$9)/$6*100) with linespoints title 'vs ext4' lw 3 pt 7 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:(($7-$9)/$7*100) with linespoints title 'vs BTRFS' lw 3 pt 9 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:(($8-$9)/$8*100) with linespoints title 'vs ZFS' lw 3 pt 11 ps 1.5\n\n";
    
    script << "unset multiplot\n";
}

int main() {
    std::cout << "Filesystem vs Succinct N-ary Tree Comparison\n";
    std::cout << "============================================\n\n";
    
    std::vector<size_t> test_sizes = {
        1000,      // 1K
        10000,     // 10K  
        100000,    // 100K
        1000000,   // 1M
        10000000   // 10M
    };
    
    std::vector<FilesystemBenchmarkResult> results;
    
    for (size_t size : test_sizes) {
        try {
            auto result = benchmark_filesystem_comparison(size);
            results.push_back(result);
            
            std::cout << "  ext4 memory: " << result.ext4_memory_kb / 1024 << " MB\n";
            std::cout << "  BTRFS memory: " << result.btrfs_memory_kb / 1024 << " MB\n";
            std::cout << "  ZFS memory: " << result.zfs_memory_kb / 1024 << " MB\n";
            std::cout << "  Succinct memory: " << result.succinct_memory_kb / 1024 << " MB\n";
            std::cout << "  Succinct vs ext4: " << std::fixed << std::setprecision(1)
                     << (double)(result.ext4_memory_kb - result.succinct_memory_kb) / result.ext4_memory_kb * 100 << "% reduction\n\n";
            
        } catch (const std::exception& e) {
            std::cout << "Failed: " << e.what() << "\n\n";
            break;
        }
    }
    
    if (!results.empty()) {
        std::string timestamp = "20250829_" + std::to_string(
            std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()).count() % 100000);
        
        std::string data_file = "filesystem_comparison_" + timestamp + ".csv";
        std::string output_base = "filesystem_comparison_" + timestamp;
        
        save_filesystem_csv(results, data_file);
        create_filesystem_gnuplot_script(data_file, output_base);
        
        std::cout << "=== Filesystem vs Succinct Comparison ===\n";
        std::cout << std::setw(10) << "Nodes" << std::setw(12) << "ext4(MB)" << std::setw(12) << "BTRFS(MB)" 
                 << std::setw(12) << "ZFS(MB)" << std::setw(15) << "Succinct(MB)" << std::setw(15) << "vs ext4(%)" << std::endl;
        std::cout << std::string(85, '-') << std::endl;
        
        for (const auto& result : results) {
            double reduction = (double)(result.ext4_memory_kb - result.succinct_memory_kb) / result.ext4_memory_kb * 100;
            std::cout << std::setw(10) << result.node_count 
                     << std::setw(12) << std::fixed << std::setprecision(1) << result.ext4_memory_kb / 1024.0
                     << std::setw(12) << result.btrfs_memory_kb / 1024.0
                     << std::setw(12) << result.zfs_memory_kb / 1024.0
                     << std::setw(15) << result.succinct_memory_kb / 1024.0
                     << std::setw(14) << std::setprecision(1) << reduction << "%"
                     << std::endl;
        }
        
        std::cout << "\nRun: gnuplot " << output_base << "_filesystem_comparison.gp\n";
        std::cout << "Data saved: " << data_file << std::endl;
    }
    
    return 0;
}