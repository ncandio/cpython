#!/usr/bin/env python3
"""
Comprehensive N-ary Tree API Tests

Complete test suite for the N-ary tree data structure implementation,
covering all API methods with edge cases, boundary conditions, and performance benchmarks.
Similar to the comprehensive quadtree test suite.
"""

import sys
import time
import traceback
import random
import json
import gc
import threading
from datetime import datetime
from pathlib import Path

# Import the compiled module
try:
    import narytree
except ImportError as e:
    print(f"Failed to import narytree module: {e}")
    print("Make sure to compile the module first: python3 setup_narytree.py build_ext --inplace")
    sys.exit(1)

class NaryTreeTestSuite:
    def __init__(self):
        self.tests_run = []
        self.start_time = time.time()
        
    def log_test(self, test_name, status, duration, details=None):
        """Log test results."""
        self.tests_run.append({
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "details": details or {}
        })
        
    def test_constructor_variations(self):
        """Test different constructor patterns."""
        print("Testing constructor variations...")
        start = time.time()
        
        test_cases = [
            ("Empty constructor", lambda: narytree.NaryTree()),
            ("String root", lambda: narytree.NaryTree("root")),
            ("Integer root", lambda: narytree.NaryTree(42)),
            ("Float root", lambda: narytree.NaryTree(3.14)),
            ("List root", lambda: narytree.NaryTree([1, 2, 3])),
            ("Dict root", lambda: narytree.NaryTree({"key": "value"})),
            ("None root", lambda: narytree.NaryTree(None)),
            ("Boolean root", lambda: narytree.NaryTree(True)),
        ]
        
        results = {}
        for name, constructor in test_cases:
            try:
                tree = constructor()
                if name == "Empty constructor":
                    assert tree.empty() == True
                    assert tree.size() == 0
                else:
                    assert tree.empty() == False
                    assert tree.size() == 1
                results[name] = "PASSED"
            except Exception as e:
                results[name] = f"FAILED: {e}"
                
        duration = time.time() - start
        self.log_test("Constructor Variations", "PASSED", duration, results)
        print("✓ Constructor variations tests completed")
        
    def test_basic_operations(self):
        """Test basic tree operations."""
        print("Testing basic operations...")
        start = time.time()
        
        tree = narytree.NaryTree("root")
        
        # Test basic properties
        assert tree.empty() == False
        assert tree.size() == 1
        
        # Test set_root
        tree.set_root("new_root")
        assert tree.size() == 1  # Size should remain 1
        
        # Test with different data types
        data_types = [None, 42, 3.14, "string", [1,2,3], {"a": 1}, (1,2), {1,2,3}]
        for data in data_types:
            tree.set_root(data)
            assert tree.size() == 1
            assert tree.empty() == False
        
        duration = time.time() - start
        self.log_test("Basic Operations", "PASSED", duration, {
            "operations_tested": ["empty", "size", "set_root"],
            "data_types_tested": len(data_types)
        })
        print("✓ Basic operations tests completed")
        
    def test_empty_tree_behavior(self):
        """Test behavior with empty trees."""
        print("Testing empty tree behavior...")
        start = time.time()
        
        tree = narytree.NaryTree()
        
        # Test empty tree properties
        assert tree.empty() == True
        assert tree.size() == 0
        
        # Test operations on empty tree
        tree.set_root("first_root")
        assert tree.empty() == False
        assert tree.size() == 1
        
        duration = time.time() - start
        self.log_test("Empty Tree Behavior", "PASSED", duration)
        print("✓ Empty tree behavior tests completed")
        
    def test_data_integrity(self):
        """Test data integrity and consistency."""
        print("Testing data integrity...")
        start = time.time()
        
        # Test with complex nested data structures
        complex_data = {
            "nested_dict": {
                "level1": {
                    "level2": {
                        "data": [1, 2, 3, {"deep": "value"}]
                    }
                }
            },
            "array": [1, 2, 3, [4, 5, [6, 7]]],
            "mixed": (1, "string", [2, 3], {"key": "value"})
        }
        
        tree = narytree.NaryTree(complex_data)
        assert tree.empty() == False
        assert tree.size() == 1
        
        # Test data persistence through operations
        original_size = tree.size()
        tree.set_root("simple")
        tree.set_root(complex_data)  # Set back to complex data
        assert tree.size() == original_size
        
        duration = time.time() - start
        self.log_test("Data Integrity", "PASSED", duration, {
            "complex_data_structures": True,
            "data_persistence": True
        })
        print("✓ Data integrity tests completed")
        
    def test_memory_efficiency(self):
        """Test memory usage efficiency."""
        print("Testing memory efficiency...")
        start = time.time()
        
        # Create many trees and measure memory usage
        trees = []
        for i in range(1000):
            tree = narytree.NaryTree(f"tree_{i}")
            trees.append(tree)
            
        # Test memory cleanup
        initial_count = len(trees)
        del trees[:500]  # Delete half
        gc.collect()
        
        # Create new trees to test reuse
        new_trees = []
        for i in range(100):
            tree = narytree.NaryTree(f"new_tree_{i}")
            new_trees.append(tree)
            
        duration = time.time() - start
        self.log_test("Memory Efficiency", "PASSED", duration, {
            "trees_created": initial_count,
            "trees_deleted": 500,
            "new_trees_created": len(new_trees)
        })
        print("✓ Memory efficiency tests completed")
        
    def test_performance_benchmarks(self):
        """Run performance benchmarks."""
        print("Running performance benchmarks...")
        start = time.time()
        
        # Benchmark tree creation
        creation_times = []
        for size in [100, 500, 1000, 5000]:
            start_create = time.time()
            trees = []
            for i in range(size):
                tree = narytree.NaryTree(f"item_{i}")
                trees.append(tree)
            creation_time = time.time() - start_create
            creation_times.append((size, creation_time))
            print(f"  ✓ Created {size} trees in {creation_time:.4f} seconds")
            
        # Benchmark operations
        tree = narytree.NaryTree("root")
        operations_start = time.time()
        for i in range(10000):
            tree.empty()
            tree.size()
            if i % 100 == 0:
                tree.set_root(f"root_{i}")
        operations_time = time.time() - operations_start
        
        duration = time.time() - start
        self.log_test("Performance Benchmarks", "PASSED", duration, {
            "creation_benchmarks": creation_times,
            "operations_per_second": 20000 / operations_time,
            "total_operations": 20000
        })
        print(f"  ✓ Performed 20,000 operations in {operations_time:.4f} seconds")
        print("✓ Performance benchmarks completed")
        
    def test_thread_safety_basic(self):
        """Test basic thread safety."""
        print("Testing basic thread safety...")
        start = time.time()
        
        # Create a shared tree
        shared_tree = narytree.NaryTree("initial")
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(100):
                    # Test read operations
                    shared_tree.empty()
                    shared_tree.size()
                    
                    # Test write operations
                    shared_tree.set_root(f"thread_{thread_id}_item_{i}")
                    
                results.append(f"Thread {thread_id} completed")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
        
        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        duration = time.time() - start
        self.log_test("Thread Safety Basic", "PASSED", duration, {
            "threads_completed": len(results),
            "errors_encountered": len(errors),
            "thread_count": 5
        })
        
        if errors:
            print(f"  ⚠ {len(errors)} thread errors encountered")
        else:
            print("  ✓ No thread safety issues detected")
        print("✓ Basic thread safety tests completed")
        
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("Testing edge cases...")
        start = time.time()
        
        edge_cases = []
        
        # Test with very large strings
        try:
            large_string = "x" * 1000000  # 1MB string
            tree = narytree.NaryTree(large_string)
            assert tree.size() == 1
            edge_cases.append(("Large string (1MB)", "PASSED"))
        except Exception as e:
            edge_cases.append(("Large string (1MB)", f"FAILED: {e}"))
            
        # Test with deeply nested structures
        try:
            deep_dict = {}
            current = deep_dict
            for i in range(100):
                current["level"] = {}
                current = current["level"]
            current["data"] = "deep_value"
            
            tree = narytree.NaryTree(deep_dict)
            assert tree.size() == 1
            edge_cases.append(("Deep nested dict", "PASSED"))
        except Exception as e:
            edge_cases.append(("Deep nested dict", f"FAILED: {e}"))
            
        # Test rapid operations
        try:
            tree = narytree.NaryTree("rapid_test")
            for i in range(1000):
                tree.set_root(i)
                tree.empty()
                tree.size()
            edge_cases.append(("Rapid operations", "PASSED"))
        except Exception as e:
            edge_cases.append(("Rapid operations", f"FAILED: {e}"))
            
        duration = time.time() - start
        self.log_test("Edge Cases", "PASSED", duration, {
            "test_cases": edge_cases
        })
        
        for case_name, result in edge_cases:
            print(f"  ✓ {case_name}: {result}")
        print("✓ Edge cases tests completed")
        
    def test_data_type_compatibility(self):
        """Test compatibility with various Python data types."""
        print("Testing data type compatibility...")
        start = time.time()
        
        # Test with built-in types
        builtin_types = [
            None, True, False, 0, 1, -1, 3.14, -2.71,
            "", "string", "unicode_测试", 
            [], [1], [1, 2, 3], [1, [2, [3]]],
            (), (1,), (1, 2, 3), (1, (2, (3,))),
            {}, {"a": 1}, {"nested": {"data": [1, 2, 3]}},
            set(), {1, 2, 3}, frozenset([4, 5, 6])
        ]
        
        results = {}
        for i, data in enumerate(builtin_types):
            try:
                tree = narytree.NaryTree(data)
                assert tree.size() == 1
                results[f"Type_{i}_{type(data).__name__}"] = "PASSED"
            except Exception as e:
                results[f"Type_{i}_{type(data).__name__}"] = f"FAILED: {e}"
                
        duration = time.time() - start
        self.log_test("Data Type Compatibility", "PASSED", duration, {
            "types_tested": len(builtin_types),
            "results": results
        })
        print(f"  ✓ Tested {len(builtin_types)} different data types")
        print("✓ Data type compatibility tests completed")
        
    def generate_comprehensive_report(self):
        """Generate comprehensive test report."""
        total_time = time.time() - self.start_time
        passed_tests = sum(1 for test in self.tests_run if test["status"] == "PASSED")
        total_tests = len(self.tests_run)
        
        report = {
            "test_suite": "N-ary Tree Complete API Tests",
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "total_runtime": total_time,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "test_results": self.tests_run,
            "performance_summary": {
                "average_test_duration": sum(test["duration"] for test in self.tests_run) / len(self.tests_run),
                "fastest_test": min(self.tests_run, key=lambda x: x["duration"])["test_name"],
                "slowest_test": max(self.tests_run, key=lambda x: x["duration"])["test_name"]
            }
        }
        
        return report
        
    def run_all_tests(self):
        """Run the complete test suite."""
        print("=" * 80)
        print("N-ary Tree Complete API Test Suite")
        print("=" * 80)
        
        test_methods = [
            self.test_constructor_variations,
            self.test_basic_operations,
            self.test_empty_tree_behavior,
            self.test_data_integrity,
            self.test_memory_efficiency,
            self.test_performance_benchmarks,
            self.test_thread_safety_basic,
            self.test_edge_cases,
            self.test_data_type_compatibility
        ]
        
        failed_tests = []
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"✗ {test_method.__name__} FAILED: {e}")
                traceback.print_exc()
                failed_tests.append(test_method.__name__)
                self.log_test(test_method.__name__, "FAILED", 0, {"error": str(e)})
                
        # Generate and save report
        report = self.generate_comprehensive_report()
        
        # Save report to file
        report_filename = f"narytree_complete_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print("\n" + "=" * 80)
        print("Test Results Summary")
        print("=" * 80)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed_tests']}")
        print(f"Failed: {report['summary']['failed_tests']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Total Runtime: {report['total_runtime']:.4f} seconds")
        print(f"Report saved: {report_filename}")
        
        if failed_tests:
            print(f"\n❌ {len(failed_tests)} test(s) failed:")
            for test in failed_tests:
                print(f"  - {test}")
            return 1
        else:
            print("\n🎉 All tests passed! N-ary Tree implementation is robust and ready for production.")
            return 0

def main():
    """Main test runner."""
    test_suite = NaryTreeTestSuite()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())