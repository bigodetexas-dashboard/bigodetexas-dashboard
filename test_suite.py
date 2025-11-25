"""
BigodeTexas Bot - Test Suite
Testes automatizados para validar funcionalidades
"""

import os
import json
import requests
import time
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, message=""):
    """Print test result"""
    symbol = "[OK]" if status else "[FAIL]"
    color = Colors.GREEN if status else Colors.RED
    print(f"{color}{symbol}{Colors.END} {name}")
    if message:
        print(f"  {Colors.YELLOW}{message}{Colors.END}")

def test_file_exists(filepath, description):
    """Test if a file exists"""
    exists = os.path.exists(filepath)
    print_test(f"File: {description}", exists, filepath if exists else f"Missing: {filepath}")
    return exists

def test_json_valid(filepath, description):
    """Test if JSON file is valid"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        print_test(f"JSON: {description}", True, "Valid JSON")
        return True
    except Exception as e:
        print_test(f"JSON: {description}", False, str(e))
        return False

def test_api_endpoint(url, description):
    """Test API endpoint"""
    try:
        response = requests.get(url, timeout=5)
        success = response.status_code == 200
        print_test(f"API: {description}", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test(f"API: {description}", False, str(e))
        return False

def test_dashboard_running():
    """Test if dashboard is running"""
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        return response.status_code == 200
    except:
        return False

# ===== MAIN TEST SUITE =====
def run_tests():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}BigodeTexas Bot - Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Test 1: Core Files
    print(f"\n{Colors.BLUE}[1] Testing Core Files...{Colors.END}")
    core_files = [
        ("bot_main.py", "Bot principal"),
        ("web_dashboard.py", "Dashboard Flask"),
        ("analytics.py", "Analytics module"),
        ("generate_heatmap.py", "Heatmap generator"),
        ("security.py", "Security module"),
        ("README.md", "Documentation")
    ]
    
    for filepath, desc in core_files:
        results['total'] += 1
        if test_file_exists(filepath, desc):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Test 2: JSON Configuration Files
    print(f"\n{Colors.BLUE}[2] Testing JSON Files...{Colors.END}")
    json_files = [
        ("missions.json", "Missions config"),
        ("items.json", "Items database"),
        ("config.json", "Bot config")
    ]
    
    for filepath, desc in json_files:
        results['total'] += 1
        if os.path.exists(filepath) and test_json_valid(filepath, desc):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Test 3: Templates
    print(f"\n{Colors.BLUE}[3] Testing Templates...{Colors.END}")
    templates = [
        ("templates/index.html", "Home page"),
        ("templates/stats.html", "Stats page"),
        ("templates/leaderboard.html", "Leaderboard"),
        ("templates/shop.html", "Shop page"),
        ("templates/heatmap.html", "Heatmap page"),
        ("templates/profile.html", "Profile page")
    ]
    
    for filepath, desc in templates:
        results['total'] += 1
        if test_file_exists(filepath, desc):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Test 4: Static Files
    print(f"\n{Colors.BLUE}[4] Testing Static Files...{Colors.END}")
    static_files = [
        ("static/css/style.css", "Main CSS"),
        ("static/js/main.js", "Main JavaScript"),
        ("static/js/charts.js", "Charts JavaScript")
    ]
    
    for filepath, desc in static_files:
        results['total'] += 1
        if test_file_exists(filepath, desc):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Test 5: Dashboard API (if running)
    print(f"\n{Colors.BLUE}[5] Testing Dashboard API...{Colors.END}")
    
    if test_dashboard_running():
        api_endpoints = [
            ("http://localhost:5000/api/stats", "Stats endpoint"),
            ("http://localhost:5000/api/players", "Players endpoint"),
            ("http://localhost:5000/api/leaderboard", "Leaderboard endpoint"),
            ("http://localhost:5000/api/shop", "Shop endpoint"),
            ("http://localhost:5000/api/wars", "Wars endpoint"),
            ("http://localhost:5000/api/export/players", "Export players"),
            ("http://localhost:5000/api/export/report", "Export report")
        ]
        
        for url, desc in api_endpoints:
            results['total'] += 1
            if test_api_endpoint(url, desc):
                results['passed'] += 1
            else:
                results['failed'] += 1
    else:
        print_test("Dashboard Status", False, "Dashboard not running. Start with run_dashboard.bat")
        print(f"{Colors.YELLOW}  Skipping API tests...{Colors.END}")
    
    # Test 6: Scripts
    print(f"\n{Colors.BLUE}[6] Testing Scripts...{Colors.END}")
    scripts = [
        ("run_bot.bat", "Bot launcher"),
        ("run_dashboard.bat", "Dashboard launcher"),
        ("run_analytics.bat", "Analytics launcher")
    ]
    
    for filepath, desc in scripts:
        results['total'] += 1
        if test_file_exists(filepath, desc):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Final Report
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Results{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Total Tests: {results['total']}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}SUCCESS: All tests passed!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}WARNING: Some tests failed. Review the output above.{Colors.END}")
    
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return results

if __name__ == "__main__":
    try:
        results = run_tests()
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results
            }, f, indent=4)
        
        print(f"Results saved to: test_results.json\n")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error running tests: {e}{Colors.END}")
