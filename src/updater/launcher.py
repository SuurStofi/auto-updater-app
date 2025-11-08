import os
import subprocess
import sys
from pathlib import Path

class Launcher:
    def __init__(self, target_path):
        self.target_path = Path(target_path)

    def launch(self):
        """Launch the downloaded executable"""
        if not self.target_path.exists():
            print(f"Error: File not found: {self.target_path}")
            return False
        
        try:
            print(f"Launching: {self.target_path}")
            
            # Use os.startfile on Windows to launch the .exe
            if sys.platform == 'win32':
                os.startfile(str(self.target_path))
            else:
                # For other platforms, use subprocess
                subprocess.Popen([str(self.target_path)])
            
            print("✓ Application launched successfully!")
            return True
            
        except Exception as e:
            print(f"Failed to launch application: {e}")
            return False