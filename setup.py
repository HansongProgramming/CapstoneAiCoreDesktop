from setuptools import setup, find_packages
import os
import urllib.request
import sys
import zipfile
import shutil
from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_file(url, target_path):
    try:
        print(f"Downloading file from {url}")
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=target_path) as t:
            urllib.request.urlretrieve(url, target_path, reporthook=t.update_to)
        print("Download completed successfully")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def extract_zip(zip_path, extract_path):
    try:
        print(f"Extracting {zip_path} to {extract_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print("Extraction completed successfully")
        return True
    except Exception as e:
        print(f"Error extracting file: {e}")
        return False

def create_directories():
    directories = ['models', 'blender']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def setup_project():
    create_directories()
    
    files = {
        "models/sam_vit_b_01ec64.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
        "blender/blender.zip": "https://download.blender.org/release/Blender3.6/blender-3.6.0-windows-x64.zip"
    }
    
    for target_path, url in files.items():
        if download_file(url, target_path):
            if target_path.endswith('.zip'):
                extract_dir = os.path.dirname(target_path)
                if extract_zip(target_path, extract_dir):
                    try:
                        os.remove(target_path)
                        print(f"Deleted zip file: {target_path}")
                    except Exception as e:
                        print(f"Error deleting zip file: {e}")

if __name__ == "__main__":
    setup_project()