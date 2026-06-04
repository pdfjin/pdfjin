import os
import re
from pathlib import Path

def add_html_extensions(root_dir):
    root_path = Path(root_dir)
    html_files = list(root_path.rglob('*.html'))
    
    # Matches href="pages/something" or href="pages/something#anchor" 
    # but only if "something" doesn't have a dot (so we don't change .html again)
    pattern = re.compile(r'href="(pages/[a-zA-Z0-9_-]+)(#.*?)?"')
    
    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = pattern.sub(r'href="\1.html\2"', content)
        
        # Also let's check for links like "href="something"" in the same directory
        # e.g., if we're in pages/dashboard.html, it might link to "ai-pdf-chat"
        # We can match href="[a-zA-Z0-9_-]+" (no slash, no dot)
        pattern_rel = re.compile(r'href="([a-zA-Z0-9_-]+)(#.*?)?"')
        
        # We should be careful with pattern_rel. Only apply it if the target file actually exists with .html.
        def repl_rel(match):
            target = match.group(1)
            anchor = match.group(2) or ''
            # Check if target.html exists in the same dir
            target_html = file_path.parent / (target + ".html")
            if target_html.exists():
                return f'href="{target}.html{anchor}"'
            # Check if target is a known folder? 
            return match.group(0)
            
        new_content = pattern_rel.sub(repl_rel, new_content)
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated internal links in {file_path.relative_to(root_path)}")

if __name__ == "__main__":
    frontend_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend"
    add_html_extensions(frontend_dir)
