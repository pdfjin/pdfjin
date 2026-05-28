import os
import glob

pages_dir = 'c:/Users/ADMIN/Desktop/pdfjin/backend/static_frontend/pages'
old_text = 'const targetApi = "https://pdfjin-api-97530578628.us-central1.run.app";'
new_text = 'const targetApi = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") ? "http://localhost:8080" : "https://pdfjin-api-97530578628.us-central1.run.app";'

count = 0
for filepath in glob.glob(os.path.join(pages_dir, '**', '*.html'), recursive=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if old_text in content:
        new_content = content.replace(old_text, new_text)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count += 1
print(f'Fixed {count} files')
