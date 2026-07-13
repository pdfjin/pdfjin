import os
import re
import hashlib

BLOG_DIR = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog'
ASSETS_DIR = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\assets\blog'

def get_base_images():
    images = []
    for f in os.listdir(ASSETS_DIR):
        if f.endswith('.png') or f.endswith('.jpg'):
            images.append(f)
    return sorted(images)

def apply_assets_hero():
    images = get_base_images()
    if not images:
        print("No images found in assets/blog")
        return
        
    for f in os.listdir(BLOG_DIR):
        if not f.endswith('.html'):
            continue
            
        path = os.path.join(BLOG_DIR, f)
        
        # Deterministic selection based on filename hash
        file_hash = int(hashlib.md5(f.encode('utf-8')).hexdigest(), 16)
        selected_image = images[file_hash % len(images)]
        
        local_url = f"/assets/blog/{selected_image}"
        abs_img_url = f"https://pdfjin.com{local_url}"
        
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Replace ld+json image
        # Match "image": "..."
        content = re.sub(r'"image":\s*"[^"]+"', f'"image": "{abs_img_url}"', content)
        
        # Replace hero image tag
        # Match <div class="blog-pos-hero-image"> ... <img src="...">
        content = re.sub(r'(<div class="blog-pos-hero-image">\s*<img src=")[^"]+(")', rf'\g<1>{local_url}\g<2>', content)
        
        # Replace open graph images
        content = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="{abs_img_url}"', content)
        content = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="{abs_img_url}"', content)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f'Fixed {f} using {selected_image}')

if __name__ == "__main__":
    apply_assets_hero()
