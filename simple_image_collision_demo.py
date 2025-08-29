#!/usr/bin/env python3
"""
Simple Image-Based Collision Detection with QuadTree & Octree
==============================================================

This script demonstrates collision detection using spatial data structures
without external image libraries - using pure numpy and our modules.
"""

import sys
import time
import random
import math
import numpy as np
import quadtree
import octree

class SimpleImageCollisionDetector:
    """2D Image collision detection using QuadTree."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.qt = quadtree.QuadTree(0, 0, width, height)
        self.pixels = []
    
    def load_pixel_data(self, pixel_array, threshold=128):
        """Load pixel data from numpy array into QuadTree."""
        print(f"🖼️  Loading {pixel_array.shape} image into QuadTree...")
        
        pixel_count = 0
        start_time = time.time()
        
        # Insert non-background pixels into QuadTree
        for y in range(pixel_array.shape[0]):
            for x in range(pixel_array.shape[1]):
                pixel_value = pixel_array[y, x]
                if pixel_value > threshold:  # Above threshold = foreground
                    pixel_data = f"pixel_({x},{y})_val_{int(pixel_value)}"
                    self.qt.insert(x, y, pixel_data)
                    self.pixels.append((x, y, pixel_value))
                    pixel_count += 1
        
        load_time = time.time() - start_time
        print(f"   ✅ Loaded {pixel_count:,} foreground pixels in {load_time:.3f}s")
        print(f"   📊 QuadTree depth: {self.qt.depth()}")
        print(f"   📊 QuadTree size: {self.qt.size()} pixels")
        
        return pixel_count
    
    def detect_object_collisions(self, objects):
        """Detect collisions between objects and image pixels."""
        print(f"🎯 Detecting collisions for {len(objects)} objects...")
        
        collisions = []
        query_start = time.time()
        
        for obj_id, (x, y, width, height, obj_type) in enumerate(objects):
            # Query rectangular region around object
            min_x = max(0, x - width//2)
            max_x = min(self.width, x + width//2)
            min_y = max(0, y - height//2)
            max_y = min(self.height, y + height//2)
            
            region_pixels = self.qt.query(min_x, min_y, max_x, max_y)
            
            if region_pixels:
                collision_info = {
                    'object_id': obj_id,
                    'object_type': obj_type,
                    'position': (x, y),
                    'size': (width, height),
                    'collision_points': len(region_pixels),
                    'bounding_box': (min_x, min_y, max_x, max_y)
                }
                collisions.append(collision_info)
        
        query_time = time.time() - query_start
        print(f"   ✅ Collision detection completed in {query_time:.4f}s")
        print(f"   🔥 Found {len(collisions)} collisions")
        
        return collisions

class Simple3DCollisionDetector:
    """3D collision detection using Octree."""
    
    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.tree = octree.Octree(0, 0, 0, width, height, depth)
        self.voxels = []
    
    def load_voxel_data(self, voxel_array, threshold=0.5):
        """Load 3D voxel data into Octree."""
        print(f"📦 Loading {voxel_array.shape} voxel data into Octree...")
        
        voxel_count = 0
        start_time = time.time()
        
        for z in range(voxel_array.shape[2]):
            for y in range(voxel_array.shape[1]):
                for x in range(voxel_array.shape[0]):
                    voxel_value = voxel_array[x, y, z]
                    if voxel_value > threshold:
                        voxel_id = f"voxel_({x},{y},{z})_val_{voxel_value:.2f}"
                        self.tree.insert(x, y, z, voxel_id)
                        self.voxels.append((x, y, z, voxel_value))
                        voxel_count += 1
        
        load_time = time.time() - start_time
        print(f"   ✅ Loaded {voxel_count:,} voxels in {load_time:.3f}s")
        print(f"   📊 Octree depth: {self.tree.depth()}")
        print(f"   📊 Memory usage: {self.tree.memory_usage():,} bytes")
        
        return voxel_count
    
    def detect_3d_collisions(self, objects_3d):
        """Detect 3D collisions using both box and sphere queries."""
        print(f"⚡ Detecting 3D collisions for {len(objects_3d)} objects...")
        
        collisions = []
        
        for obj_id, (x, y, z, radius, obj_type) in enumerate(objects_3d):
            # Spherical collision detection
            collision_voxels = self.tree.query_radius(x, y, z, radius)
            
            # Also test box collision for comparison
            box_voxels = self.tree.query(x-radius, y-radius, z-radius, 
                                       x+radius, y+radius, z+radius)
            
            if collision_voxels or box_voxels:
                collision_info = {
                    'object_id': obj_id,
                    'object_type': obj_type,
                    'position': (x, y, z),
                    'radius': radius,
                    'sphere_collisions': len(collision_voxels),
                    'box_collisions': len(box_voxels),
                    'total_voxels': len(set(
                        [(v[0], v[1], v[2]) for v in collision_voxels] + 
                        [(v[0], v[1], v[2]) for v in box_voxels]
                    ))
                }
                collisions.append(collision_info)
        
        print(f"   ✅ Found {len(collisions)} 3D collisions")
        return collisions

def create_test_image(width=400, height=300):
    """Create a test image using numpy."""
    print(f"🎨 Creating test {width}x{height} image...")
    
    # Start with black background
    image = np.zeros((height, width), dtype=np.uint8)
    
    # Draw rectangle
    image[50:100, 50:150] = 255
    
    # Draw circle (approximation)
    center_x, center_y = 240, 120
    radius = 40
    y, x = np.ogrid[:height, :width]
    mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
    image[mask] = 180
    
    # Add diamond shape
    diamond_x, diamond_y = 150, 200
    diamond_size = 25
    for dy in range(-diamond_size, diamond_size):
        for dx in range(-diamond_size + abs(dy), diamond_size - abs(dy)):
            px, py = diamond_x + dx, diamond_y + dy
            if 0 <= px < width and 0 <= py < height:
                image[py, px] = 120
    
    # Add random noise
    for _ in range(1000):
        x, y = random.randint(0, width-1), random.randint(0, height-1)
        image[y, x] = random.randint(100, 200)
    
    print(f"   ✅ Created image with shapes and noise")
    return image

def create_test_3d_data(width=60, height=60, depth=60):
    """Create test 3D voxel data."""
    print(f"🧊 Creating test {width}x{height}x{depth} voxel data...")
    
    voxel_data = np.zeros((width, height, depth))
    
    # Create 3D sphere in center
    center_x, center_y, center_z = width//2, height//2, depth//2
    
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                dist = math.sqrt((x-center_x)**2 + (y-center_y)**2 + (z-center_z)**2)
                if dist < 20:
                    voxel_data[x, y, z] = 1.0 - (dist / 20)  # Gradient sphere
    
    # Add 3D "building" structure
    building_x, building_y = width//4, height//4
    for x in range(building_x, building_x + 15):
        for y in range(building_y, building_y + 15):
            for z in range(depth//2, depth//2 + 20):
                if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
                    voxel_data[x, y, z] = 0.8
    
    # Add random voxels
    for _ in range(2000):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        z = random.randint(0, depth-1)
        voxel_data[x, y, z] = random.uniform(0.5, 1.0)
    
    print(f"   ✅ Created 3D scene with sphere, building, and random voxels")
    return voxel_data

def performance_benchmark():
    """Benchmark collision detection performance."""
    print("\n⚡ PERFORMANCE BENCHMARK")
    print("=" * 35)
    
    # Test parameters
    image_size = (800, 600)
    num_pixels = 8000
    num_objects = 200
    
    print(f"Testing with {image_size[0]}x{image_size[1]} image, "
          f"{num_pixels:,} pixels, {num_objects} objects")
    
    # Generate test data
    pixels = []
    for _ in range(num_pixels):
        x = random.randint(0, image_size[0]-1)
        y = random.randint(0, image_size[1]-1)
        value = random.randint(128, 255)
        pixels.append((x, y, value))
    
    objects = []
    for i in range(num_objects):
        x = random.randint(50, image_size[0]-50)
        y = random.randint(50, image_size[1]-50)
        w = random.randint(20, 100)
        h = random.randint(20, 100)
        objects.append((x, y, w, h, f"obj_{i}"))
    
    # QuadTree method
    print(f"\n🌳 QuadTree Method:")
    qt_start = time.time()
    
    qt = quadtree.QuadTree(0, 0, image_size[0], image_size[1])
    for x, y, value in pixels:
        qt.insert(x, y, f"pixel_{value}")
    
    qt_collisions = 0
    for obj_x, obj_y, obj_w, obj_h, obj_id in objects:
        results = qt.query(obj_x - obj_w//2, obj_y - obj_h//2,
                          obj_x + obj_w//2, obj_y + obj_h//2)
        if results:
            qt_collisions += 1
    
    qt_time = time.time() - qt_start
    
    # Brute force method
    print(f"🐌 Brute Force Method:")
    bf_start = time.time()
    
    bf_collisions = 0
    for obj_x, obj_y, obj_w, obj_h, obj_id in objects:
        for px, py, pval in pixels:
            if (obj_x - obj_w//2 <= px <= obj_x + obj_w//2 and
                obj_y - obj_h//2 <= py <= obj_y + obj_h//2):
                bf_collisions += 1
                break
    
    bf_time = time.time() - bf_start
    
    # Results
    speedup = bf_time / qt_time if qt_time > 0 else float('inf')
    
    print(f"\n📊 Results:")
    print(f"   QuadTree: {qt_time:.4f}s, {qt_collisions} collisions, depth={qt.depth()}")
    print(f"   Brute Force: {bf_time:.4f}s, {bf_collisions} collisions")
    print(f"   🚀 Speedup: {speedup:.1f}x faster with QuadTree")

def main():
    """Main demonstration."""
    print("🎯 SIMPLE IMAGE COLLISION DETECTION DEMO")
    print("=" * 45)
    
    # Demo 1: 2D Image Collision Detection
    print("\n🖼️  DEMO 1: 2D Image Collision Detection")
    print("-" * 40)
    
    # Create test image
    test_image = create_test_image(400, 300)
    
    # Set up collision detector
    detector = SimpleImageCollisionDetector(400, 300)
    pixel_count = detector.load_pixel_data(test_image, threshold=80)
    
    # Define game objects to test
    game_objects = [
        (100, 75, 40, 30, "player"),          # Should hit rectangle
        (240, 120, 50, 50, "enemy"),          # Should hit circle
        (150, 200, 60, 40, "projectile"),     # Should hit diamond
        (320, 180, 35, 35, "power_up"),       # May hit noise
        (50, 50, 20, 20, "corner_object"),    # Corner of rectangle
        (10, 10, 30, 30, "background_obj")    # Should miss everything
    ]
    
    # Detect collisions
    collisions = detector.detect_object_collisions(game_objects)
    
    print(f"\n🔥 2D Collision Results:")
    for collision in collisions:
        obj = collision
        print(f"   🎯 {obj['object_type']} at {obj['position']} -> "
              f"{obj['collision_points']} pixel collisions")
    
    # Demo 2: 3D Voxel Collision Detection
    print(f"\n\n📦 DEMO 2: 3D Voxel Collision Detection")
    print("-" * 40)
    
    # Create test 3D data
    voxel_data = create_test_3d_data(60, 60, 60)
    
    # Set up 3D collision detector
    detector_3d = Simple3DCollisionDetector(60, 60, 60)
    voxel_count = detector_3d.load_voxel_data(voxel_data, threshold=0.3)
    
    # Define 3D objects
    objects_3d = [
        (30, 30, 30, 12, "center_sphere"),     # Should hit main sphere
        (15, 15, 45, 8, "building_probe"),     # Should hit building
        (50, 50, 50, 6, "corner_scout"),       # Edge area
        (30, 30, 10, 15, "surface_crawler"),   # Should hit sphere surface
        (5, 5, 5, 10, "edge_detector")         # Corner area
    ]
    
    # Detect 3D collisions
    collisions_3d = detector_3d.detect_3d_collisions(objects_3d)
    
    print(f"\n⚡ 3D Collision Results:")
    for collision in collisions_3d:
        obj = collision
        print(f"   🎯 {obj['object_type']} at {obj['position']} (r={obj['radius']}) -> "
              f"sphere:{obj['sphere_collisions']}, box:{obj['box_collisions']} voxels")
    
    # Performance benchmark
    performance_benchmark()
    
    # Summary
    print(f"\n🎉 DEMONSTRATION COMPLETED")
    print(f"\n✅ Key Capabilities Demonstrated:")
    print(f"   • 2D image-based collision detection with QuadTree")
    print(f"   • Pixel-level spatial indexing and querying")
    print(f"   • 3D voxel collision detection with Octree")
    print(f"   • Both spherical and box collision queries")
    print(f"   • Significant performance advantages over brute force")
    print(f"   • Efficient memory usage and fast query times")

if __name__ == "__main__":
    main()