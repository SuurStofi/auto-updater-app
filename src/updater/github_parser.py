import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class GitHubParser:
    def __init__(self, repo_url):
        self.repo_url = repo_url.rstrip('/')
        # Determine if it's a specific release page or the repo URL
        if '/releases/tag/' in self.repo_url:
            self.releases_url = self.repo_url
            # Also create expanded_assets URL for faster loading
            # Replace /releases/tag/ with /releases/expanded_assets/
            self.expanded_assets_url = self.repo_url.replace('/releases/tag/', '/releases/expanded_assets/')
        else:
            self.releases_url = f"{self.repo_url}/releases/latest"
            self.expanded_assets_url = f"{self.repo_url}/releases/expanded_assets/latest"
        
    def get_latest_exe_info(self):
        """
        Parse GitHub releases page for latest .exe file
        Uses expanded_assets endpoint for immediate asset loading
        Returns: dict with download_url, sha256, release_date, filename
        """
        try:
            # Try expanded_assets endpoint first (loads assets immediately)
            print(f"Fetching GitHub Release (expanded assets): {self.expanded_assets_url}")
            response = requests.get(self.expanded_assets_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all Box-row items (each asset is in one)
            box_rows = soup.find_all('li', class_='Box-row')
            print(f"Found {len(box_rows)} asset rows")
            
            for row in box_rows:
                # Look for .exe link in this row
                exe_link = row.find('a', href=re.compile(r'\.exe'))
                
                if not exe_link:
                    continue
                
                href = exe_link.get('href', '')
                if not href.startswith('http'):
                    href = f"https://github.com{href}"
                
                filename = href.split('/')[-1]
                print(f"Processing: {filename} from {href}")
                
                # Extract metadata from the same row
                sha256 = None
                release_date = None
                file_size = None
                
                # Find SHA256 in clipboard-copy element
                clipboard = row.find('clipboard-copy', value=re.compile(r'sha256:'))
                if clipboard:
                    sha256_value = clipboard.get('value', '')
                    sha256 = sha256_value.replace('sha256:', '') if 'sha256:' in sha256_value else None
                
                # Find release date in relative-time element
                time_elem = row.find('relative-time')
                if time_elem:
                    release_date = time_elem.get('datetime')
                
                # Find file size - look for spans with MB/KB/GB
                spans = row.find_all('span', class_=re.compile(r'color-fg-muted'))
                for span in spans:
                    text = span.get_text(strip=True)
                    if any(unit in text for unit in ['MB', 'KB', 'GB', 'B']):
                        file_size = text
                        break
                
                print(f"  SHA256: {sha256}")
                print(f"  Date: {release_date}")
                print(f"  Size: {file_size}")
                
                # Return first .exe found (they're usually only one)
                return {
                    'download_url': href,
                    'filename': filename,
                    'sha256': sha256,
                    'release_date': release_date,
                    'file_size': file_size
                }
            
            print("No .exe files found in any row")
            return None
            
        except Exception as e:
            print(f"Failed to parse GitHub releases: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_network_page(self):
        """
        Parse GitHub Network/Assets page for .exe files
        Uses expanded_assets endpoint for immediate asset loading
        Searches for headers with .exe and extracts SHA256 hash and release date
        Returns: list of dicts with download_url, sha256, release_date, filename, file_size
        """
        try:
            # Use expanded_assets endpoint which loads assets immediately without JS
            print(f"Fetching expanded assets: {self.expanded_assets_url}")
            response = requests.get(self.expanded_assets_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            exe_files = []
            
            # Find all Box-row items (each asset is in one)
            box_rows = soup.find_all('li', class_='Box-row')
            print(f"Found {len(box_rows)} asset rows")
            
            for row in box_rows:
                # Look for .exe link in this row
                exe_link = row.find('a', href=re.compile(r'\.exe'))
                
                if not exe_link:
                    continue
                
                href = exe_link.get('href', '')
                if not href.startswith('http'):
                    href = f"https://github.com{href}"
                
                filename = href.split('/')[-1]
                print(f"Processing: {filename}")
                
                # Extract metadata from the same row
                sha256 = None
                release_date = None
                file_size = None
                
                # Find SHA256 in clipboard-copy element
                clipboard = row.find('clipboard-copy', value=re.compile(r'sha256:'))
                if clipboard:
                    sha256_value = clipboard.get('value', '')
                    sha256 = sha256_value.replace('sha256:', '') if 'sha256:' in sha256_value else None
                
                # Find release date in relative-time element
                time_elem = row.find('relative-time')
                if time_elem:
                    release_date = time_elem.get('datetime')
                
                # Find file size - look for spans with MB/KB/GB
                spans = row.find_all('span', class_=re.compile(r'color-fg-muted'))
                for span in spans:
                    text = span.get_text(strip=True)
                    if any(unit in text for unit in ['MB', 'KB', 'GB', 'B']):
                        file_size = text
                        break
                
                exe_files.append({
                    'download_url': href,
                    'filename': filename,
                    'sha256': sha256,
                    'release_date': release_date,
                    'file_size': file_size
                })
                
                print(f"  SHA256: {sha256}")
                print(f"  Date: {release_date}")
                print(f"  Size: {file_size}")
            
            # Sort by release date (newest first) if available
            if exe_files:
                exe_files.sort(key=lambda x: x['release_date'] or '', reverse=True)
            
            print(f"Total .exe files found: {len(exe_files)}")
            return exe_files
            
        except Exception as e:
            print(f"Failed to parse GitHub network page: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def check_for_updates(self, local_sha256, local_date):
        """
        Check if there's a newer version available
        Compares SHA256 hash and release date
        """
        latest_info = self.get_latest_exe_info()
        
        if not latest_info:
            return False, None
        
        # Check SHA256 hash
        if latest_info['sha256'] != local_sha256:
            # Also check date to confirm it's newer
            if latest_info['release_date']:
                remote_date = datetime.fromisoformat(latest_info['release_date'].replace('Z', '+00:00'))
                if local_date and remote_date > local_date:
                    return True, latest_info
        
        return False, None
    
    def check_for_updates_network(self, local_sha256, local_date):
        """
        Check for updates using network page parsing
        Checks all .exe files and compares SHA256 hash and dates
        Returns the newest file that differs from local version
        """
        exe_files = self.parse_network_page()
        
        if not exe_files:
            return False, None
        
        # Check each file (they're sorted by date, newest first)
        for exe_info in exe_files:
            # Compare SHA256 hash
            if exe_info['sha256'] and exe_info['sha256'] != local_sha256:
                # Check if it's newer by comparing dates
                if exe_info['release_date']:
                    try:
                        remote_date = datetime.fromisoformat(exe_info['release_date'].replace('Z', '+00:00'))
                        
                        # If no local date, consider it an update
                        if not local_date:
                            return True, exe_info
                        
                        # Ensure local_date is timezone-aware
                        if local_date.tzinfo is None:
                            from datetime import timezone
                            local_date = local_date.replace(tzinfo=timezone.utc)
                        
                        # Compare dates
                        if remote_date > local_date:
                            return True, exe_info
                    except Exception as e:
                        print(f"Error parsing date: {e}")
                        # If date parsing fails but hashes differ, assume update needed
                        return True, exe_info
        
        return False, None