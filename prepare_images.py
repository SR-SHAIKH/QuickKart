import os
import glob
from PIL import Image

def process_image(pattern, output_name):
    artifacts_dir = r"C:\Users\shaik\.gemini\antigravity\brain\4c3455c6-e3a7-428a-8ecb-7ade8a30ecbb"
    output_dir = r"c:\Users\shaik\OneDrive\Desktop\QuickKart-main\QuickKart-main\static\images\products"
    os.makedirs(output_dir, exist_ok=True)
    
    files = glob.glob(os.path.join(artifacts_dir, pattern))
    if not files:
        print(f"No file found for {pattern}")
        return
        
    latest_file = max(files, key=os.path.getctime)
    print(f"Processing {latest_file} -> {output_name}")
    
    try:
        img = Image.open(latest_file)
        # Convert to RGB if necessary
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Resize to a reasonable e-commerce size (e.g. 500x500 max) to compress size
        img.thumbnail((500, 500), Image.Resampling.LANCZOS)
        
        output_path = os.path.join(output_dir, output_name)
        img.save(output_path, "JPEG", quality=85, optimize=True)
        print(f"Saved {output_path}")
    except Exception as e:
        print(f"Failed to process {latest_file}: {e}")

if __name__ == "__main__":
    process_image("*banana*.png", "banana.jpg")
    process_image("*milk*.png", "milk.jpg")
    process_image("*chips*.png", "chips.jpg")
    process_image("*coke*.png", "coke.jpg")
    process_image("*bread*.png", "bread.jpg")
    process_image("*eggs*.png", "eggs.jpg")
