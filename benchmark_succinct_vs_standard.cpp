#include "Modules/nary_tree.cpp"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>
#include <iomanip>

struct BenchmarkResult {
    size_t node_count;
    size_t standard_memory_bytes;
    size_t succinct_memory_bytes;
    double memory_reduction_percent;
    double encode_time_ms;
    double decode_time_ms;
    size_t structure_bits;
    bool integrity_check;
};

NaryTree<std::string> create_balanced_tree(size_t target_nodes) {
    if (target_nodes == 0) return NaryTree<std::string>();
    
    NaryTree<std::string> tree("root_0");
    auto* root = tree.root();
    
    std::vector<NaryTree<std::string>::Node*> current_level = {root};
    size_t nodes_created = 1;
    
    while (nodes_created < target_nodes && !current_level.empty()) {
        std::vector<NaryTree<std::string>::Node*> next_level;
        
        for (auto* node : current_level) {
            // Add 3 children per node for balanced ternary tree
            int children_to_add = std::min((int)(target_nodes - nodes_created), 3);
            for (int i = 0; i < children_to_add; ++i) {
                auto& child = node->add_child("node_" + std::to_string(nodes_created));
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

BenchmarkResult benchmark_tree_size(size_t node_count) {
    std::cout << "Benchmarking " << node_count << " nodes... " << std::flush;
    
    BenchmarkResult result;
    result.node_count = node_count;
    
    // Create test tree
    auto tree = create_balanced_tree(node_count);
    auto stats = tree.get_statistics();
    
    // Calculate standard memory usage (realistic estimate)
    size_t node_overhead = sizeof(void*) * 4 + sizeof(std::vector<void*>) + 16; // 64 bytes per node
    result.standard_memory_bytes = stats.total_nodes * node_overhead;
    
    // Encode to succinct format
    auto start = std::chrono::high_resolution_clock::now();
    auto encoding = tree.encode_succinct();
    auto encode_duration = std::chrono::high_resolution_clock::now() - start;
    result.encode_time_ms = std::chrono::duration<double, std::milli>(encode_duration).count();
    
    result.succinct_memory_bytes = encoding.memory_usage();
    result.structure_bits = encoding.structure_bits.size();
    
    // Test decode
    start = std::chrono::high_resolution_clock::now();
    auto decoded_tree = NaryTree<std::string>::decode_succinct(encoding);
    auto decode_duration = std::chrono::high_resolution_clock::now() - start;
    result.decode_time_ms = std::chrono::duration<double, std::milli>(decode_duration).count();
    
    // Verify integrity
    auto decoded_stats = decoded_tree.get_statistics();
    result.integrity_check = (decoded_stats.total_nodes == stats.total_nodes);
    
    // Calculate efficiency
    result.memory_reduction_percent = 
        (double)(result.standard_memory_bytes - result.succinct_memory_bytes) / 
        result.standard_memory_bytes * 100.0;
    
    std::cout << "Done\n";
    return result;
}

void save_csv_data(const std::vector<BenchmarkResult>& results, const std::string& filename) {
    std::ofstream file(filename);
    file << "nodes,standard_memory_mb,succinct_memory_mb,memory_reduction_percent,";
    file << "encode_time_ms,decode_time_ms,structure_bits,integrity_check\n";
    
    for (const auto& result : results) {
        file << result.node_count << ","
             << result.standard_memory_bytes / (1024.0 * 1024.0) << ","
             << result.succinct_memory_bytes / (1024.0 * 1024.0) << ","
             << result.memory_reduction_percent << ","
             << result.encode_time_ms << ","
             << result.decode_time_ms << ","
             << result.structure_bits << ","
             << (result.integrity_check ? 1 : 0) << "\n";
    }
}

void create_gnuplot_script(const std::string& data_file, const std::string& output_base) {
    std::string script_file = output_base + "_comparison.gp";
    std::ofstream script(script_file);
    
    script << "#!/usr/bin/env gnuplot\n";
    script << "set terminal pngcairo enhanced font 'Arial,12' size 1400,1000\n";
    script << "set output '" << output_base << "_memory_comparison.png'\n\n";
    script << "set multiplot layout 2,2 title \"Standard vs Succinct N-ary Tree Comparison\" font 'Arial,16'\n\n";
    
    script << "# Memory usage comparison\n";
    script << "set title \"Memory Usage: Standard vs Succinct\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Memory Usage (MB)\"\n";
    script << "set logscale xy\n";
    script << "set grid\n";
    script << "plot '" << data_file << "' using 1:2 with linespoints title 'Standard Implementation' lw 2 pt 7, \\\n";
    script << "     '" << data_file << "' using 1:3 with linespoints title 'Succinct Encoding' lw 2 pt 9\n\n";
    
    script << "# Memory reduction percentage\n";
    script << "set title \"Memory Reduction Percentage\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Memory Reduction (%)\"\n";
    script << "unset logscale y\n";
    script << "set logscale x\n";
    script << "plot '" << data_file << "' using 1:4 with linespoints title 'Memory Savings' lw 2 pt 7\n\n";
    
    script << "# Encode/Decode time\n";
    script << "set title \"Encode/Decode Performance\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Time (ms)\"\n";
    script << "set logscale xy\n";
    script << "plot '" << data_file << "' using 1:5 with linespoints title 'Encode Time' lw 2 pt 7, \\\n";
    script << "     '" << data_file << "' using 1:6 with linespoints title 'Decode Time' lw 2 pt 9\n\n";
    
    script << "# Structure bits vs theoretical\n";
    script << "set title \"Structure Bits vs Theoretical Minimum\"\n";
    script << "set xlabel \"Number of Nodes\"\n";
    script << "set ylabel \"Structure Bits\"\n";
    script << "set logscale xy\n";
    script << "plot '" << data_file << "' using 1:7 with linespoints title 'Actual Structure Bits' lw 2 pt 7, \\\n";
    script << "     '" << data_file << "' using 1:($1*2) with lines title 'Theoretical Minimum (2n)' lw 2\n\n";
    script << "unset multiplot\n";
    
    std::cout << "Created gnuplot script: " << script_file << std::endl;
}

int main() {
    std::cout << "Large-Scale Succinct N-ary Tree Benchmark\n";
    std::cout << "==========================================\n\n";
    
    // Progressive test sizes: 10M, 100M, 1B nodes
    std::vector<size_t> test_sizes = {
        1000,      // 1K
        10000,     // 10K  
        100000,    // 100K
        1000000,   // 1M
        10000000,  // 10M
        100000000  // 100M (as requested)
    };
    
    std::vector<BenchmarkResult> results;
    
    for (size_t size : test_sizes) {
        try {
            auto result = benchmark_tree_size(size);
            results.push_back(result);
            
            // Print immediate results
            std::cout << "  Standard: " << result.standard_memory_bytes / (1024*1024) << " MB\n";
            std::cout << "  Succinct: " << result.succinct_memory_bytes / (1024*1024) << " MB\n";
            std::cout << "  Reduction: " << std::fixed << std::setprecision(1) 
                     << result.memory_reduction_percent << "%\n";
            std::cout << "  Encode: " << std::setprecision(2) << result.encode_time_ms << " ms\n\n";
            
        } catch (const std::exception& e) {
            std::cout << "Failed: " << e.what() << "\n\n";
            break;
        }
    }
    
    if (!results.empty()) {
        // Save data and create plots
        std::string timestamp = "20250829_" + std::to_string(
            std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()).count() % 100000);
        
        std::string data_file = "succinct_vs_standard_" + timestamp + ".csv";
        std::string output_base = "succinct_vs_standard_" + timestamp;
        
        save_csv_data(results, data_file);
        create_gnuplot_script(data_file, output_base);
        
        std::cout << "=== Final Results Summary ===\n";
        std::cout << std::setw(12) << "Nodes" << std::setw(15) << "Standard(MB)" 
                 << std::setw(15) << "Succinct(MB)" << std::setw(15) << "Reduction(%)" << std::endl;
        std::cout << std::string(60, '-') << std::endl;
        
        for (const auto& result : results) {
            std::cout << std::setw(12) << result.node_count 
                     << std::setw(15) << std::fixed << std::setprecision(2) 
                     << result.standard_memory_bytes / (1024.0*1024.0)
                     << std::setw(15) << result.succinct_memory_bytes / (1024.0*1024.0)
                     << std::setw(14) << std::setprecision(1) << result.memory_reduction_percent << "%"
                     << std::endl;
        }
        
        std::cout << "\nRun: gnuplot " << output_base << "_comparison.gp\n";
        std::cout << "Data saved: " << data_file << std::endl;
    }
    
    return 0;
}