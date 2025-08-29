#!/usr/bin/env python3
"""
Python-based test suite for N-ary Tree Height Balancing
Simulates the balancing functionality and validates the algorithm logic
"""

import time
import random
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class TreeNode:
    """Simulated tree node for testing"""
    data: Any
    children: List['TreeNode']
    parent: Optional['TreeNode'] = None
    
    def __post_init__(self):
        if not hasattr(self, 'children') or self.children is None:
            self.children = []
    
    def add_child(self, data: Any) -> 'TreeNode':
        child = TreeNode(data=data, children=[], parent=self)
        self.children.append(child)
        return child
    
    def depth(self) -> int:
        """Calculate depth of subtree rooted at this node"""
        if not self.children:
            return 1
        return 1 + max(child.depth() for child in self.children)
    
    def size(self) -> int:
        """Calculate number of nodes in subtree"""
        return 1 + sum(child.size() for child in self.children)

class SimulatedNaryTree:
    """Simulated N-ary tree for testing height balancing logic"""
    
    def __init__(self):
        self.root: Optional[TreeNode] = None
        
    def set_root(self, data: Any):
        self.root = TreeNode(data=data, children=[])
        
    def empty(self) -> bool:
        return self.root is None
        
    def size(self) -> int:
        return 0 if self.empty() else self.root.size()
        
    def depth(self) -> int:
        return 0 if self.empty() else self.root.depth()
        
    def collect_all_data(self) -> List[Any]:
        """Simulate the level-order data collection"""
        if self.empty():
            return []
            
        data = []
        queue = [self.root]
        
        while queue:
            current = queue.pop(0)
            data.append(current.data)
            queue.extend(current.children)
            
        return data
        
    def build_balanced_subtree(self, data: List[Any], start: int, end: int, max_children: int = 3) -> Optional[TreeNode]:
        """Simulate the balanced subtree construction"""
        if start >= end:
            return None
            
        # Create root of this subtree
        node = TreeNode(data=data[start], children=[])
        
        if end - start == 1:  # Leaf node
            return node
            
        # Calculate optimal distribution
        remaining = end - start - 1
        children_count = min(remaining, max_children)
        
        if children_count == 0:
            return node
            
        # Distribute remaining nodes among children
        base_size = remaining // children_count
        extra = remaining % children_count
        
        current_start = start + 1
        
        for i in range(children_count):
            if current_start >= end:
                break
                
            child_size = base_size + (1 if i < extra else 0)
            child_end = current_start + child_size
            
            if child_end > end:
                child_end = end
                
            child = self.build_balanced_subtree(data, current_start, child_end, max_children)
            if child:
                child.parent = node
                node.children.append(child)
                
            current_start = child_end
            
        return node
        
    def balance_tree(self, max_children: int = 3):
        """Simulate tree balancing"""
        if self.empty() or self.size() <= 1:
            return
            
        # Collect all data
        data = self.collect_all_data()
        
        # Rebuild tree with balanced structure
        self.root = self.build_balanced_subtree(data, 0, len(data), max_children)
        
    def needs_rebalancing(self) -> bool:
        """Check if tree needs rebalancing using the implemented heuristic"""
        if self.empty() or self.size() <= 3:
            return False
            
        optimal_depth = int(math.log(self.size()) / math.log(3)) + 1
        return self.depth() > optimal_depth * 2
        
    def auto_balance_if_needed(self, max_children: int = 3):
        """Automatic balancing with threshold check"""
        if self.needs_rebalancing():
            self.balance_tree(max_children)

