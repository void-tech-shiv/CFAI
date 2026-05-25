import os
import shutil

base_dir = r"d:\HONORS CLASS\term3\CFAI\pg byme"
backend_dir = os.path.join(base_dir, "Backend")
os.makedirs(backend_dir, exist_ok=True)

folders_to_move = ["datasets", "models", "algorithms", "utils"]
for folder in folders_to_move:
    src = os.path.join(base_dir, folder)
    dst = os.path.join(backend_dir, folder)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {folder} to Backend")
    else:
        print(f"{folder} not found in {base_dir}")
