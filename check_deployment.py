import requests

def check_url(url, search_term):
    try:
        print(f"Checking {url}...")
        response = requests.get(url)
        if response.status_code == 200:
            if search_term in response.text:
                print(f"[OK] '{search_term}' found in response.")
                return True
            else:
                print(f"[FAIL] '{search_term}' NOT found in response.")
                return False
        else:
            print(f"[FAIL] Status Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

print("--- Checking Deployment ---")
check_url("https://bigodetexas-dashboard.onrender.com/shop", "cart.js?v=2")
check_url("https://bigodetexas-dashboard.onrender.com/static/js/cart.js", "[DEBUG]")
