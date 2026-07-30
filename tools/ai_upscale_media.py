import os
import subprocess
from PIL import Image

RE_BIN = r"tools\realesrgan\realesrgan-ncnn-vulkan.exe"
RE_MODELS = r"tools\realesrgan\models"
RAW_EXTRACTIONS = r"Village_Image\video_extractions"
HIGHLIGHTS_DIR = r"Village_Image\highlights"
ASSETS_PHOTOS_DIR = r"assets\photos"
HERO_TARGET = r"assets\hero.jpg"

os.makedirs(HIGHLIGHTS_DIR, exist_ok=True)
os.makedirs(ASSETS_PHOTOS_DIR, exist_ok=True)

def upscale_with_realesrgan(input_path, output_path, scale=4, model_name="realesrgan-x4plus"):
    """
    Run 4x Real-ESRGAN AI deep learning upscaler using Vulkan GPU/CPU acceleration.
    """
    cmd = [
        RE_BIN,
        "-i", input_path,
        "-o", output_path,
        "-s", str(scale),
        "-m", RE_MODELS,
        "-n", model_name,
        "-f", "jpg"
    ]
    print(f"[Real-ESRGAN] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"-> Successfully upscaled {os.path.basename(input_path)} to {output_path}")
        return True
    else:
        print(f"Error upscaling {input_path}: {result.stderr}")
        return False

def main():
    if not os.path.exists(RAW_EXTRACTIONS):
        print(f"Error: {RAW_EXTRACTIONS} directory not found.")
        return

    raw_files = [f for f in sorted(os.listdir(RAW_EXTRACTIONS)) if f.endswith('.jpg')]
    print(f"Found {len(raw_files)} raw video extractions to AI-upscale.")

    # Process all raw video extractions with 4x Real-ESRGAN
    ai_upscaled_files = []
    
    for idx, f in enumerate(raw_files, start=1):
        in_file = os.path.join(RAW_EXTRACTIONS, f)
        out_name = f"ai_video_highlight_{idx:02d}.jpg"
        out_path = os.path.join(HIGHLIGHTS_DIR, out_name)
        
        success = upscale_with_realesrgan(in_file, out_path, scale=4, model_name="realesrgan-x4plus")
        if success and os.path.exists(out_path):
            with Image.open(out_path) as im:
                w, h = im.size
                print(f"Real-ESRGAN Output #{idx}: {out_name} -> {w}x{h} resolution!")
                # Copy to assets/photos/
                asset_copy = os.path.join(ASSETS_PHOTOS_DIR, out_name)
                im.save(asset_copy, format="JPEG", quality=95, optimize=True)
                
                ai_upscaled_files.append({
                    'filename': out_name,
                    'path': out_path,
                    'width': w,
                    'height': h,
                    'aspect': w / float(h),
                    'is_landscape': (w / float(h)) >= 1.2
                })

    # Pick the sharpest 4x AI-upscaled landscape image for Hero
    landscapes = [img for img in ai_upscaled_files if img['is_landscape']]
    if landscapes:
        best_hero = landscapes[0]
        with Image.open(best_hero['path']) as im:
            im.save(HERO_TARGET, format="JPEG", quality=95, optimize=True)
            print(f"\n[AI HERO UPGRADE] Overwrote assets/hero.jpg with 4x Real-ESRGAN enhanced image ({im.width}x{im.height})!")

if __name__ == "__main__":
    main()
