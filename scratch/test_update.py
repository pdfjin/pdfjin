import os
from datetime import datetime

def update_blog_index(topic, slug):
    index_path = "frontend/pages/blog.html"
    if not os.path.exists(index_path):
        print("Warning: blog.html not found, skipping index update.")
        return
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    desc = f"Learn all about {topic}. A comprehensive guide by PDFjin."
    today = datetime.now().strftime("%b %d, %Y")
    
    card_html = f"""
            <article class="blog-card">
                <span class="post-tag">Guide</span>
                <h3><a href="blog/{slug}">{topic}</a></h3>
                <p>{desc}</p>
                <a href="blog/{slug}" class="read-more">Read Full Article</a>
                <div class="card-footer"><span>{today}</span> • <span>5 min read</span></div>
            </article>"""

    if '<div class="blog-grid">' in content:
        content = content.replace('<div class="blog-grid">', f'<div class="blog-grid">\n{card_html}')
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated blog.html index.")
    else:
        print('Error: Could not find <div class="blog-grid"> in blog.html')

update_blog_index("Test Topic", "test-slug-guide.html")
