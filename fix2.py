import os
import glob
import re

dirs = ['c:/Users/ADMIN/Desktop/pdfjin/frontend/pages/*.html', 'c:/Users/ADMIN/Desktop/pdfjin/backend/static_frontend/pages/*.html']
count = 0
for d in dirs:
    for f in glob.glob(d):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        new_content = re.sub(
            r'(<div class="faq-preview-section section-inner" id="faq-preview-accordion"[^>]*>\s*)<div class="section-header reveal">',
            r'\1<div class="section-header">',
            content
        )
        if new_content != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            count += 1

print(f"Fix applied to {count} files")
