# Octree Testing Guide

This document describes the comprehensive test suite for the CPython octree module.

## Overview

The octree module test suite consists of several test modules that thoroughly validate the functionality, performance, and reliability of the 3D spatial indexing implementation.

## Test Modules

### Core Test Modules

1. **`test_octree_comprehensive.py`** - Primary comprehensive test suite
   - Complete API functionality testing
   - Edge case validation
   - Error handling verification
   - Memory management tests
   - Follows CPython testing conventions

2. **`test_octree_performance.py`** - Performance and benchmarking tests
   - Insertion performance benchmarks
   - Query performance analysis
   - Memory efficiency tests  
   - Scalability analysis

3. **`test_octree_full_suite.py`** - Test suite runner and coordinator
   - Orchestrates all test modules
   - Provides detailed reporting
   - Custom test runner with timing and statistics

### Specialized Test Modules

4. **`test_octree.py`** - Original basic test suite
   - Fundamental functionality tests
   - Basic insertion and query operations

5. **`test_octree_subdivision.py`** - Subdivision behavior analysis
   - Detailed subdivision mechanism testing
   - Visual/explanatory subdivision tests

6. **`test_octree_stress_api.py`** - API stress testing
   - Boundary condition testing
   - Invalid input handling
   - Concurrent access patterns

7. **`test_octree_stress_*`** - Additional stress test modules
   - High-load scenario testing
   - Memory pressure tests
   - Performance under stress

## Running Tests

### Quick Start

From the CPython source directory:

```bash
# Run all octree tests
python run_octree_tests.py

# Run with minimal output
python run_octree_tests.py -q

# Run only performance tests
python run_octree_tests.py --performance

# List available test modules
python run_octree_tests.py --list
```

### Using Python's unittest

```bash
# Run comprehensive tests
python -m unittest test.test_octree_comprehensive -v

# Run performance tests (requires CPU resources)
python -m unittest test.test_octree_performance -v

# Run full suite
python -m unittest test.test_octree_full_suite -v
```

### Using CPython's test framework

```bash
# Run octree tests through CPython test framework
python -m test test_octree_comprehensive

# Run with resource allocation
python -m test -u cpu,memory test_octree_performance
```

## Test Categories

### Functional Tests
- **Creation & Initialization**: Valid/invalid octree creation
- **Point Insertion**: Basic insertion, boundary cases, out-of-bounds
- **Query Operations**: Bounding box queries, radius queries, empty results
- **Tree Properties**: Size, depth, memory usage, emptiness checks
- **Data Management**: Clear operations, data association

### Performance Tests
- **Insertion Performance**: Timing point insertion with various data sizes
- **Query Performance**: Benchmarking different query types and sizes
- **Memory Efficiency**: Memory usage per point, scaling analysis
- **Scalability**: Performance characteristics with large datasets

### Stress Tests
- **API Abuse**: Rapid operations, invalid inputs, boundary hammering
- **Concurrent Access**: Thread safety (if supported)
- **Memory Pressure**: Large objects, memory limits
- **Edge Cases**: Extreme coordinates, precision limits

### Subdivision Tests
- **Threshold Behavior**: Subdivision triggering at capacity limits
- **Octant Distribution**: Proper point distribution across octants
- **Deep Subdivision**: Cascading subdivision with clustered points
- **Maximum Depth**: Behavior at subdivision limits

## Test Data Patterns

The test suite uses various data distribution patterns:

1. **Uniform Distribution**: Points spread evenly throughout space
2. **Clustered Distribution**: Points grouped around specific centers
3. **Grid Distribution**: Points arranged in regular grid patterns
4. **Boundary Distribution**: Points concentrated at octree boundaries
5. **Random Distribution**: Pseudo-random point placement

## Performance Benchmarks

The performance tests establish baseline expectations:

- **Insertion Rate**: Should handle >1000 points/second
- **Query Response**: Small region queries <1ms
- **Memory Efficiency**: <1KB per point storage overhead
- **Scalability**: Better than O(n²) time complexity

## Error Handling

Tests validate proper error handling for:

- Invalid octree bounds (min > max)
- Out-of-bounds point insertion
- Invalid query parameters
- NaN and infinity coordinate values
- Memory allocation failures

## CPython Integration

The tests follow CPython conventions:

- Use of `test.support` utilities
- Resource requirement decorators (`@support.requires_resource`)
- Proper module import error handling
- Standard unittest.TestCase structure
- Appropriate skip conditions

## Debugging Tests

For test debugging:

```bash
# Run specific test class
python -m unittest test.test_octree_comprehensive.OctreeCreationTest -v

# Run single test method
python -m unittest test.test_octree_comprehensive.OctreeCreationTest.test_valid_creation -v

# Run with Python debugger
python -m pdb -m unittest test.test_octree_comprehensive -v
```

## Test Results Interpretation

### Success Indicators
- All tests pass without errors or failures
- Performance benchmarks meet expectations
- Memory usage scales reasonably
- Subdivision behaves correctly

### Common Issues
- **Import Errors**: Octree module not compiled or not in path
- **Performance Failures**: Hardware-dependent benchmark failures
- **Memory Issues**: System memory constraints affecting large tests
- **Precision Issues**: Floating-point precision edge cases

## Contributing

When adding new octree tests:

1. Follow existing test patterns and naming conventions
2. Include docstrings explaining test purpose
3. Use appropriate test categories (functional/performance/stress)
4. Add resource requirements for expensive tests
5. Include both positive and negative test cases
6. Update this documentation

## Dependencies

- Python 3.15+ (CPython development version)
- Compiled octree module
- Standard library test utilities
- Sufficient system resources for performance tests

For questions or issues with the test suite, refer to the octree module documentation or CPython development guidelines.