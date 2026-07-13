import os
import re

blog_dir = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog'
images = {}
for filename in os.listdir(blog_dir):
    if not filename.endswith('.html'): continue
    with open(os.path.join(blog_dir, filename), 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'<div class="blog-pos-hero-image">\s*<img src="(.*?)"', content)
    if match:
        img_url = match.group(1)
        if img_url in images:
            images[img_url].append(filename)
        else:
            images[img_url] = [filename]

duplicates = {k: v for k, v in images.items() if len(v) > 1}
if duplicates:
    print('Duplicates found:')
    for k, v in duplicates.items():
        print(f'{k}: {v}')
else:
    print('No duplicate hero images found.')
