import os

blog_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
files = [f for f in os.listdir(blog_dir) if f.endswith('.html')]

for filename in files:
    path = os.path.join(blog_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add blog.css if missing
    if 'css/blog.css' not in content:
        content = content.replace('<link rel="stylesheet" href="../../css/tool-page.css">', 
                                 '<link rel="stylesheet" href="../../css/tool-page.css">\n    <link rel="stylesheet" href="../../css/blog.css">')
    
    # 2. Add blog-pos-page class to body if missing
    if '<body class="blog-pos-page">' not in content:
        content = content.replace('<body>', '<body class="blog-pos-page">')
    
    # 3. Standardize paths if any were missed
    content = content.replace('href="../../cs/style.css"', 'href="../../css/style.css"')
    content = content.replace('href="../../cs/tool-page.css"', 'href="../../css/tool-page.css"')
    content = content.replace('src="../../jsmain.js>', 'src="../../js/main.js">')
    content = content.replace('src="../../asetsblog/', 'src="../../assets/blog/')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Professionalized: {filename}")
