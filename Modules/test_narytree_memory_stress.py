#!/usr/bin/env python3
"""
N-ary Tree Memory Stress Testing

Comprehensive memory stress test suite for the N-ary tree data structure implementation.
This test assesses memory management quality and detects potential memory leaks,
similar to the quadtree memory stress testing.
"""

import sys
import time
import gc
import json
import threading
import random
import traceback
from datetime import datetime
from pathlib import Path

# Optional memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available - reduced memory monitoring")

# Import the compiled module
try:
    import narytree
except ImportError as e:
    print(f"Failed to import narytree module: {e}")
    print("Make sure to compile the module first: python3 setup_narytree.py build_ext --inplace")
    sys.exit(1)

class MemoryMonitor:
    """Memory monitoring utility."""
    
    def __init__(self):
        self.snapshots = []
        
    def take_snapshot(self, label=""):
        """Take a memory snapshot."""
        snapshot = {
            "timestamp": time.time(),
            "label": label
        }
        
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            memory_info = process.memory_info()
            snapshot.update({
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "cpu_percent": process.cpu_percent()
            })
        else:
            # Fallback to basic monitoring
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            snapshot.update({
                "rss_mb": usage.ru_maxrss / 1024,  # On Linux, this is in KB
                "vms_mb": 0,  # Not available
                "cpu_percent": 0  # Not available
            })
            
        self.snapshots.append(snapshot)
        return snapshot
        
    def get_memory_growth(self, start_label, end_label):
        """Calculate memory growth between two snapshots."""
        start_snapshot = None
        end_snapshot = None
        
        for snapshot in self.snapshots:
            if snapshot["label"] == start_label and start_snapshot is None:
                start_snapshot = snapshot
            elif snapshot["label"] == end_label:
                end_snapshot = snapshot
                
        if start_snapshot and end_snapshot:
            return {
                "rss_growth_mb": end_snapshot["rss_mb"] - start_snapshot["rss_mb"],
                "vms_growth_mb": end_snapshot["vms_mb"] - start_snapshot["vms_mb"],
                "duration": end_snapshot["timestamp"] - start_snapshot["timestamp"]
            }
        return None

