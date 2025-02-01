import sys
import os
import zipfile
import gdown
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QLineEdit

class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AiCore Installer")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()

        self.url_label = QLabel("File ID (Do Not Change):", self)
        self.layout.addWidget(self.url_label)

        self.file_id_input = QLineEdit(self)
        self.file_id_input.setText('1LDmjCVwyybmjDWLVelE9TS398ndFys1w')  # Default file ID
        self.layout.addWidget(self.file_id_input)

        self.destination_label = QLabel("Choose download & extract location:", self)
        self.layout.addWidget(self.destination_label)

        self.select_folder_button = QPushButton("Select Folder", self)
        self.select_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_folder_button)

        self.selected_folder_label = QLabel("No folder selected.", self)
        self.layout.addWidget(self.selected_folder_label)

        self.download_button = QPushButton("Download & Extract", self)
        self.download_button.clicked.connect(self.download_and_extract)
        self.layout.addWidget(self.download_button)

        self.status_label = QLabel("", self)
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selected_folder_label.setText(f"Selected folder: {folder}")
            self.folder_path = folder
        else:
            self.selected_folder_label.setText("No folder selected.")

    def download_and_extract(self):
        file_id = self.file_id_input.text()
        if hasattr(self, 'folder_path') and self.folder_path:
            destination = os.path.join(self.folder_path, 'AiCore.zip')
            extract_dir = os.path.join(self.folder_path, 'AiCore X SpatterSense')

            try:
                # Step 1: Download ZIP from Google Drive
                self.status_label.setText("Downloading...")
                gdown.download(f'https://drive.google.com/uc?id={file_id}', destination, quiet=False)

                # Step 2: Extract the ZIP file
                os.makedirs(extract_dir, exist_ok=True)
                with zipfile.ZipFile(destination, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

                self.status_label.setText(f'AiCore x SpatterSense located at: {extract_dir}')
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")
        else:
            self.status_label.setText("Please select a folder first.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec_())
