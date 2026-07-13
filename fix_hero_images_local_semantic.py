import os
import re

BLOG_DIR = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog'

# Define our local assets
BASE_URL = "https://pdfjin.com/"
ASSET_PATH_PREFIX = "../../assets/blog/"
ABS_ASSET_PREFIX = "https://pdfjin.com/assets/blog/"

semantic_map = {
    'audio': 'ai-audio-overview-podcast.png',
    'podcast': 'ai-audio-overview-podcast.png',
    'voice': 'ai-audio-overview-podcast.png',
    
    'compress': 'blog-reduce.png',
    'shrink': 'blog-reduce.png',
    'reduce': 'blog-reduce.png',
    'size': 'blog-reduce.png',
    
    'excel': 'blog-excel.png',
    'spreadsheet': 'blog-excel.png',
    'csv': 'blog-excel.png',
    'financial': 'blog-excel.png',
    'bank': 'blog-excel.png',
    'invoice': 'blog-excel.png',
    
    'merge': 'blog-merge.png',
    'combine': 'blog-merge.png',
    
    'word': 'blog-pdf-word.png',
    'textbook': 'blog-pdf-word.png',
    'docx': 'blog-pdf-word.png',
    'literature': 'blog-pdf-word.png',
    'academic': 'blog-pdf-word.png',
    
    'sign': 'blog-sign.png',
    'contract': 'blog-sign.png',
    'legal': 'blog-sign.png',
    'lease': 'blog-sign.png',
    'agreement': 'blog-sign.png',
    
    'edit': 'blog-edit.png',
    'format': 'blog-edit.png',
    'ocr': 'blog-edit.png',
    'redact': 'blog-edit.png',
    'extract': 'blog-edit.png',
    
    'medical': 'hero/hero_2.png',
    'health': 'hero/hero_2.png',
    
    'engineering': 'hero/hero_3.png',
    'chart': 'hero/hero_3.png',
    
    'security': 'hero/hero_4.png',
    'privacy': 'hero/hero_4.png',
    'safe': 'hero/hero_4.png',
    
    'hr': 'hero/hero_5.png',
    'resume': 'hero/hero_5.png',
    'employee': 'hero/hero_5.png',
    
    'translate': 'hero/hero_1.png',
    'language': 'hero/hero_1.png'
}

fallbacks = ['hero/hero_1.png', 'hero/hero_2.png', 'hero/hero_3.png', 'hero/hero_4.png', 'hero/hero_5.png', 'blog-edit.png', 'blog-pdf-word.png']

for f in os.listdir(BLOG_DIR):
    if f.endswith('.html'):
        path = os.path.join(BLOG_DIR, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract title from headline
        m = re.search(r'"headline":\s*"([^"]+)"', content)
        if m:
            topic = m.group(1).lower()
        else:
            m = re.search(r'<meta property="og:title" content="([^"]+) \| PDFjin"', content)
            if m:
                topic = m.group(1).lower()
            else:
                topic = f.replace('-', ' ').lower()
                
        # Find best image using whole word boundary matching
        selected_img = None
        for key, img in semantic_map.items():
            if re.search(rf'\b{key}\b', topic):
                selected_img = img
                break
                
        if not selected_img:
            # Deterministic fallback based on hash
            selected_img = fallbacks[abs(hash(f)) % len(fallbacks)]
            
        rel_img = ASSET_PATH_PREFIX + selected_img
        abs_img = ABS_ASSET_PREFIX + selected_img
        
        # Replace ld+json image
        content = re.sub(r'"image":\s*"[^"]+"', f'"image": "{abs_img}"', content)
        
        # Replace hero image tag
        content = re.sub(r'(<div class="blog-pos-hero-image">\s*<img src=")[^"]+(")', rf'\g<1>{rel_img}\g<2>', content)
        
        # Replace open graph images
        content = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="{abs_img}"', content)
        content = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="{abs_img}"', content)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f'Fixed {f} with image: {selected_img}')
