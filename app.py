import requests
import subprocess
import os
import time
import urllib3
import threading
from PIL import Image, ImageDraw
import pystray

# Suppress network SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

last_app_command = "none"
is_running = True  # Flag to track if the app should keep looping

def create_tray_icon():
    """Generates a small colored circle to use as a taskbar icon."""
    # Create an 64x64 image with a transparent background
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Draw a vibrant blue circle to show the app is alive
    dc.ellipse((4, 4, 60, 60), fill='#1e90ff', outline='#ffffff', width=3)
    return image

def on_exit_clicked(icon, item):
    """Safely shuts down the background loops when 'Exit' is clicked from the tray."""
    global is_running
    print("Shutting down agent via tray icon...")
    is_running = False
    icon.stop()

def setup_tray():
    """Initializes and runs the taskbar system tray icon."""
    icon_image = create_tray_icon()
    menu = pystray.Menu(pystray.MenuItem('Exit SRVC Agent', on_exit_clicked))
    icon = pystray.Icon("SRVC_Agent", icon_image, "SRVC Remote Controller Active", menu)
    icon.run()

def get_combined_commands():
    base_url = "https://andomatthew1234.github.io/service/control.txt"
    url = f"{base_url}?v={int(time.time())}"
    
    try:
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
        return "false", "error"

def main_loop():
    """The core engine that checks GitHub Pages every 10 seconds."""
    global last_app_command
    
    print("==================================================")
    print(" Starting DEPLOYED Remote Controller Agent        ")
    print(" Tray Icon active in the taskbar corner.          ")
    print("==================================================")
    
    while is_running:
        shutdown_cmd, app_cmd = get_combined_commands()
        
        if shutdown_cmd == "true":
            print("🚨 CRITICAL: Shutdown command caught!")
            if os.name == 'nt': 
                os.system("shutdown /s /t 1")
            else: 
                os.system("shutdown -h now")
            break
            
        if app_cmd and app_cmd.lower() != "none" and app_cmd.lower() != "error" and app_cmd != last_app_command:
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
            
        elif app_cmd and app_cmd.lower() == "none":
            last_app_command = "none"
            
        time.sleep(10)

if __name__ == "__main__":
    # 1. Start the system tray icon on its own dedicated thread
    tray_thread = threading.Thread(target=setup_tray, daemon=True)
    tray_thread.start()
    
    # 2. Run the main processing loop on the primary thread
    main_loop()
    