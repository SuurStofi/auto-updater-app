import requests
from pathlib import Path
from datetime import datetime
from updater.github_parser import GitHubParser
from utils.hash_utils import calculate_sha256, verify_file_hash

class Downloader:
    def __init__(self, url, save_dir, source_type="Direct URL"):
        self.url = url
        self.source_type = source_type
        self.app_dir = Path(save_dir)
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = None
        self.metadata_file = self.app_dir / "update_metadata.json"
        
    def get_download_info(self):
        """Get download URL based on source type"""
        print(f"Getting download info for source type: {self.source_type}")
        print(f"URL: {self.url}")
        
        if self.source_type == "GitHub Release":
            parser = GitHubParser(self.url)
            info = parser.get_latest_exe_info()
            if info:
                print(f"GitHub Release: Found {info['filename']}")
                return info['download_url'], info['filename'], info['sha256'], info['release_date']
            print("GitHub Release: No exe info found")
            return None, None, None, None
            
        elif self.source_type == "GitHub Network (Assets)":
            # Use expanded_assets endpoint for immediate loading
            parser = GitHubParser(self.url)
            exe_files = parser.parse_network_page()
            if exe_files:
                info = exe_files[0]
                print(f"GitHub Network: Found {info['filename']}")
                return info['download_url'], info['filename'], info['sha256'], info['release_date']
            print("GitHub Network: No exe files found")
            return None, None, None, None
            
        else:
            # Direct URL
            filename = self.url.split('/')[-1]
            if not filename.endswith('.exe'):
                filename = 'downloaded_app.exe'
            print(f"Direct URL: Using filename {filename}")
            return self.url, filename, None, None
    
    def download(self):
        try:
            download_url, filename, remote_sha256, release_date = self.get_download_info()
            
            if not download_url:
                error_msg = f"Could not get download URL from {self.source_type}"
                if self.source_type in ["GitHub Release", "GitHub Network (Assets)"]:
                    error_msg += "\n\nPossible reasons:"
                    error_msg += "\n• No .exe files found in the release"
                    error_msg += "\n• The release has no assets"
                    error_msg += "\n• The URL may be incorrect"
                    error_msg += "\n\nPlease check:"
                    error_msg += f"\n1. Visit the URL in a browser: {self.url}"
                    error_msg += "\n2. Verify that .exe files are attached to the release"
                    error_msg += "\n3. Try using 'Direct URL' mode with a direct download link"
                print(error_msg)
                return False
            
            self.file_path = self.app_dir / filename
            
            # Download file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(self.file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify SHA256 if available
            if remote_sha256:
                if not verify_file_hash(self.file_path, remote_sha256):
                    local_sha256 = calculate_sha256(self.file_path)
                    print(f"SHA256 mismatch! Expected: {remote_sha256}, Got: {local_sha256}")
                    return False
            
            # Save metadata
            import json
            metadata = {
                'sha256': calculate_sha256(self.file_path),
                'release_date': release_date,
                'filename': filename,
                'source_url': self.url,
                'source_type': self.source_type
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f)
            
            return True
            
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    def check_for_updates(self):
        """Check if update is needed"""
        import json
        
        if not self.metadata_file.exists():
            return True  # No metadata, need to download
        
        with open(self.metadata_file, 'r') as f:
            metadata = json.load(f)
        
        if self.source_type == "GitHub Release":
            parser = GitHubParser(self.url)
            local_date = datetime.fromisoformat(metadata['release_date'].replace('Z', '+00:00')) if metadata.get('release_date') else None
            needs_update, info = parser.check_for_updates(metadata.get('sha256'), local_date)
            return needs_update
        elif self.source_type == "GitHub Network (Assets)":
            parser = GitHubParser(self.url)
            local_date = datetime.fromisoformat(metadata['release_date'].replace('Z', '+00:00')) if metadata.get('release_date') else None
            needs_update, info = parser.check_for_updates_network(metadata.get('sha256'), local_date)
            return needs_update
        
        return False