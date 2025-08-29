# Octree Module

A high-performance 3D spatial indexing data structure for efficient storage and querying of 3D points in Python.

## Overview

The Octree module provides a templated C++ implementation with Python bindings for spatial data organization in three-dimensional space. It enables efficient nearest-neighbor searches, range queries, and collision detection for 3D applications.

## Features

### Template-Based Design
- **Flexible Coordinate Types**: Support for `float`, `double`, and `int` coordinate systems
- **Configurable Parameters**: Compile-time customization of `MaxPointsPerNode` and `MaxDepth`
- **Type Safety**: Static assertions ensure arithmetic coordinate types
- **Memory Efficient**: Smart pointer-based memory management with move semantics

### Core Data Structures

#### Point3D<T>
```cpp
template<typename T>
struct Point3D {
    T x, y, z;              // Coordinates
    PyObject* data;         // Associated Python object
};
```

#### BoundingBox3D<T>
```cpp
template<typename T>
struct BoundingBox3D {
    T min_x, min_y, min_z;  // Minimum bounds
    T max_x, max_y, max_z;  // Maximum bounds
};
```

#### Octree<T, MaxPointsPerNode, MaxDepth>
```cpp
template<typename T, size_t MaxPointsPerNode = 8, size_t MaxDepth = 16>
class Octree {
    // 8-way spatial subdivision for 3D space
};
```

### Spatial Operations

- **Point Insertion**: Automatic subdivision when capacity exceeded
- **Bounding Box Queries**: Efficient rectangular region searches
- **Radius Queries**: Spherical region searches with distance calculations
- **Tree Management**: Size, depth, and clear operations

## Python API

### Basic Usage

```python
import octree

# Create octree with bounding box (min_x, min_y, min_z, max_x, max_y, max_z)
tree = octree.Octree(0, 0, 0, 100, 100, 100)

# Insert points with optional data
tree.insert(10, 20, 30)                    # Point only
tree.insert(50, 60, 70, "custom_data")     # Point with data

# Query points in bounding box
points = tree.query(0, 0, 0, 50, 50, 50)   # Returns list of (x, y, z, data) tuples

# Query points within radius
points = tree.query_radius(25, 25, 25, 20) # Center + radius

# Tree information
count = tree.size()     # Number of points
depth = tree.depth()    # Maximum tree depth
tree.clear()           # Remove all points
```

### Method Reference

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `insert(x, y, z, data=None)` | coordinates + optional data | `bool` | Insert point, returns success |
| `query(min_x, min_y, min_z, max_x, max_y, max_z)` | bounding box | `list` | Range query |
| `query_radius(center_x, center_y, center_z, radius)` | center + radius | `list` | Circular query |
| `size()` | none | `int` | Point count |
| `depth()` | none | `int` | Tree depth |
| `clear()` | none | `None` | Remove all points |

## Implementation Details

### Octant Organization
The octree divides 3D space into 8 octants:
- `TOP_LEFT_FRONT` (0): -x, +y, +z
- `TOP_RIGHT_FRONT` (1): +x, +y, +z
- `TOP_LEFT_BACK` (2): -x, +y, -z
- `TOP_RIGHT_BACK` (3): +x, +y, -z
- `BOTTOM_LEFT_FRONT` (4): -x, -y, +z
- `BOTTOM_RIGHT_FRONT` (5): +x, -y, +z
- `BOTTOM_LEFT_BACK` (6): -x, -y, -z
- `BOTTOM_RIGHT_BACK` (7): +x, -y, -z

### Performance Characteristics
- **Insertion**: O(log n) average, O(depth) worst case
- **Query**: O(log n + k) where k is result size
- **Memory**: O(n) space complexity
- **Subdivision**: Triggered when node exceeds `MaxPointsPerNode`

### Template Specializations
```cpp
using OctreeFloat = Octree<float>;      // Single precision
using OctreeDouble = Octree<double>;    // Double precision (Python default)
using OctreeInt = Octree<int>;          // Integer coordinates
```

## Integration with CPython

### Build Configuration
The module integrates with CPython's build system through:
- `Setup.stdlib.in`: Module definition with C++17 compilation flags
- `configure.ac`: Build system configuration
- Python C API bindings for seamless integration

### Memory Management
- **Reference Counting**: Proper Python object lifecycle management
- **Exception Safety**: C++ exceptions converted to Python exceptions
- **Resource Cleanup**: RAII pattern with smart pointers

## Use Cases

- **3D Graphics**: Frustum culling, collision detection
- **Spatial Databases**: Geographic information systems
- **Scientific Computing**: Particle simulations, molecular modeling
- **Game Development**: Level-of-detail systems, spatial partitioning
- **Computer Vision**: 3D point cloud processing

## Performance Notes

- Optimal performance with balanced point distributions
- Consider coordinate scale and precision requirements
- Tune `MaxPointsPerNode` based on query patterns
- Monitor tree depth for degenerate cases

## Comparison with QuadTree

| Feature | QuadTree | Octree |
|---------|----------|--------|
| Dimensions | 2D (x, y) | 3D (x, y, z) |
| Subdivisions | 4 quadrants | 8 octants |
| Use Cases | 2D spatial indexing | 3D spatial indexing |
| Memory | Lower per node | Higher per node |
| Complexity | Same algorithmic complexity | Same algorithmic complexity |

## Requirements

- **C++17**: Template features, constexpr, structured bindings
- **Python 3.15+**: CPython development version
- **Build Tools**: Standard CPython build environment