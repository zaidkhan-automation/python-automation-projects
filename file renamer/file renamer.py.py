import os

# Get the folder where the script itself is saved
folder = os.path.dirname(os.path.abspath("test"))
new_name = "holiday"

for count, filename in enumerate(os.listdir(folder), start=1):
    file_path = os.path.join(folder, filename)
    if os.path.isfile(file_path):
        ext = os.path.splitext(filename)[1]
        new_filename = f"{new_name}_{count}{ext}"
        new_path = os.path.join(folder, new_filename)
        os.rename(file_path, new_path)
        print(f"Renamed: {filename} -> {new_filename}")