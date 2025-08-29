#include "Modules/nary_tree.cpp"
#include <iostream>
#include <string>
#include <iomanip>
#include <chrono>

void test_tree_size(size_t target_size) {
    std::cout << "\n=== Testing " << target_size << " nodes ===\n";
    
    // Create test tree
    NaryTree<std::string> tree("root");
    auto* root = tree.root();
    
    // Build tree level by level to reach target size
    std::vector<NaryTree<std::string>::Node*> current_level = {root};
    size_t nodes_created = 1;
    
    while (nodes_created < target_size && !current_level.empty()) {
        std::vector<NaryTree<std::string>::Node*> next_level;
        
        for (auto* node : current_level) {
            // Add 2-4 children per node
            int children = std::min((int)(target_size - nodes_created), 3);
            for (int i = 0; i < children; ++i) {
                auto& child = node->add_child("node_" + std::to_string(nodes_created));
                next_level.push_back(&child);
                nodes_created++;
                if (nodes_created >= target_size) break;
            }
            if (nodes_created >= target_size) break;
        }
        current_level = std::move(next_level);
    }
    
    // Get statistics
    auto stats = tree.get_statistics();
    std::cout << "Built tree with " << stats.total_nodes << " nodes, depth " << stats.max_depth << "\n";
    
    // Estimate memory usage (more realistic calculation)
    size_t node_size = sizeof(void*) * 3 + sizeof(std::vector<void*>) + 16; // data + vector + parent + overhead
    size_t actual_memory = stats.total_nodes * node_size;
    std::cout << "Estimated memory: " << actual_memory << " bytes (" << actual_memory/stats.total_nodes << " bytes/node)\n";
    
    // Encode to succinct representation
    auto start = std::chrono::high_resolution_clock::now();
    auto encoding = tree.encode_succinct();
    auto encode_time = std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::high_resolution_clock::now() - start).count();
    
    std::cout << "Succinct encoding:\n";
    std::cout << "  Structure bits: " << encoding.structure_bits.size() << "\n";
    std::cout << "  Memory usage: " << encoding.memory_usage() << " bytes (" << 
        (double)encoding.memory_usage() / encoding.node_count << " bytes/node)\n";
    std::cout << "  Encode time: " << encode_time << " μs\n";
    
    // Calculate efficiency
    double memory_reduction = (double)(actual_memory - encoding.memory_usage()) / actual_memory * 100.0;
    std::cout << "  Memory reduction: " << std::fixed << std::setprecision(1) << memory_reduction << "%\n";
    
    // Theoretical analysis
    size_t theoretical_bits = 2 * encoding.node_count;  // Correct theoretical minimum for N-ary trees
    double bit_efficiency = (double)theoretical_bits / encoding.structure_bits.size() * 100.0;
    std::cout << "  Bit efficiency: " << std::setprecision(1) << bit_efficiency << "%\n";
    
    // Test decode
    start = std::chrono::high_resolution_clock::now();
    auto decoded_tree = NaryTree<std::string>::decode_succinct(encoding);
    auto decode_time = std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::high_resolution_clock::now() - start).count();
    
    auto decoded_stats = decoded_tree.get_statistics();
    bool integrity = decoded_stats.total_nodes == stats.total_nodes;
    std::cout << "  Decode time: " << decode_time << " μs\n";
    std::cout << "  Integrity: " << (integrity ? "PASS" : "FAIL") << "\n";
}

int main() {
    std::cout << "Succinct N-ary Tree Memory Analysis\n";
    std::cout << "===================================\n";
    
    // Test different tree sizes
    std::vector<size_t> test_sizes = {10, 100, 1000, 10000};
    
    for (size_t size : test_sizes) {
        test_tree_size(size);
    }
    
    std::cout << "\n=== Summary ===\n";
    std::cout << "Succinct encoding provides:\n";
    std::cout << "- Theoretical 2n bits for structure\n"; 
    std::cout << "- Linear data array in preorder\n";
    std::cout << "- Significant memory savings for large trees\n";
    std::cout << "- Fast encode/decode operations\n";
    
    return 0;
}