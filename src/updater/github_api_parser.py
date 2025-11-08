"""
GitHub API Parser - More reliable than web scraping
Uses GitHub's official REST API to get release information
"""

import requests
import re
from datetime import datetime

class GitHubAPIParser:
    def __init__(self, repo_url):
        """
        Initialize parser with GitHub repository URL
        
        Args:
            repo_url: Can be:
                - https://github.com/owner/repo
                - https://github.com/owner/repo/releases/tag/v1.0
                - https://github.com/owner/repo/releases/latest
        """
        self.repo_url = repo_url.rstrip('/')
        self.owner, self.repo, self.tag = self._parse_url(repo_url)
        
    def _parse_url(self, url):
        """Extract owner, repo, and tag from GitHub URL"""
        # Remove https://github.com/
        path = url.replace('https://github.com/', '').replace('http://github.com/', '')
        
        # Parse different URL formats
        if '/releases/tag/' in path:
            # https://github.com/owner/repo/releases/tag/v1.0
            match = re.match(r'([^/]+)/([^/]+)/releases/tag/(.+)', path)
            if match:
                return match.group(1), match.group(2), match.group(3)
        elif '/releases/latest' in path:
            # https://github.com/owner/repo/releases/latest
            match = re.match(r'([^/]+)/([^/]+)', path)
            if match:
                return match.group(1), match.group(2), 'latest'
        else:
            # https://github.com/owner/repo
            match = re.match(r'([^/]+)/([^/]+)', path)
            if match:
                return match.group(1), match.group(2), 'latest'
        
        raise ValueError(f"Could not parse GitHub URL: {url}")
    
    def get_release_info(self):
        """
        Get release information using GitHub API
        
        Returns:
            dict with release data or None if failed
        """
        try:
            if self.tag == 'latest':
                api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
            else:
                api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/tags/{self.tag}"
            
            print(f"Fetching from GitHub API: {api_url}")
            
            response = requests.get(api_url)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Failed to fetch from GitHub API: {e}")
            return None
    
    def get_exe_assets(self):
        """
        Get all .exe assets from the release
        
        Returns:
            list of dicts with asset information
        """
        release_data = self.get_release_info()
        
        if not release_data:
            return []
        
        exe_assets = []
        
        for asset in release_data.get('assets', []):
            if asset['name'].endswith('.exe'):
                exe_assets.append({
                    'filename': asset['name'],
                    'download_url': asset['browser_download_url'],
                    'size': asset['size'],
                    'size_mb': round(asset['size'] / (1024 * 1024), 2),
                    'created_at': asset['created_at'],
                    'updated_at': asset['updated_at'],
                    'download_count': asset['download_count'],
                    'id': asset['id']
                })
        
        # Sort by created date (newest first)
        exe_assets.sort(key=lambda x: x['created_at'], reverse=True)
        
        return exe_assets
    
    def get_latest_exe(self):
        """
        Get the latest .exe asset
        
        Returns:
            dict with asset info or None
        """
        exe_assets = self.get_exe_assets()
        return exe_assets[0] if exe_assets else None
    
    def check_for_updates(self, local_created_at):
        """
        Check if there's a newer version available
        
        Args:
            local_created_at: ISO format date string of local version
        
        Returns:
            tuple: (needs_update: bool, asset_info: dict or None)
        """
        latest_exe = self.get_latest_exe()
        
        if not latest_exe:
            return False, None
        
        if not local_created_at:
            return True, latest_exe
        
        try:
            local_date = datetime.fromisoformat(local_created_at.replace('Z', '+00:00'))
            remote_date = datetime.fromisoformat(latest_exe['created_at'].replace('Z', '+00:00'))
            
            if remote_date > local_date:
                return True, latest_exe
        except Exception as e:
            print(f"Error comparing dates: {e}")
        
        return False, None


# Test function
if __name__ == "__main__":
    test_urls = [
        "https://github.com/SuurStofi/auto-updater-app/releases/tag/auto-updating-app",
        "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/latest",
    ]
    
    for url in test_urls:
        print("\n" + "=" * 70)
        print(f"Testing: {url}")
        print("=" * 70)
        
        try:
            parser = GitHubAPIParser(url)
            print(f"Owner: {parser.owner}")
            print(f"Repo: {parser.repo}")
            print(f"Tag: {parser.tag}")
            
            exe_assets = parser.get_exe_assets()
            
            if exe_assets:
                print(f"\n✓ Found {len(exe_assets)} .exe asset(s):")
                for asset in exe_assets:
                    print(f"\n  Filename: {asset['filename']}")
                    print(f"  Size: {asset['size_mb']} MB")
                    print(f"  Created: {asset['created_at']}")
                    print(f"  Downloads: {asset['download_count']}")
                    print(f"  URL: {asset['download_url']}")
            else:
                print("\n✗ No .exe assets found in this release")
                
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
