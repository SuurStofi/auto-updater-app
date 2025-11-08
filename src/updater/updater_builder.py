"""
Builder for creating standalone updater.exe
Embeds configuration and compiles to executable
"""

import PyInstaller.__main__
from pathlib import Path
import json
import shutil


class UpdaterBuilder:
    def __init__(self, save_dir):
        """
        Args:
            save_dir: Directory where updater.exe will be created
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.src_dir = Path(__file__).parent
        self.template_file = self.src_dir / "standalone_updater.py"
        self.temp_file = self.save_dir / "updater_configured.py"
    
    def build(self, source_type, url, sha256=None, release_date=None, target_filename=None):
        """
        Build standalone updater.exe with embedded configuration
        
        Args:
            source_type: "Direct URL", "GitHub Release", or "GitHub Network (Assets)"
            url: URL to check for updates
            sha256: Current file's SHA256 hash
            release_date: Current file's release date
            target_filename: Name of the application executable
        """
        print(f"Building updater.exe...")
        print(f"  Source: {source_type}")
        print(f"  URL: {url}")
        print(f"  Save location: {self.save_dir}")
        
        # Read template
        with open(self.template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Create configuration
        config = {
            'source_type': source_type,
            'url': url,
            'last_sha256': sha256 or '',
            'last_date': release_date or '',
            'target_filename': target_filename or ''
        }
        
        # Replace placeholder with actual config
        config_str = json.dumps(config, indent=2)
        configured_content = template_content.replace(
            "CONFIG = {\n    'source_type': 'PLACEHOLDER_SOURCE_TYPE',\n    'url': 'PLACEHOLDER_URL',\n    'last_sha256': 'PLACEHOLDER_SHA256',\n    'last_date': 'PLACEHOLDER_DATE',\n    'target_filename': 'PLACEHOLDER_FILENAME'\n}",
            f"CONFIG = {config_str}"
        )
        
        # Write configured version
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            f.write(configured_content)
        
        # Build executable
        try:
            PyInstaller.__main__.run([
                str(self.temp_file),
                '--onefile',
                '--name=updater',
                f'--distpath={self.save_dir}',
                f'--workpath={self.save_dir / "build"}',
                f'--specpath={self.save_dir}',
                '--clean',
                '--noconfirm',
                '--console',  # Keep console for progress messages
            ])
            
            # Clean up temporary files
            self.temp_file.unlink(missing_ok=True)
            (self.save_dir / "updater.spec").unlink(missing_ok=True)
            build_dir = self.save_dir / "build"
            if build_dir.exists():
                shutil.rmtree(build_dir)
            
            updater_exe = self.save_dir / "updater.exe"
            if updater_exe.exists():
                print(f"✓ updater.exe created successfully!")
                print(f"  Location: {updater_exe}")
                return updater_exe
            else:
                print("✗ Failed to create updater.exe")
                return None
                
        except Exception as e:
            print(f"✗ Build failed: {e}")
            return None
