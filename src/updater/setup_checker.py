import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from .github_parser import GitHubParser

class SetupChecker:
    def __init__(self, url, source_type, save_dir):
        self.url = url
        self.source_type = source_type
        self.app_dir = Path(save_dir)
        self.target_exe = self.app_dir / "target_app.exe"
        
    def needs_setup(self):
        """Check if initial setup is needed"""
        return not self.target_exe.exists()
    
    def perform_setup(self):
        """Perform initial setup by downloading required files"""
        try:
            if self.source_type == "GitHub Release":
                parser = GitHubParser(self.url)
                exe_data = parser.parse_release_page()
                if not exe_data:
                    return False, "No executable found in GitHub release"
                    
                download_url = exe_data[0]['url']
                expected_hash = exe_data[0]['sha256']
                
            else:  # Direct URL
                download_url = self.url
                expected_hash = None
            
            # Create directory if doesn't exist
            self.app_dir.mkdir(parents=True, exist_ok=True)
            
            # Download file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(self.target_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            return True, "Setup completed successfully"
            
        except Exception as e:
            return False, f"Setup failed: {str(e)}"