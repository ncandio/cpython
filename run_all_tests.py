#!/usr/bin/env python3
"""
Complete Test Runner for Spatial Data Structures
================================================

This script provides an easy way to run all available tests and demos
for QuadTree and Octree spatial data structures.
"""

import os
import sys
import time
import subprocess

def run_script(script_path, description):
    """Run a Python script and capture results."""
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {description}")
    print(f"📁 Script: {script_path}")
    print(f"{'='*60}")
    
    if not os.path.exists(script_path):
        print(f"❌ ERROR: Script not found: {script_path}")
        return False
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description} completed in {duration:.2f}s")
            print(f"📊 Output preview:")
            # Show first and last few lines of output
            lines = result.stdout.split('\n')
            if len(lines) > 20:
                print('\n'.join(lines[:10]))
                print(f"... [{len(lines)-20} lines omitted] ...")
                print('\n'.join(lines[-10:]))
            else:
                print(result.stdout)
        else:
            print(f"❌ FAILED: {description} failed in {duration:.2f}s")
            print(f"Return code: {result.returncode}")
            if result.stderr:
                print(f"Error output:\n{result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT: {description} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"💥 EXCEPTION: {description} crashed: {e}")
        return False

def main():
    """Run all tests and demos."""
    print("🎯 COMPREHENSIVE SPATIAL DATA STRUCTURE TEST RUNNER")
    print("=" * 55)
    
    base_path = "/home/nico/WORK_ROOT/cpython"
    
    # Define all tests and demos to run
    test_suite = [
        # Basic functionality tests
        {
            "script": f"{base_path}/demo_spatial_modules.py",
            "description": "Basic Module Demonstration",
            "category": "Basic"
        },
        
        # Original tests
        {
            "script": f"{base_path}/Lib/test/test_octree.py", 
            "description": "Core Octree Unit Tests",
            "category": "Core Tests"
        },
        {
            "script": f"{base_path}/Lib/test/test_octree_subdivision.py",
            "description": "Octree Subdivision Analysis",
            "category": "Core Tests"
        },
        
        # Stress tests
        {
            "script": f"{base_path}/Lib/test/test_octree_stress_collisions.py",
            "description": "Octree Collision Stress Tests", 
            "category": "Stress Tests"
        },
        {
            "script": f"{base_path}/Lib/test/test_octree_stress_objects.py",
            "description": "Octree Object Creation Stress Tests",
            "category": "Stress Tests"
        },
        {
            "script": f"{base_path}/Lib/test/test_octree_stress_api.py",
            "description": "Octree API Robustness Stress Tests",
            "category": "Stress Tests"
        },
        
        # Application demos
        {
            "script": f"{base_path}/simple_image_collision_demo.py",
            "description": "Image-Based Collision Detection Demo",
            "category": "Applications"
        },
        {
            "script": f"{base_path}/game_collision_examples.py",
            "description": "Game Development Collision Examples",
            "category": "Applications"
        },
        
        # QuadTree tests if available
        {
            "script": f"{base_path}/simple_quadtree_test.py",
            "description": "Simple QuadTree Test",
            "category": "QuadTree"
        },
        {
            "script": f"{base_path}/subdivision_demo.py", 
            "description": "Subdivision Demonstration",
            "category": "Educational"
        }
    ]
    
    # Run all tests
    results = []
    categories = {}
    
    for test in test_suite:
        success = run_script(test["script"], test["description"])
        results.append({
            "name": test["description"],
            "category": test["category"], 
            "success": success,
            "script": test["script"]
        })
        
        # Group by category
        if test["category"] not in categories:
            categories[test["category"]] = {"passed": 0, "failed": 0}
        
        if success:
            categories[test["category"]]["passed"] += 1
        else:
            categories[test["category"]]["failed"] += 1
        
        # Brief pause between tests
        time.sleep(1)
    
    # Generate summary report
    print(f"\n{'='*60}")
    print(f"📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*60}")
    
    total_passed = sum(1 for r in results if r["success"])
    total_failed = len(results) - total_passed
    success_rate = (total_passed / len(results)) * 100
    
    print(f"🎯 Overall Results:")
    print(f"   ✅ Passed: {total_passed}/{len(results)} ({success_rate:.1f}%)")
    print(f"   ❌ Failed: {total_failed}/{len(results)}")
    
    print(f"\n📋 Results by Category:")
    for category, stats in categories.items():
        total_cat = stats["passed"] + stats["failed"]
        cat_rate = (stats["passed"] / total_cat) * 100 if total_cat > 0 else 0
        print(f"   {category}: {stats['passed']}/{total_cat} passed ({cat_rate:.0f}%)")
    
    print(f"\n📝 Detailed Results:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} - {result['name']}")
    
    if total_failed > 0:
        print(f"\n⚠️  Failed Tests:")
        for result in results:
            if not result["success"]:
                print(f"   • {result['name']}: {result['script']}")
    
    print(f"\n🏁 Test Runner Completed!")
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)