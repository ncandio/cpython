#!/usr/bin/env python3
"""
Simple N-ary Tree API Tests

Basic functionality test suite for the N-ary tree data structure implementation.
This test verifies core operations and basic tree management.
"""

import sys
import time
import traceback
import random
import json
from datetime import datetime

# Import the compiled module
try:
    import narytree
except ImportError as e:
    print(f"Failed to import narytree module: {e}")
    print("Make sure to compile the module first: python3 setup_narytree.py build_ext --inplace")
    sys.exit(1)

def test_basic_tree_creation():
    """Test basic tree creation and initialization."""
    print("Testing basic tree creation...")
    
    # Test empty tree creation
    empty_tree = narytree.NaryTree()
    assert empty_tree.empty() == True
    assert empty_tree.size() == 0
    
    # Test tree with root data
    tree = narytree.NaryTree("root")
    assert tree.empty() == False
    assert tree.size() == 1
    
    print("✓ Basic tree creation tests passed")

def test_root_operations():
    """Test root node operations."""
    print("Testing root operations...")
    
    # Test setting root on empty tree
    tree = narytree.NaryTree()
    tree.set_root("new_root")
    assert tree.empty() == False
    assert tree.size() == 1
    
    # Test setting root on existing tree
    tree.set_root("updated_root")
    assert tree.empty() == False
    assert tree.size() == 1
    
    print("✓ Root operations tests passed")

def test_tree_properties():
    """Test tree property methods."""
    print("Testing tree properties...")
    
    # Test empty tree properties
    empty_tree = narytree.NaryTree()
    assert empty_tree.empty() == True
    assert empty_tree.size() == 0
    
    # Test non-empty tree properties
    tree = narytree.NaryTree(42)
    assert tree.empty() == False
    assert tree.size() == 1
    
    # Test various data types
    string_tree = narytree.NaryTree("hello")
    list_tree = narytree.NaryTree([1, 2, 3])
    dict_tree = narytree.NaryTree({"key": "value"})
    
    for t in [string_tree, list_tree, dict_tree]:
        assert t.empty() == False
        assert t.size() == 1
    
    print("✓ Tree properties tests passed")

def test_data_types():
    """Test tree with various Python data types."""
    print("Testing various data types...")
    
    test_data = [
        None,
        True,
        False,
        42,
        3.14159,
        "string_data",
        [1, 2, 3],
        {"key": "value", "nested": {"data": 123}},
        (1, 2, 3),
        set([4, 5, 6])
    ]
    
    for data in test_data:
        tree = narytree.NaryTree(data)
        assert tree.empty() == False
        assert tree.size() == 1
        print(f"  ✓ Successfully stored {type(data).__name__}: {data}")
    
    print("✓ Data types tests passed")

def test_error_handling():
    """Test error handling and edge cases."""
    print("Testing error handling...")
    
    # Test various edge cases that should not crash
    tree = narytree.NaryTree()
    
    # These should work fine
    tree.set_root("")  # Empty string
    tree.set_root(0)   # Zero
    tree.set_root(None)  # None
    
    print("✓ Error handling tests passed")

def run_performance_test():
    """Run basic performance test."""
    print("Running basic performance test...")
    
    start_time = time.time()
    
    # Create multiple trees with different data
    trees = []
    for i in range(1000):
        tree = narytree.NaryTree(f"data_{i}")
        trees.append(tree)
    
    creation_time = time.time() - start_time
    
    # Test operations on trees
    start_time = time.time()
    for tree in trees:
        tree.empty()
        tree.size()
    
    operation_time = time.time() - start_time
    
    print(f"  ✓ Created 1000 trees in {creation_time:.4f} seconds")
    print(f"  ✓ Performed 2000 operations in {operation_time:.4f} seconds")
    print("✓ Performance test completed")

def generate_test_report():
    """Generate a comprehensive test report."""
    report = {
        "test_name": "N-ary Tree Simple API Tests",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "tests_run": [],
        "overall_status": "PASSED",
        "summary": {}
    }
    
    return report

def main():
    """Run all tests."""
    print("=" * 60)
    print("N-ary Tree Simple API Test Suite")
    print("=" * 60)
    
    start_time = time.time()
    tests_passed = 0
    tests_failed = 0
    
    test_functions = [
        test_basic_tree_creation,
        test_root_operations,
        test_tree_properties,
        test_data_types,
        test_error_handling,
        run_performance_test
    ]
    
    for test_func in test_functions:
        try:
            test_func()
            tests_passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} FAILED: {e}")
            traceback.print_exc()
            tests_failed += 1
            continue
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Runtime: {total_time:.4f} seconds")
    print(f"Success Rate: {(tests_passed/(tests_passed+tests_failed))*100:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 All tests passed! N-ary Tree implementation is working correctly.")
        return 0
    else:
        print(f"\n❌ {tests_failed} test(s) failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())