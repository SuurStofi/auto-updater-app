from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLineEdit, 
                           QPushButton, QLabel, QFileDialog, QHBoxLayout)
from PyQt6.QtWidgets import QApplication
import sys

class MainWindow(QMainWindow):
    def __init__(self, last_url='', last_dir=''):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Auto Updater")
        self.setGeometry(100, 100, 500, 250)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # URL input section
        self.url_label = QLabel("Enter the URL for the executable:")
        self.url_entry = QLineEdit(last_url)
        
        # Directory selection section
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("Save location:")
        self.dir_entry = QLineEdit(last_dir)
        self.dir_button = QPushButton("Browse...")
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_entry)
        dir_layout.addWidget(self.dir_button)
        
        self.update_button = QPushButton("Create Auto-Updater")
        self.status_label = QLabel("")
        
        # Add widgets to layout
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_entry)
        layout.addLayout(dir_layout)
        layout.addWidget(self.update_button)
        layout.addWidget(self.status_label)
        
        # Connect signals
        self.update_button.clicked.connect(self.start_update)
        self.dir_button.clicked.connect(self.select_directory)
        
        # Initialize callback functions
        self.on_update_requested = None
        self.on_autostart_toggled = None

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.dir_entry.text() or ""
        )
        if dir_path:
            self.dir_entry.setText(dir_path)

    def start_update(self):
        url = self.url_entry.text()
        save_dir = self.dir_entry.text()
        
        if not url:
            self.status_label.setText("Please enter a valid URL.")
            return
            
        if not save_dir:
            self.status_label.setText("Please select a save location.")
            return
            
        if self.on_update_requested:
            self.status_label.setText(f"Creating auto-updater...")
            self.on_update_requested(url, save_dir)

    def run(self):
        app = QApplication(sys.argv)
        self.show()
        return app.exec()