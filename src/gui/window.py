from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLineEdit, 
                           QPushButton, QLabel, QFileDialog, QHBoxLayout,
                           QComboBox, QMessageBox)

class MainWindow(QMainWindow):
    def __init__(self, last_url='', last_dir=''):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Auto Updater")
        self.setGeometry(100, 100, 500, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Source type selection
        source_layout = QHBoxLayout()
        self.source_label = QLabel("Update Source:")
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Direct URL", "GitHub Release", "GitHub Network (Assets)"])
        source_layout.addWidget(self.source_label)
        source_layout.addWidget(self.source_combo)
        
        # URL input section
        self.url_label = QLabel("Enter GitHub repository URL or direct download URL:")
        self.url_entry = QLineEdit(last_url)
        
        # Directory selection section
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("Save location:")
        self.dir_entry = QLineEdit(last_dir)
        self.dir_button = QPushButton("Browse...")
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_entry)
        dir_layout.addWidget(self.dir_button)
        
        # Buttons section
        button_layout = QHBoxLayout()
        self.build_button = QPushButton("Build Updater.exe")
        self.test_button = QPushButton("Test Update")
        button_layout.addWidget(self.build_button)
        button_layout.addWidget(self.test_button)
        
        self.status_label = QLabel("")
        
        # Add widgets to layout
        layout.addLayout(source_layout)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_entry)
        layout.addLayout(dir_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        
        # Connect signals
        self.build_button.clicked.connect(self.build_updater)
        self.test_button.clicked.connect(self.test_update)
        self.dir_button.clicked.connect(self.select_directory)
        self.source_combo.currentTextChanged.connect(self.update_url_label)
        
        # Initialize callback functions
        self.on_build_requested = None
        self.on_test_requested = None
        self.on_autostart_toggled = None

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.dir_entry.text() or ""
        )
        if dir_path:
            self.dir_entry.setText(dir_path)

    def build_updater(self):
        url = self.url_entry.text()
        save_dir = self.dir_entry.text()
        source_type = self.source_combo.currentText()
        
        if not url:
            self.status_label.setText("Please enter a valid URL.")
            return
            
        if not save_dir:
            self.status_label.setText("Please select a save location.")
            return
            
        if self.on_build_requested:
            self.status_label.setText(f"Building updater.exe...")
            self.on_build_requested(url, save_dir, source_type)
    
    def test_update(self):
        url = self.url_entry.text()
        save_dir = self.dir_entry.text()
        source_type = self.source_combo.currentText()
        
        if not url:
            self.status_label.setText("Please enter a valid URL.")
            return
            
        if not save_dir:
            self.status_label.setText("Please select a save location.")
            return
            
        if self.on_test_requested:
            self.status_label.setText(f"Testing update process...")
            self.on_test_requested(url, save_dir, source_type)

    def update_url_label(self, source_type):
        if source_type == "GitHub Release":
            self.url_label.setText("Enter GitHub repository URL (e.g., https://github.com/user/repo):")
        elif source_type == "GitHub Network (Assets)":
            self.url_label.setText("Enter GitHub release page with .exe assets (e.g., https://github.com/user/repo/releases/tag/v1.0):")
        else:
            self.url_label.setText("Enter direct download URL:")