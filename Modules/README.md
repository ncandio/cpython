# QuadTree - Modern C++17 Spatial Data Structure

A high-performance spatial quadtree implementation for CPython, built with modern C++17 features. This module provides efficient 2D spatial indexing, range queries, and collision detection for point-based data.

## Features

### Core Functionality
- **Fast Point Insertion**: O(log n) average case insertion with automatic subdivision
- **Spatial Range Queries**: Efficiently query points within rectangular regions
- **Collision Detection**: Built-in collision detection with configurable radius
- **Data Attachment**: Associate arbitrary Python objects with points
- **Memory Efficient**: Smart pointer-based memory management with RAII

### Modern C++17 Implementation
- Constexpr functions for compile-time optimizations
- Smart pointers (`std::unique_ptr`) for automatic memory management
- Move semantics for efficient object transfers
- Exception-safe design with proper error handling
- Scoped enums and modern C++ best practices

### Python Integration
- Native Python C API integration
- Proper reference counting for attached Python objects
- Comprehensive error handling with meaningful messages
- Full support for Python's object model

## Installation

### Requirements
- Python 3.6 or higher
- C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)
- setuptools

### Build from Source
```bash
# Clone or navigate to the module directory
cd /path/to/cpython/Modules

# Build the extension
python3 setup.py build_ext --inplace

# Or install system-wide
python3 setup.py install
```

## Quick Start

```python
import quadtree

# Create a quadtree covering a 100x100 area
qt = quadtree.QuadTree(0, 0, 100, 100)

# Insert points (with optional data)
qt.insert(10, 20)                    # Point without data
qt.insert(30, 40, "important")       # Point with string data
qt.insert(50, 60, {"id": 1})         # Point with dict data

# Check if points exist
print(qt.contains(10, 20))           # True
print(qt.contains(99, 99))           # False

# Query points in a region
points = qt.query(0, 0, 50, 50)      # Get all points in rectangle
print(f"Found {len(points)} points")

# Detect collisions within radius
collisions = qt.detect_collisions(15.0)
for collision in collisions:
    p1 = collision["point1"]
    p2 = collision["point2"]
    print(f"Collision: {p1} <-> {p2}")

# Get statistics
print(f"Total points: {qt.size()}")
print(f"Tree depth: {qt.depth()}")
print(f"Subdivisions: {qt.subdivisions()}")
print(f"Boundary: {qt.boundary()}")
```

## API Reference

### Constructor

#### `QuadTree(x, y, width, height)`
Creates a new quadtree with the specified boundary.

**Parameters:**
- `x` (float): Left boundary coordinate
- `y` (float): Top boundary coordinate  
- `width` (float): Width of the boundary (must be > 0)
- `height` (float): Height of the boundary (must be > 0)

**Raises:**
- `ValueError`: If width or height is <= 0

### Methods

#### `insert(x, y, data=None) -> bool`
Insert a point into the quadtree.

**Parameters:**
- `x` (float): X coordinate
- `y` (float): Y coordinate
- `data` (object, optional): Python object to associate with the point

**Returns:**
- `bool`: True if insertion succeeded, False if point is outside boundary

#### `contains(x, y) -> bool`
Check if a point exists in the quadtree.

**Parameters:**
- `x` (float): X coordinate
- `y` (float): Y coordinate

**Returns:**
- `bool`: True if point exists, False otherwise

#### `query(x, y, width, height) -> list`
Query all points within a rectangular region.

**Parameters:**
- `x` (float): Left boundary of query rectangle
- `y` (float): Top boundary of query rectangle
- `width` (float): Width of query rectangle (must be >= 0)
- `height` (float): Height of query rectangle (must be >= 0)

**Returns:**
- `list`: List of tuples `(x, y)` or `(x, y, data)` for points in the region

**Raises:**
- `ValueError`: If width or height is < 0

#### `detect_collisions(radius) -> list`
Detect all point pairs within the specified distance.

**Parameters:**
- `radius` (float): Maximum distance for collision detection (must be >= 0)

**Returns:**
- `list`: List of collision dictionaries with `"point1"` and `"point2"` keys

**Raises:**
- `ValueError`: If radius is < 0

#### `get_all_points() -> list`
Get all points in the quadtree.

**Returns:**
- `list`: All points as tuples `(x, y)` or `(x, y, data)`

#### `size() -> int`
Get the total number of points in the quadtree.

**Returns:**
- `int`: Number of points

#### `empty() -> bool`
Check if the quadtree is empty.

**Returns:**
- `bool`: True if empty, False otherwise

