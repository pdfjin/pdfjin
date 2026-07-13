import os
import re

BLOG_DIR = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog'
HERO_DIR = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\assets\blog\hero'

def apply_local_hero():
    for f in os.listdir(BLOG_DIR):
        if not f.endswith('.html'):
            continue
            
        path = os.path.join(BLOG_DIR, f)
        
        # Check if the specific hero image exists
        image_filename = "hero_" + f.replace('.html', '.png')
        image_path = os.path.join(HERO_DIR, image_filename)
        
        if not os.path.exists(image_path):
            print(f"Warning: Hero image {image_filename} not found for {f}. Falling back to a default.")
            image_filename = "hero_1.png" # Fallback if specific one is missing
        
        local_url = f"/assets/blog/hero/{image_filename}"
        abs_img_url = f"https://pdfjin.com{local_url}"
        
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Replace ld+json image
        content = re.sub(r'"image":\s*"[^"]+"', f'"image": "{abs_img_url}"', content)
        
        # Replace hero image tag
        content = re.sub(r'(<div class="blog-pos-hero-image">\s*<img src=")[^"]+(")', rf'\g<1>{local_url}\g<2>', content)
        
        # Replace open graph images
        content = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="{abs_img_url}"', content)
        content = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="{abs_img_url}"', content)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f'Fixed {f} using {image_filename}')

if __name__ == "__main__":
    apply_local_hero()
