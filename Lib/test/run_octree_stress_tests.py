#!/usr/bin/env python3
"""
Octree Comprehensive Stress Test Runner
=======================================

This script runs all octree stress tests and generates a comprehensive report.
"""

import sys
import time
import subprocess
import json
import os
from datetime import datetime

def run_test_suite(test_file, description):
    """Run a specific test suite and capture results."""
    print(f"\n{'='*80}")
    print(f"🚀 RUNNING: {description}")
    print(f"📁 File: {test_file}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        # Run the test with python3
        env = os.environ.copy()
        env['PYTHONPATH'] = 'Modules:.'
        
        result = subprocess.run(
            ['python3', test_file],
            cwd='/home/nico/WORK_ROOT/cpython',
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per test suite
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        success = result.returncode == 0
        
        test_result = {
            'name': description,
            'file': test_file,
            'success': success,
            'duration': duration,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
        if success:
            print(f"✅ {description} PASSED in {duration:.2f}s")
        else:
            print(f"❌ {description} FAILED in {duration:.2f}s")
            print(f"Return code: {result.returncode}")
            if result.stderr:
                print(f"Errors:\n{result.stderr}")
        
        return test_result
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} TIMED OUT after 10 minutes")
        return {
            'name': description,
            'file': test_file,
            'success': False,
            'duration': 600,
            'return_code': -1,
            'stdout': '',
            'stderr': 'Test timed out after 10 minutes'
        }
        
    except Exception as e:
        print(f"💥 {description} CRASHED: {e}")
        return {
            'name': description,
            'file': test_file,
            'success': False,
            'duration': 0,
            'return_code': -2,
            'stdout': '',
            'stderr': f'Exception: {e}'
        }

def generate_report(results, output_file):
    """Generate a comprehensive test report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(results),
        'passed_tests': sum(1 for r in results if r['success']),
        'failed_tests': sum(1 for r in results if not r['success']),
        'total_duration': sum(r['duration'] for r in results),
        'results': results
    }
    
    # Save JSON report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate summary
    print(f"\n{'='*80}")
    print(f"📊 OCTREE STRESS TEST SUMMARY")
    print(f"{'='*80}")
    print(f"🕐 Timestamp: {report['timestamp']}")
    print(f"📈 Total Tests: {report['total_tests']}")
    print(f"✅ Passed: {report['passed_tests']}")
    print(f"❌ Failed: {report['failed_tests']}")
    print(f"⏱️ Total Duration: {report['total_duration']:.2f}s ({report['total_duration']/60:.1f} minutes)")
    print(f"📄 Report saved to: {output_file}")
    
    success_rate = (report['passed_tests'] / report['total_tests']) * 100
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    print(f"{'Test Suite':<40} {'Status':<10} {'Duration':<12} {'Details'}")
    print("-" * 80)
    
    for result in results:
        status = "PASS" if result['success'] else "FAIL"
        duration_str = f"{result['duration']:.2f}s"
        
        details = ""
        if not result['success']:
            if result['return_code'] == -1:
                details = "TIMEOUT"
            elif result['return_code'] == -2:
                details = "CRASH"
            else:
                details = f"RC={result['return_code']}"
        
        print(f"{result['name']:<40} {status:<10} {duration_str:<12} {details}")
    
    return report

def main():
    """Run all octree stress tests."""
    print("🔥 OCTREE COMPREHENSIVE STRESS TEST SUITE")
    print("=" * 50)
    
    # Test suites to run
    test_suites = [
        {
            'file': 'Lib/test/test_octree_stress_collisions.py',
            'description': 'Collision Detection Stress Tests'
        },
        {
            'file': 'Lib/test/test_octree_stress_objects.py', 
            'description': 'Object Creation Stress Tests'
        },
        {
            'file': 'Lib/test/test_octree_stress_api.py',
            'description': 'API Robustness Stress Tests'
        }
    ]
    
    results = []
    overall_start = time.time()
    
    # Run each test suite
    for suite in test_suites:
        result = run_test_suite(suite['file'], suite['description'])
        results.append(result)
        
        # Brief pause between test suites
        time.sleep(2)
    
    overall_duration = time.time() - overall_start
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"octree_stress_test_report_{timestamp}.json"
    
    report = generate_report(results, report_file)
    
    print(f"\n🏁 ALL STRESS TESTS COMPLETED")
    print(f"⏱️ Overall Duration: {overall_duration:.2f}s ({overall_duration/60:.1f} minutes)")
    
    # Return appropriate exit code
    if report['failed_tests'] == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️ {report['failed_tests']} TEST(S) FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())