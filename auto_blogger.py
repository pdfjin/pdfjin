import os
import csv
import json
import subprocess
from datetime import datetime
import google.generativeai as genai
import urllib.parse
import re

# Configuration
CSV_FILE = "blog_topics.csv"
BLOG_DIR = r"frontend/pages/blog"
TEMPLATE_FILE = r"frontend/pages/blog/excel-to-pdf-guide.html"

# Configure Gemini
API_KEY = os.getenv("GEMINI_API_KEY", "")
if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    exit(1)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

def get_pending_topics(limit=1):
    topics = []
    if not os.path.exists(CSV_FILE):
        return topics
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["status"] == "pending":
                topics.append(row["topic"])
                if len(topics) == limit:
                    break
    return topics

def update_topic_status(topic):
    rows = []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["topic"] == topic:
                row["status"] = "published"
            rows.append(row)
    
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["topic", "status"])
        writer.writeheader()
        writer.writerows(rows)

def generate_blog_content(topic):
    prompt = f"""
Write a ~1000 word blog post about "{topic}".
INSTRUCTIONS:
1. Use shorter sentences and mostly active voice.
2. No paragraph should exceed 250 words.
3. Start with a catchy heading (<h2>), then a description/intro.
4. Add closing remarks with a natural CTA to try PDFjin's free tools.
5. Keep it creative, informative, persuasive, and authoritative.
6. Insert keywords naturally, ensure smooth/coherent flow, and strictly avoid robotic or generic AI phrasing.
7. Format the output STRICTLY as HTML tags (<h2>, <p>, <ul>, <li>, <strong>). DO NOT wrap it in a full <html> document, just the inner content block. DO NOT use markdown code blocks (```html).
    """
    response = model.generate_content(prompt)
    html_content = response.text.replace("```html", "").replace("```", "").strip()
    return html_content

def generate_slug(topic):
    slug = "".join([c.lower() if c.isalnum() else "-" for c in topic])
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug + "-guide.html"

def generate_image_url(topic):
    encoded = urllib.parse.quote(topic)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=630&nologo=true"

def build_html_page(topic, html_body, slug, image_url):
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    desc = f"Learn all about {topic}. A comprehensive guide by PDFjin."
    today = datetime.now().strftime("%b %d, %Y")
    iso_date = datetime.now().strftime("%Y-%m-%d")

    template = re.sub(r'<title>.*?</title>', f'<title>PDFjin | {topic}</title>', template)
    template = re.sub(r'<meta name="description" content="[^"]+"', f'<meta name="description" content="{desc}"', template)
    template = re.sub(r'<meta property="og:title" content="[^"]+"', f'<meta property="og:title" content="{topic} | PDFjin"', template)
    template = re.sub(r'<meta property="og:description" content="[^"]+"', f'<meta property="og:description" content="{desc}"', template)
    template = re.sub(r'<meta name="twitter:title" content="[^"]+"', f'<meta name="twitter:title" content="{topic} | PDFjin"', template)
    template = re.sub(r'<meta name="twitter:description" content="[^"]+"', f'<meta name="twitter:description" content="{desc}"', template)
    
    template = re.sub(r'https://pdfjin.com/pages/blog/[^"]+', f'https://pdfjin.com/pages/blog/{slug}', template)
    template = re.sub(r'"headline":\s*"[^"]+"', f'"headline": "{topic}"', template)
    template = re.sub(r'"datePublished":\s*"[^"]+"', f'"datePublished": "{iso_date}"', template)
    
    template = re.sub(r'<img src="\.\./\.\./assets/blog/[^"]+"', f'<img src="{image_url}"', template)
    template = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="{image_url}"', template)
    template = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="{image_url}"', template)

    body_pattern = r'(<section class="blog-pos-content">)(.*?)(</section>)'
    template = re.sub(r'<h1>.*?</h1>', f'<h1>{topic}</h1>', template)
    template = re.sub(r'<span>[A-Z][a-z]{2} \d{1,2}, \d{4}</span>', f'<span>{today}</span>', template)

    template = re.sub(body_pattern, r'\1\n' + html_body.replace('\\', '\\\\') + r'\n\3', template, flags=re.DOTALL)
    return template

def main():
    topics = get_pending_topics(limit=1)
    if not topics:
        print("No pending topics found.")
        return

    topic = topics[0]
    print(f"Generating post: {topic}")
    
    html_body = generate_blog_content(topic)
    slug = generate_slug(topic)
    image_url = generate_image_url(topic)

    final_html = build_html_page(topic, html_body, slug, image_url)

    out_path = os.path.join(BLOG_DIR, slug)
    # Ensure dir exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    update_topic_status(topic)
    print(f"Saved post to {out_path}")

    print("Regenerating RSS and Sitemap...")
    # Use generic python command (works cross platform)
    subprocess.run(["python", "generate_rss.py"], check=True)
    subprocess.run(["python", "generate_sitemap.py"], check=True)

    # Check if we are running in CI (GitHub Actions)
    if os.getenv("GITHUB_ACTIONS"):
        print("Running in CI. Skipping manual git push and deploy-cloud.ps1 since GitHub Actions will handle it.")
    else:
        print("Pushing to GitHub...")
        try:
            subprocess.run(["git", "add", "blog_topics.csv", out_path, "frontend/sitemap.xml", "frontend/pages/blog/rss.xml"], check=True)
            subprocess.run(["git", "commit", "-m", f"auto-blog: Published {slug}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Deploying to Cloud Run...")
            subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ".\\deploy-cloud.ps1"], check=True)
        except Exception as e:
            print(f"Local deploy error: {e}")

    print("Auto-blogging sequence complete!")

if __name__ == "__main__":
    main()
