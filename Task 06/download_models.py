import urllib.request
import os
import sys

print("Downloading YOLOv3 weights...")

# Try multiple sources for robustness
weights_sources = [
    "https://github.com/patrick013/ObjectDetection---Tiny-YOLOv3/raw/master/model/yolov3.weights",
    "https://pjreddie.com/media/files/yolov3.weights",
]

cfg_url = "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg"
names_url = "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names"

models_dir = "models"
os.makedirs(models_dir, exist_ok=True)

weights_path = os.path.join(models_dir, "yolov3.weights")
cfg_path = os.path.join(models_dir, "yolov3.cfg")
names_path = os.path.join(models_dir, "coco.names")

# Download with progress
def download_file(url, destination, file_size_mb=""):
    try:
        print(f"  Trying: {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 1024 * 1024  # 1MB chunks
            downloaded = 0
            
            with open(destination, 'wb') as out_file:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    out_file.write(chunk)
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"  Downloaded: {downloaded/1024/1024:.1f}MB / {total_size/1024/1024:.1f}MB ({percent:.1f}%)", end='\r')
        print("\n  ✓ Success!")
        return True
    except Exception as e:
        print(f"\n  ✗ Failed: {e}")
        return False

if not os.path.exists(weights_path):
    print(f"Downloading yolov3.weights (~237MB)...")
    downloaded = False
    for weights_url in weights_sources:
        if download_file(weights_url, weights_path):
            downloaded = True
            break
    if not downloaded:
        print("⚠ Could not download weights from any source.")
        print("  Please download manually from: https://pjreddie.com/media/files/yolov3.weights")
        print("  and save to: models/yolov3.weights")
else:
    print("✓ yolov3.weights already exists")

if not os.path.exists(cfg_path):
    print("Downloading yolov3.cfg...")
    if download_file(cfg_url, cfg_path):
        pass
    else:
        print("⚠ Could not download config file")
else:
    print("✓ yolov3.cfg already exists")

if not os.path.exists(names_path):
    print("Downloading coco.names...")
    if download_file(names_url, names_path):
        pass
    else:
        print("⚠ Could not download names file")
else:
    print("✓ coco.names already exists")

print("\n" + "="*50)
if os.path.exists(weights_path) and os.path.exists(cfg_path) and os.path.exists(names_path):
    print("✓ All files ready! You can now run: python app.py")
else:
    print("⚠ Some files are missing. Please check the errors above.")
    print("  You can still run the app with CASCADE detection mode as fallback.")

