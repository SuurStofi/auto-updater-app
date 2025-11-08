# auto-updater

This project is a simple auto-updater application that allows users to update their software from a specified URL. The application features a graphical user interface (GUI) for easy interaction and integrates itself into the system's autostart settings.

## Features

- User-friendly GUI for inputting the update URL.
- Automatic integration into system autostart.
- Detection and manual launch if removed from autostart.
- Downloads and installs the executable file from the provided URL.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd auto-updater
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage

- Open the application and enter the URL of the executable file you wish to download and install.
- The application will handle the download and installation process.
- Ensure that the application is set to run on startup for automatic updates.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.