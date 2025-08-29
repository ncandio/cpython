/**
 * Comprehensive test suite for N-ary Tree Height Balancing
 * Tests the self-balancing functionality with various scenarios
 */

#include <iostream>
#include <vector>
#include <string>
#include <cassert>
#include <chrono>
#include <random>
#include <algorithm>
#include "nary_tree.cpp"

class HeightBalancingTester {
private:
    size_t tests_passed = 0;
    size_t tests_failed = 0;
    
    void assert_test(bool condition, const std::string& test_name) {
        if (condition) {
            std::cout << "✓ " << test_name << " PASSED\n";
            tests_passed++;
        } else {
            std::cout << "✗ " << test_name << " FAILED\n";
            tests_failed++;
        }
    }
    
public:
    void run_all_tests() {
        std::cout << "=== N-ary Tree Height Balancing Test Suite ===\n\n";
        
        test_basic_balancing();
        test_already_balanced_tree();
        test_single_node_tree();
        test_empty_tree();
        test_different_branching_factors();
        test_large_sequential_data();
        test_random_data();
        test_needs_rebalancing_heuristic();
        test_auto_balance_functionality();
        test_memory_stats();
        test_performance_characteristics();
        test_data_integrity();
        
        print_summary();
    }
    
private:
    void test_basic_balancing() {
        std::cout << "Testing basic balancing functionality...\n";
        
        NaryTree<int> tree;
        
        // Create unbalanced tree (linear chain)
        tree.set_root(1);
        auto* current = tree.root();
        for (int i = 2; i <= 10; ++i) {
            current = &current->add_child(i);
        }
        
        // Verify unbalanced structure
        size_t depth_before = tree.depth();
        assert_test(depth_before == 10, "Unbalanced tree has correct depth");
        
        // Balance the tree
        tree.balance_tree(3);
        
        // Verify balanced structure
        size_t depth_after = tree.depth();
        assert_test(depth_after <= 4, "Balanced tree has reduced depth");
        assert_test(tree.size() == 10, "All nodes preserved during balancing");
        
        // Verify tree is still valid
        assert_test(tree.root() != nullptr, "Root exists after balancing");
        assert_test(!tree.empty(), "Tree is not empty after balancing");
    }
    
    void test_already_balanced_tree() {
        std::cout << "\nTesting balancing of already balanced tree...\n";
        
        NaryTree<std::string> tree;
        tree.set_root("root");
        
        // Create a well-balanced tree
        auto* root = tree.root();
        auto& child1 = root->add_child("child1");
        auto& child2 = root->add_child("child2");
        auto& child3 = root->add_child("child3");
        
        child1.add_child("grandchild1");
        child1.add_child("grandchild2");
        child2.add_child("grandchild3");
        child3.add_child("grandchild4");
        
        size_t depth_before = tree.depth();
        tree.balance_tree(3);
        size_t depth_after = tree.depth();
        
        assert_test(depth_before == depth_after, "Already balanced tree depth unchanged");
        assert_test(tree.size() == 8, "Node count preserved");
    }
    
    void test_single_node_tree() {
        std::cout << "\nTesting single node tree balancing...\n";
        
        NaryTree<double> tree;
        tree.set_root(3.14);
        
        size_t depth_before = tree.depth();
        tree.balance_tree();
        size_t depth_after = tree.depth();
        
        assert_test(depth_before == 1 && depth_after == 1, "Single node tree unchanged");
        assert_test(tree.size() == 1, "Single node preserved");
        assert_test(tree.root()->data() == 3.14, "Root data preserved");
    }
    
    void test_empty_tree() {
        std::cout << "\nTesting empty tree balancing...\n";
        
        NaryTree<int> tree;
        tree.balance_tree();
        
        assert_test(tree.empty(), "Empty tree remains empty");
        assert_test(tree.size() == 0, "Size remains zero");
        assert_test(tree.depth() == 0, "Depth remains zero");
    }
    
