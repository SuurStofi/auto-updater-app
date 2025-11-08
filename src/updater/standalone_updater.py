"""
Standalone updater template that will be compiled into updater.exe
This file gets embedded with configuration and runs independently
"""

import requests
import json
import hashlib
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import re
import sys
import os
import time

# Configuration will be injected here by the builder
CONFIG = {
    'source_type': 'PLACEHOLDER_SOURCE_TYPE',
    'url': 'PLACEHOLDER_URL',
    'last_sha256': 'PLACEHOLDER_SHA256',
    'last_date': 'PLACEHOLDER_DATE',
    'target_filename': 'PLACEHOLDER_FILENAME'
}

class StandaloneUpdater:
    def __init__(self):
        # Get the directory where updater.exe is located
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            self.app_dir = Path(sys.executable).parent
        else:
            # Running as script
            self.app_dir = Path(__file__).parent
        
        self.metadata_file = self.app_dir / "update_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """Load saved metadata or use embedded config"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
            # Ensure source_type and url are present (merge with CONFIG)
            # Support both 'url' and 'source_url' for backward compatibility
            if 'url' not in self.metadata or not self.metadata['url']:
                self.metadata['url'] = self.metadata.get('source_url') or CONFIG.get('url')
            if 'source_type' not in self.metadata or not self.metadata['source_type']:
                self.metadata['source_type'] = CONFIG.get('source_type')
        else:
            # First run - use embedded config
            self.metadata = CONFIG.copy()
    
    def save_metadata(self, sha256, release_date, filename):
        """Save metadata for future checks"""
        # Preserve source_type and url from config
        if 'source_type' not in self.metadata or not self.metadata['source_type']:
            self.metadata['source_type'] = CONFIG.get('source_type')
        if 'url' not in self.metadata or not self.metadata['url']:
            self.metadata['url'] = CONFIG.get('url')
        
        self.metadata.update({
            'last_sha256': sha256,
            'last_date': release_date,
            'target_filename': filename
        })
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def calculate_sha256(self, file_path):
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def parse_github_page(self, url):
        """Parse GitHub expanded_assets page for .exe files"""
        try:
            # Convert to expanded_assets URL
            if '/releases/tag/' in url:
                url = url.replace('/releases/tag/', '/releases/expanded_assets/')
            elif '/releases/latest' in url:
                url = url.replace('/releases/latest', '/releases/expanded_assets/latest')
            else:
                url = f"{url}/releases/expanded_assets/latest"
            
            print(f"Checking for updates: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all Box-row items (each asset is in one)
            box_rows = soup.find_all('li', class_='Box-row')
            
            for row in box_rows:
                # Look for .exe link in this row
                exe_link = row.find('a', href=re.compile(r'\.exe'))
                
                if not exe_link:
                    continue
                
                href = exe_link.get('href', '')
                if not href.startswith('http'):
                    href = f"https://github.com{href}"
                
                filename = href.split('/')[-1]
                
                # Extract metadata from the same row
                sha256 = None
                release_date = None
                
                # Find SHA256 in clipboard-copy element
                clipboard = row.find('clipboard-copy', value=re.compile(r'sha256:'))
                if clipboard:
                    sha256_value = clipboard.get('value', '')
                    sha256 = sha256_value.replace('sha256:', '') if 'sha256:' in sha256_value else None
                
                # Find release date in relative-time element
                time_elem = row.find('relative-time')
                if time_elem:
                    release_date = time_elem.get('datetime')
                
                return {
                    'download_url': href,
                    'filename': filename,
                    'sha256': sha256,
                    'release_date': release_date
                }
            
            return None
            
        except Exception as e:
            print(f"Error parsing GitHub page: {e}")
            return None
    
    def check_for_updates(self):
        """Check if update is available"""
        source_type = self.metadata.get('source_type', 'GitHub Network (Assets)')
        url = self.metadata.get('url')
        
        # Validate URL
        if not url or url == 'PLACEHOLDER_URL':
            print(f"Error: No URL configured")
            print(f"Source type: {source_type}")
            print(f"URL: {url}")
            print("\nThe updater was not built correctly.")
            print("Please rebuild using the Auto-Updater GUI.")
            return False, None
        
        if source_type in ['GitHub Release', 'GitHub Network (Assets)']:
            remote_info = self.parse_github_page(url)
            
            if not remote_info:
                print("No .exe files found in release")
                print(f"URL checked: {url}")
                return False, None
            
            local_sha256 = self.metadata.get('last_sha256')
            local_date = self.metadata.get('last_date')
            
            # Compare SHA256
            if remote_info['sha256'] != local_sha256:
                # Check date to confirm it's newer
                if remote_info['release_date']:
                    try:
                        remote_date = datetime.fromisoformat(remote_info['release_date'].replace('Z', '+00:00'))
                        
                        if local_date:
                            local_date_obj = datetime.fromisoformat(local_date.replace('Z', '+00:00'))
                            if remote_date > local_date_obj:
                                print(f"Update available: {remote_info['filename']}")
                                print(f"  Remote date: {remote_info['release_date']}")
                                print(f"  Local date: {local_date}")
                                return True, remote_info
                        else:
                            # No local date, assume update available
                            return True, remote_info
                    except Exception as e:
                        print(f"Date comparison error: {e}")
                        # If hashes differ, assume update needed
                        return True, remote_info
            
            print("Already up to date!")
            return False, None
        
        return False, None
    
    def download_update(self, update_info):
        """Download and verify the update"""
        try:
            download_url = update_info['download_url']
            filename = update_info['filename']
            expected_sha256 = update_info['sha256']
            release_date = update_info['release_date']
            
            target_path = self.app_dir / filename
            
            print(f"Downloading: {filename}")
            print(f"From: {download_url}")
            
            # Download file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        progress = (downloaded / total_size) * 100
                        print(f"\rProgress: {progress:.1f}%", end='')
            
            print("\n✓ Download complete")
            
            # Verify SHA256 if available
            if expected_sha256:
                print("Verifying file integrity...")
                calculated_sha256 = self.calculate_sha256(target_path)
                
                if calculated_sha256 != expected_sha256:
                    print(f"✗ SHA256 mismatch!")
                    print(f"  Expected: {expected_sha256}")
                    print(f"  Got: {calculated_sha256}")
                    target_path.unlink()  # Delete corrupted file
                    return False
                
                print("✓ File integrity verified")
            
            # Save metadata
            self.save_metadata(expected_sha256 or calculated_sha256, release_date, filename)
            
            print(f"✓ Update installed: {target_path}")
            return True
            
        except Exception as e:
            print(f"✗ Download failed: {e}")
            return False
    
    def launch_app(self):
        """Launch the updated application"""
        filename = self.metadata.get('target_filename')
        if not filename:
            print("No target file specified")
            return
        
        app_path = self.app_dir / filename
        
        if not app_path.exists():
            print(f"Application not found: {app_path}")
            return
        
        try:
            print(f"Launching: {app_path}")
            if sys.platform == 'win32':
                os.startfile(str(app_path))
            else:
                import subprocess
                subprocess.Popen([str(app_path)])
        except Exception as e:
            print(f"Failed to launch: {e}")
    
    def run(self):
        """Main update process"""
        print("=" * 60)
        print("Auto-Updater")
        print("=" * 60)
        print(f"Installation directory: {self.app_dir}")
        print(f"Source: {self.metadata.get('source_type')}")
        print(f"URL: {self.metadata.get('url')}")
        print()
        
        # Check for updates
        needs_update, update_info = self.check_for_updates()
        
        if needs_update:
            print("\nUpdate found! Downloading...")
            if self.download_update(update_info):
                print("\n✓ Update completed successfully!")
                
                # Ask user if they want to launch
                try:
                    response = input("\nLaunch application now? (y/n): ")
                    if response.lower() in ['y', 'yes']:
                        self.launch_app()
                except:
                    # If running as compiled exe without console, just launch
                    time.sleep(2)
                    self.launch_app()
            else:
                print("\n✗ Update failed")
        else:
            print("\n✓ You have the latest version")
            
            # Launch existing app
            try:
                response = input("\nLaunch application? (y/n): ")
                if response.lower() in ['y', 'yes']:
                    self.launch_app()
            except:
                time.sleep(2)
                self.launch_app()


if __name__ == "__main__":
    updater = StandaloneUpdater()
    updater.run()
    
    # Keep console open to see messages
    input("\nPress Enter to exit...")
