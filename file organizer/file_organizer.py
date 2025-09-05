import os
import shutil

# 👉 EDIT THIS: put the folder you want to organize
source_folder = r"C:\Users\HP\Downloads"   # e.g., Windows
# source_folder = r"/Users/HP/Downloads"   # e.g., Mac/Linux

# Create target folders inside the source folder
docs_folder = os.path.join(source_folder, "Documents")
videos_folder = os.path.join(source_folder, "Videos")
os.makedirs(docs_folder, exist_ok=True)
os.makedirs(videos_folder, exist_ok=True)

# File type lists (add more if you like)
pdf_exts = (".pdf",)
video_exts = (".mp4", ".mkv", ".avi", ".mov")

# Go through items in the source folder
for name in os.listdir(source_folder):
    path = os.path.join(source_folder, name)
    if not os.path.isfile(path):
        continue  # skip folders

    lower = name.lower()
    if lower.endswith(pdf_exts):
        shutil.move(path, os.path.join(docs_folder, name))
        print(f"Moved {name} -> Documents")
    elif lower.endswith(video_exts):
        shutil.move(path, os.path.join(videos_folder, name))
        print(f"Moved {name} -> Videos")