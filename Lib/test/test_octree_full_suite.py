"""Full test suite runner for octree module.

This module provides a comprehensive test runner that executes all
octree-related tests in the proper order and generates detailed reports.
"""

import unittest
import sys
import time
import warnings
from test import support
from test.support import import_helper

# Import all octree test modules
try:
    # Try to import existing test modules
    test_modules = []
    
    try:
        from . import test_octree
        test_modules.append(('test_octree', test_octree))
    except ImportError:
        pass
    
    try:
        from . import test_octree_comprehensive
        test_modules.append(('test_octree_comprehensive', test_octree_comprehensive))
    except ImportError:
        pass
    
    try:
        from . import test_octree_performance
        test_modules.append(('test_octree_performance', test_octree_performance))
    except ImportError:
        pass
    
    try:
        from . import test_octree_subdivision
        test_modules.append(('test_octree_subdivision', test_octree_subdivision))
    except ImportError:
        pass
    
    try:
        from . import test_octree_stress_api
        test_modules.append(('test_octree_stress_api', test_octree_stress_api))
    except ImportError:
        pass
    
    try:
        from . import test_octree_stress_collisions
        test_modules.append(('test_octree_stress_collisions', test_octree_stress_collisions))
    except ImportError:
        pass
    
    try:
        from . import test_octree_stress_objects
        test_modules.append(('test_octree_stress_objects', test_octree_stress_objects))
    except ImportError:
        pass

except ImportError:
    # Fallback: try importing as standalone modules
    test_modules = []
    
    for module_name in ['test_octree', 'test_octree_comprehensive', 
                       'test_octree_performance', 'test_octree_subdivision',
                       'test_octree_stress_api', 'test_octree_stress_collisions',
                       'test_octree_stress_objects']:
        try:
            module = __import__(module_name)
            test_modules.append((module_name, module))
        except ImportError:
            continue

# Check if octree module is available
try:
    import octree
    OCTREE_AVAILABLE = True
except ImportError:
    OCTREE_AVAILABLE = False
    octree = None


class OctreeTestResult(unittest.TestResult):
    """Custom test result class for detailed octree test reporting."""
    
    def __init__(self):
        super().__init__()
        self.test_times = {}
        self.module_results = {}
        self.start_time = None
        
    def startTest(self, test):
        """Record test start time."""
        super().startTest(test)
        self.start_time = time.time()
        
    def stopTest(self, test):
        """Record test completion time."""
        super().stopTest(test)
        if self.start_time:
            test_time = time.time() - self.start_time
            self.test_times[str(test)] = test_time
            
            # Track results by module
            module_name = test.__class__.__module__
            if module_name not in self.module_results:
                self.module_results[module_name] = {
                    'tests': 0, 'failures': 0, 'errors': 0, 'time': 0
                }
            
            self.module_results[module_name]['tests'] += 1
            self.module_results[module_name]['time'] += test_time
            
    def addFailure(self, test, err):
        """Record test failure."""
        super().addFailure(test, err)
        module_name = test.__class__.__module__
        if module_name in self.module_results:
            self.module_results[module_name]['failures'] += 1
            
    def addError(self, test, err):
        """Record test error."""
        super().addError(test, err)
        module_name = test.__class__.__module__
        if module_name in self.module_results:
            self.module_results[module_name]['errors'] += 1


