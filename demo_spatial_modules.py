#!/usr/bin/env python3
"""
Demonstration of System-Wide Spatial Data Structures
===================================================

This script demonstrates the usage of both QuadTree and Octree modules
that are now available system-wide for Python developers.
"""

def demo_quadtree():
    """Demonstrate QuadTree for 2D spatial indexing."""
    print("🌳 QuadTree Demo - 2D Spatial Indexing")
    print("=" * 45)
    
    import quadtree
    
    # Create a QuadTree for a 200x200 area
    qt = quadtree.QuadTree(-100, -100, 100, 100)
    
    # Insert some cities with coordinates
    cities = [
        (40.7128, -74.0060, "New York"),
        (34.0522, -118.2437, "Los Angeles"), 
        (41.8781, -87.6298, "Chicago"),
        (29.7604, -95.3698, "Houston"),
        (33.4484, -112.0740, "Phoenix")
    ]
    
    print("Inserting cities:")
    for lat, lon, name in cities:
        # Scale coordinates to fit our quadtree bounds
        x = lon + 100  # Shift longitude
        y = lat        # Use latitude directly
        qt.insert(x, y, name)
        print(f"  📍 {name}: ({lat:.2f}, {lon:.2f})")
    
    print(f"\nQuadTree size: {qt.size()} cities")
    
    # Query for cities in a region
    results = qt.query(30, 25, 80, 45)  # Roughly eastern US
    print(f"Cities in eastern region: {len(results)}")
    for point in results:
        print(f"  🏙️  {point}")
    
    print()

def demo_octree():
    """Demonstrate Octree for 3D spatial indexing."""
    print("🎯 Octree Demo - 3D Spatial Indexing")
    print("=" * 42)
    
    import octree
    
    # Create an Octree for a 200x200x200 volume
    tree = octree.Octree(-100, -100, -100, 100, 100, 100)
    
    # Insert some 3D objects (like game entities or 3D points)
    objects_3d = [
        (10, 20, 30, "Player"),
        (-30, 40, -50, "Enemy_1"),
        (60, -70, 80, "Treasure"),
        (-90, -10, 20, "NPC_1"),
        (0, 0, 0, "Origin_Marker"),
        (50, 50, 50, "Checkpoint"),
        (-25, 35, -15, "Power_Up")
    ]
    
    print("Inserting 3D objects:")
    for x, y, z, name in objects_3d:
        tree.insert(x, y, z, name)
        print(f"  🎮 {name}: ({x}, {y}, {z})")
    
    print(f"\nOctree statistics:")
    print(f"  📊 Size: {tree.size()} objects")
    print(f"  📊 Depth: {tree.depth()}")
    print(f"  📊 Memory: {tree.memory_usage()} bytes")
    print(f"  📊 Subdivisions: {tree.subdivision_count()}")
    
    # Query for objects in a region
    results = tree.query(-50, -50, -50, 50, 50, 50)  # Central cube
    print(f"\nObjects in central region (-50 to 50 on all axes):")
    for obj in results:
        x, y, z, name = obj
        print(f"  🎯 {name}: ({x}, {y}, {z})")
    
    # Radius query around origin
    radius_results = tree.query_radius(0, 0, 0, 30)
    print(f"\nObjects within radius 30 of origin:")
    for obj in radius_results:
        x, y, z, name = obj
        print(f"  🔘 {name}: ({x}, {y}, {z})")
    
    print()

def demo_performance_comparison():
    """Compare performance characteristics of both structures."""
    print("⚡ Performance Comparison")
    print("=" * 30)
    
    import time
    import random
    import quadtree
    import octree
    
    # Test data sizes
    test_size = 10000
    
    print(f"Testing with {test_size:,} random points/objects...")
    
    # QuadTree performance
    print("\n🌳 QuadTree Performance:")
    qt = quadtree.QuadTree(-1000, -1000, 1000, 1000)
    
    start_time = time.time()
    for i in range(test_size):
        x = random.uniform(-800, 800)
        y = random.uniform(-800, 800)
        qt.insert(x, y, f"point_{i}")
    quad_insert_time = time.time() - start_time
    
    start_time = time.time()
    results = qt.query(-100, -100, 100, 100)
    quad_query_time = time.time() - start_time
    
    print(f"  📊 Insert time: {quad_insert_time:.3f}s ({test_size/quad_insert_time:.0f} points/sec)")
    print(f"  📊 Query time: {quad_query_time:.6f}s")
    print(f"  📊 Query results: {len(results)} points")
    print(f"  📊 Final size: {qt.size()} points")
    
    # Octree performance
    print("\n🎯 Octree Performance:")
    tree = octree.Octree(-1000, -1000, -1000, 1000, 1000, 1000)
    
    start_time = time.time()
    for i in range(test_size):
        x = random.uniform(-800, 800)
        y = random.uniform(-800, 800)
        z = random.uniform(-800, 800)
        tree.insert(x, y, z, f"object_{i}")
    octree_insert_time = time.time() - start_time
    
    start_time = time.time()
    results = tree.query(-100, -100, -100, 100, 100, 100)
    octree_query_time = time.time() - start_time
    
    print(f"  📊 Insert time: {octree_insert_time:.3f}s ({test_size/octree_insert_time:.0f} objects/sec)")
    print(f"  📊 Query time: {octree_query_time:.6f}s")
    print(f"  📊 Query results: {len(results)} objects")
    print(f"  📊 Final size: {tree.size()} objects")
    print(f"  📊 Tree depth: {tree.depth()}")
    print(f"  📊 Memory usage: {tree.memory_usage():,} bytes")
    
    print()

if __name__ == "__main__":
    print("🚀 SPATIAL DATA STRUCTURES - SYSTEM-WIDE DEMO")
    print("=" * 55)
    print("Both QuadTree and Octree modules are now available system-wide!")
    print("Any Python developer can simply use: import quadtree, import octree")
    print()
    
    try:
        demo_quadtree()
        demo_octree()
        demo_performance_comparison()
        
        print("✅ SUCCESS: Both modules are working perfectly!")
        print("\n📚 Available APIs:")
        print("\nQuadTree methods:")
        import quadtree
        qt = quadtree.QuadTree(0, 0, 1, 1)
        print(f"  {[m for m in dir(qt) if not m.startswith('_')]}")
        
        print("\nOctree methods:")  
        import octree
        tree = octree.Octree(0, 0, 0, 1, 1, 1)
        print(f"  {[m for m in dir(tree) if not m.startswith('_')]}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("Please check module installation.")