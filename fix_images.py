import os
import glob
import re

blog_dir = 'frontend/pages/blog'
files = glob.glob(f'{blog_dir}/*.html')

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'image.pollinations.ai' in content:
        # Replace broken pollinations images with a local default image
        content = re.sub(
            r'<img src="https://image\.pollinations\.ai/[^"]+"',
            r'<img src="../../assets/blog/blog-pdf-word.png"',
            content
        )
        content = re.sub(
            r'<meta property="og:image" content="https://image\.pollinations\.ai/[^"]+"',
            r'<meta property="og:image" content="https://pdfjin.com/assets/blog/blog-pdf-word.png"',
            content
        )
        content = re.sub(
            r'<meta name="twitter:image" content="https://image\.pollinations\.ai/[^"]+"',
            r'<meta name="twitter:image" content="https://pdfjin.com/assets/blog/blog-pdf-word.png"',
            content
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {filepath}')

# Also fix auto_blogger.py
auto_blogger_path = 'auto_blogger.py'
with open(auto_blogger_path, 'r', encoding='utf-8') as f:
    auto_blogger = f.read()

if 'https://image.pollinations.ai' in auto_blogger:
    auto_blogger = auto_blogger.replace(
        'return f\"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=630&nologo=true\"',
        'return \"../../assets/blog/blog-pdf-word.png\"'
    )
    with open(auto_blogger_path, 'w', encoding='utf-8') as f:
        f.write(auto_blogger)
    print('Fixed auto_blogger.py')

