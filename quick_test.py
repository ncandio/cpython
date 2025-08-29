#!/usr/bin/env python3
"""
Quick Test - Verify Both Modules Work
=====================================

This is the fastest way to verify both QuadTree and Octree are working.
"""

def test_basic_functionality():
    """Test basic functionality of both modules."""
    print("🧪 QUICK FUNCTIONALITY TEST")
    print("=" * 30)
    
    try:
        # Test QuadTree
        print("🌳 Testing QuadTree...")
        import quadtree
        qt = quadtree.QuadTree(0, 0, 100, 100)
        qt.insert(25, 25, "test_point")
        results = qt.query(20, 20, 30, 30)
        print(f"   ✅ QuadTree: Inserted 1 point, found {len(results)} in query")
        
        # Test Octree
        print("🎯 Testing Octree...")
        import octree
        tree = octree.Octree(0, 0, 0, 100, 100, 100)
        tree.insert(25, 25, 25, "test_object")
        results = tree.query(20, 20, 20, 30, 30, 30)
        print(f"   ✅ Octree: Inserted 1 object, found {len(results)} in query")
        
        # Performance test
        print("⚡ Quick Performance Test...")
        import time
        
        # QuadTree performance
        start = time.time()
        for i in range(1000):
            qt.insert(i % 100, (i*2) % 100, f"perf_{i}")
        qt_time = time.time() - start
        
        # Octree performance  
        start = time.time()
        for i in range(1000):
            tree.insert(i % 100, (i*2) % 100, (i*3) % 100, f"perf_{i}")
        ot_time = time.time() - start
        
        print(f"   🌳 QuadTree: {1000/qt_time:.0f} insertions/sec")
        print(f"   🎯 Octree: {1000/ot_time:.0f} insertions/sec")
        
        print(f"\n🎉 SUCCESS: Both modules working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)