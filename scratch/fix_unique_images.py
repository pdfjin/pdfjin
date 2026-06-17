import os, glob, re, urllib.request, urllib.parse, random

blog_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
assets_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\assets\blog"

for html_file in glob.glob(os.path.join(blog_dir, "*.html")):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "blog-pdf-word.png" in content:
        match = re.search(r'<h1>(.*?)</h1>', content)
        if match:
            topic = match.group(1)
            slug = os.path.basename(html_file)
            image_filename = slug.replace(".html", ".png")
            image_path = os.path.join(assets_dir, image_filename)
            
            prompt = f"A professional, modern blog post cover image about {topic}. Flat design, highly relevant, clean, wide landscape."
            seed = random.randint(1, 10000000)
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1280&height=720&nologo=true&seed={seed}"
            
            print(f"Downloading image for {topic}...")
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
                with urllib.request.urlopen(req, timeout=30) as response:
                    image_data = response.read()
                    with open(image_path, "wb") as img_f:
                        img_f.write(image_data)
                
                content = content.replace("blog-pdf-word.png", image_filename)
                content = content.replace("https://pdfjin.com/assets/blog/blog-pdf-word.png", f"https://pdfjin.com/assets/blog/{image_filename}")
                content = re.sub(r'<img src="\.\./\.\./assets/blog/[^"]+"', f'<img src="../../assets/blog/{image_filename}"', content)
                content = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="https://pdfjin.com/assets/blog/{image_filename}"', content)
                content = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="https://pdfjin.com/assets/blog/{image_filename}"', content)
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed {slug}")
            except Exception as e:
                print(f"Failed to generate for {topic}: {e}")

# Fix blog.html index file
blog_index = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog.html"
if os.path.exists(blog_index):
    with open(blog_index, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We look for: <a href="blog/{slug}"><img src="../assets/blog/blog-pdf-word.png"
    # and replace with correct image filename.
    for slug in os.listdir(blog_dir):
        if slug.endswith(".html"):
            image_filename = slug.replace(".html", ".png")
            # The regex matches the link and the fallback image
            pattern = rf'<a href="blog/{slug}"><img src="\.\./assets/blog/blog-pdf-word\.png"'
            replacement = f'<a href="blog/{slug}"><img src="../assets/blog/{image_filename}"'
            content = re.sub(pattern, replacement, content)
            
            # Or if it doesn't have the <a> wrapper
            pattern2 = rf'<img src="\.\./assets/blog/blog-pdf-word\.png"([^>]+)><a href="blog/{slug}">'
            # Wait, our card_html format is:
            # <article class="blog-card">
            #     <a href="blog/{slug}"><img src="../assets/blog/{image_url}" ...></a>
            #     <span class="post-tag">Guide</span>
            #     <h3><a href="blog/{slug}">{topic}</a></h3>
            
            # Let's just do a brute force replacement for each block.
            # Split by <article class="blog-card">
            
    blocks = content.split('<article class="blog-card">')
    for i in range(1, len(blocks)):
        block = blocks[i]
        # find the slug in this block
        match = re.search(r'href="blog/([^"]+)"', block)
        if match:
            slug = match.group(1)
            image_filename = slug.replace(".html", ".png")
            block = block.replace("../assets/blog/blog-pdf-word.png", f"../assets/blog/{image_filename}")
            blocks[i] = block
    content = '<article class="blog-card">'.join(blocks)
            
    with open(blog_index, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed blog.html index.")

