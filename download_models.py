import os
import urllib.request
from pathlib import Path

def download_file(url, target_path):
    print(f"Downloading {url} to {target_path}...")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, target_path)
    print(f"✅ Downloaded {target_path.name}")

def main():
    # RTMDet-Tiny (MMDet 3.x)
    CONFIG_URL = "https://raw.githubusercontent.com/open-mmlab/mmdetection/main/configs/rtmdet/rtmdet_tiny_8xb32-300e_coco.py"
    CHECKPOINT_URL = "https://download.openmmlab.com/mmdetection/v3.0/rtmdet/rtmdet_tiny_8xb32-300e_coco/rtmdet_tiny_8xb32-300e_coco_20220902_112414-78e30dcc.pth"
    
    config_path = Path("configs/rtmdet_tiny_8xb32-300e_coco.py")
    checkpoint_path = Path("checkpoints/rtmdet_tiny_8xb32-300e_coco.pth")
    
    if not config_path.exists():
        download_file(CONFIG_URL, config_path)
    else:
        print(f"✅ Config already exists: {config_path}")
        
    if not checkpoint_path.exists():
        download_file(CHECKPOINT_URL, checkpoint_path)
    else:
        print(f"✅ Checkpoint already exists: {checkpoint_path}")

if __name__ == "__main__":
    main()
