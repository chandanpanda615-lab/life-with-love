import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

VID_DIR = r"Village_Image\images\WhatsApp Business Video"
RAW_OUT_DIR = r"Village_Image\video_extractions"
HIGH_RES_DIR = r"Village_Image\highlights"
ASSETS_PHOTOS_DIR = r"assets\photos"

os.makedirs(RAW_OUT_DIR, exist_ok=True)
os.makedirs(HIGH_RES_DIR, exist_ok=True)
os.makedirs(ASSETS_PHOTOS_DIR, exist_ok=True)

def score_frame(frame):
    """
    Multi-metric frame quality score:
    - Laplacian variance (sharpness)
    - Sobel gradient magnitude (edge detail)
    - Contrast (std dev of grayscale intensity)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Ignore dark/underexposed frames
    mean_brightness = np.mean(gray)
    if mean_brightness < 35 or mean_brightness > 235:
        return 0.0
    
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    contrast = np.std(gray)
    
    # Sobel edge density
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edge_density = np.mean(np.sqrt(sobelx**2 + sobely**2))
    
    # Combined score
    score = (laplacian_var * 0.5) + (contrast * 1.5) + (edge_density * 2.0)
    return score

def super_enhance_frame(bgr_frame, scale_factor=2.0):
    """
    Advanced Multi-Stage Image Enhancement Pipeline:
    1. OpenCV detail enhancement (boost fine textures without adding noise)
    2. Denoise with FastNLM
    3. High-quality Lanczos resampling
    4. Fine-tuned unsharp mask
    5. Natural color & contrast tuning
    """
    # Step 1: Detail enhancement in OpenCV
    detailed = cv2.detailEnhance(bgr_frame, sigma_s=10, sigma_r=0.15)
    
    # Step 2: Convert to RGB
    rgb = cv2.cvtColor(detailed, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    
    # Step 3: High precision upscale using Lanczos
    new_w = int(pil_img.width * scale_factor)
    new_h = int(pil_img.height * scale_factor)
    upscaled = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Step 4: Multi-stage Unsharp Mask
    # Stage 1: Fine detail sharpening
    sharpened1 = upscaled.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=2))
    # Stage 2: Broad edge definition
    sharpened2 = sharpened1.filter(ImageFilter.UnsharpMask(radius=2.5, percent=60, threshold=4))
    
    # Step 5: Color & Contrast Adjustment
    contrast_enhancer = ImageEnhance.Contrast(sharpened2)
    contrast_adjusted = contrast_enhancer.enhance(1.08)
    
    color_enhancer = ImageEnhance.Color(contrast_adjusted)
    final_img = color_enhancer.enhance(1.05)
    
    return final_img

def extract_all_video_gems():
    if not os.path.exists(VID_DIR):
        print(f"Error: {VID_DIR} not found.")
        return
    
    video_files = [f for f in sorted(os.listdir(VID_DIR)) if f.endswith('.mp4')]
    print(f"Found {len(video_files)} video files in {VID_DIR}\n")
    
    extracted_candidates = []
    
    for vid_file in video_files:
        vid_path = os.path.join(VID_DIR, vid_file)
        cap = cv2.VideoCapture(vid_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Scan every 3rd frame for exhaustive search
        frame_scores = []
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % 3 == 0:
                score = score_frame(frame)
                frame_scores.append((frame_idx, score, frame.copy()))
            
            frame_idx += 1
            
        cap.release()
        
        # Sort by score descending
        frame_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Pick the top 2 sharpest, non-duplicate frames (separated by at least 1 sec)
        top_frames = []
        min_frame_gap = int(fps * 1.5)
        
        for f_idx, score, f_mat in frame_scores:
            if not top_frames:
                top_frames.append((f_idx, score, f_mat))
            else:
                if all(abs(f_idx - existing[0]) >= min_frame_gap for existing in top_frames):
                    top_frames.append((f_idx, score, f_mat))
            if len(top_frames) >= 2:
                break
                
        for rank, (f_idx, score, f_mat) in enumerate(top_frames, start=1):
            time_sec = f_idx / fps
            raw_filename = f"{vid_file[:-4]}_frame_{f_idx}_t{time_sec:.1f}s.jpg"
            raw_path = os.path.join(RAW_OUT_DIR, raw_filename)
            
            # Save raw extracted frame
            cv2.imwrite(raw_path, f_mat)
            
            h, w = f_mat.shape[:2]
            aspect = w / float(h)
            
            extracted_candidates.append({
                'video': vid_file,
                'frame_idx': f_idx,
                'time_sec': time_sec,
                'score': score,
                'raw_path': raw_path,
                'bgr_mat': f_mat,
                'width': w,
                'height': h,
                'aspect': aspect,
                'is_landscape': aspect >= 1.2
            })
            
            print(f"[{vid_file}] Selected Frame #{f_idx} (t={time_sec:.1f}s): {w}x{h}, Quality Score={score:.1f}")

    print(f"\nExtracted total of {len(extracted_candidates)} top candidate frames from {len(video_files)} videos!")
    
    # Sort all extracted frames across ALL videos by quality score
    extracted_candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Pick top 12 landscape frames + top 6 portrait frames
    landscapes = [c for c in extracted_candidates if c['is_landscape']]
    portraits = [c for c in extracted_candidates if not c['is_landscape']]
    
    print(f"Available extracted landscape frames: {len(landscapes)}, portrait frames: {len(portraits)}")
    
    top_selection = landscapes[:10] + portraits[:5]
    top_selection.sort(key=lambda x: x['score'], reverse=True)
    
    # Process and apply super-enhancement
    manifest_rows = ["filename,video_source,timestamp,width,height,quality_score,hero_candidate"]
    
    print("\n--- Applying Super Enhancement Pipeline ---")
    for idx, item in enumerate(top_selection, start=1):
        # Scale 2.2x for maximum crispness
        scale = 2.2 if item['is_landscape'] else 1.8
        enhanced_pil = super_enhance_frame(item['bgr_mat'], scale_factor=scale)
        
        out_name = f"video_highlight_{idx:02d}.jpg"
        out_path = os.path.join(HIGH_RES_DIR, out_name)
        asset_path = os.path.join(ASSETS_PHOTOS_DIR, out_name)
        
        enhanced_pil.save(out_path, format="JPEG", quality=95, optimize=True)
        enhanced_pil.save(asset_path, format="JPEG", quality=95, optimize=True)
        
        is_hero = "Yes" if idx in [1, 2, 3] and item['is_landscape'] else "No"
        manifest_rows.append(f"{out_name},{item['video']},{item['time_sec']:.1f}s,{enhanced_pil.width},{enhanced_pil.height},{item['score']:.1f},{is_hero}")
        
        print(f"Saved {out_name}: {enhanced_pil.width}x{enhanced_pil.height} (from {item['video']} @ {item['time_sec']:.1f}s, score={item['score']:.1f})")
    
    # Overwrite assets/hero.jpg with the #1 highest-scoring landscape video frame
    if landscapes:
        best_hero_item = landscapes[0]
        hero_enhanced = super_enhance_frame(best_hero_item['bgr_mat'], scale_factor=2.4)
        hero_target_path = os.path.join("assets", "hero.jpg")
        hero_enhanced.save(hero_target_path, format="JPEG", quality=95, optimize=True)
        print(f"\n[HERO OVERWRITE] Updated assets/hero.jpg with pristine frame from {best_hero_item['video']} @ {best_hero_item['time_sec']:.1f}s ({hero_enhanced.width}x{hero_enhanced.height})")
    
    manifest_file = os.path.join(HIGH_RES_DIR, "video_manifest.csv")
    with open(manifest_file, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_rows))
    print(f"Saved video manifest to {manifest_file}")

if __name__ == "__main__":
    extract_all_video_gems()
