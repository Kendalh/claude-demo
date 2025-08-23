#!/usr/bin/env python3
"""
PagerDuty Incident Analytics Dashboard - Test Runner
Simple script to run all tests and provide coverage summary
"""

import subprocess
import sys
import os
import re
from datetime import datetime

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        return result
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def parse_test_results(output):
    """Parse pytest output to extract test statistics"""
    stats = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'warnings': 0,
        'errors': 0,
        'pass_rate': 0.0
    }
    
    # Look for summary line like "17 failed, 78 passed, 2 warnings"
    summary_pattern = r'(\d+)\s+failed,\s+(\d+)\s+passed(?:,\s+(\d+)\s+warnings)?'
    summary_match = re.search(summary_pattern, output)
    
    if summary_match:
        stats['failed'] = int(summary_match.group(1))
        stats['passed'] = int(summary_match.group(2))
        if summary_match.group(3):
            stats['warnings'] = int(summary_match.group(3))
    else:
        # Look for passed-only results like "95 passed"
        passed_pattern = r'(\d+)\s+passed'
        passed_match = re.search(passed_pattern, output)
        if passed_match:
            stats['passed'] = int(passed_match.group(1))
    
    # Look for errors during collection
    error_pattern = r'(\d+)\s+error'
    error_match = re.search(error_pattern, output)
    if error_match:
        stats['errors'] = int(error_match.group(1))
    
    stats['total'] = stats['passed'] + stats['failed'] + stats['errors']
    if stats['total'] > 0:
        stats['pass_rate'] = (stats['passed'] / stats['total']) * 100
    
    return stats

def parse_coverage_results(output):
    """Parse coverage output to extract coverage statistics"""
    coverage = {
        'total_statements': 0,
        'missing_statements': 0,
        'coverage_percentage': 0.0,
        'files': []
    }
    
    # Look for coverage summary table
    lines = output.split('\n')
    in_coverage_table = False
    
    for line in lines:
        # Start of coverage table
        if 'Name' in line and 'Stmts' in line and 'Miss' in line and 'Cover' in line:
            in_coverage_table = True
            continue
        
        # End of coverage table
        if in_coverage_table and line.startswith('------'):
            continue
        
        # TOTAL line
        if in_coverage_table and line.startswith('TOTAL'):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    coverage['total_statements'] = int(parts[1])
                    coverage['missing_statements'] = int(parts[2])
                    coverage['coverage_percentage'] = float(parts[3].rstrip('%'))
                except (ValueError, IndexError):
                    pass
            break
        
        # Individual file lines
        if in_coverage_table and line.strip() and not line.startswith('Name'):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    file_info = {
                        'name': parts[0],
                        'statements': int(parts[1]),
                        'missing': int(parts[2]),
                        'coverage': float(parts[3].rstrip('%'))
                    }
                    coverage['files'].append(file_info)
                except (ValueError, IndexError):
                    pass
    
    return coverage