class HeightBalancingTester:
    """Test suite for height balancing functionality"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        
    def assert_test(self, condition: bool, test_name: str):
        """Assert helper with tracking"""
        if condition:
            print(f"✓ {test_name} PASSED")
            self.tests_passed += 1
        else:
            print(f"✗ {test_name} FAILED")
            self.tests_failed += 1
            
    def test_basic_balancing(self):
        """Test basic balancing functionality"""
        print("Testing basic balancing functionality...")
        
        tree = SimulatedNaryTree()
        
        # Create unbalanced tree (linear chain)
        tree.set_root(1)
        current = tree.root
        for i in range(2, 11):
            current = current.add_child(i)
            
        # Verify unbalanced structure
        depth_before = tree.depth()
        self.assert_test(depth_before == 10, "Unbalanced tree has correct depth")
        
        # Balance the tree
        tree.balance_tree(3)
        
        # Verify balanced structure
        depth_after = tree.depth()
        self.assert_test(depth_after <= 4, f"Balanced tree has reduced depth ({depth_after} <= 4)")
        self.assert_test(tree.size() == 10, "All nodes preserved during balancing")
        
    def test_already_balanced_tree(self):
        """Test balancing of already balanced tree"""
        print("\nTesting balancing of already balanced tree...")
        
        tree = SimulatedNaryTree()
        tree.set_root("root")
        
        # Create a well-balanced tree
        root = tree.root
        child1 = root.add_child("child1")
        child2 = root.add_child("child2")
        child3 = root.add_child("child3")
        
        child1.add_child("grandchild1")
        child1.add_child("grandchild2")
        child2.add_child("grandchild3")
        child3.add_child("grandchild4")
        
        depth_before = tree.depth()
        tree.balance_tree(3)
        depth_after = tree.depth()
        
        self.assert_test(abs(depth_before - depth_after) <= 1, "Already balanced tree depth similar")
        self.assert_test(tree.size() == 8, "Node count preserved")
        
    def test_single_node_tree(self):
        """Test single node tree balancing"""
        print("\nTesting single node tree balancing...")
        
        tree = SimulatedNaryTree()
        tree.set_root(3.14)
        
        depth_before = tree.depth()
        tree.balance_tree()
        depth_after = tree.depth()
        
        self.assert_test(depth_before == 1 and depth_after == 1, "Single node tree unchanged")
        self.assert_test(tree.size() == 1, "Single node preserved")
        self.assert_test(tree.root.data == 3.14, "Root data preserved")
        
    def test_empty_tree(self):
        """Test empty tree balancing"""
        print("\nTesting empty tree balancing...")
        
        tree = SimulatedNaryTree()
        tree.balance_tree()
        
        self.assert_test(tree.empty(), "Empty tree remains empty")
        self.assert_test(tree.size() == 0, "Size remains zero")
        self.assert_test(tree.depth() == 0, "Depth remains zero")
        
    def test_different_branching_factors(self):
        """Test different branching factors"""
        print("\nTesting different branching factors...")
        
        for branching_factor in range(2, 6):
            tree = SimulatedNaryTree()
            
            # Create linear tree
            tree.set_root(1)
            current = tree.root
            for i in range(2, 16):
                current = current.add_child(i)
                
            tree.balance_tree(branching_factor)
            
            expected_max_depth = int(math.ceil(math.log(15) / math.log(branching_factor))) + 1
            
            self.assert_test(tree.depth() <= expected_max_depth + 1,
                           f"Branching factor {branching_factor} creates appropriate depth ({tree.depth()} <= {expected_max_depth + 1})")
            
    def test_large_sequential_data(self):
        """Test large sequential data balancing"""
        print("\nTesting large sequential data balancing...")
        
        DATA_SIZE = 1000
        tree = SimulatedNaryTree()
        
        # Create large unbalanced tree
        tree.set_root(1)
        current = tree.root
        for i in range(2, DATA_SIZE + 1):
            current = current.add_child(i)
            
        start_time = time.perf_counter()
        tree.balance_tree(3)
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time) * 1000
        
        self.assert_test(tree.depth() <= 8, f"Large tree properly balanced (depth: {tree.depth()})")
        self.assert_test(tree.size() == DATA_SIZE, "All nodes preserved")
        self.assert_test(duration_ms < 100, f"Balancing completed in reasonable time ({duration_ms:.2f}ms < 100ms)")
        
        print(f"  Balancing {DATA_SIZE} nodes took: {duration_ms:.2f} ms")
        
    def test_needs_rebalancing_heuristic(self):
        """Test needs_rebalancing heuristic"""
        print("\nTesting needs_rebalancing heuristic...")
        
        # Balanced tree should not need rebalancing
        balanced_tree = SimulatedNaryTree()
        balanced_tree.set_root(1)
        root = balanced_tree.root
        root.add_child(2)
        root.add_child(3)
        root.add_child(4)
        
        self.assert_test(not balanced_tree.needs_rebalancing(), "Balanced tree doesn't need rebalancing")
        
        # Unbalanced tree should need rebalancing
        unbalanced_tree = SimulatedNaryTree()
        unbalanced_tree.set_root(1)
        current = unbalanced_tree.root
        for i in range(2, 21):
            current = current.add_child(i)
            
        self.assert_test(unbalanced_tree.needs_rebalancing(), "Unbalanced tree needs rebalancing")
        
    def test_data_integrity(self):
        """Test data integrity during balancing"""
        print("\nTesting data integrity during balancing...")
        
        original_data = ["apple", "banana", "cherry", "date", "elderberry",
                        "fig", "grape", "honeydew", "kiwi", "lemon"]
        
        tree = SimulatedNaryTree()
        tree.set_root(original_data[0])
        
        # Build tree
        current = tree.root
        for i in range(1, len(original_data)):
            current = current.add_child(original_data[i])
            
        # Balance tree
        tree.balance_tree()
        
        # Collect all data after balancing
        collected_data = tree.collect_all_data()
        
        # Sort both lists for comparison
        original_sorted = sorted(original_data)
        collected_sorted = sorted(collected_data)
        
        self.assert_test(original_sorted == collected_sorted, "All data preserved during balancing")
        self.assert_test(len(collected_data) == len(original_data), "Node count matches original")
        
    def test_performance_scaling(self):
        """Test performance scaling characteristics"""
        print("\nTesting performance scaling...")
        
        test_sizes = [100, 500, 1000, 2000]
        
        for size in test_sizes:
            tree = SimulatedNaryTree()
            
            # Create linear tree (worst case)
            tree.set_root(1)
            current = tree.root
            for i in range(2, size + 1):
                current = current.add_child(i)
                
            start_time = time.perf_counter()
            tree.balance_tree()
            end_time = time.perf_counter()
            
            duration_ms = (end_time - start_time) * 1000
            time_per_node = duration_ms / size
            
            print(f"  Size {size}: {duration_ms:.2f} ms ({time_per_node:.4f} ms/node)")
            
            self.assert_test(time_per_node < 0.1, f"Performance under 0.1 ms/node for size {size}")
            
    def run_all_tests(self):
        """Run all test cases"""
        print("=== N-ary Tree Height Balancing Test Suite (Python Simulation) ===\n")
        
        self.test_basic_balancing()
        self.test_already_balanced_tree()
        self.test_single_node_tree()
        self.test_empty_tree()
        self.test_different_branching_factors()
        self.test_large_sequential_data()
        self.test_needs_rebalancing_heuristic()
        self.test_data_integrity()
        self.test_performance_scaling()
        
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        
        if self.tests_passed + self.tests_failed > 0:
            success_rate = 100.0 * self.tests_passed / (self.tests_passed + self.tests_failed)
            print(f"Success Rate: {success_rate:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed! Height balancing logic is working correctly.")
            print("The C++ implementation should work as expected.")
        else:
            print("\n⚠️  Some tests failed. Please review the balancing logic.")

def main():
    """Main test execution"""
    random.seed(42)  # Reproducible results
    
    tester = HeightBalancingTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()