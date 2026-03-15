import os
import re

def fix_html_files(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 1. Replace index.html links with /
                # Matches index.html, ../index.html, ../../index.html, etc.
                # But only in href attributes
                content = re.sub(r'href="(\.\./)*index\.html(#\w+)?"', r'href="/\2"', content)
                
                # 2. Add or update canonical tag
                # Determine the canonical URL
                rel_path = os.path.relpath(file_path, root_dir).replace('\\', '/')
                if rel_path == "index.html":
                    canonical_url = "https://pdfjin.com/"
                else:
                    canonical_url = f"https://pdfjin.com/{rel_path}"
                
                canonical_tag = f'<link rel="canonical" href="{canonical_url}" />'
                
                # Check if canonical already exists
                if '<link rel="canonical"' in content:
                    # Update existing canonical (if any)
                    content = re.sub(r'<link rel="canonical" href="[^"]+" />', canonical_tag, content)
                else:
                    # Insert before </head>
                    content = content.replace('</head>', f'  {canonical_tag}\n</head>')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

if __name__ == "__main__":
    frontend_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend"
    fix_html_files(frontend_dir)
