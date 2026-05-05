import os
import csv
import time
from pathlib import Path
from google import genai
from google.genai import types

# ============ CONFIGURATION ============
API_KEY = os.environ.get("GEMINI_API_KEY")
PHOTO_FOLDER = os.environ.get(
    "MAATI_PHOTO_FOLDER",
    r"C:\Users\chandan.p\Pictures\Village_Image\Photoes_Gallery",
)  # change this, or set MAATI_PHOTO_FOLDER
OUTPUT_FOLDER = os.environ.get(
    "MAATI_OUTPUT_FOLDER",
    PHOTO_FOLDER,
)  # same folder is fine, or set MAATI_OUTPUT_FOLDER
MODEL_NAME = "gemini-2.5-pro"
# =======================================

PROMPT = """You are documenting a village in Kandhamal district, Odisha, India for a rural-immersion travel project called Maati Katha. The village is Sarangada — a mixed community of Kondh tribal families, Brahmins, Kshatriyas, other tribes, and converted Christians. The terrain is Eastern Ghats foothills with red lateritic soil, deep clay earth, and turmeric agriculture. The village runs east-west along a 1km market spine; sunrise faces the fields, sunset faces the jungle.

For this photograph, write a 4-paragraph description with this exact structure:

PARAGRAPH 1 — Physical content: What is literally in the frame. Structures, people (described by what they wear or are doing, never by name), animals, vegetation, objects. Be specific. If you see a chulha, say chulha. If you see ragi or paddy, say so only if you are confident; otherwise say "a grain crop."

PARAGRAPH 2 — Light and time: Quality of light, likely time of day, weather, season cues if visible.

PARAGRAPH 3 — Material and cultural texture: Details a foreign visitor would notice but might not understand — building materials (mud walls, tiled roof, thatched roof), tools, fabrics, colors, the relationship between built and natural environment. Be observational, not interpretive.

PARAGRAPH 4 — Mood and editorial note: What feeling the image carries. Avoid travel-brochure language ("vibrant," "exotic," "unspoiled"). Avoid romanticizing poverty. If the image is ordinary, call it ordinary. If something feels staged, say so.

Be specific. Be honest. Do not invent details you cannot see. If you are uncertain about something, name the uncertainty."""


def describe_photos():
    if not API_KEY:
        raise RuntimeError(
            "Missing GEMINI_API_KEY. Set it in your environment before running this script."
        )

    client = genai.Client(api_key=API_KEY)
    
    photo_path = Path(PHOTO_FOLDER)
    output_path = Path(OUTPUT_FOLDER)
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
    photos = sorted([
        p for p in photo_path.iterdir() 
        if p.suffix.lower() in image_extensions
    ])
    
    if not photos:
        print(f"No images found in {PHOTO_FOLDER}")
        return
    
    print(f"Found {len(photos)} images. Starting...\n")
    
    results = []
    
    for i, photo in enumerate(photos, 1):
        print(f"[{i}/{len(photos)}] Processing: {photo.name}")
        
        try:
            with open(photo, 'rb') as f:
                image_bytes = f.read()
            
            mime_type = f"image/{photo.suffix.lower().replace('.', '').replace('jpg', 'jpeg')}"
            
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    PROMPT
                ]
            )
            
            description = response.text
            results.append({
                "filename": photo.name,
                "description": description
            })
            print(f"  Done. ({len(description)} chars)\n")
            
            # Polite pause to avoid rate limits
            time.sleep(2)
            
        except Exception as e:
            print(f"  ERROR on {photo.name}: {e}\n")
            results.append({
                "filename": photo.name,
                "description": f"[ERROR: {str(e)}]"
            })
    
    # Write CSV
    csv_file = output_path / "sarangada_photo_descriptions.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "description"])
        writer.writeheader()
        writer.writerows(results)
    
    # Write Markdown
    md_file = output_path / "sarangada_photo_descriptions.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Sarangada Photo Descriptions\n\n")
        f.write(f"Generated using {MODEL_NAME}. Total: {len(results)} images.\n\n")
        f.write("---\n\n")
        for r in results:
            f.write(f"## {r['filename']}\n\n")
            f.write(f"{r['description']}\n\n")
            f.write("---\n\n")
    
    print(f"\nDone. Results saved to:")
    print(f"  {csv_file}")
    print(f"  {md_file}")


if __name__ == "__main__":
    describe_photos()
