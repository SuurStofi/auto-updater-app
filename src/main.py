from PyQt6.QtWidgets import QApplication, QMessageBox
import sys
from gui.window import MainWindow
from updater.downloader import Downloader
from updater.launcher import Launcher
from updater.updater_builder import UpdaterBuilder
from utils.autostart import add_to_autostart, remove_from_autostart
from utils.config import load_config, save_config

def main():
    # Initialize Qt Application
    app = QApplication(sys.argv)

    # Load configuration
    config = load_config()
    last_url = config.get('last_url', '')
    last_dir = config.get('last_dir', '')

    # Initialize the GUI
    window = MainWindow(last_url, last_dir)

    # Connect GUI signals to updater functions
    window.on_build_requested = lambda url, save_dir, source_type: build_updater(url, save_dir, source_type, window)
    window.on_test_requested = lambda url, save_dir, source_type: test_update(url, save_dir, source_type, window)
    window.on_autostart_toggled = lambda enabled: toggle_autostart(enabled)

    # Show the window
    window.show()

    # Start the event loop
    sys.exit(app.exec())

def build_updater(url, save_dir, source_type, window):
    """Build standalone updater.exe with embedded configuration"""
    # Save settings
    config = load_config()
    config['last_url'] = url
    config['last_dir'] = save_dir
    config['source_type'] = source_type
    save_config(config)

    print(f"\n{'='*70}")
    print(f"Building updater.exe...")
    print(f"Source Type: {source_type}")
    print(f"URL: {url}")
    print(f"Save Directory: {save_dir}")
    print(f"{'='*70}\n")

    # First, download the latest version to get metadata
    downloader = Downloader(url, save_dir, source_type)
    if downloader.download():
        print("\n✓ Downloaded latest version for metadata extraction")
        
        # Get file metadata
        from utils.hash_utils import calculate_sha256, get_file_metadata
        metadata = get_file_metadata(downloader.file_path)
        
        # Build updater.exe
        builder = UpdaterBuilder(save_dir)
        updater_exe = builder.build(
            source_type=source_type,
            url=url,
            sha256=metadata['sha256'],
            release_date=metadata.get('modified_date'),
            target_filename=downloader.file_path.name
        )
        
        if updater_exe:
            window.status_label.setText(f"✓ updater.exe created: {updater_exe}")
            QMessageBox.information(
                window,
                "Success",
                f"updater.exe created successfully!\n\nLocation: {updater_exe}\n\nYou can now run updater.exe to check for updates and download new versions."
            )
        else:
            window.status_label.setText("✗ Failed to build updater.exe")
            QMessageBox.critical(window, "Error", "Failed to build updater.exe")
    else:
        window.status_label.setText("✗ Failed to download initial version")
        QMessageBox.critical(
            window,
            "Error",
            f"Failed to download from {source_type}.\nPlease check the URL and try again."
        )

def test_update(url, save_dir, source_type, window):
    """Test the update process without building exe"""
    # Save settings
    config = load_config()
    config['last_url'] = url
    config['last_dir'] = save_dir
    config['source_type'] = source_type
    save_config(config)

    print(f"\n{'='*70}")
    print(f"Testing update process...")
    print(f"Source Type: {source_type}")
    print(f"URL: {url}")
    print(f"Save Directory: {save_dir}")
    print(f"{'='*70}\n")

    downloader = Downloader(url, save_dir, source_type)
    if downloader.download():
        print("\n✓ Download successful!")
        print(f"✓ File saved: {downloader.file_path}")
        
        from utils.hash_utils import get_file_metadata
        metadata = get_file_metadata(downloader.file_path)
        print(f"\nFile Metadata:")
        print(f"  SHA256: {metadata['sha256']}")
        print(f"  Size: {metadata['size']} bytes")
        print(f"  Modified: {metadata.get('modified_date', 'N/A')}")
        
        window.status_label.setText(f"✓ Test successful! File: {downloader.file_path.name}")
        
        # Ask if user wants to launch
        reply = QMessageBox.question(
            window,
            "Launch Application?",
            f"Download successful!\n\nFile: {downloader.file_path.name}\nSize: {metadata['size']:,} bytes\n\nDo you want to launch the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            launcher = Launcher(downloader.file_path)
            launcher.launch()
    else:
        print(f"\n✗ Download failed for source type: {source_type}")
        window.status_label.setText("✗ Test failed")
        QMessageBox.critical(
            window,
            "Test Failed",
            f"Failed to download from {source_type}.\n\nTroubleshooting:\n1. Check the URL: {url}\n2. For GitHub modes, ensure .exe files are in the release\n3. Try 'Direct URL' mode with a direct download link"
        )

def update_application(url, save_dir, source_type):
    # Save settings
    config = load_config()
    config['last_url'] = url
    config['last_dir'] = save_dir
    config['source_type'] = source_type
    save_config(config)

    print(f"\n{'='*70}")
    print(f"Starting update process...")
    print(f"Source Type: {source_type}")
    print(f"URL: {url}")
    print(f"Save Directory: {save_dir}")
    print(f"{'='*70}\n")

    downloader = Downloader(url, save_dir, source_type)
    if downloader.download():
        print("\n✓ Download successful!")
        print(f"✓ File saved: {downloader.file_path}")
        launcher = Launcher(downloader.file_path)
        launcher.launch()
    else:
        print(f"\n✗ Download failed for source type: {source_type}")
        print("\nTroubleshooting:")
        print(f"1. Check the URL: {url}")
        print("2. If using GitHub modes, ensure .exe files are attached to the release")
        print("3. Try 'Direct URL' mode with a direct download link instead")

def toggle_autostart(enabled):
    if enabled:
        add_to_autostart()
    else:
        remove_from_autostart()

if __name__ == "__main__":
    main()