# How to Run Spatial Data Structure Tests

## 🚀 **Quick Start - Run Everything**

### **Option 1: Run All Tests (Recommended)**
```bash
cd /home/nico/WORK_ROOT/cpython
python3 run_all_tests.py
```
This runs all available tests and demos with a comprehensive summary.

### **Option 2: Run Individual Tests**

#### **Basic Functionality**
```bash
# Basic module demonstration
python3 demo_spatial_modules.py

# Core octree tests
python3 Lib/test/test_octree.py

# Subdivision analysis
python3 Lib/test/test_octree_subdivision.py
```

#### **Stress Tests**
```bash
# Collision detection stress tests
python3 Lib/test/test_octree_stress_collisions.py

# Object creation stress tests  
python3 Lib/test/test_octree_stress_objects.py

# API robustness stress tests
python3 Lib/test/test_octree_stress_api.py

# All stress tests together
python3 Lib/test/run_octree_stress_tests.py
```

#### **Application Examples**
```bash
# Image collision detection
python3 simple_image_collision_demo.py

# Game development examples
python3 game_collision_examples.py
```

#### **Educational Demos**
```bash
# QuadTree basics
python3 simple_quadtree_test.py

# Subdivision visualization
python3 subdivision_demo.py
```

## 📊 **What Each Test Does**

### **Core Tests**
- **`test_octree.py`**: 21 unit tests covering basic functionality
- **`test_octree_subdivision.py`**: Detailed subdivision algorithm analysis
- **`demo_spatial_modules.py`**: Basic usage demonstration

### **Stress Tests**
- **`test_octree_stress_collisions.py`**: Collision detection with 50K+ objects
- **`test_octree_stress_objects.py`**: Memory management and object lifecycle
- **`test_octree_stress_api.py`**: API robustness under extreme conditions

### **Applications**
- **`simple_image_collision_demo.py`**: Image-based collision detection
- **`game_collision_examples.py`**: Game development scenarios

### **Performance Benchmarks**
- **All stress tests**: Include performance comparisons vs brute force
- **Memory usage tracking**: Monitor memory efficiency
- **Scalability tests**: Performance with increasing data sizes

## 🎯 **Expected Results**

### **All Tests Should Pass**
✅ Core functionality: 21/21 tests pass  
✅ Stress tests: All performance benchmarks complete  
✅ Application demos: Real-world scenarios work  

### **Performance Expectations**
- **QuadTree**: 1M+ insertions/sec, microsecond queries
- **Octree**: 500K+ insertions/sec, sub-millisecond queries  
- **Memory**: 200-500 bytes per object
- **Scalability**: Handles 50K+ objects efficiently

## 🛠️ **Troubleshooting**

### **If Tests Fail**
1. **Check module availability**:
   ```bash
   python3 -c "import quadtree, octree; print('✅ Modules available')"
   ```

2. **Verify installation**:
   ```bash
   ls -la /usr/local/lib/python3.15/lib-dynload/*tree*
   ```

3. **Check Python version**:
   ```bash
   python3 --version  # Should be Python 3.15+
   ```

### **Common Issues**
- **Import Error**: Modules not installed system-wide
- **Timeout**: Large stress tests may take several minutes
- **Memory Error**: Stress tests require sufficient RAM

## 📈 **Performance Monitoring**

### **During Tests, Monitor**:
- **CPU Usage**: Should be efficient
- **Memory Usage**: Watch for memory leaks
- **Execution Time**: Compare with benchmarks

### **Key Metrics**:
- **Insertion Rate**: Objects/second inserted
- **Query Time**: Microseconds per query
- **Memory Efficiency**: Bytes per object
- **Tree Depth**: Subdivision levels reached

## 🎮 **Interactive Testing**

### **Quick Manual Test**:
```python
# Test QuadTree
import quadtree
qt = quadtree.QuadTree(0, 0, 100, 100)
qt.insert(50, 50, "center_point")
results = qt.query(40, 40, 60, 60)
print(f"Found: {results}")

# Test Octree  
import octree
tree = octree.Octree(0, 0, 0, 100, 100, 100)
tree.insert(50, 50, 50, "center_object")
results = tree.query(40, 40, 40, 60, 60, 60)
print(f"Found: {results}")
```

## 🏁 **Success Criteria**

### **✅ All Tests Pass When**:
- No import errors
- All functionality tests complete
- Performance benchmarks within expected ranges
- Memory usage remains stable
- No crashes or exceptions

### **📊 Expected Output**:
```
🎯 Overall Results:
   ✅ Passed: 10/10 (100.0%)
   ❌ Failed: 0/10

🏁 Test Runner Completed!
```

---

**Both QuadTree and Octree are ready for production use in Python applications!**