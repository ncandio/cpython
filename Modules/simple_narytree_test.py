#!/usr/bin/env python3
"""
Simple test for the current narytree module API
"""

import narytree

def test_current_api():
    """Test the currently available API methods"""
    print("=== Testing Current NaryTree API ===")
    
    # Test 1: Create empty tree
    print("1. Testing empty tree creation...")
    tree = narytree.NaryTree()
    print(f"   Empty: {tree.empty()}")
    print(f"   Size: {tree.size()}")
    assert tree.empty() == True
    assert tree.size() == 0
    print("   ✓ Empty tree tests passed")
    
    # Test 2: Set root
    print("\n2. Testing set_root...")
    tree.set_root("root_data")
    print(f"   Empty after set_root: {tree.empty()}")
    print(f"   Size after set_root: {tree.size()}")
    assert tree.empty() == False
    assert tree.size() == 1
    print("   ✓ set_root tests passed")
    
    # Test 3: Test with different data types
    print("\n3. Testing different data types...")
    tree.set_root(42)
    assert tree.size() == 1
    tree.set_root([1, 2, 3])
    assert tree.size() == 1
    tree.set_root({"key": "value"})
    assert tree.size() == 1
    print("   ✓ Data type tests passed")
    
    # Test 4: Multiple trees
    print("\n4. Testing multiple trees...")
    tree1 = narytree.NaryTree()
    tree2 = narytree.NaryTree()
    tree1.set_root("tree1")
    tree2.set_root("tree2")
    assert tree1.size() == 1 and tree2.size() == 1
    assert not tree1.empty() and not tree2.empty()
    print("   ✓ Multiple trees tests passed")
    
    # Test 5: Available methods
    print("\n5. Available methods:")
    methods = [m for m in dir(tree) if not m.startswith('_')]
    for method in methods:
        print(f"   - {method}")
    
    print("\n=== All Current API Tests Passed! ===")

if __name__ == "__main__":
    test_current_api()