    void test_different_branching_factors() {
        std::cout << "\nTesting different branching factors...\n";
        
        for (size_t branching_factor = 2; branching_factor <= 5; ++branching_factor) {
            NaryTree<int> tree;
            
            // Create linear tree
            tree.set_root(1);
            auto* current = tree.root();
            for (int i = 2; i <= 15; ++i) {
                current = &current->add_child(i);
            }
            
            tree.balance_tree(branching_factor);
            
            size_t expected_max_depth = static_cast<size_t>(
                std::ceil(std::log(15) / std::log(branching_factor))
            );
            
            assert_test(tree.depth() <= expected_max_depth + 1, 
                       "Branching factor " + std::to_string(branching_factor) + " creates appropriate depth");
        }
    }
    
    void test_large_sequential_data() {
        std::cout << "\nTesting large sequential data balancing...\n";
        
        const size_t DATA_SIZE = 1000;
        NaryTree<size_t> tree;
        
        // Create large unbalanced tree
        tree.set_root(1);
        auto* current = tree.root();
        for (size_t i = 2; i <= DATA_SIZE; ++i) {
            current = &current->add_child(i);
        }
        
        auto start = std::chrono::high_resolution_clock::now();
        tree.balance_tree(3);
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        assert_test(tree.depth() <= 8, "Large tree properly balanced");  // log_3(1000) ≈ 6.3
        assert_test(tree.size() == DATA_SIZE, "All nodes preserved");
        assert_test(duration.count() < 10000, "Balancing completed in reasonable time (<10ms)");
        
        std::cout << "  Balancing 1000 nodes took: " << duration.count() << " μs\n";
    }
    
    void test_random_data() {
        std::cout << "\nTesting random data balancing...\n";
        
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(1, 1000);
        
        NaryTree<int> tree;
        std::vector<int> values;
        
        // Generate random values
        for (int i = 0; i < 100; ++i) {
            values.push_back(dis(gen));
        }
        
        // Build tree in random order
        tree.set_root(values[0]);
        auto* current = tree.root();
        for (size_t i = 1; i < values.size(); ++i) {
            if (i % 3 == 0 && current->parent()) {
                current = current->parent();  // Sometimes go back up
            }
            current = &current->add_child(values[i]);
        }
        
        size_t depth_before = tree.depth();
        tree.balance_tree();
        size_t depth_after = tree.depth();
        
        assert_test(depth_after < depth_before, "Random tree depth reduced");
        assert_test(tree.size() == 100, "All nodes preserved in random tree");
    }
    
    void test_needs_rebalancing_heuristic() {
        std::cout << "\nTesting needs_rebalancing heuristic...\n";
        
        // Balanced tree should not need rebalancing
        NaryTree<int> balanced_tree;
        balanced_tree.set_root(1);
        auto* root = balanced_tree.root();
        root->add_child(2);
        root->add_child(3);
        root->add_child(4);
        
        assert_test(!balanced_tree.needs_rebalancing(), "Balanced tree doesn't need rebalancing");
        
        // Unbalanced tree should need rebalancing
        NaryTree<int> unbalanced_tree;
        unbalanced_tree.set_root(1);
        auto* current = unbalanced_tree.root();
        for (int i = 2; i <= 20; ++i) {
            current = &current->add_child(i);
        }
        
        assert_test(unbalanced_tree.needs_rebalancing(), "Unbalanced tree needs rebalancing");
    }
    
    void test_auto_balance_functionality() {
        std::cout << "\nTesting auto-balance functionality...\n";
        
        NaryTree<int> tree;
        
        // Create unbalanced tree
        tree.set_root(1);
        auto* current = tree.root();
        for (int i = 2; i <= 25; ++i) {
            current = &current->add_child(i);
        }
        
        size_t depth_before = tree.depth();
        tree.auto_balance_if_needed();
        size_t depth_after = tree.depth();
        
        assert_test(depth_after < depth_before, "Auto-balance reduced tree depth");
        
        // Try auto-balance on already balanced tree
        size_t depth_before_2nd = tree.depth();
        tree.auto_balance_if_needed();
        size_t depth_after_2nd = tree.depth();
        
        assert_test(depth_before_2nd == depth_after_2nd, "Auto-balance skips already balanced tree");
    }
    
