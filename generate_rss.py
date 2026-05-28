import os
import re
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Configuration
BASE_URL = "https://pdfjin.com"
BLOG_DIR = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
OUTPUT_FILE = os.path.join(BLOG_DIR, "rss.xml")

def extract_metadata(html_content):
    metadata = {}
    
    # Extract Title
    title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
    if title_match:
        metadata['title'] = title_match.group(1)
    else:
        title_match = re.search(r'<title>([^<]+)</title>', html_content)
        metadata['title'] = title_match.group(1) if title_match else 'Untitled Post'

    # Extract Description
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', html_content)
    if not desc_match:
        desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html_content)
    metadata['description'] = desc_match.group(1) if desc_match else ''

    # Extract URL
    url_match = re.search(r'<meta property="og:url" content="([^"]+)"', html_content)
    metadata['url'] = url_match.group(1) if url_match else ''
    
    # Extract Date from JSON-LD
    date_match = re.search(r'"datePublished":\s*"([^"]+)"', html_content)
    if date_match:
        # Assuming format YYYY-MM-DD
        date_str = date_match.group(1)
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # Format to RFC 822 for RSS (e.g. Sun, 24 May 2026 00:00:00 +0000)
            metadata['pubDate'] = dt.strftime("%a, %d %b %Y 00:00:00 +0000")
        except:
            metadata['pubDate'] = ""
    else:
        metadata['pubDate'] = ""

    return metadata

def generate_rss():
    print(f"Starting RSS generation for {BASE_URL}/pages/blog ...")
    
    rss = ET.Element("rss", version="2.0", attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"})
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "PDFjin Blog"
    ET.SubElement(channel, "link").text = f"{BASE_URL}/pages/blog.html"
    ET.SubElement(channel, "description").text = "Latest updates and tutorials from PDFjin."
    ET.SubElement(channel, "language").text = "en-us"
    
    # Add atom link
    atom_link = ET.SubElement(channel, "atom:link", href=f"{BASE_URL}/pages/blog/rss.xml", rel="self", type="application/rss+xml")
    
    if not os.path.exists(BLOG_DIR):
        print(f"Error: Directory {BLOG_DIR} does not exist.")
        return
        
    posts = []
    
    # Scan blog posts
    for file in os.listdir(BLOG_DIR):
        if file.endswith(".html"):
            file_path = os.path.join(BLOG_DIR, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            meta = extract_metadata(content)
            if not meta.get('url'):
                meta['url'] = f"{BASE_URL}/pages/blog/{file}"
                
            # If we don't have a valid title/date we skip or use fallback, but let's try to add all .html
            posts.append({
                'title': meta.get('title', 'Untitled'),
                'link': meta.get('url'),
                'description': meta.get('description', ''),
                'pubDate': meta.get('pubDate', ''),
                'guid': meta.get('url')
            })
            
    # Sort posts by date (this requires parsing pubDate, but since we format it, it's a bit tricky. We can rely on basic text sorting or convert back).
    def sort_key(post):
        try:
            return datetime.strptime(post['pubDate'], "%a, %d %b %Y %H:%M:%S +0000")
        except:
            return datetime.min

    posts.sort(key=sort_key, reverse=True)

    for post in posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post['title']
        ET.SubElement(item, "link").text = post['link']
        ET.SubElement(item, "description").text = post['description']
        if post['pubDate']:
            ET.SubElement(item, "pubDate").text = post['pubDate']
        ET.SubElement(item, "guid").text = post['guid']

    # Prettify XML
    raw_string = ET.tostring(rss, 'utf-8')
    reparsed = minidom.parseString(raw_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Minidom adds an xml declaration automatically
        f.write(pretty_xml)

    print(f"Success! RSS generated at: {OUTPUT_FILE}")
    print(f"Total Items: {len(posts)}")

if __name__ == "__main__":
    generate_rss()
