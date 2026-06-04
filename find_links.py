import os, re
from pathlib import Path

root_dir = Path(r'c:\Users\ADMIN\Desktop\pdfjin\frontend').resolve()
html_files = list(root_dir.rglob('*.html'))
existing_files = {str(f.relative_to(root_dir)).replace('\\', '/') for f in html_files}
broken_links = []

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    links = re.findall(r'href="([^"#:]+\.html)(#[^"]*)?"', content)
    file_rel_dir = html_file.parent.relative_to(root_dir)
    
    for link, anchor in links:
        if link.startswith('/'):
            target = link[1:]
        else:
            try:
                target = str((root_dir / file_rel_dir / link).resolve().relative_to(root_dir)).replace('\\', '/')
            except ValueError:
                target = 'OUTSIDE_ROOT: ' + link
        
        if target not in existing_files:
            broken_links.append((str(html_file.relative_to(root_dir)), link, target))

if broken_links:
    for bl in broken_links:
        print(f'{bl[0]} -> {bl[1]} (Resolved: {bl[2]})')
else:
    print('No broken links')