    void test_memory_stats() {
        std::cout << "\nTesting memory statistics...\n";
        
        NaryTree<int> tree;
        
        // Empty tree stats
        auto empty_stats = tree.get_memory_stats();
        assert_test(empty_stats.total_estimated_bytes == 0, "Empty tree has zero memory usage");
        
        // Populate tree
        tree.set_root(1);
        for (int i = 2; i <= 10; ++i) {
            tree.root()->add_child(i);
        }
        
        auto stats = tree.get_memory_stats();
        assert_test(stats.total_estimated_bytes > 0, "Non-empty tree has memory usage");
        assert_test(stats.memory_per_node > 0, "Memory per node is positive");
        assert_test(stats.node_memory_bytes == 10 * sizeof(NaryTree<int>::Node), 
                   "Node memory calculation correct");
        
        std::cout << "  Memory per node: " << stats.memory_per_node << " bytes\n";
        std::cout << "  Total estimated memory: " << stats.total_estimated_bytes << " bytes\n";
    }
    
    void test_performance_characteristics() {
        std::cout << "\nTesting performance characteristics...\n";
        
        const std::vector<size_t> test_sizes = {100, 500, 1000, 2000};
        
        for (size_t size : test_sizes) {
            NaryTree<size_t> tree;
            
            // Create linear tree (worst case)
            tree.set_root(1);
            auto* current = tree.root();
            for (size_t i = 2; i <= size; ++i) {
                current = &current->add_child(i);
            }
            
            auto start = std::chrono::high_resolution_clock::now();
            tree.balance_tree();
            auto end = std::chrono::high_resolution_clock::now();
            
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            double time_per_node = static_cast<double>(duration.count()) / size;
            
            std::cout << "  Size " << size << ": " << duration.count() << " μs (" 
                     << time_per_node << " μs/node)\n";
            
            assert_test(time_per_node < 10.0, "Performance under 10 μs/node for size " + std::to_string(size));
        }
    }
    
    void test_data_integrity() {
        std::cout << "\nTesting data integrity during balancing...\n";
        
        std::vector<std::string> original_data = {
            "apple", "banana", "cherry", "date", "elderberry",
            "fig", "grape", "honeydew", "kiwi", "lemon"
        };
        
        NaryTree<std::string> tree;
        tree.set_root(original_data[0]);
        
        // Build tree
        auto* current = tree.root();
        for (size_t i = 1; i < original_data.size(); ++i) {
            current = &current->add_child(original_data[i]);
        }
        
        // Balance tree
        tree.balance_tree();
        
        // Collect all data after balancing
        std::vector<std::string> collected_data;
        tree.for_each([&collected_data](const auto& node) {
            collected_data.push_back(node.data());
        });
        
        // Sort both vectors for comparison
        std::sort(original_data.begin(), original_data.end());
        std::sort(collected_data.begin(), collected_data.end());
        
        assert_test(original_data == collected_data, "All data preserved during balancing");
        assert_test(collected_data.size() == original_data.size(), "Node count matches original");
    }
    
    void print_summary() {
        std::cout << "\n" << std::string(50, '=') << "\n";
        std::cout << "TEST SUMMARY\n";
        std::cout << std::string(50, '=') << "\n";
        std::cout << "Tests Passed: " << tests_passed << "\n";
        std::cout << "Tests Failed: " << tests_failed << "\n";
        std::cout << "Success Rate: " << (100.0 * tests_passed / (tests_passed + tests_failed)) << "%\n";
        
        if (tests_failed == 0) {
            std::cout << "\n🎉 All tests passed! Height balancing implementation is working correctly.\n";
        } else {
            std::cout << "\n⚠️  Some tests failed. Please review the implementation.\n";
        }
    }
};

int main() {
    HeightBalancingTester tester;
    tester.run_all_tests();
    return 0;
}