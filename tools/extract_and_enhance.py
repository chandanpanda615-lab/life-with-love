import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

IMG_DIR = r"Village_Image\images\WhatsApp Business Images"
VID_DIR = r"Village_Image\images\WhatsApp Business Video"
OUT_DIR = r"Village_Image\highlights"
ASSETS_DIR = r"assets"
PHOTOS_ASSET_DIR = r"assets\photos"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PHOTOS_ASSET_DIR, exist_ok=True)

def calculate_sharpness(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def enhance_image(pil_img, target_width=1920, target_height=None):
    # Determine aspect ratio and target dimensions
    w, h = pil_img.size
    if target_height is None:
        target_height = int(h * (target_width / float(w)))
    
    # Upscale / downscale using high quality Lanczos resampling
    resized = pil_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Apply subtle unsharp mask for clarity
    sharpened = resized.filter(ImageFilter.UnsharpMask(radius=1.5, percent=110, threshold=3))
    
    # Subtle contrast enhancement (1.05x)
    enhancer = ImageEnhance.Contrast(sharpened)
    enhanced = enhancer.enhance(1.05)
    
    # Color tone enhancement (1.03x)
    color_enhancer = ImageEnhance.Color(enhanced)
    final_img = color_enhancer.enhance(1.03)
    
    return final_img

def process_videos():
    extracted_frames = []
    if not os.path.exists(VID_DIR):
        return extracted_frames
    
    print("Processing videos...")
    for vid_file in sorted(os.listdir(VID_DIR)):
        if not vid_file.endswith('.mp4'):
            continue
        
        vid_path = os.path.join(VID_DIR, vid_file)
        cap = cv2.VideoCapture(vid_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample every ~1 second
        sample_interval = int(fps)
        best_frame = None
        best_score = -1.0
        best_time_sec = 0.0
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % sample_interval == 0:
                score = calculate_sharpness(frame)
                # Ensure frame is not too dark or all black
                mean_val = np.mean(frame)
                if mean_val > 25 and score > best_score:
                    best_score = score
                    best_frame = frame.copy()
                    best_time_sec = frame_idx / fps
            frame_idx += 1
            
        cap.release()
        
        if best_frame is not None:
            # Convert BGR (OpenCV) to RGB (Pillow)
            rgb_frame = cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            extracted_frames.append({
                'source': vid_file,
                'img': pil_img,
                'score': best_score,
                'aspect': pil_img.width / float(pil_img.height),
                'type': 'video_frame',
                'time_sec': best_time_sec
            })
            print(f"Extracted best frame from {vid_file}: {pil_img.width}x{pil_img.height}, sharpness score={best_score:.1f}")
            
    return extracted_frames

def process_photos():
    photos = []
    if not os.path.exists(IMG_DIR):
        return photos
    
    print("Processing raw photos...")
    for img_file in sorted(os.listdir(IMG_DIR)):
        if not (img_file.endswith('.jpg') or img_file.endswith('.png')):
            continue
        
        img_path = os.path.join(IMG_DIR, img_file)
        try:
            with Image.open(img_path) as im:
                im_rgb = im.convert('RGB')
                # Calculate sharpness on numpy array
                arr = np.array(im_rgb)
                gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
                score = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                photos.append({
                    'source': img_file,
                    'img': im_rgb.copy(),
                    'score': score,
                    'aspect': im_rgb.width / float(im_rgb.height),
                    'type': 'photo'
                })
                print(f"Loaded photo {img_file}: {im_rgb.width}x{im_rgb.height}, sharpness score={score:.1f}")
        except Exception as e:
            print(f"Error loading {img_file}: {e}")
            
    return photos

def main():
    photos = process_photos()
    video_frames = process_videos()
    
    all_media = photos + video_frames
    print(f"\nTotal media candidates: {len(all_media)}")
    
    # Sort candidates by sharpness score descending
    all_media.sort(key=lambda x: x['score'], reverse=True)
    
    # Separate horizontal (landscape) vs vertical (portrait)
    landscapes = [m for m in all_media if m['aspect'] >= 1.2]
    portraits = [m for m in all_media if m['aspect'] < 1.2]
    
    print(f"Landscapes: {len(landscapes)}, Portraits: {len(portraits)}")
    
    # Pick top 10 landscape and top 5 portrait to make top 15 highlights
    curated = landscapes[:10] + portraits[:5]
    
    manifest_rows = ["filename,source_type,original_source,width,height,description,hero_candidate"]
    
    # Process and save curated images
    for idx, item in enumerate(curated, start=1):
        is_landscape = item['aspect'] >= 1.2
        target_w = 1920 if is_landscape else 1080
        
        enhanced_pil = enhance_image(item['img'], target_width=target_w)
        out_name = f"highlight_{idx:02d}.jpg"
        out_path = os.path.join(OUT_DIR, out_name)
        
        # Save without EXIF data
        enhanced_pil.save(out_path, format="JPEG", quality=90, optimize=True)
        
        # Also copy to assets/photos for site inclusion
        asset_path = os.path.join(PHOTOS_ASSET_DIR, out_name)
        enhanced_pil.save(asset_path, format="JPEG", quality=90, optimize=True)
        
        is_hero_candidate = "Yes" if idx in [1, 2, 3] and is_landscape else "No"
        desc = f"Landscape view of Sarangada from {item['source']}" if is_landscape else f"Village life frame from {item['source']}"
        manifest_rows.append(f"{out_name},{item['type']},{item['source']},{enhanced_pil.width},{enhanced_pil.height},\"{desc}\",{is_hero_candidate}")
        
        print(f"Saved {out_name} ({enhanced_pil.width}x{enhanced_pil.height}) [from {item['source']}]")
    
    # Save manifest.csv
    manifest_path = os.path.join(OUT_DIR, "manifest.csv")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_rows))
    print(f"\nSaved manifest to {manifest_path}")
    
    # Select the #1 landscape as Hero image and overwrite assets/hero.jpg
    if landscapes:
        best_hero = landscapes[0]
        # Crop 16:9 / 4:3 optimal hero section from the best landscape image
        hero_img = enhance_image(best_hero['img'], target_width=1920)
        hero_path = os.path.join(ASSETS_DIR, "hero.jpg")
        hero_img.save(hero_path, format="JPEG", quality=92, optimize=True)
        print(f"\n[HERO UPDATE] Overwrote assets/hero.jpg with top candidate from {best_hero['source']} ({hero_img.width}x{hero_img.height})")

if __name__ == "__main__":
    main()
