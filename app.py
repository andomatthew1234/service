import requests
import os
import time
import urllib3

# Suppress the warning that appears when you bypass SSL verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_status_and_shutdown():
    url = "https://raw.githubusercontent.com/andomatthew1234/service/main/status.txt"
    
    try:
        # Fetch the contents, explicitly ignoring the school's SSL certificate interception
        response = requests.get(url, verify=False)
        response.raise_for_status() 
        
        status = response.text.strip().lower()
        
        if status == 'true':
            print("Status is 'true'. Initiating system shutdown...")
            
            if os.name == 'nt':
                os.system("shutdown /s /t 1")
            else:
                os.system("shutdown -h now")
                
        elif status == 'false':
            print("Status is 'false'. No action taken.")
        else:
            print(f"Unknown status received: '{status}'. Expected 'true' or 'false'.")
            
    except requests.exceptions.RequestException as e:
        print(f"Failed to reach the GitHub repository: {e}")

if __name__ == "__main__":
    print("Starting status checker...")
    check_status_and_shutdown()