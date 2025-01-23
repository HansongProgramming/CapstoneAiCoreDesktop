from setuptools import setup, find_packages
import os
import urllib.request
import sys

def download_file(url, target_path):
    try:
        print(f"Downloading file from {url} to {target_path}")
        urllib.request.urlretrieve(url, target_path)
        print("Download completed successfully")
    except Exception as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)

def create_directories():
    directory = "models"
    
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

def setup_project():
    create_directories()
    
    temp_url = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fdl.fbaipublicfiles.com%2Fsegment_anything%2Fsam_vit_b_01ec64.pth&psig=AOvVaw1OEoTNaFKJZzi7Q3mddSzh&ust=1737723778953000&source=images&cd=vfe&opi=89978449&ved=0CAQQn5wMahcKEwiQyevc84uLAxUAAAAAHQAAAAAQBA"
    download_file(temp_url, "models/sam_vit_b_01ec64.pth")

if __name__ == "__main__":
    setup_project()