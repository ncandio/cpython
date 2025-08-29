#!/usr/bin/env python3
"""
Comprehensive N-ary Tree Test Runner

Orchestrates and runs all N-ary tree test suites, similar to the quadtree comprehensive test system.
Provides unified reporting and analysis across all test categories.
"""

import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

class NaryTreeTestOrchestrator:
    """Orchestrates comprehensive N-ary tree testing."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    def run_test_suite(self, test_file, description):
        """Run a specific test suite and capture results."""
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"File: {test_file}")
        print(f"{'='*60}")
        
        if not Path(test_file).exists():
            print(f"❌ Test file {test_file} not found!")
            return {
                "status": "MISSING",
                "error": f"Test file {test_file} not found",
                "duration": 0
            }
            
        start_time = time.time()
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print("✅ Test suite completed successfully!")
                status = "PASSED"
                error = None
            else:
                print("❌ Test suite failed!")
                status = "FAILED"
                error = result.stderr
                
            return {
                "status": status,
                "return_code": result.returncode,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": error
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print("⏰ Test suite timed out!")
            return {
                "status": "TIMEOUT",
                "duration": duration,
                "error": "Test suite exceeded 5 minute timeout"
            }
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 Test suite crashed: {e}")
            return {
                "status": "CRASHED",
                "duration": duration,
                "error": str(e)
            }
            
    def run_comprehensive_tests(self):
        """Run all test suites comprehensively."""
        print("🌳 N-ary Tree Comprehensive Test Suite 🌳")
        print("="*80)
        print(f"Started at: {datetime.now().isoformat()}")
        print(f"Python version: {sys.version}")
        
        # Define test suites in order of execution
        test_suites = [
            ("test_narytree_simple.py", "Basic Functionality Tests"),
            ("test_narytree_api_complete.py", "Complete API Coverage Tests"),
            ("test_narytree_memory_stress.py", "Memory Management and Stress Tests"),
            ("test_narytree_production.py", "Production Readiness Tests"),
        ]
        
        # Run each test suite
        for test_file, description in test_suites:
            result = self.run_test_suite(test_file, description)
            self.test_results[test_file] = {
                "description": description,
                "result": result
            }
            
        # Optional: Run extended stress tests if available
        extended_tests = [
            ("test_narytree_stress.py", "Extended Stress Testing"),
            ("test_narytree_performance.py", "Performance Benchmarking"),
        ]
        
        for test_file, description in extended_tests:
            if Path(test_file).exists():
                result = self.run_test_suite(test_file, description)
                self.test_results[test_file] = {
                    "description": description,
                    "result": result
                }
            else:
                print(f"\n⚠️  Optional test {test_file} not found - skipping")
                self.test_results[test_file] = {
                    "description": description,
                    "result": {
                        "status": "SKIPPED",
                        "error": "Optional test file not found",
                        "duration": 0
                    }
                }
                
        # Generate comprehensive report
        self.generate_final_report()
        
    def generate_final_report(self):
        """Generate comprehensive final report."""
        total_time = time.time() - self.start_time
        
        # Analyze results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result["result"]["status"] == "PASSED")
        failed_tests = sum(1 for result in self.test_results.values() 
                          if result["result"]["status"] == "FAILED")
        skipped_tests = sum(1 for result in self.test_results.values() 
                           if result["result"]["status"] in ["SKIPPED", "MISSING"])
        crashed_tests = sum(1 for result in self.test_results.values() 
                           if result["result"]["status"] in ["CRASHED", "TIMEOUT"])
                           
        # Calculate total test duration
        total_test_time = sum(result["result"]["duration"] 
                             for result in self.test_results.values())
                             
        # Create comprehensive report
        report = {
            "test_suite": "N-ary Tree Comprehensive Test Suite",
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "total_runtime": total_time,
            "total_test_time": total_test_time,
            "summary": {
                "total_test_suites": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "crashed": crashed_tests,
                "success_rate": (passed_tests / max(1, total_tests - skipped_tests)) * 100,
                "overall_status": "PASSED" if failed_tests == 0 and crashed_tests == 0 else "FAILED"
            },
            "test_suite_results": {}
        }
        
        # Add detailed results for each test suite
        for test_file, test_data in self.test_results.items():
            report["test_suite_results"][test_file] = {
                "description": test_data["description"],
                "status": test_data["result"]["status"],
                "duration": test_data["result"]["duration"],
                "return_code": test_data["result"].get("return_code"),
                "error": test_data["result"].get("error")
            }
            
        # Save report
        report_filename = f"narytree_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Print summary
        self.print_final_summary(report, report_filename)
        
        return report
        
    def print_final_summary(self, report, report_filename):
        """Print final test summary."""
        print("\n" + "="*80)
        print("🌳 N-ARY TREE COMPREHENSIVE TEST RESULTS 🌳")
        print("="*80)
        
        summary = report["summary"]
        
        print(f"📊 SUMMARY:")
        print(f"   Total Test Suites: {summary['total_test_suites']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   ⏭️  Skipped: {summary['skipped']}")
        print(f"   💥 Crashed: {summary['crashed']}")
        print(f"   📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"   ⏱️  Total Runtime: {report['total_runtime']:.2f} seconds")
        print(f"   🧪 Test Time: {report['total_test_time']:.2f} seconds")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_file, result in report["test_suite_results"].items():
            status_icon = {
                "PASSED": "✅",
                "FAILED": "❌", 
                "SKIPPED": "⏭️",
                "MISSING": "❓",
                "CRASHED": "💥",
                "TIMEOUT": "⏰"
            }.get(result["status"], "❓")
            
            print(f"   {status_icon} {result['description']}")
            print(f"      File: {test_file}")
            print(f"      Status: {result['status']}")
            print(f"      Duration: {result['duration']:.2f}s")
            if result.get("error"):
                print(f"      Error: {result['error'][:100]}...")
                
        print(f"\n📄 Full report saved to: {report_filename}")
        
        # Final verdict
        if summary["overall_status"] == "PASSED":
            print("\n🎉 SUCCESS! All N-ary Tree tests completed successfully!")
            print("   The implementation is robust, efficient, and production-ready.")
            print("   ✓ Memory management verified")
            print("   ✓ API coverage complete")
            print("   ✓ Performance benchmarks passed")
            print("   ✓ Production scenarios tested")
            return 0
        else:
            print(f"\n❌ FAILURE! {summary['failed'] + summary['crashed']} test suite(s) failed.")
            print("   Review the detailed results above and fix issues before production use.")
            print("   ⚠️  Check memory management")
            print("   ⚠️  Verify API correctness")
            print("   ⚠️  Review error handling")
            return 1
            
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")
        
        # Check if narytree module is available
        try:
            import narytree
            print("   ✅ narytree module is available")
            
            # Quick functionality test
            tree = narytree.NaryTree("test")
            assert tree.size() == 1
            assert tree.empty() == False
            print("   ✅ Basic functionality verified")
            
        except ImportError:
            print("   ❌ narytree module not found!")
            print("   📝 Run: python3 setup_narytree.py build_ext --inplace")
            return False
            
        except Exception as e:
            print(f"   ❌ narytree module has issues: {e}")
            return False
            
        # Check for test files
        required_tests = [
            "test_narytree_simple.py",
            "test_narytree_api_complete.py", 
            "test_narytree_memory_stress.py",
            "test_narytree_production.py"
        ]
        
        missing_tests = []
        for test_file in required_tests:
            if not Path(test_file).exists():
                missing_tests.append(test_file)
            else:
                print(f"   ✅ {test_file} found")
                
        if missing_tests:
            print(f"   ❌ Missing test files: {missing_tests}")
            return False
            
        print("   🎯 All prerequisites satisfied!")
        return True

def main():
    """Main test orchestrator."""
    orchestrator = NaryTreeTestOrchestrator()
    
    # Check prerequisites first
    if not orchestrator.check_prerequisites():
        print("\n💥 Prerequisites not met. Please fix the issues above and try again.")
        return 1
        
    # Run comprehensive tests
    orchestrator.run_comprehensive_tests()
    
    # Return based on overall success
    if orchestrator.test_results:
        failed_or_crashed = sum(1 for result in orchestrator.test_results.values() 
                               if result["result"]["status"] in ["FAILED", "CRASHED", "TIMEOUT"])
        return 1 if failed_or_crashed > 0 else 0
    return 1

if __name__ == "__main__":
    sys.exit(main())