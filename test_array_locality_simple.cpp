#include <iostream>
#include <chrono>
#include <vector>
#include <random>
#include <memory>
#include <iomanip>

// Include the array-based implementation
#include "Modules/nary_tree_array_based.cpp"

int main() {
    std::cout << "Array-Based N-ary Tree Locality Test\n";
    std::cout << std::string(50, '=') << '\n';
    
    // Create a complex tree structure
    ArrayBasedNaryTree<std::string> tree("root");
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // Build a tree with multiple levels and branching
    auto root = tree.root();
    
    // Level 1: 5 children
    std::vector<ArrayBasedNaryTree<std::string>::NodeRef> level1;
    for (int i = 0; i < 5; ++i) {
        level1.push_back(root.add_child("L1_" + std::to_string(i)));
    }
    
    // Level 2: 3-4 children per level1 node
    std::vector<ArrayBasedNaryTree<std::string>::NodeRef> level2;
    for (auto& parent : level1) {
        for (int i = 0; i < 4; ++i) {
            level2.push_back(parent.add_child("L2_" + std::to_string(i)));
        }
    }
    
    // Level 3: 2-3 children per level2 node
    for (auto& parent : level2) {
        for (int i = 0; i < 3; ++i) {
            parent.add_child("L3_" + std::to_string(i));
        }
    }
    
    auto creation_end = std::chrono::high_resolution_clock::now();
    double creation_time = std::chrono::duration<double, std::milli>(creation_end - start).count();
    
    std::cout << "Tree creation completed in " << creation_time << " ms\n";
    std::cout << "Tree size: " << tree.size() << " nodes\n\n";
    
    // Print initial layout
    std::cout << "Layout before optimization:\n";
    tree.print_layout();
    
    // Optimize for better locality
    std::cout << "\nOptimizing layout...\n";
    tree.optimize_layout();
    
    std::cout << "\nLayout after breadth-first optimization:\n";
    tree.print_layout();
    
    // Test traversal performance
    std::cout << "\nTraversal Performance Tests:\n";
    std::cout << std::string(40, '-') << '\n';
    
    // Breadth-first traversal (optimal for array layout)
    start = std::chrono::high_resolution_clock::now();
    int bf_count = 0;
    tree.for_each_breadth_first([&bf_count](const auto& node) {
        bf_count++;
        volatile int dummy = node.data().length(); // Prevent optimization
    });
    auto bf_end = std::chrono::high_resolution_clock::now();
    double bf_time = std::chrono::duration<double, std::milli>(bf_end - start).count();
    
    // Sequential traversal (best cache locality)
    start = std::chrono::high_resolution_clock::now();
    int seq_count = 0;
    tree.for_each_sequential([&seq_count](const auto& node) {
        seq_count++;
        volatile int dummy = node.data().length(); // Prevent optimization
    });
    auto seq_end = std::chrono::high_resolution_clock::now();
    double seq_time = std::chrono::duration<double, std::milli>(seq_end - start).count();
    
    std::cout << "Breadth-first traversal: " << bf_time << " ms (" << bf_count << " nodes)\n";
    std::cout << "Sequential traversal:    " << seq_time << " ms (" << seq_count << " nodes)\n";
    
    // Memory analysis
    auto stats = tree.get_memory_stats();
    std::cout << "\nMemory Analysis:\n";
    std::cout << std::string(30, '-') << '\n';
    std::cout << "Total memory:      " << stats.total_memory / 1024.0 << " KB\n";
    std::cout << "Node overhead:     " << stats.node_overhead / 1024.0 << " KB\n";
    std::cout << "Data memory:       " << stats.data_memory / 1024.0 << " KB\n";
    std::cout << "Fragmentation:     " << stats.fragmentation / 1024.0 << " KB\n";
    std::cout << "Locality score:    " << std::fixed << std::setprecision(3) << stats.locality_score << "/1.0\n";
    
    // Cache efficiency estimation
    double cache_efficiency = stats.locality_score * 100;
    std::cout << "Est. cache efficiency: " << std::setprecision(1) << cache_efficiency << "%\n";
    
    std::cout << "\nLocality Benefits:\n";
    std::cout << "• Breadth-first layout reduces cache misses\n";
    std::cout << "• Sequential memory access patterns\n";
    std::cout << "• Children stored near parents\n";
    std::cout << "• Better CPU prefetching\n";
    std::cout << "• Reduced memory fragmentation\n";
    
    return 0;
}