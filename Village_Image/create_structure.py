import os

# Base path
base_path = r"C:\Users\chandan.p\Pictures\maati-katha-research"

# Folder structure
folders = [
    base_path,
    os.path.join(base_path, "01-visual"),
    os.path.join(base_path, "01-visual", "bhuvan-screenshots"),
    os.path.join(base_path, "01-visual", "toposheets"),
    os.path.join(base_path, "02-land"),
    os.path.join(base_path, "03-history"),
]

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create notes.md file
notes_file_path = os.path.join(base_path, "01-visual", "notes.md")

if not os.path.exists(notes_file_path):
    with open(notes_file_path, "w", encoding="utf-8") as f:
        f.write("# Notes\n\nStart documenting your observations here.\n")

print("Folder structure created successfully.")