class OctreeTestRunner(unittest.TextTestRunner):
    """Custom test runner for octree tests."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resultclass = OctreeTestResult
        
    def run(self, test):
        """Run tests and provide detailed reporting."""
        print("=" * 70)
        print("OCTREE MODULE COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        if not OCTREE_AVAILABLE:
            print("❌ OCTREE MODULE NOT AVAILABLE")
            print("   The octree module could not be imported.")
            print("   Please ensure it is compiled and available in the Python path.")
            return None
        
        print(f"✅ Octree module successfully imported")
        print(f"   Module: {octree.__file__ if hasattr(octree, '__file__') else 'built-in'}")
        print("")
        
        # Run the tests
        result = super().run(test)
        
        # Print detailed results
        self._print_detailed_results(result)
        
        return result
    
    def _print_detailed_results(self, result):
        """Print detailed test results."""
        print("\n" + "=" * 70)
        print("DETAILED TEST RESULTS")
        print("=" * 70)
        
        # Overall summary
        total_time = sum(result.test_times.values())
        print(f"Total tests run: {result.testsRun}")
        print(f"Total time: {total_time:.3f}s")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        # Module breakdown
        if result.module_results:
            print(f"\n{'Module':^30} {'Tests':^8} {'Pass':^8} {'Fail':^8} {'Error':^8} {'Time(s)':^10}")
            print("-" * 75)
            
            for module_name, stats in result.module_results.items():
                passed = stats['tests'] - stats['failures'] - stats['errors']
                module_short = module_name.split('.')[-1]
                print(f"{module_short:^30} {stats['tests']:^8} {passed:^8} "
                      f"{stats['failures']:^8} {stats['errors']:^8} {stats['time']:^10.3f}")
        
        # Performance summary for performance tests
        performance_tests = [name for name in result.test_times.keys() 
                           if 'performance' in name.lower() or 'stress' in name.lower()]
        
        if performance_tests:
            print(f"\nPerformance Test Summary:")
            print(f"{'Test':^40} {'Time(s)':^10}")
            print("-" * 52)
            
            for test_name in sorted(performance_tests, key=lambda x: result.test_times[x]):
                short_name = test_name.split('.')[-1]
                print(f"{short_name:^40} {result.test_times[test_name]:^10.4f}")
        
        # Failures and errors
        if result.failures:
            print(f"\n❌ FAILURES ({len(result.failures)}):")
            for test, traceback in result.failures:
                print(f"   {test}")
                # Print first few lines of traceback
                lines = traceback.split('\n')[:5]
                for line in lines:
                    if line.strip():
                        print(f"     {line}")
        
        if result.errors:
            print(f"\n❌ ERRORS ({len(result.errors)}):")
            for test, traceback in result.errors:
                print(f"   {test}")
                # Print first few lines of traceback
                lines = traceback.split('\n')[:5]
                for line in lines:
                    if line.strip():
                        print(f"     {line}")
        
        # Final verdict
        print("\n" + "=" * 70)
        if result.wasSuccessful():
            print("🎉 ALL TESTS PASSED!")
            print("   The octree implementation is working correctly.")
        else:
            print("⚠️  SOME TESTS FAILED!")
            print("   Please review the failures and errors above.")
        print("=" * 70)


def create_test_suite():
    """Create comprehensive test suite for octree module."""
    if not OCTREE_AVAILABLE:
        # Return empty suite if octree not available
        return unittest.TestSuite()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests in logical order (basic -> comprehensive -> performance -> stress)
    test_order = [
        'test_octree_comprehensive',
        'test_octree', 
        'test_octree_subdivision',
        'test_octree_performance',
        'test_octree_stress_api',
        'test_octree_stress_collisions',
        'test_octree_stress_objects',
    ]
    
    added_modules = set()
    
    # Add modules in preferred order
    for module_name in test_order:
        for mod_name, module in test_modules:
            if mod_name == module_name and module not in added_modules:
                try:
                    module_suite = loader.loadTestsFromModule(module)
                    suite.addTest(module_suite)
                    added_modules.add(module)
                    print(f"Added test module: {mod_name}")
                except Exception as e:
                    print(f"Warning: Could not load tests from {mod_name}: {e}")
    
    # Add any remaining modules
    for mod_name, module in test_modules:
        if module not in added_modules:
            try:
                module_suite = loader.loadTestsFromModule(module)
                suite.addTest(module_suite)
                added_modules.add(module)
                print(f"Added test module: {mod_name}")
            except Exception as e:
                print(f"Warning: Could not load tests from {mod_name}: {e}")
    
    return suite


def run_octree_tests(verbosity=2):
    """Run all octree tests with detailed output."""
    # Filter warnings for cleaner output
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        warnings.simplefilter("ignore", PendingDeprecationWarning)
        
        # Create test suite
        suite = create_test_suite()
        
        if suite.countTestCases() == 0:
            print("No octree tests found or octree module not available.")
            return None
        
        # Run tests with custom runner
        runner = OctreeTestRunner(verbosity=verbosity, buffer=True)
        result = runner.run(suite)
        
        return result


# Support for running as main module
if __name__ == '__main__':
    # Parse command line arguments
    verbosity = 2
    if len(sys.argv) > 1 and sys.argv[1] == '-q':
        verbosity = 0
    elif len(sys.argv) > 1 and sys.argv[1] == '-v':
        verbosity = 2
    elif len(sys.argv) > 1 and sys.argv[1] == '-vv':
        verbosity = 3
    
    # Run the tests
    result = run_octree_tests(verbosity)
    
    # Exit with appropriate code
    if result is None:
        sys.exit(1)  # Module not available
    elif not result.wasSuccessful():
        sys.exit(1)  # Tests failed
    else:
        sys.exit(0)  # All good


# Support for test discovery
def load_tests(loader, tests, pattern):
    """Support test discovery."""
    return create_test_suite()