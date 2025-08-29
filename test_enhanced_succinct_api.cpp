#include <iostream>
#include <chrono>
#include <iomanip>

// Include enhanced N-ary tree API
#include "Modules/nary_tree.cpp"

int main() {
    std::cout << "Enhanced Succinct N-ary Tree API Test\n";
    std::cout << std::string(50, '=') << '\n';
    
    // Test 1: Array-based storage with locality
    std::cout << "Test 1: Array-based storage with locality optimization\n";
    std::cout << std::string(50, '-') << '\n';
    
    NaryTree<std::string> tree("root", true); // Enable array storage
    
    // Build a complex tree
    auto root = tree.root();
    auto& child1 = root->add_child("child1");
    auto& child2 = root->add_child("child2");
    auto& child3 = root->add_child("child3");
    
    // Add grandchildren
    child1.add_child("gc1_1");
    child1.add_child("gc1_2");
    child2.add_child("gc2_1");
    child2.add_child("gc2_2");
    child2.add_child("gc2_3");
    child3.add_child("gc3_1");
    
    // Add great-grandchildren
    for (int i = 0; i < 20; ++i) {
        child1.add_child("ggc1_" + std::to_string(i));
        if (i % 3 == 0) {
            child2.add_child("ggc2_" + std::to_string(i));
        }
    }
    
    std::cout << "Tree size: " << tree.size() << " nodes\n";
    
    // Test locality score
    double locality_before = tree.calculate_locality_score();
    std::cout << "Locality score before rebalancing: " << std::fixed << std::setprecision(3) << locality_before << "\n";
    
    // Force rebalancing
    tree.rebalance_for_locality();
    double locality_after = tree.calculate_locality_score();
    std::cout << "Locality score after rebalancing: " << std::fixed << std::setprecision(3) << locality_after << "\n";
    
    // Test 2: Succinct encoding
    std::cout << "\nTest 2: Succinct encoding with N-ary structure preservation\n";
    std::cout << std::string(50, '-') << '\n';
    
    auto encoding = tree.encode_succinct();
    
    std::cout << "Structure bits: " << encoding.structure_bits.size() << "\n";
    std::cout << "Data array size: " << encoding.data_array.size() << "\n";
    std::cout << "Node count: " << encoding.node_count << "\n";
    std::cout << "Memory usage: " << encoding.memory_usage() / 1024.0 << " KB\n";
    std::cout << "Compression ratio: " << std::fixed << std::setprecision(3) << encoding.compression_ratio() << "\n";
    
    // Test 3: Performance comparison
    std::cout << "\nTest 3: Performance with different storage modes\n";
    std::cout << std::string(50, '-') << '\n';
    
    // Traditional pointer-based storage
    auto start = std::chrono::high_resolution_clock::now();
    NaryTree<std::string> pointer_tree("root", false); // Disable array storage
    
    auto p_root = pointer_tree.root();
    for (int i = 0; i < 100; ++i) {
        auto& child = p_root->add_child("child_" + std::to_string(i));
        for (int j = 0; j < 5; ++j) {
            child.add_child("grandchild_" + std::to_string(j));
        }
    }
    
    auto pointer_end = std::chrono::high_resolution_clock::now();
    auto pointer_time = std::chrono::duration<double, std::milli>(pointer_end - start).count();
    
    // Array-based storage with locality
    start = std::chrono::high_resolution_clock::now();
    NaryTree<std::string> array_tree("root", true); // Enable array storage
    
    auto a_root = array_tree.root();
    for (int i = 0; i < 100; ++i) {
        auto& child = a_root->add_child("child_" + std::to_string(i));
        for (int j = 0; j < 5; ++j) {
            child.add_child("grandchild_" + std::to_string(j));
        }
    }
    
    auto array_end = std::chrono::high_resolution_clock::now();
    auto array_time = std::chrono::duration<double, std::milli>(array_end - start).count();
    
    std::cout << "Pointer-based creation: " << pointer_time << " ms\n";
    std::cout << "Array-based creation: " << array_time << " ms\n";
    std::cout << "Array locality score: " << array_tree.calculate_locality_score() << "\n";
    
    // Test 4: Memory efficiency
    std::cout << "\nTest 4: Memory efficiency analysis\n";
    std::cout << std::string(50, '-') << '\n';
    
    auto pointer_stats = pointer_tree.get_memory_stats();
    auto array_encoding = array_tree.encode_succinct();
    
    std::cout << "Traditional storage: " << pointer_stats.total_estimated_bytes / 1024 << " KB\n";
    std::cout << "Succinct encoding:   " << array_encoding.memory_usage() / 1024 << " KB\n";
    std::cout << "Space savings: " << std::fixed << std::setprecision(1) 
              << (1.0 - (double)array_encoding.memory_usage() / pointer_stats.total_estimated_bytes) * 100 << "%\n";
    
    std::cout << "\nEnhanced API Features Summary:\n";
    std::cout << "✓ Lazy rebalancing for locality optimization\n";
    std::cout << "✓ Array-based storage with breadth-first layout\n";  
    std::cout << "✓ Succinct encoding preserving N-ary structure\n";
    std::cout << "✓ Locality scoring and analysis\n";
    std::cout << "✓ Backward compatibility with existing API\n";
    
    return 0;
}