import os
import re

def update_links():
    frontend_dir = 'frontend'
    # Pattern for HTML hrefs: href="pages/filename.html"
    html_pattern = re.compile(r'href="pages/([^"]+)\.html"')
    # Pattern for JS redirects: window.location.href = 'pages/filename.html'
    js_pattern = re.compile(r"location\.href\s*=\s*'pages/([^']+)\.html'")
    
    for root, dirs, files in os.walk(frontend_dir):
        for file in files:
            if file.endswith('.html') or file.endswith('.js'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = html_pattern.sub(r'href="pages/\1"', content)
                    new_content = js_pattern.sub(r"location.href = 'pages/\1'", new_content)
                    
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    update_links()
