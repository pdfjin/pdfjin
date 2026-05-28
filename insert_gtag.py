import os
import glob

gtag_snippet = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=AW-18124600701"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'AW-18124600701');
    </script>
"""

frontend_dir = "c:/Users/ADMIN/Desktop/pdfjin/frontend"
html_files = glob.glob(f"{frontend_dir}/**/*.html", recursive=True)

count = 0
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already contains gtag
    if 'AW-18124600701' in content:
        continue

    # Insert right before </head>
    if '</head>' in content:
        content = content.replace('</head>', f"{gtag_snippet}</head>")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
    elif '<head>' in content:
        content = content.replace('<head>', f"<head>{gtag_snippet}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
    else:
        print(f"No <head> or </head> found in {filepath}")

print(f"Successfully inserted gtag into {count} files.")
