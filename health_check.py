"""
Health Check Monitor for BigodeTexas Bot
Monitora status do bot e dashboard
"""

import requests
import time
import json
from datetime import datetime
import os

# Configurações
DASHBOARD_URL = "http://localhost:5000"
CHECK_INTERVAL = 300  # 5 minutos
LOG_FILE = "logs/health_check.log"

def log_message(message, level="INFO"):
    """Log message to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    
    print(log_entry.strip())

def check_dashboard():
    """Check if dashboard is responding"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            log_message("Dashboard: OK")
            return True
        else:
            log_message(f"Dashboard: HTTP {response.status_code}", "WARNING")
            return False
    except requests.exceptions.ConnectionError:
        log_message("Dashboard: OFFLINE - Connection refused", "ERROR")
        return False
    except requests.exceptions.Timeout:
        log_message("Dashboard: TIMEOUT", "ERROR")
        return False
    except Exception as e:
        log_message(f"Dashboard: ERROR - {str(e)}", "ERROR")
        return False

def check_api_endpoints():
    """Check critical API endpoints"""
    endpoints = [
        "/api/stats",
        "/api/players",
        "/api/leaderboard"
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{DASHBOARD_URL}{endpoint}", timeout=5)
            results[endpoint] = response.status_code == 200
        except:
            results[endpoint] = False
    
    failed = [k for k, v in results.items() if not v]
    if failed:
        log_message(f"API endpoints failed: {', '.join(failed)}", "WARNING")
    else:
        log_message("All API endpoints: OK")
    
    return len(failed) == 0

def check_data_files():
    """Check if critical data files exist"""
    files = [
        "players_db.json",
        "economy.json",
        "config.json",
        "items.json"
    ]
    
    missing = []
    for file in files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        log_message(f"Missing data files: {', '.join(missing)}", "ERROR")
        return False
    else:
        log_message("Data files: OK")
        return True

def generate_health_report():
    """Generate health report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "dashboard": check_dashboard(),
        "api_endpoints": check_api_endpoints(),
        "data_files": check_data_files()
    }
    
    # Save report
    os.makedirs("reports", exist_ok=True)
    with open("reports/health_report.json", 'w') as f:
        json.dump(report, f, indent=4)
    
    return report

def main():
    """Main monitoring loop"""
    log_message("Health Check Monitor started")
    log_message(f"Checking every {CHECK_INTERVAL} seconds")
    
    while True:
        try:
            log_message("=" * 50)
            report = generate_health_report()
            
            # Check if everything is OK
            all_ok = all(report.values() if k != 'timestamp' else True for k in report)
            
            if all_ok:
                log_message("System Status: HEALTHY", "INFO")
            else:
                log_message("System Status: DEGRADED", "WARNING")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log_message("Health Check Monitor stopped by user")
            break
        except Exception as e:
            log_message(f"Monitor error: {str(e)}", "ERROR")
            time.sleep(60)

if __name__ == "__main__":
    main()
