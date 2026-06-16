import requests
import subprocess
import os
import time
import urllib3
import base64

# Suppress the school's network SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

last_app_command = "none"

def get_live_file_content(filename):
    """Fetches a file directly from the live GitHub API and brutally forces it to bypass caches."""
    base_url = f"https://api.github.com/repos/andomatthew1234/service/contents/{filename}"
    
    # Generate a changing timestamp to keep the URL unique
    timestamp = int(time.time())
    url = f"{base_url}?cb={timestamp}"
    
    # HTTP Headers that explicitly demand a live, non-cached response
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "If-None-Match": f"forced-bypass-{timestamp}" # Tricks the server into thinking the previous data is invalid
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        json_data = response.json()
        
        # Decode the base64 content from GitHub
        base64_content = json_data['content']
        decoded_bytes = base64.b64decode(base64_content)
        cleaned_text = decoded_bytes.decode('utf-8').strip().lower()
        
        return cleaned_text
    except Exception as e:
        print(f"Error fetching {filename} from API: {e}")
        return None

def check_shutdown_status():
    status = get_live_file_content("status.txt")
    
    if status == 'true':
        print("🚨 CRITICAL COMMAND: Shutdown is 'true'. Initiating system shutdown...")
        if os.name == 'nt':
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown -h now")
        return True
    return False

def check_app_status():
    global last_app_command
    command = get_live_file_content("app_status.txt")
    
    if not command:
        return
        
    if command == "none":
        print("App Status: 'none'. Waiting for an app command...")
        last_app_command = "none"
        return
        
    if command == last_app_command:
        print(f"App Status: Still reading '{command}' (Skipped to protect RAM).")
        return

    available_apps = {
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe"
    }
    
    if command in available_apps:
        app_to_run = available_apps[command]
        print(f"🔥 NEW APP COMMAND RECEIVED! Launching {command} ({app_to_run})...")
        subprocess.Popen(app_to_run)
        last_app_command = command
    else:
        print(f"Unknown app command received: '{command}'.")
        last_app_command = command

if __name__ == "__main__":
    print("==================================================")
    print(" Starting FORCE-LIVE Remote Controller Agent      ")
    print("==================================================")
    
    while True:
        is_shutting_down = check_shutdown_status()
        
        if not is_shutting_down:
            check_app_status()
            
        print("--- Loop finished. Sleeping for 5 seconds ---\n")
        time.sleep(5)