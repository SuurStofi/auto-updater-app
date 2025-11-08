import requests
from pathlib import Path

class Downloader:
    def __init__(self, url, save_dir):
        self.url = url
        self.app_dir = Path(save_dir)
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.app_dir / "target_app.exe"
        
    def download(self):
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            
            with open(self.file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False