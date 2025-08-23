#!/usr/bin/env python3
"""
Simple test runner for octree tests.

This script provides an easy way to run all octree tests from the command line.
It can be run from the project root directory.

Usage:
    python run_octree_tests.py [options]
    
Options:
    -q, --quiet     : Minimal output
    -v, --verbose   : Verbose output (default)
    -vv, --very-verbose : Very verbose output
    --performance   : Run only performance tests
    --basic        : Run only basic functionality tests
    --stress       : Run only stress tests
    --help, -h     : Show this help message
"""

import sys
import os
import argparse

# Add Lib directory to path so we can import test modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Lib'))

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="Run octree module tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Minimal output')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-vv', '--very-verbose', action='store_true',
                       help='Very verbose output')
    parser.add_argument('--performance', action='store_true',
                       help='Run only performance tests')
    parser.add_argument('--basic', action='store_true',
                       help='Run only basic functionality tests')
    parser.add_argument('--stress', action='store_true',
                       help='Run only stress tests')
    parser.add_argument('--list', action='store_true',
                       help='List available test modules')
    
    args = parser.parse_args()
    
    # Determine verbosity
    if args.quiet:
        verbosity = 0
    elif args.very_verbose:
        verbosity = 3
    else:
        verbosity = 2  # Default verbose
    
    print("🚀 Octree Test Runner")
    print("=" * 50)
    
    # Check if octree module is available
    try:
        import octree
        print(f"✅ Octree module found: {octree}")
    except ImportError as e:
        print(f"❌ Octree module not available: {e}")
        print("\nTo build the octree module:")
        print("1. Make sure you're in the CPython source directory")
        print("2. Run: ./configure")
        print("3. Run: make")
        print("4. The octree module should be built automatically")
        return 1
    
    # Import test modules
    try:
        if args.list:
            list_test_modules()
            return 0
        
        # Import the main test suite
        from test.test_octree_full_suite import run_octree_tests
        
        # Run specific test categories if requested
        if args.performance or args.basic or args.stress:
            return run_specific_tests(args, verbosity)
        else:
            # Run all tests
            print("\n🧪 Running comprehensive octree test suite...")
            result = run_octree_tests(verbosity)
            
            if result is None:
                return 1
            elif result.wasSuccessful():
                print(f"\n🎉 Success! All {result.testsRun} tests passed.")
                return 0
            else:
                print(f"\n❌ Failed! {len(result.failures + result.errors)} out of {result.testsRun} tests failed.")
                return 1
                
    except ImportError as e:
        print(f"❌ Could not import test modules: {e}")
        print("\nMake sure you're running this from the CPython source directory.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def list_test_modules():
    """List available test modules."""
    print("\n📋 Available octree test modules:")
    
    test_modules = [
        ('test_octree', 'Original octree tests'),
        ('test_octree_comprehensive', 'Comprehensive functionality tests'),
        ('test_octree_performance', 'Performance and benchmarking tests'),
        ('test_octree_subdivision', 'Subdivision behavior tests'),
        ('test_octree_stress_api', 'API stress tests'),
        ('test_octree_stress_collisions', 'Collision detection stress tests'),
        ('test_octree_stress_objects', 'Object management stress tests'),
        ('test_octree_full_suite', 'Complete test suite runner'),
    ]
    
    for module_name, description in test_modules:
        try:
            __import__(f'test.{module_name}')
            status = "✅ Available"
        except ImportError:
            status = "❌ Not found"
        
        print(f"  {module_name:30} - {description:40} {status}")


def run_specific_tests(args, verbosity):
    """Run specific categories of tests."""
    import unittest
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if args.basic:
        print("\n🧪 Running basic functionality tests...")
        try:
            from test import test_octree_comprehensive
            suite.addTest(loader.loadTestsFromModule(test_octree_comprehensive))
        except ImportError:
            print("❌ Basic test module not available")
            return 1
    
    if args.performance:
        print("\n⚡ Running performance tests...")
        try:
            from test import test_octree_performance
            suite.addTest(loader.loadTestsFromModule(test_octree_performance))
        except ImportError:
            print("❌ Performance test module not available")
            return 1
    
    if args.stress:
        print("\n💪 Running stress tests...")
        stress_modules = [
            'test_octree_stress_api',
            'test_octree_stress_collisions', 
            'test_octree_stress_objects'
        ]
        
        for module_name in stress_modules:
            try:
                module = __import__(f'test.{module_name}', fromlist=[module_name])
                suite.addTest(loader.loadTestsFromModule(module))
            except ImportError:
                print(f"⚠️  Stress test module {module_name} not available")
    
    if suite.countTestCases() == 0:
        print("❌ No tests found for specified categories")
        return 1
    
    # Run the selected tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print(f"\n🎉 Success! All {result.testsRun} selected tests passed.")
        return 0
    else:
        print(f"\n❌ Failed! {len(result.failures + result.errors)} out of {result.testsRun} tests failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())