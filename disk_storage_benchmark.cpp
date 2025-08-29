#include "Modules/nary_tree.cpp"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>
#include <iomanip>
#include <filesystem>

struct DiskBenchmarkResult {
    size_t node_count;
    size_t standard_disk_bytes;
    size_t succinct_disk_bytes;
    double disk_reduction_percent;
    double save_time_ms;
    double load_time_ms;
    size_t structure_bits;
    bool integrity_check;
};

NaryTree<std::string> create_test_tree(size_t target_nodes) {
    if (target_nodes == 0) return NaryTree<std::string>();
    
    NaryTree<std::string> tree("root_" + std::to_string(0));
    auto* root = tree.root();
    
    std::vector<NaryTree<std::string>::Node*> current_level = {root};
    size_t nodes_created = 1;
    
    while (nodes_created < target_nodes && !current_level.empty()) {
        std::vector<NaryTree<std::string>::Node*> next_level;
        
        for (auto* node : current_level) {
            int children_to_add = std::min((int)(target_nodes - nodes_created), 3);
            for (int i = 0; i < children_to_add; ++i) {
                auto& child = node->add_child("data_" + std::to_string(nodes_created));
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

void save_standard_format(const NaryTree<std::string>& tree, const std::string& filename) {
    std::ofstream file(filename, std::ios::binary);
    
    // Simple serialization: each node as "parent_id:node_id:data\n"
    std::function<void(const NaryTree<std::string>::Node*, int, int&)> serialize;
    serialize = [&](const NaryTree<std::string>::Node* node, int parent_id, int& next_id) {
        if (!node) return;
        int current_id = next_id++;
        file << parent_id << ":" << current_id << ":" << node->data() << "\n";
        
        for (size_t i = 0; i < node->child_count(); ++i) {
            serialize(&node->child(i), current_id, next_id);
        }
    };
    
    int id = 0;
    serialize(tree.root(), -1, id);
}

void save_succinct_format(const typename NaryTree<std::string>::SuccinctEncoding& encoding, const std::string& filename) {
    std::ofstream file(filename, std::ios::binary);
    
    // Write header
    size_t node_count = encoding.node_count;
    file.write(reinterpret_cast<const char*>(&node_count), sizeof(node_count));
    
    // Write structure bits (pack into bytes)
    size_t bit_count = encoding.structure_bits.size();
    file.write(reinterpret_cast<const char*>(&bit_count), sizeof(bit_count));
    
    // Pack bits into bytes
    std::vector<uint8_t> packed_bits((bit_count + 7) / 8, 0);
    for (size_t i = 0; i < bit_count; ++i) {
        if (encoding.structure_bits[i]) {
            packed_bits[i / 8] |= (1 << (i % 8));
        }
    }
    file.write(reinterpret_cast<const char*>(packed_bits.data()), packed_bits.size());
    
    // Write data array
    size_t data_count = encoding.data_array.size();
    file.write(reinterpret_cast<const char*>(&data_count), sizeof(data_count));
    for (const auto& data : encoding.data_array) {
        size_t str_len = data.length();
        file.write(reinterpret_cast<const char*>(&str_len), sizeof(str_len));
        file.write(data.c_str(), str_len);
    }
}

DiskBenchmarkResult benchmark_disk_storage(size_t node_count) {
    std::cout << "Disk benchmark " << node_count << " nodes... " << std::flush;
    
    DiskBenchmarkResult result;
    result.node_count = node_count;
    
    // Create test tree
    auto tree = create_test_tree(node_count);
    
    // Save standard format
    std::string standard_file = "standard_" + std::to_string(node_count) + ".dat";
    auto start = std::chrono::high_resolution_clock::now();
    save_standard_format(tree, standard_file);
    auto save_standard_time = std::chrono::duration<double, std::milli>(
        std::chrono::high_resolution_clock::now() - start).count();
    
    // Get standard file size
    result.standard_disk_bytes = std::filesystem::file_size(standard_file);
    
    // Encode to succinct
    start = std::chrono::high_resolution_clock::now();
    auto encoding = tree.encode_succinct();
    auto encode_time = std::chrono::duration<double, std::milli>(
        std::chrono::high_resolution_clock::now() - start).count();
    
    // Save succinct format
    std::string succinct_file = "succinct_" + std::to_string(node_count) + ".dat";
    start = std::chrono::high_resolution_clock::now();
    save_succinct_format(encoding, succinct_file);
    result.save_time_ms = std::chrono::duration<double, std::milli>(
        std::chrono::high_resolution_clock::now() - start).count() + encode_time;
    
    // Get succinct file size
    result.succinct_disk_bytes = std::filesystem::file_size(succinct_file);
    result.structure_bits = encoding.structure_bits.size();
    
    // Test loading (just measure decode time)
    start = std::chrono::high_resolution_clock::now();
    auto decoded_tree = NaryTree<std::string>::decode_succinct(encoding);
    result.load_time_ms = std::chrono::duration<double, std::milli>(
        std::chrono::high_resolution_clock::now() - start).count();
    
    // Verify integrity
    result.integrity_check = (decoded_tree.size() == tree.size());
    
    // Calculate disk reduction
    result.disk_reduction_percent = 
        (double)(result.standard_disk_bytes - result.succinct_disk_bytes) / 
        result.standard_disk_bytes * 100.0;
    
    // Cleanup temp files
    std::filesystem::remove(standard_file);
    std::filesystem::remove(succinct_file);
    
    std::cout << "Done\n";
    return result;
}

void save_disk_csv(const std::vector<DiskBenchmarkResult>& results, const std::string& filename) {
    std::ofstream file(filename);
    file << "nodes,standard_disk_mb,succinct_disk_mb,disk_reduction_percent,";
    file << "save_time_ms,load_time_ms,structure_bits,integrity_check\n";
    
    for (const auto& result : results) {
        file << result.node_count << ","
             << result.standard_disk_bytes / (1024.0 * 1024.0) << ","
             << result.succinct_disk_bytes / (1024.0 * 1024.0) << ","
             << result.disk_reduction_percent << ","
             << result.save_time_ms << ","
             << result.load_time_ms << ","
             << result.structure_bits << ","
             << (result.integrity_check ? 1 : 0) << "\n";
    }
}

void create_disk_gnuplot_script(const std::string& data_file, const std::string& output_base) {
    std::string script_file = output_base + "_disk_comparison.gp";
    std::ofstream script(script_file);
    
    script << "#!/usr/bin/env gnuplot\n";
    script << "set terminal pngcairo enhanced font 'Arial,14' size 1400,1000\n";
    script << "set output '" << output_base << "_disk_analysis.png'\n\n";
    script << "set datafile separator \",\"\n";
    script << "set key outside right\n\n";
    script << "set multiplot layout 2,2 title \"Disk Storage: Standard vs Succinct N-ary Tree\" font 'Arial,16'\n\n";
    
    script << "# Disk usage comparison\n";
    script << "set title \"Disk Usage: Standard vs Succinct\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Disk Usage (MB)\"\n";
    script << "set logscale xy\n";
    script << "set grid\n";
    script << "plot '" << data_file << "' using 1:2 with linespoints title 'Standard Format' lw 3 pt 7 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:3 with linespoints title 'Succinct Format' lw 3 pt 9 ps 1.5\n\n";
    
    script << "# Disk reduction percentage\n";
    script << "set title \"Disk Space Reduction\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Disk Reduction (%)\"\n";
    script << "unset logscale y\n";
    script << "set logscale x\n";
    script << "plot '" << data_file << "' using 1:4 with linespoints title 'Disk Savings' lw 3 pt 7 ps 1.5\n\n";
    
    script << "# Save/Load performance\n";
    script << "set title \"Save/Load Performance\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Time (ms)\"\n";
    script << "set logscale xy\n";
    script << "plot '" << data_file << "' using 1:5 with linespoints title 'Save Time' lw 3 pt 7 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:6 with linespoints title 'Load Time' lw 3 pt 9 ps 1.5\n\n";
    
    script << "# Progressive data growth\n";
    script << "set title \"Progressive Disk Space Growth\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Cumulative Disk Space (MB)\"\n";
    script << "set logscale xy\n";
    script << "plot '" << data_file << "' using 1:($2) with linespoints title 'Standard Cumulative' lw 3 pt 7 ps 1.5, \\\n";
    script << "     '" << data_file << "' using 1:($3) with linespoints title 'Succinct Cumulative' lw 3 pt 9 ps 1.5\n\n";
    
    script << "unset multiplot\n";
}

int main() {
    std::cout << "Disk Storage Benchmark: Standard vs Succinct N-ary Tree\n";
    std::cout << "======================================================\n\n";
    
    std::vector<size_t> test_sizes = {
        1000,      // 1K
        10000,     // 10K  
        100000,    // 100K
        1000000,   // 1M
        10000000   // 10M
    };
    
    std::vector<DiskBenchmarkResult> results;
    
    for (size_t size : test_sizes) {
        try {
            auto result = benchmark_disk_storage(size);
            results.push_back(result);
            
            std::cout << "  Standard disk: " << result.standard_disk_bytes / (1024*1024) << " MB\n";
            std::cout << "  Succinct disk: " << result.succinct_disk_bytes / (1024*1024) << " MB\n";
            std::cout << "  Disk reduction: " << std::fixed << std::setprecision(1) 
                     << result.disk_reduction_percent << "%\n";
            std::cout << "  Save time: " << std::setprecision(2) << result.save_time_ms << " ms\n\n";
            
        } catch (const std::exception& e) {
            std::cout << "Failed: " << e.what() << "\n\n";
            break;
        }
    }
    
    if (!results.empty()) {
        std::string timestamp = "20250829_" + std::to_string(
            std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()).count() % 100000);
        
        std::string data_file = "disk_progressive_" + timestamp + ".csv";
        std::string output_base = "disk_progressive_" + timestamp;
        
        save_disk_csv(results, data_file);
        create_disk_gnuplot_script(data_file, output_base);
        
        std::cout << "=== Progressive Disk Usage Results ===\n";
        std::cout << std::setw(12) << "Nodes" << std::setw(15) << "Standard(MB)" 
                 << std::setw(15) << "Succinct(MB)" << std::setw(15) << "Reduction(%)" << std::endl;
        std::cout << std::string(60, '-') << std::endl;
        
        for (const auto& result : results) {
            std::cout << std::setw(12) << result.node_count 
                     << std::setw(15) << std::fixed << std::setprecision(2) 
                     << result.standard_disk_bytes / (1024.0*1024.0)
                     << std::setw(15) << result.succinct_disk_bytes / (1024.0*1024.0)
                     << std::setw(14) << std::setprecision(1) << result.disk_reduction_percent << "%"
                     << std::endl;
        }
        
        std::cout << "\nRun: gnuplot " << output_base << "_disk_comparison.gp\n";
        std::cout << "Data saved: " << data_file << std::endl;
    }
    
    return 0;
}