from PyQt6.QtWidgets import QApplication
import sys
from gui.window import MainWindow
from updater.downloader import Downloader
from updater.launcher import Launcher
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
    window.on_update_requested = lambda url, save_dir: update_application(url, save_dir)
    window.on_autostart_toggled = lambda enabled: toggle_autostart(enabled)

    # Show the window
    window.show()

    # Start the event loop
    sys.exit(app.exec())

def update_application(url, save_dir):
    # Save settings
    config = load_config()
    config['last_url'] = url
    config['last_dir'] = save_dir
    save_config(config)

    downloader = Downloader(url, save_dir)
    if downloader.download():
        launcher = Launcher(downloader.file_path, save_dir)
        launcher.launch()

def toggle_autostart(enabled):
    if enabled:
        add_to_autostart()
    else:
        remove_from_autostart()

if __name__ == "__main__":
    main()