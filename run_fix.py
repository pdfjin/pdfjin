import glob
import os

files1 = glob.glob('frontend/pages/blog/*.html')
files2 = glob.glob('backend/static_frontend/pages/blog/*.html')
for f in files1 + files2:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if '\\"' in content:
        content = content.replace('\\"', '"')
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print('Fixed', f)
