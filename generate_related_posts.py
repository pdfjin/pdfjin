import os
import random
import re

BLOG_DIR = r"frontend/pages/blog"

def get_all_posts():
    posts = []
    for f in os.listdir(BLOG_DIR):
        if f.endswith(".html"):
            path = os.path.join(BLOG_DIR, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                title_match = re.search(r'<h1>(.*?)</h1>', content)
                if title_match:
                    posts.append({"slug": f, "title": title_match.group(1)})
    return posts

def update_all_posts():
    posts = get_all_posts()
    for f in os.listdir(BLOG_DIR):
        if not f.endswith(".html"):
            continue
        path = os.path.join(BLOG_DIR, f)
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        if 'class="related-posts-container"' in content:
            # To allow refreshing or just ignore. If we want it to be always 10 random, we can replace it.
            # The prompt says "Below each post of blog shows 10 random blocg post headings"
            # It's safer to just skip to avoid massive git diffs, OR we could regenerate it.
            # Let's regenerate it so it stays fresh.
            content = re.sub(r'<div class="related-posts-container".*?</div>', '', content, flags=re.DOTALL)
            pass

        other_posts = [p for p in posts if p["slug"] != f]
        num_to_pick = min(10, len(other_posts))
        if num_to_pick == 0:
            continue
            
        random_posts = random.sample(other_posts, num_to_pick)
        
        html_snippet = '\n<div class="related-posts-container" style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eaeaea;">\n'
        html_snippet += '    <h3>Related Articles</h3>\n'
        html_snippet += '    <ul style="list-style: none; padding: 0; line-height: 1.8;">\n'
        for p in random_posts:
            html_snippet += f'        <li style="margin-bottom: 10px;">&rarr; <a href="{p["slug"]}" style="color: var(--primary); font-weight: 500; text-decoration: none;">{p["title"]}</a></li>\n'
        html_snippet += '    </ul>\n'
        html_snippet += '</div>\n'
        html_snippet += '</section>'

        if '</section>' in content:
            new_content = content.replace('</section>', html_snippet, 1)
            with open(path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Added related posts to {f}")

if __name__ == "__main__":
    update_all_posts()
