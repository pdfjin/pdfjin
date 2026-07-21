import os
import glob

directory = 'frontend/pages/blog'
html_files = glob.glob(os.path.join(directory, '*.html'))

for file_path in html_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target = '<a href="../ai-pdf-podcast.html">AI Podcast</a>'
        replacement = '<a href="../ai-audio-overview.html">Audio Overview</a>'
        
        if target in content:
            new_content = content.replace(target, replacement)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {file_path}")
    except Exception as e:
        print(f"Error on {file_path}: {e}")
