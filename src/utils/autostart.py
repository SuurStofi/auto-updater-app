import winreg
import os
from pathlib import Path

def add_to_autostart():
    updater_path = Path.home() / "AppData" / "Local" / "AutoUpdater" / "updater.exe"
    if updater_path.exists():
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as registry_key:
                winreg.SetValueEx(registry_key, "AutoUpdater", 0, winreg.REG_SZ, str(updater_path))
            return True
        except Exception as e:
            print(f"Failed to add to autostart: {e}")
    return False

def remove_from_autostart():
    key = winreg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as registry_key:
            winreg.DeleteValue(registry_key, "AutoUpdater")
        return True
    except Exception as e:
        print(f"Failed to remove from autostart: {e}")
    return False