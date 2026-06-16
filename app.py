import requests
import subprocess
import os
import time
import urllib3

# Suppress the network SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

last_app_command = "none"

def get_combined_commands():
    """Fetches your control file from GitHub Pages—completely immune to API limits."""
    # Your custom live GitHub Pages URL
    base_url = "https://andomatthew1234.github.io/service/control.txt"
    
    # Simple cache-buster so your network doesn't serve an old copy
    url = f"{base_url}?v={int(time.time())}"
    
    try:
        # Bypassing verification to navigate school firewalls cleanly
        response = requests.get(url, verify=False)
        response.raise_for_status()
        
        decoded_text = response.text.strip()
        
        if "," in decoded_text:
            shutdown_part, app_part = decoded_text.split(",", 1)
            return shutdown_part.strip().lower(), app_part.strip()
        else:
            return "false", "none"
    except Exception as e:
        print(f"Connection delay or lookup error: {e}")
        return None, None

if __name__ == "__main__":
    print("==================================================")
    print(" Starting DEPLOYED Remote Controller Agent        ")
    print(" Strategy: GitHub Pages Hosting (Zero Rate Limits)")
    print("==================================================")
    
    while True:
        shutdown_cmd, app_cmd = get_combined_commands()
        
        # 1. Power State Evaluation
        if shutdown_cmd == "true":
            print("🚨 CRITICAL: Shutdown command caught!")
            if os.name == 'nt': 
                os.system("shutdown /s /t 1")
            else: 
                os.system("shutdown -h now")
            break
            
        # 2. Variable-Mapped Application Deployment
        if app_cmd and app_cmd.lower() != "none" and app_cmd != last_app_command:
            real_local_path = os.path.expandvars(app_cmd)
            print(f"🔥 Live change detected! Translated path: {real_local_path}")
            
            if os.path.exists(real_local_path):
                try:
                    subprocess.Popen([real_local_path])
                    print("Successfully deployed target executable directly.")
                except Exception as e:
                    print(f"Error executing file: {e}")
            else:
                print(f"⚠️ Target file path not found locally: '{real_local_path}'")
                
            last_app_command = app_cmd
            
        elif app_cmd.lower() == "none":
            last_app_command = "none"
            
        # Because GitHub Pages has no API caps, you can lower this to 5 or 10 seconds safely!
        print("Sleeping for 10 seconds before next sync loop...\n")
        time.sleep(10)