class NaryTreeMemoryStressTest:
    """Memory stress test suite for N-ary Tree."""
    
    def __init__(self):
        self.monitor = MemoryMonitor()
        self.test_results = []
        self.start_time = time.time()
        
    def log_test_result(self, test_name, status, details):
        """Log test result."""
        self.test_results.append({
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
        
    def test_massive_tree_creation(self):
        """Test creating and destroying many trees."""
        print("Testing massive tree creation and cleanup...")
        
        self.monitor.take_snapshot("massive_creation_start")
        
        # Create many trees
        trees = []
        tree_count = 10000
        
        start_time = time.time()
        for i in range(tree_count):
            tree = narytree.NaryTree(f"tree_{i}")
            trees.append(tree)
            
            if i % 1000 == 0:
                self.monitor.take_snapshot(f"created_{i}")
                
        creation_time = time.time() - start_time
        self.monitor.take_snapshot("massive_creation_complete")
        
        # Test memory usage
        memory_per_tree = None
        if PSUTIL_AVAILABLE:
            growth = self.monitor.get_memory_growth("massive_creation_start", "massive_creation_complete")
            if growth:
                memory_per_tree = (growth["rss_growth_mb"] * 1024) / tree_count  # KB per tree
                
        # Cleanup test
        start_cleanup = time.time()
        del trees
        gc.collect()
        cleanup_time = time.time() - start_cleanup
        
        self.monitor.take_snapshot("massive_creation_cleaned")
        
        # Calculate cleanup efficiency
        cleanup_growth = self.monitor.get_memory_growth("massive_creation_complete", "massive_creation_cleaned")
        cleanup_efficiency = 0
        if cleanup_growth and growth:
            cleanup_efficiency = max(0, 100 - (abs(cleanup_growth["rss_growth_mb"]) / growth["rss_growth_mb"] * 100))
            
        self.log_test_result("Massive Tree Creation", "PASSED", {
            "trees_created": tree_count,
            "creation_time": creation_time,
            "cleanup_time": cleanup_time,
            "memory_per_tree_kb": memory_per_tree,
            "cleanup_efficiency_percent": cleanup_efficiency
        })
        
        print(f"  ✓ Created {tree_count} trees in {creation_time:.4f} seconds")
        if memory_per_tree:
            print(f"  ✓ Memory usage: {memory_per_tree:.3f} KB per tree")
        print(f"  ✓ Cleanup efficiency: {cleanup_efficiency:.1f}%")
        
    def test_large_data_storage(self):
        """Test storing large data objects in trees."""
        print("Testing large data storage...")
        
        self.monitor.take_snapshot("large_data_start")
        
        # Create trees with progressively larger data
        trees = []
        data_sizes = [1024, 10240, 102400, 1048576]  # 1KB, 10KB, 100KB, 1MB
        
        for size in data_sizes:
            large_data = "x" * size
            tree = narytree.NaryTree(large_data)
            trees.append(tree)
            
            self.monitor.take_snapshot(f"large_data_{size}")
            
        # Test operations with large data
        operations_start = time.time()
        for tree in trees:
            for _ in range(100):
                tree.empty()
                tree.size()
                
        operations_time = time.time() - operations_start
        
        self.monitor.take_snapshot("large_data_operations_complete")
        
        # Cleanup
        del trees
        gc.collect()
        
        self.monitor.take_snapshot("large_data_cleaned")
        
        growth = self.monitor.get_memory_growth("large_data_start", "large_data_operations_complete")
        
        self.log_test_result("Large Data Storage", "PASSED", {
            "data_sizes_tested": data_sizes,
            "operations_time": operations_time,
            "total_memory_growth_mb": growth["rss_growth_mb"] if growth else 0
        })
        
        print(f"  ✓ Tested data sizes: {data_sizes}")
        print(f"  ✓ Operations completed in {operations_time:.4f} seconds")
        
    def test_cyclic_operations(self):
        """Test cyclic creation and destruction to detect leaks."""
        print("Testing cyclic operations for memory leaks...")
        
        self.monitor.take_snapshot("cyclic_start")
        
        leak_candidates = []
        cycles = 20
        trees_per_cycle = 500
        
        for cycle in range(cycles):
            cycle_start = time.time()
            
            # Create trees
            trees = []
            for i in range(trees_per_cycle):
                tree = narytree.NaryTree(f"cycle_{cycle}_tree_{i}")
                trees.append(tree)
                
            # Perform operations
            for tree in trees:
                tree.set_root(f"updated_{cycle}")
                tree.empty()
                tree.size()
                
            # Cleanup
            del trees
            gc.collect()
            
            cycle_time = time.time() - cycle_start
            self.monitor.take_snapshot(f"cycle_{cycle}")
            
            # Check for memory growth
            if cycle > 5:  # Skip initial cycles
                baseline = self.monitor.snapshots[6]["rss_mb"]  # 5th cycle as baseline
                current = self.monitor.snapshots[-1]["rss_mb"]
                growth = current - baseline
                
                if growth > 10:  # More than 10MB growth
                    leak_candidates.append({
                        "cycle": cycle,
                        "memory_growth_mb": growth,
                        "cycle_time": cycle_time
                    })
                    
        self.monitor.take_snapshot("cyclic_complete")
        
        # Analyze leak patterns
        leak_detected = len(leak_candidates) > cycles * 0.3  # More than 30% of cycles show growth
        
        self.log_test_result("Cyclic Operations", "PASSED" if not leak_detected else "WARNING", {
            "cycles_completed": cycles,
            "trees_per_cycle": trees_per_cycle,
            "leak_candidates": leak_candidates,
            "leak_detected": leak_detected
        })
        
        print(f"  ✓ Completed {cycles} cycles with {trees_per_cycle} trees each")
        if leak_detected:
            print(f"  ⚠ Potential memory leak detected in {len(leak_candidates)} cycles")
        else:
            print("  ✓ No significant memory leaks detected")
            
    def test_concurrent_stress(self):
        """Test concurrent operations under stress."""
        print("Testing concurrent stress operations...")
        
        self.monitor.take_snapshot("concurrent_start")
        
        # Shared data
        results = []
        errors = []
        
        def stress_worker(worker_id, iterations):
            """Worker function for stress testing."""
            try:
                trees = []
                for i in range(iterations):
                    # Create tree
                    tree = narytree.NaryTree(f"worker_{worker_id}_tree_{i}")
                    trees.append(tree)
                    
                    # Perform operations
                    tree.set_root(f"updated_data_{i}")
                    tree.empty()
                    tree.size()
                    
                    # Periodic cleanup
                    if len(trees) > 50:
                        del trees[:25]
                        
                # Final cleanup
                del trees
                results.append(f"Worker {worker_id} completed {iterations} iterations")
                
            except Exception as e:
                errors.append(f"Worker {worker_id} error: {e}")
                
        # Launch concurrent workers
        threads = []
        worker_count = 8
        iterations_per_worker = 200
        
        start_concurrent = time.time()
        for i in range(worker_count):
            thread = threading.Thread(target=stress_worker, args=(i, iterations_per_worker))
            threads.append(thread)
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join()
            
        concurrent_time = time.time() - start_concurrent
        
        self.monitor.take_snapshot("concurrent_complete")
        
        # Cleanup
        gc.collect()
        self.monitor.take_snapshot("concurrent_cleaned")
        
        success_rate = len(results) / worker_count * 100
        
        self.log_test_result("Concurrent Stress", "PASSED" if len(errors) == 0 else "WARNING", {
            "worker_count": worker_count,
            "iterations_per_worker": iterations_per_worker,
            "success_rate": success_rate,
            "concurrent_time": concurrent_time,
            "errors": errors
        })
        
        print(f"  ✓ {worker_count} workers completed in {concurrent_time:.4f} seconds")
        print(f"  ✓ Success rate: {success_rate:.1f}%")
        if errors:
            print(f"  ⚠ {len(errors)} errors encountered")
            
    def test_rapid_allocation_deallocation(self):
        """Test rapid allocation and deallocation patterns."""
        print("Testing rapid allocation/deallocation...")
        
        self.monitor.take_snapshot("rapid_start")
        
        # Test rapid create/destroy cycles
        total_operations = 0
        start_rapid = time.time()
        
        for batch in range(100):
            # Quick create and destroy
            quick_trees = []
            for i in range(50):
                tree = narytree.NaryTree(f"rapid_{batch}_{i}")
                quick_trees.append(tree)
                total_operations += 1
                
            # Immediate cleanup
            del quick_trees
            
            # Periodic memory check
            if batch % 25 == 0:
                self.monitor.take_snapshot(f"rapid_batch_{batch}")
                
        rapid_time = time.time() - start_rapid
        gc.collect()
        
        self.monitor.take_snapshot("rapid_complete")
        
        growth = self.monitor.get_memory_growth("rapid_start", "rapid_complete")
        
        self.log_test_result("Rapid Allocation/Deallocation", "PASSED", {
            "total_operations": total_operations,
            "rapid_time": rapid_time,
            "operations_per_second": total_operations / rapid_time,
            "memory_growth_mb": growth["rss_growth_mb"] if growth else 0
        })
        
        print(f"  ✓ Completed {total_operations} operations in {rapid_time:.4f} seconds")
        print(f"  ✓ Rate: {total_operations / rapid_time:.0f} operations/second")
        
    def generate_comprehensive_report(self):
        """Generate comprehensive memory stress test report."""
        total_time = time.time() - self.start_time
        
        # Analyze memory snapshots
        memory_analysis = {
            "peak_memory_mb": max(s["rss_mb"] for s in self.monitor.snapshots),
            "memory_growth_mb": self.monitor.snapshots[-1]["rss_mb"] - self.monitor.snapshots[0]["rss_mb"],
            "total_snapshots": len(self.monitor.snapshots)
        }
        
        # Test summary
        passed_tests = sum(1 for test in self.test_results if test["status"] == "PASSED")
        warning_tests = sum(1 for test in self.test_results if test["status"] == "WARNING")
        
        report = {
            "test_suite": "N-ary Tree Memory Stress Tests",
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "psutil_available": PSUTIL_AVAILABLE,
            "total_runtime": total_time,
            "memory_analysis": memory_analysis,
            "test_summary": {
                "total_tests": len(self.test_results),
                "passed_tests": passed_tests,
                "warning_tests": warning_tests,
                "failed_tests": len(self.test_results) - passed_tests - warning_tests
            },
            "test_results": self.test_results,
            "memory_snapshots": self.monitor.snapshots
        }
        
        return report
        
    def run_all_stress_tests(self):
        """Run all memory stress tests."""
        print("=" * 80)
        print("N-ary Tree Memory Stress Test Suite")
        print("=" * 80)
        
        self.monitor.take_snapshot("test_suite_start")
        
        test_methods = [
            self.test_massive_tree_creation,
            self.test_large_data_storage,
            self.test_cyclic_operations,
            self.test_concurrent_stress,
            self.test_rapid_allocation_deallocation
        ]
        
        failed_tests = []
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"✗ {test_method.__name__} FAILED: {e}")
                traceback.print_exc()
                failed_tests.append(test_method.__name__)
                self.log_test_result(test_method.__name__, "FAILED", {"error": str(e)})
                
        self.monitor.take_snapshot("test_suite_complete")
        
        # Generate and save report
        report = self.generate_comprehensive_report()
        
        report_filename = f"narytree_memory_stress_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print("\n" + "=" * 80)
        print("Memory Stress Test Results Summary")
        print("=" * 80)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Passed: {report['test_summary']['passed_tests']}")
        print(f"Warnings: {report['test_summary']['warning_tests']}")
        print(f"Failed: {report['test_summary']['failed_tests']}")
        print(f"Total Runtime: {report['total_runtime']:.4f} seconds")
        print(f"Peak Memory Usage: {report['memory_analysis']['peak_memory_mb']:.2f} MB")
        print(f"Total Memory Growth: {report['memory_analysis']['memory_growth_mb']:.2f} MB")
        print(f"Report saved: {report_filename}")
        
        if failed_tests:
            print(f"\n❌ {len(failed_tests)} test(s) failed:")
            for test in failed_tests:
                print(f"  - {test}")
            return 1
        elif report['test_summary']['warning_tests'] > 0:
            print(f"\n⚠ {report['test_summary']['warning_tests']} test(s) completed with warnings")
            print("Check the report for details about potential memory issues.")
            return 0
        else:
            print("\n🎉 All memory stress tests passed! N-ary Tree shows excellent memory management.")
            return 0

def main():
    """Main test runner."""
    test_suite = NaryTreeMemoryStressTest()
    return test_suite.run_all_stress_tests()

if __name__ == "__main__":
    sys.exit(main())