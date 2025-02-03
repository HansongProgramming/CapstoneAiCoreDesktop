import sys
import os
import gdown
import zipfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QProgressBar, 
                           QCheckBox, QFileDialog, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
class DownloaderThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_id, destination):
        super().__init__()
        self.file_id = file_id
        self.destination = destination

    def run(self):
        try:
            zip_path = os.path.join(self.destination, "download.zip")
            
            url = f"https://drive.google.com/uc?id={self.file_id}"
            gdown.download(url, zip_path, quiet=False)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.destination)
            
            os.remove(zip_path)
            
            self.progress.emit(100)  
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('AiCore Installer')
        self.setFixedSize(500, 200)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        img_label = QLabel()
        img_path = os.path.join('images', 'SplashScreen.png')

        pixmap = QPixmap(img_path)
        scaled_pixmap = pixmap.scaled(480, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        img_label.setPixmap(scaled_pixmap)
        img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(img_label)

        location_layout = QHBoxLayout()
        location_label = QLabel('Location:')
        self.location_input = QLineEdit()
        self.location_input.setReadOnly(True)
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_location)
        
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_input)
        location_layout.addWidget(browse_button)
        layout.addLayout(location_layout)

        # Progress section
        progress_layout = QHBoxLayout()
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_download)
        self.start_button.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.start_button)
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)

        self.shortcut_checkbox = QCheckBox('Create desktop shortcut?')
        layout.addWidget(self.shortcut_checkbox)

        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.show()

    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if folder:
            self.location_input.setText(folder)
            self.start_button.setEnabled(True)

    def start_download(self):
        if not self.location_input.text():
            self.status_label.setText('Please select a destination folder first')
            return

        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText('Downloading...')

        self.downloader = DownloaderThread('1LDmjCVwyybmjDWLVelE9TS398ndFys1w', 
                                         self.location_input.text())
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
        desktop_path = os.path.expanduser("~/Desktop")
        shortcut_path = os.path.join(desktop_path, "Downloaded_Content.lnk")
        
        try:
            with open(shortcut_path, 'w') as f:
                f.write(f"[InternetShortcut]\nURL=file://{self.location_input.text()}")
            self.status_label.setText('Download completed and shortcut created!')
        except Exception as e:
            self.status_label.setText(f'Shortcut creation failed: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())