def print_header():
    """Print test run header"""
    print("=" * 70)
    print("🧪 PagerDuty Incident Analytics Dashboard - Test Runner")
    print("=" * 70)
    print(f"📅 Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_test_summary(stats):
    """Print formatted test summary"""
    print("📊 TEST RESULTS SUMMARY")
    print("-" * 30)
    print(f"Total Tests:    {stats['total']:3d}")
    print(f"✅ Passed:      {stats['passed']:3d}")
    print(f"❌ Failed:      {stats['failed']:3d}")
    if stats['errors'] > 0:
        print(f"💥 Errors:      {stats['errors']:3d}")
    if stats['warnings'] > 0:
        print(f"⚠️  Warnings:    {stats['warnings']:3d}")
    print(f"📈 Pass Rate:   {stats['pass_rate']:5.1f}%")
    print()

def print_coverage_summary(coverage):
    """Print formatted coverage summary"""
    print("📊 CODE COVERAGE SUMMARY")
    print("-" * 30)
    print(f"Total Statements:    {coverage['total_statements']:4d}")
    print(f"Missing Statements:  {coverage['missing_statements']:4d}")
    print(f"Coverage Percentage: {coverage['coverage_percentage']:5.1f}%")
    print()
    
    if coverage['files']:
        print("📁 FILE-BY-FILE COVERAGE")
        print("-" * 50)
        print(f"{'File':<25} {'Stmts':>6} {'Miss':>6} {'Cover':>7}")
        print("-" * 50)
        for file_info in coverage['files']:
            print(f"{file_info['name']:<25} {file_info['statements']:6d} {file_info['missing']:6d} {file_info['coverage']:6.1f}%")
        print()

def print_component_breakdown(stats, component_tests):
    """Print component-wise test breakdown"""
    print("🏗️ COMPONENT BREAKDOWN")
    print("-" * 40)
    
    for component, info in component_tests.items():
        status_icon = "✅" if info['pass_rate'] >= 80 else "⚠️" if info['pass_rate'] >= 60 else "❌"
        print(f"{status_icon} {component:<20} {info['passed']:2d}/{info['total']:2d} ({info['pass_rate']:5.1f}%)")
    print()

def get_component_stats(output):
    """Extract component-wise statistics from test output"""
    components = {
        'Incident Model': {'total': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0},
        'Database Layer': {'total': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0},
        'Analytics Layer': {'total': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0},
        'API Client': {'total': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0},
        'Web Application': {'total': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0}
    }
    
    lines = output.split('\n')
    current_component = None
    
    for line in lines:
        # Map test files to components
        if 'test_incident_v2.py' in line:
            current_component = 'Incident Model'
        elif 'test_database_v2.py' in line:
            current_component = 'Database Layer'
        elif 'test_analytics_v2.py' in line:
            current_component = 'Analytics Layer'
        elif 'test_pagerduty_client_v2.py' in line:
            current_component = 'API Client'
        elif 'test_app_v2.py' in line:
            current_component = 'Web Application'
        
        # Count results
        if current_component and ('PASSED' in line or 'FAILED' in line):
            components[current_component]['total'] += 1
            if 'PASSED' in line:
                components[current_component]['passed'] += 1
            else:
                components[current_component]['failed'] += 1
    
    # Calculate pass rates
    for component in components:
        total = components[component]['total']
        if total > 0:
            components[component]['pass_rate'] = (components[component]['passed'] / total) * 100
    
    return components

def main():
    """Main test runner function"""
    print_header()
    
    # Check if we're in the right directory
    if not os.path.exists('test'):
        print("❌ Error: 'test' directory not found. Please run this script from the pagerduty directory.")
        sys.exit(1)
    
    # Install test dependencies if needed
    print("🔧 Checking test dependencies...")
    deps_result = run_command("pip3 show pytest pytest-cov", capture_output=True)
    if deps_result and deps_result.returncode != 0:
        print("📦 Installing test dependencies...")
        install_result = run_command("pip3 install -r test/test_requirements.txt pytest-cov")
        if install_result and install_result.returncode != 0:
            print("❌ Failed to install test dependencies")
            sys.exit(1)
    
    print("🚀 Running tests with coverage analysis...")
    print()
    
    # Run tests with coverage
    test_cmd = "python3 -m pytest test/ --cov=. --cov-report=term-missing --tb=short -v"
    result = run_command(test_cmd, capture_output=True)
    
    if result is None:
        print("❌ Failed to run tests")
        sys.exit(1)
    
    # Parse results
    test_stats = parse_test_results(result.stdout + result.stderr)
    coverage_stats = parse_coverage_results(result.stdout + result.stderr)
    component_stats = get_component_stats(result.stdout + result.stderr)
    
    # Print summaries
    print_test_summary(test_stats)
    print_coverage_summary(coverage_stats)
    print_component_breakdown(test_stats, component_stats)
    
    # Overall assessment
    print("🎯 OVERALL ASSESSMENT")
    print("-" * 25)
    
    if test_stats['pass_rate'] >= 90:
        print("🥇 Excellent - Production Ready!")
    elif test_stats['pass_rate'] >= 80:
        print("🥈 Good - Minor fixes needed")
    elif test_stats['pass_rate'] >= 70:
        print("🥉 Fair - Some work required")
    else:
        print("⚠️  Needs Attention - Major fixes needed")
    
    if coverage_stats['coverage_percentage'] >= 80:
        print(f"📊 Coverage: Excellent ({coverage_stats['coverage_percentage']:.1f}%)")
    elif coverage_stats['coverage_percentage'] >= 60:
        print(f"📊 Coverage: Good ({coverage_stats['coverage_percentage']:.1f}%)")
    else:
        print(f"📊 Coverage: Needs Improvement ({coverage_stats['coverage_percentage']:.1f}%)")
    
    print()
    print("✨ Test run completed!")
    
    # Return exit code based on test results
    if test_stats['failed'] > 0 or test_stats['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()