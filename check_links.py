import os
import re
from pathlib import Path

def check_links():
    root_dir = Path(r"c:\Users\ADMIN\Desktop\pdfjin\frontend")
    html_files = list(root_dir.rglob("*.html"))
    
    # Store all existing local files (relative to frontend)
    existing_files = set()
    for f in html_files:
        existing_files.add(str(f.relative_to(root_dir)).replace("\\", "/"))
    
    broken_links = []
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all hrefs that look like local html files
        # Matches: href="pages/tool.html", href="../page.html", href="page.html"
        links = re.findall(r'href="([^"#:]+\.html)(#[^"]*)?"', content)
        
        file_rel_dir = html_file.parent.relative_to(root_dir)
        
        for link, anchor in links:
            # Handle absolute root paths (if any)
            if link.startswith("/"):
                target = link[1:]
            else:
                # Handle relative paths
                target = str((file_rel_dir / link).resolve().relative_to(root_dir)).replace("\\", "/")
            
            if target not in existing_files:
                broken_links.append({
                    "src": str(html_file.relative_to(root_dir)),
                    "link": link,
                    "target_resolved": target
                })
                
    if broken_links:
        print(f"Found {len(broken_links)} broken links:")
        for bl in broken_links:
            print(f"File: {bl['src']} -> Link: {bl['link']} (Resolved: {bl['target_resolved']})")
    else:
        print("No broken internal links found.")

if __name__ == "__main__":
    check_links()
