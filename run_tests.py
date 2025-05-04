#!/usr/bin/env python
"""
Test runner script with coverage reporting.
"""
import os
import sys
import subprocess
import argparse
import webbrowser

def run_tests(verbose=False, html_report=False, module=None):
    """Run tests with optional coverage reporting.
    
    Args:
        verbose (bool): Whether to show verbose output
        html_report (bool): Whether to generate an HTML coverage report
        module (str): Specific test module to run
    """
    # Construct the pytest command using python -m for better compatibility
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbose flag if specified
    if verbose:
        cmd.append("-v")
    
    # Add coverage flags
    cmd.extend(["--cov=src"])
    
    # Add HTML report if specified
    if html_report:
        cmd.append("--cov-report=html")
    else:
        cmd.append("--cov-report=term")
    
    # Add specific module if specified
    if module:
        cmd.append(module)
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run the tests
        result = subprocess.run(cmd, check=False)
        return_code = result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1
    
    # Open the HTML report if generated
    if html_report and return_code == 0:
        report_index = os.path.join("htmlcov", "index.html")
        if os.path.exists(report_index):
            print(f"Opening coverage report: {report_index}")
            # Use appropriate command based on platform
            if sys.platform == "win32":
                os.system(f"start {report_index}")
            elif sys.platform == "darwin":
                os.system(f"open {report_index}")
            else:
                os.system(f"xdg-open {report_index}")
    
    return return_code

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests with coverage reporting")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--module", help="Run a specific test module")
    
    args = parser.parse_args()
    
    sys.exit(run_tests(verbose=args.verbose, html_report=args.html, module=args.module)) 