import requests
import subprocess
import time
import urllib3

# Suppress the school's network SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_app_status():
    # URL pointing to your new app_status.txt file
    url = "https://raw.githubusercontent.com/andomatthew1234/service/main/app_status.txt"
    
    try:
        # Fetch the content and clean it up
        response = requests.get(url, verify=False)
        response.raise_for_status()
        command = response.text.strip().lower()
        
        if command == "none":
            print("Status is 'none'. Waiting for a command...")
            return
            
        # Dictionary mapping keywords in your text file to Windows system apps
        # 'calc' is Calculator, 'notepad' is Notepad, 'mspaint' is MS Paint
        available_apps = {
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe"
        }
        
        if command in available_apps:
            app_to_run = available_apps[command]
            print(f"Command received! Launching {command} ({app_to_run})...")
            
            # Popen launches the app in the background so our script can keep running
            subprocess.Popen(app_to_run)
            
            print("To prevent opening millions of windows, remember to change GitHub back to 'none'!")
        else:
            print(f"Unknown command received: '{command}'. Try 'calculator', 'notepad', or 'paint'.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error checking GitHub: {e}")

if __name__ == "__main__":
    print("Starting Remote App Launcher...")
    
    # Run a continuous loop so it checks every few seconds
    while True:
        check_app_status()
        time.sleep(5)  # Waits 5 seconds before checking GitHub again