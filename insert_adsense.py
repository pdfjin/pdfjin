import os
import glob

adsense_snippet = """
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4117768235037658" crossorigin="anonymous"></script>
"""

frontend_dir = "c:/Users/ADMIN/Desktop/pdfjin/frontend"
html_files = glob.glob(f"{frontend_dir}/**/*.html", recursive=True)

count = 0
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already contains adsense
    if 'ca-pub-4117768235037658' in content:
        continue

    # Insert right before </head>
    if '</head>' in content:
        content = content.replace('</head>', f"{adsense_snippet}</head>")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
    elif '<head>' in content:
        content = content.replace('<head>', f"<head>{adsense_snippet}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
    else:
        print(f"No <head> or </head> found in {filepath}")

print(f"Successfully inserted adsense into {count} files.")
