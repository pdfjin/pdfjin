import os
import re
import hashlib
import shutil

# The generated images paths
brain_dir = r"C:\Users\ADMIN\.gemini\antigravity\brain\7e3a4cc9-9f36-4c4d-9be4-6999a2dbefad"
hero_images = []
for f in os.listdir(brain_dir):
    if f.startswith("blog_hero_") and f.endswith(".png"):
        hero_images.append(os.path.join(brain_dir, f))

hero_images.sort()

# Target directories
blog_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
assets_hero_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\assets\blog\hero"

os.makedirs(assets_hero_dir, exist_ok=True)

# Copy the images to the assets directory
copied_images = []
for i, src in enumerate(hero_images):
    dest_name = f"hero_{i+1}.png"
    dest_path = os.path.join(assets_hero_dir, dest_name)
    shutil.copy(src, dest_path)
    copied_images.append(f"../../assets/blog/hero/{dest_name}")
    print(f"Copied {src} to {dest_path}")

print(f"Copied {len(copied_images)} hero images.")

if not copied_images:
    print("No hero images found to copy!")
    exit(1)

# Now iterate over all blog posts
for f in os.listdir(blog_dir):
    if not f.endswith(".html"):
        continue
    
    filepath = os.path.join(blog_dir, f)
    
    # Deterministic selection
    file_hash = int(hashlib.md5(f.encode('utf-8')).hexdigest(), 16)
    selected_image = copied_images[file_hash % len(copied_images)]
    
    # Absolute URL for meta tags
    # Assuming domain is https://pdfjin.com
    absolute_image_url = selected_image.replace("../../", "https://pdfjin.com/")
    
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
        
    # Replace ld+json image
    content = re.sub(r'"image":\s*"https://image\.pollinations\.ai[^"]+"', f'"image": "{absolute_image_url}"', content)
    
    # Replace hero image tag
    content = re.sub(r'(<div class="blog-pos-hero-image">\s*<img src=")[^"]+(")', rf'\g<1>{selected_image}\g<2>', content)
    
    # Replace open graph images
    content = re.sub(r'<meta property="og:image" content="https://image\.pollinations\.ai[^"]+"', f'<meta property="og:image" content="{absolute_image_url}"', content)
    content = re.sub(r'<meta name="twitter:image" content="https://image\.pollinations\.ai[^"]+"', f'<meta name="twitter:image" content="{absolute_image_url}"', content)
    
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)
        
print("Successfully updated all blog posts to use local hero images.")
