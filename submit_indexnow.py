import requests
import xml.etree.ElementTree as ET
import os

KEY = "606c7becc4104846a80250335c7a2966"
HOST = "pdfjin.com"
KEY_LOCATION = f"https://pdfjin.com/{KEY}.txt"

def get_urls_from_sitemap(sitemap_path):
    urls = []
    if not os.path.exists(sitemap_path):
        print(f"Sitemap not found at {sitemap_path}")
        return urls
        
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # XML namespace for sitemap
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        for url in root.findall('ns:url', ns):
            loc = url.find('ns:loc', ns)
            if loc is not None and loc.text:
                urls.append(loc.text)
                
    except Exception as e:
        print(f"Error parsing sitemap: {e}")
        
    return urls

def submit_to_indexnow(urls):
    if not urls:
        print("No URLs to submit.")
        return

    print(f"Submitting {len(urls)} URLs to IndexNow...")
    
    endpoint = "https://api.indexnow.org/indexnow"
    
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls
    }
    
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 200:
            print("Successfully submitted URLs to IndexNow (Bing/Yandex).")
        elif response.status_code == 202:
            print("Successfully submitted URLs to IndexNow (Accepted/Processing).")
        else:
            print(f"Failed to submit. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error submitting to IndexNow: {e}")

if __name__ == "__main__":
    sitemap_file = os.path.join("frontend", "sitemap.xml")
    blog_sitemap_file = os.path.join("frontend", "sitemap-blog.xml")
    
    all_urls = []
    all_urls.extend(get_urls_from_sitemap(sitemap_file))
    all_urls.extend(get_urls_from_sitemap(blog_sitemap_file))
    
    if all_urls:
        submit_to_indexnow(all_urls)
    else:
        print("Could not find any URLs in sitemaps to submit.")
