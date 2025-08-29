#!/usr/bin/env python3
"""
Image-Based Collision Detection with QuadTree & Octree
======================================================

This script demonstrates how to use QuadTree and Octree for:
1. Image-based 2D collision detection
2. Pixel clustering and spatial analysis
3. 3D voxel collision detection
4. Performance comparison with brute force methods
"""

import sys
import time
import random
import math
import numpy as np
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("PIL/Pillow not available. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw, ImageFont

import quadtree
import octree

class ImageCollisionDetector:
    """2D Image collision detection using QuadTree."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.qt = quadtree.QuadTree(0, 0, width, height)
        self.pixels = []
        self.collision_regions = []
    
    def load_from_array(self, image_array, threshold=128):
        """Load pixels from numpy array into QuadTree."""
        print(f"🖼️  Loading {image_array.shape} image into QuadTree...")
        
        pixel_count = 0
        start_time = time.time()
        
        # Convert grayscale if needed
        if len(image_array.shape) == 3:
            image_array = np.mean(image_array, axis=2)
        
        # Insert non-background pixels into QuadTree
        for y in range(image_array.shape[0]):
            for x in range(image_array.shape[1]):
                pixel_value = image_array[y, x]
                if pixel_value > threshold:  # Above threshold = foreground
                    pixel_data = f"pixel_({x},{y})_val_{int(pixel_value)}"
                    self.qt.insert(x, y, pixel_data)
                    self.pixels.append((x, y, pixel_value))
                    pixel_count += 1
        
        load_time = time.time() - start_time
        print(f"   ✅ Loaded {pixel_count:,} foreground pixels in {load_time:.3f}s")
        print(f"   📊 QuadTree depth: {self.qt.depth()}")
        print(f"   📊 QuadTree subdivisions: {self.qt.subdivisions()}")
        
        return pixel_count
    
    def detect_object_collisions(self, objects):
        """Detect collisions between objects and image pixels."""
        print(f"🎯 Detecting collisions for {len(objects)} objects...")
        
        collisions = []
        query_start = time.time()
        
        for obj_id, (x, y, width, height, obj_type) in enumerate(objects):
            # Query rectangular region around object
            region_pixels = self.qt.query(x - width//2, y - height//2, 
                                        x + width//2, y + height//2)
            
            if region_pixels:
                collision_info = {
                    'object_id': obj_id,
                    'object_type': obj_type,
                    'position': (x, y),
                    'size': (width, height),
                    'collision_points': len(region_pixels),
                    'pixels': region_pixels
                }
                collisions.append(collision_info)
        
        query_time = time.time() - query_start
        print(f"   ✅ Collision detection completed in {query_time:.4f}s")
        print(f"   🔥 Found {len(collisions)} collisions")
        
        return collisions
    
    def find_dense_regions(self, region_size=50):
        """Find dense pixel regions using spatial queries."""
        print(f"🔍 Finding dense regions with {region_size}x{region_size} windows...")
        
        dense_regions = []
        step = region_size // 2
        
        for y in range(0, self.height - region_size, step):
            for x in range(0, self.width - region_size, step):
                region_pixels = self.qt.query(x, y, x + region_size, y + region_size)
                
                if len(region_pixels) > 20:  # Threshold for "dense"
                    dense_regions.append({
                        'position': (x + region_size//2, y + region_size//2),
                        'size': (region_size, region_size),
                        'pixel_count': len(region_pixels),
                        'density': len(region_pixels) / (region_size * region_size)
                    })
        
        # Sort by density
        dense_regions.sort(key=lambda r: r['density'], reverse=True)
        
        print(f"   ✅ Found {len(dense_regions)} dense regions")
        return dense_regions[:10]  # Return top 10

class VoxelCollisionDetector:
    """3D Voxel collision detection using Octree."""
    
    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.tree = octree.Octree(0, 0, 0, width, height, depth)
        self.voxels = []
    
    def load_from_3d_array(self, voxel_data, threshold=0.5):
        """Load 3D voxel data into Octree."""
        print(f"📦 Loading {voxel_data.shape} voxel data into Octree...")
        
        voxel_count = 0
        start_time = time.time()
        
        for z in range(voxel_data.shape[2]):
            for y in range(voxel_data.shape[1]):
                for x in range(voxel_data.shape[0]):
                    voxel_value = voxel_data[x, y, z]
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
        """Detect 3D collisions between objects and voxels."""
        print(f"⚡ Detecting 3D collisions for {len(objects_3d)} objects...")
        
        collisions = []
        
        for obj_id, (x, y, z, radius, obj_type) in enumerate(objects_3d):
            # Use spherical query for more realistic 3D collision
            collision_voxels = self.tree.query_radius(x, y, z, radius)
            
            if collision_voxels:
                collision_info = {
                    'object_id': obj_id,
                    'object_type': obj_type,
                    'position': (x, y, z),
                    'radius': radius,
                    'collision_count': len(collision_voxels),
                    'voxels': collision_voxels
                }
                collisions.append(collision_info)
        
        print(f"   ✅ Found {len(collisions)} 3D collisions")
        return collisions

def create_sample_image(width=400, height=300):
    """Create a sample image for testing."""
    print(f"🎨 Creating sample {width}x{height} image...")
    
    # Create image with various shapes
    image = Image.new('RGB', (width, height), 'black')
    draw = ImageDraw.Draw(image)
    
    # Draw some shapes
    draw.rectangle([50, 50, 150, 100], fill='white')  # Rectangle
    draw.ellipse([200, 80, 280, 160], fill='gray')     # Circle
    draw.polygon([(100, 200), (150, 150), (200, 200), (150, 250)], fill='lightgray')  # Diamond
    
    # Add some random noise
    for _ in range(500):
        x, y = random.randint(0, width-1), random.randint(0, height-1)
        draw.point((x, y), fill='darkgray')
    
    return image

def create_sample_3d_data(width=50, height=50, depth=50):
    """Create sample 3D voxel data."""
    print(f"🧊 Creating sample {width}x{height}x{depth} voxel data...")
    
    voxel_data = np.zeros((width, height, depth))
    
    # Create 3D shapes
    center_x, center_y, center_z = width//2, height//2, depth//2
    
    # Sphere in center
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                dist = math.sqrt((x-center_x)**2 + (y-center_y)**2 + (z-center_z)**2)
                if dist < 15:
                    voxel_data[x, y, z] = 1.0 - (dist / 15)  # Gradient sphere
    
    # Add some random voxels
    for _ in range(1000):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)  
        z = random.randint(0, depth-1)
        voxel_data[x, y, z] = random.uniform(0.5, 1.0)
    
    return voxel_data

def performance_comparison():
    """Compare QuadTree vs brute force for collision detection."""
    print("\n⚡ PERFORMANCE COMPARISON: QuadTree vs Brute Force")
    print("=" * 60)
    
    # Create test data
    width, height = 800, 600
    num_objects = 100
    
    # Generate random image pixels
    pixels = [(random.randint(0, width-1), random.randint(0, height-1), 
               random.randint(100, 255)) for _ in range(5000)]
    
    # Generate test objects
    objects = [(random.randint(0, width-1), random.randint(0, height-1),
                random.randint(20, 80), random.randint(20, 80), f"obj_{i}")
               for i in range(num_objects)]
    
    # QuadTree method
    qt = quadtree.QuadTree(0, 0, width, height)
    
    qt_start = time.time()
    for x, y, value in pixels:
        qt.insert(x, y, f"pixel_{value}")
    qt_insert_time = time.time() - qt_start
    
    qt_start = time.time()
    qt_collisions = 0
    for obj_x, obj_y, obj_w, obj_h, obj_id in objects:
        results = qt.query(obj_x - obj_w//2, obj_y - obj_h//2,
                          obj_x + obj_w//2, obj_y + obj_h//2)
        if results:
            qt_collisions += 1
    qt_query_time = time.time() - qt_start
    
    # Brute force method
    bf_start = time.time()
    bf_collisions = 0
    for obj_x, obj_y, obj_w, obj_h, obj_id in objects:
        for px, py, pval in pixels:
            if (obj_x - obj_w//2 <= px <= obj_x + obj_w//2 and
                obj_y - obj_h//2 <= py <= obj_y + obj_h//2):
                bf_collisions += 1
                break  # Found collision, move to next object
    bf_query_time = time.time() - bf_start
    
    # Results
    print(f"📊 QuadTree Results:")
    print(f"   Insert time: {qt_insert_time:.4f}s")
    print(f"   Query time: {qt_query_time:.4f}s")
    print(f"   Collisions found: {qt_collisions}")
    print(f"   Tree depth: {qt.depth()}")
    
    print(f"\n📊 Brute Force Results:")
    print(f"   Query time: {bf_query_time:.4f}s")
    print(f"   Collisions found: {bf_collisions}")
    
    speedup = bf_query_time / qt_query_time if qt_query_time > 0 else float('inf')
    print(f"\n🚀 Performance Speedup: {speedup:.1f}x faster with QuadTree")

def main():
    """Main demonstration function."""
    print("🎯 IMAGE-BASED COLLISION DETECTION DEMONSTRATION")
    print("=" * 55)
    
    # Demo 1: 2D Image Collision Detection
    print("\n🖼️  DEMO 1: 2D Image Collision Detection")
    print("-" * 40)
    
    # Create and load sample image
    sample_image = create_sample_image(400, 300)
    image_array = np.array(sample_image.convert('L'))  # Convert to grayscale
    
    detector = ImageCollisionDetector(400, 300)
    pixel_count = detector.load_from_array(image_array, threshold=50)
    
    # Define some game objects
    game_objects = [
        (100, 75, 40, 30, "player"),
        (240, 120, 50, 50, "enemy"),
        (150, 200, 60, 40, "projectile"),
        (320, 180, 35, 35, "power_up"),
        (80, 250, 25, 25, "bullet")
    ]
    
    # Detect collisions
    collisions = detector.detect_object_collisions(game_objects)
    
    print("\n🔥 Collision Results:")
    for collision in collisions:
        obj = collision
        print(f"   🎯 {obj['object_type']} at {obj['position']} "
              f"collided with {obj['collision_points']} pixels")
    
    # Find dense regions
    dense_regions = detector.find_dense_regions(60)
    print(f"\n📍 Top Dense Regions:")
    for i, region in enumerate(dense_regions[:5]):
        print(f"   {i+1}. Position {region['position']}, "
              f"Density: {region['density']:.2%}")
    
    # Demo 2: 3D Voxel Collision Detection
    print("\n\n📦 DEMO 2: 3D Voxel Collision Detection")
    print("-" * 40)
    
    voxel_data = create_sample_3d_data(50, 50, 50)
    voxel_detector = VoxelCollisionDetector(50, 50, 50)
    voxel_count = voxel_detector.load_from_3d_array(voxel_data, threshold=0.3)
    
    # Define 3D objects
    objects_3d = [
        (25, 25, 25, 8, "sphere_collision"),
        (10, 10, 40, 12, "corner_object"),
        (40, 15, 30, 6, "small_probe"),
        (30, 35, 15, 10, "moving_entity")
    ]
    
    # Detect 3D collisions
    collisions_3d = voxel_detector.detect_3d_collisions(objects_3d)
    
    print("\n⚡ 3D Collision Results:")
    for collision in collisions_3d:
        obj = collision
        print(f"   🎯 {obj['object_type']} at {obj['position']} "
              f"(radius={obj['radius']}) collided with {obj['collision_count']} voxels")
    
    # Performance comparison
    performance_comparison()
    
    print(f"\n🎉 DEMONSTRATION COMPLETED")
    print(f"Both QuadTree and Octree provide efficient spatial indexing for:")
    print(f"   ✅ 2D image-based collision detection")
    print(f"   ✅ Pixel clustering and analysis") 
    print(f"   ✅ 3D voxel collision detection")
    print(f"   ✅ Significant performance improvements over brute force")

if __name__ == "__main__":
    main()