#### `depth() -> int`
Get the maximum depth of the quadtree.

**Returns:**
- `int`: Maximum depth (0 for empty tree)

#### `subdivisions() -> int`
Get the number of subdivisions in the quadtree.

**Returns:**
- `int`: Number of internal nodes that have been subdivided

#### `boundary() -> tuple`
Get the boundary of the quadtree.

**Returns:**
- `tuple`: `(x, y, width, height)` of the quadtree boundary

## Performance Characteristics

### Time Complexity
- **Insertion**: O(log n) average, O(n) worst case (highly unbalanced)
- **Point Query**: O(log n) average, O(n) worst case
- **Range Query**: O(log n + k) where k is the number of results
- **Collision Detection**: O(n²) for all points (uses optimized spatial query)

### Space Complexity
- **Memory Usage**: O(n) where n is the number of points
- **Tree Structure**: Maximum depth of 10 levels (configurable)
- **Node Capacity**: 4 points per leaf node before subdivision

### Optimization Features
- **Smart Pointers**: Automatic memory management with RAII
- **Move Semantics**: Efficient object transfers without copying
- **Constexpr Functions**: Compile-time optimizations for geometry calculations
- **Reserved Capacity**: Pre-allocated vectors to reduce reallocations
- **Squared Distance**: Avoids expensive sqrt() calls in collision detection

## Use Cases

### Game Development
```python
# Collision detection for game objects
game_objects = quadtree.QuadTree(0, 0, 1920, 1080)

# Add game entities
game_objects.insert(player.x, player.y, player)
for enemy in enemies:
    game_objects.insert(enemy.x, enemy.y, enemy)

# Check collisions
collisions = game_objects.detect_collisions(32.0)  # 32 pixel radius
```

### Geographic Information Systems (GIS)
```python
# Spatial indexing for geographic data
poi_index = quadtree.QuadTree(-180, -90, 360, 180)  # World coordinates

# Add points of interest
poi_index.insert(-74.006, 40.7128, {"name": "New York", "population": 8000000})
poi_index.insert(-0.1276, 51.5074, {"name": "London", "population": 9000000})

# Query nearby locations
nearby = poi_index.query(-75, 40, 2, 2)  # 2-degree radius around NYC
```

### Scientific Computing
```python
# Particle simulation
particles = quadtree.QuadTree(0, 0, 1000, 1000)

# Add particles with properties
for i in range(10000):
    x, y = random.uniform(0, 1000), random.uniform(0, 1000)
    particles.insert(x, y, {"mass": random.uniform(1, 10), "velocity": (0, 0)})

# Efficient neighbor finding for force calculations
for collision in particles.detect_collisions(50.0):
    # Calculate forces between nearby particles
    pass
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_quadtree_simple.py
```

The test suite covers:
- Basic functionality (insertion, querying, containment)
- Data attachment and preservation
- Collision detection accuracy
- Edge cases and error conditions
- Performance with large datasets

## Development

### Building for Development
```bash
# Debug build with symbols
CFLAGS="-g -O0" python3 setup.py build_ext --inplace

# Release build with optimizations
CFLAGS="-O3 -DNDEBUG" python3 setup.py build_ext --inplace
```

### Code Organization
- `quadtree.cpp`: Main implementation with C++17 features
- `setup.py`: Build configuration with platform-specific optimizations
- `test_quadtree_simple.py`: Comprehensive test suite
- `README.md`: This documentation

### Contributing
This is part of the CPython project. Follow CPython's contribution guidelines for any modifications.

## Technical Details

### Memory Management
- Uses `std::unique_ptr` for automatic memory management
- Proper Python reference counting for attached data objects
- RAII ensures exception-safe cleanup
- Move semantics minimize memory allocations

### Thread Safety
The quadtree is **not thread-safe**. For concurrent access, use external synchronization:

```python
import threading
qt_lock = threading.Lock()

# Thread-safe insertion
with qt_lock:
    qt.insert(x, y, data)
```

### Limitations
- Maximum tree depth: 10 levels (prevents infinite subdivision)
- Node capacity: 4 points per leaf (optimal for most use cases)
- 2D only: Designed specifically for 2D spatial data
- No point removal: Currently insertion-only (removal can be added if needed)

## License

This module is part of CPython and follows the same licensing terms.

## Version History

### 2.0.0 (Current)
- Complete rewrite in modern C++17
- Added data attachment support
- Improved collision detection
- Enhanced error handling
- Comprehensive test suite

### 1.0.0 (Legacy)
- Basic quadtree implementation
- Simple point insertion and querying
- Limited Python integration