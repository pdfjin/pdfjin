import os, glob, re, urllib.parse, random

blog_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"

for html_file in glob.glob(os.path.join(blog_dir, "*.html")):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace ANY hero image in the HTML with the unique pollinations URL
    match = re.search(r'<h1>(.*?)</h1>', content)
    if match:
        topic = match.group(1)
        slug = os.path.basename(html_file)
        
        prompt = f"A professional, modern blog post cover image about {topic}. Flat design, highly relevant, clean, wide landscape."
        seed = random.randint(1, 10000000)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1280&height=720&nologo=true&seed={seed}"
        
        # Replace <img> tag
        content = re.sub(r'<img src="\.\./\.\./assets/blog/[^"]+"', f'<img src="{url}"', content)
        # Some might just have blog-pdf-word.png without the path
        content = re.sub(r'<img src="[^"]*blog-pdf-word\.png"[^>]*>', f'<img src="{url}" alt="{topic}">', content)
        
        # Replace OG tags
        content = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="{url}"', content)
        content = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="{url}"', content)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {slug}")

# Fix blog.html index file
blog_index = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog.html"
if os.path.exists(blog_index):
    with open(blog_index, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = content.split('<article class="blog-card">')
    for i in range(1, len(blocks)):
        block = blocks[i]
        match = re.search(r'href="blog/([^"]+)"', block)
        if match:
            slug = match.group(1)
            # Find the topic from the <h3>
            topic_match = re.search(r'<h3><a href="blog/[^"]+">(.*?)</a></h3>', block)
            if topic_match:
                topic = topic_match.group(1)
                prompt = f"A professional, modern blog post cover image about {topic}. Flat design, highly relevant, clean, wide landscape."
                seed = random.randint(1, 10000000)
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1280&height=720&nologo=true&seed={seed}"
                
                # Replace the image src
                block = re.sub(r'<img src="\.\./assets/blog/[^"]+"', f'<img src="{url}"', block)
                blocks[i] = block
                
    content = '<article class="blog-card">'.join(blocks)
            
    with open(blog_index, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed blog.html index.")

