#!/usr/bin/env python3
"""
Simple test to import quadtree, octree, and narytree modules
"""

def test_imports():
    """Test importing all three spatial data structure modules"""
    print("Testing spatial data structure module imports...")
    
    try:
        import quadtree
        print("✓ quadtree module imported successfully")
        print(f"  quadtree module: {quadtree}")
    except ImportError as e:
        print(f"✗ Failed to import quadtree: {e}")
    
    try:
        import octree
        print("✓ octree module imported successfully")
        print(f"  octree module: {octree}")
    except ImportError as e:
        print(f"✗ Failed to import octree: {e}")
    
    try:
        import narytree
        print("✓ narytree module imported successfully")
        print(f"  narytree module: {narytree}")
    except ImportError as e:
        print(f"✗ Failed to import narytree: {e}")

if __name__ == "__main__":
    test_imports()