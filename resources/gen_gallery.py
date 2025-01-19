import os

# Constants
IMG_DIR = "./figs"
WIDTH = 200   # Default width
HEIGHT = 0  # Default height

# List all image files in IMG_DIR, sorted by filenames
file_list = sorted([f for f in os.listdir(IMG_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))])

HEADER = """
# [Pix](https://en.wikipedia.org/wiki/Pixel#Etymology)
"""

print(HEADER)

# Generate and print the output for each image file
for FILENAME in file_list:
    # Dynamically build the size attributes based on WIDTH and HEIGHT
    size_attributes = []
    if WIDTH > 0:
        size_attributes.append(f"width={WIDTH}")
    if HEIGHT > 0:
        size_attributes.append(f"height={HEIGHT}")
    
    # Join the size attributes with a comma, if any
    size_string = ", ".join(size_attributes)
    
    # Format the template
    template = f"![]({IMG_DIR}/{FILENAME}){{{size_string}, loading=lazy}}"
    print(template)