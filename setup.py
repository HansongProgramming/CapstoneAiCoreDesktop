import sys
import os
import gdown
import zipfile
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QProgressBar, 
                           QCheckBox, QFileDialog, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import win32com.client

class DownloaderThread(QThread):
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_id, destination):
        super().__init__()
        self.file_id = file_id
        self.destination = destination

    def run(self):
        try:
            zip_path = os.path.join(self.destination, "AiCore.zip")
            url = f"https://drive.google.com/uc?id={self.file_id}"
            self.status_update.emit("Downloading")
            
            gdown.download(url, zip_path, quiet=True)
            
            self.progress.emit(0)
            self.status_update.emit("Extracting")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_count = len(zip_ref.namelist())
                for i, file in enumerate(zip_ref.namelist()):
                    zip_ref.extract(file, self.destination)
                    progress = int(((i + 1) / file_count) * 100)
                    self.progress.emit(progress)

            os.remove(zip_path)
            self.progress.emit(100)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_id = None
        self.initUI()
        self.fetch_file_id()

    def initUI(self):
        self.setFixedSize(550, 420)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("AiCore Installer")
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)
        
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        
        img_label = QLabel()
        pixmap = QPixmap(self.get_resource_path("images/Banner_Portrait.png"))
        scaled_pixmap = pixmap.scaled(300, 420, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        img_label.setPixmap(scaled_pixmap)
        img_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(img_label)
        
        menu_layout = QHBoxLayout()
        menu_layout.addStretch()
        self.exit_button = QPushButton("X")
        self.exit_button.setFixedSize(20,20)
        self.exit_button.clicked.connect(lambda: self.exit())
        menu_layout.addWidget(self.exit_button)
        right_layout.addLayout(menu_layout)
        right_layout.setContentsMargins(10,5,10,0)
        
        message = QLabel('Thank you for choosing AiCore!')
        message.setStyleSheet("font-size:15px")
        right_layout.addWidget(message)
        
        location_layout = QHBoxLayout()
        location_label = QLabel('Location:')
        self.location_input = QLineEdit()
        self.location_input.setReadOnly(True)
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_location)
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_input)
        location_layout.addWidget(browse_button)
        right_layout.addLayout(location_layout)
        
        progress_layout = QHBoxLayout()
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_download)
        self.start_button.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.start_button)
        progress_layout.addWidget(self.progress_bar)
        right_layout.addLayout(progress_layout)
        
        self.shortcut_checkbox = QCheckBox('Create desktop shortcut?')
        right_layout.addWidget(self.shortcut_checkbox)
        
        self.status_label = QLabel('Fetching file ID...')
        self.status_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.status_label)
        
        self.show()
        
    def exit(self):
        self.window().close()
    
    def fetch_file_id(self):
        url = "https://hansongprogramming.github.io/CapstoneAiCoreDesktop/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            h1_tag = soup.find('h1')
            h2_tag = soup.find('h2')
            
            if h1_tag:
                self.file_id = h1_tag.text.strip()
                self.status_label.setText(f"AiCore: {h2_tag}")
            else:
                self.status_label.setText("Error: No file ID found")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
    
    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if folder:
            self.location_input.setText(folder)
            self.start_button.setEnabled(True if self.file_id else False)
            
    def get_resource_path(self, relative_path):
        if getattr(sys, 'frozen', False): 
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def start_download(self):
        if not self.file_id:
            self.status_label.setText("Error: File ID not retrieved")
            return
        
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Downloading...")
        
        self.downloader = DownloaderThread(self.file_id, self.location_input.text())
        self.downloader.progress.connect(self.update_progress)
        self.downloader.finished.connect(self.download_finished)
        self.downloader.error.connect(self.download_error)
        self.downloader.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def download_finished(self):
        self.status_label.setText('Download and extraction completed!')
        self.start_button.setEnabled(True)
        
        if self.shortcut_checkbox.isChecked():
            self.create_desktop_shortcut()
    
    def download_error(self, error_message):
        self.status_label.setText(f'Error: {error_message}')
        self.start_button.setEnabled(True)
        
    def create_desktop_shortcut(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop_path, "AiCore.lnk") 

        target_exe = os.path.join(f"{self.location_input.text()}/AiCore", "AiCore.exe")

        if not os.path.exists(target_exe):
            self.status_label.setText("Shortcut creation failed: AiCore.exe not found!")
            return

        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = target_exe
            shortcut.WorkingDirectory = os.path.dirname(target_exe)
            shortcut.Save()

            self.status_label.setText("Download completed and shortcut created!")
        except Exception as e:
            self.status_label.setText(f"Shortcut creation failed: {str(e)}")
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
