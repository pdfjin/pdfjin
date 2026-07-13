import os
import re
import urllib.parse
import random

BLOG_DIR = r'frontend/pages/blog'

def generate_image(topic, slug):
    prompt = f'A professional, modern blog post cover image about {topic}. Flat design, highly relevant, clean, wide landscape.'
    seed = random.randint(1, 10000000)
    url = f'https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1280&height=720&nologo=true&seed={seed}'
    return url

for f in os.listdir(BLOG_DIR):
    if f.endswith('.html'):
        path = os.path.join(BLOG_DIR, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract title from headline
        m = re.search(r'"headline":\s*"([^"]+)"', content)
        if m:
            topic = m.group(1)
        else:
            m = re.search(r'<meta property="og:title" content="([^"]+) \| PDFjin"', content)
            if m:
                topic = m.group(1)
            else:
                continue # Skip if no topic found
                
        image_url = generate_image(topic, f)
        
        # Replace ld+json image
        content = re.sub(r'"image":\s*"[^"]+"', f'"image": "{image_url}"', content)
        
        # Replace hero image
        content = re.sub(r'(<div class="blog-pos-hero-image">\s*<img src=")[^"]+(")', rf'\g<1>{image_url}\g<2>', content)
        
        # Replace open graph images
        content = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="{image_url}"', content)
        content = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="{image_url}"', content)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f'Fixed {f}')
