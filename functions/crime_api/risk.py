import requests
import sys

if len(sys.argv) < 2:
    print("Usage: python risk.py <state_name>")
    sys.exit(1)

state = sys.argv[1]
try:
    r = requests.get(f"http://127.0.0.1:5000/risk/{state}", timeout=5).json()
    if 'error' in r:
        print(f"Error: {r['error']}")
    else:
        print(f"\nState      : {r['state']}")
        print(f"Risk Rate  : {r['risk_rate']}/100")
        print(f"No. of Cases: {r['no_of_cases']}\n")
except:
    print("Server not running. Start it first: python main.py")