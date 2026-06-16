import requests
import subprocess
import time
import urllib3

# Suppress the school's network SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Track the last command we executed so we don't repeat it infinitely
last_command = "none"

def check_app_status():
    global last_command # Allows us to update the variable outside this function
    
    base_url = "https://raw.githubusercontent.com/andomatthew1234/service/main/app_status.txt"
    timestamp = int(time.time())
    url = f"{base_url}?v={timestamp}"
    
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        command = response.text.strip().lower()
        
        # Scenario 1: The file says 'none'
        if command == "none":
            print("Status is 'none'. Waiting for a command...")
            last_command = "none" # Reset tracking so it's ready for a new app
            return
            
        # Scenario 2: It's the SAME command we just executed 5 seconds ago
        if command == last_command:
            print(f"Still reading '{command}', but we already handled it. Skipping to protect your RAM...")
            return

        available_apps = {
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe"
        }
        
        # Scenario 3: It's a BRAND NEW command
        if command in available_apps:
            app_to_run = available_apps[command]
            print(f"🔥 NEW COMMAND RECEIVED! Launching {command} ({app_to_run})...")
            
            subprocess.Popen(app_to_run)
            
            # Save this command so we don't run it again on the next loop
            last_command = command
            print("Successfully launched. Ignoring further requests for this app until it changes.")
        else:
            print(f"Unknown command received: '{command}'. Try 'calculator', 'notepad', or 'paint'.")
            # Update last_command so it doesn't spam the 'Unknown command' message either
            last_command = command
            
    except requests.exceptions.RequestException as e:
        print(f"Error checking GitHub: {e}")

if __name__ == "__main__":
    print("Starting Smart Remote App Launcher (Anti-Spam Mode)...")
    
    while True:
        check_app_status()
        time.sleep(5)