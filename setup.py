import sys
import os
import urllib.request
import zipfile
import shutil
import winshell
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool)

    def __init__(self, url, target_path):
        super().__init__()
        self.url = url
        self.target_path = target_path
    
    def run(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(self.url, headers=headers)
            
            with urllib.request.urlopen(req) as response, open(self.target_path, 'wb') as out_file:
                total_size = int(response.getheader('Content-Length', 0))
                downloaded = 0
                chunk_size = 1024
                
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    percent = int((downloaded / total_size) * 100)
                    self.progress_signal.emit(percent)
            
            self.finished_signal.emit(True)
        except Exception as e:
            print(f"Error downloading file: {e}")
            self.finished_signal.emit(False)

def extract_zip(zip_path, extract_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        return True
    except Exception as e:
        print(f"Error extracting file: {e}")
        return False

def create_directories():
    directories = ['models', 'blender']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

class InstallerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Python Installer GUI")
        self.setGeometry(100, 100, 400, 250)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Click Install to start the process.")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.install_button = QPushButton("Install")
        self.install_button.clicked.connect(self.start_installation)
        layout.addWidget(self.install_button)
        
        self.setLayout(layout)
    
    def start_installation(self):
        base_dir = QFileDialog.getExistingDirectory(self, "Select Installation Directory")
        if not base_dir:
            QMessageBox.warning(self, "Warning", "Installation directory not selected.")
            return
        
        os.makedirs(base_dir, exist_ok=True)
        os.chdir(base_dir)
        
        self.download_files()
    
    def download_files(self):
        self.status_label.setText("Downloading files...")
        files = {
            "models/sam_vit_b_01ec64.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
            "blender/blender-3.6.0-windows-x64.zip": "https://download.blender.org/release/Blender3.6/blender-3.6.0-windows-x64.zip"
        }
        
        self.current_downloads = []
        for target_path, url in files.items():
            thread = DownloadThread(url, target_path)
            thread.progress_signal.connect(self.progress_bar.setValue)
            thread.finished_signal.connect(lambda success, path=target_path: self.handle_download_completion(success, path))
            self.current_downloads.append(thread)
            thread.start()
    
    def handle_download_completion(self, success, path):
        if success:
            if path.endswith('.zip'):
                extract_dir = os.path.dirname(path)
                if extract_zip(path, extract_dir):
                    os.remove(path)
        
        if all(not t.isRunning() for t in self.current_downloads):
            self.status_label.setText("Installation complete!")
            self.create_shortcut(os.path.join(os.getcwd(), "blender", "blender.exe"), "Blender")
            QMessageBox.information(self, "Success", "Installation complete!")
    
    def create_shortcut(self, target_path, shortcut_name):
        if os.path.exists(target_path):
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
            
            with winshell.shortcut(shortcut_path) as shortcut:
                shortcut.path = target_path
                shortcut.description = "Shortcut to Installed Application"
                shortcut.working_directory = os.path.dirname(target_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstallerGUI()
    window.show()
    sys.exit(app.exec())
