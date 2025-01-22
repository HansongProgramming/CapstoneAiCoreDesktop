import os
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIF opener for Pillow
register_heif_opener()

def convert_heic_to_png(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):  # Recursively traverse directories
        for filename in files:
            if filename.lower().endswith('.heic'):
                # Construct input and output paths
                input_path = os.path.join(root, filename)
                
                # Preserve subfolder structure in the output directory
                relative_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, relative_path)
                os.makedirs(output_subdir, exist_ok=True)
                
                output_path = os.path.join(output_subdir, f"{os.path.splitext(filename)[0]}.png")

                try:
                    # Open HEIC file using Pillow
                    image = Image.open(input_path)
                    
                    # Save as PNG
                    image.save(output_path, format="PNG")
                    print(f"Converted: {input_path} -> {output_path}")
                except Exception as e:
                    print(f"Failed to convert {filename}: {e}")

# Specify input and output directories
input_directory = input("Enter the path of the directory containing HEIC files: ")
output_directory = input("Enter the path of the output directory for PNG files: ")

convert_heic_to_png(input_directory, output_directory)
