import json
import xml.etree.ElementTree as ET
import requests
from google.oauth2 import service_account
import google.auth.transport.requests
import time
import os

# Configuration
SERVICE_ACCOUNT_FILE = r'c:\Users\ADMIN\Desktop\pdfjin\pdgjin-8561015a833b.json'
SITEMAP_FILE = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\sitemap.xml'
SCOPES = ['https://www.googleapis.com/auth/indexing']
ENDPOINT = 'https://indexing.googleapis.com/v3/urlNotifications:publish'

def get_urls_from_sitemap(sitemap_path):
    print(f"Reading sitemap: {sitemap_path}")
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    # XML namespace handling
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = []
    for url in root.findall('ns:url', namespace):
        loc = url.find('ns:loc', namespace).text
        urls.append(loc)
    return urls

def notify_google(urls):
    print("Authenticating with Google Indexing API...")
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Error: Could not find service account key at {SERVICE_ACCOUNT_FILE}")
        return

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    except Exception as e:
        print(f"Failed to load credentials: {e}")
        return

    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    token = credentials.token

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    success_count = 0
    error_count = 0

    print(f"Starting submission of {len(urls)} URLs to Google...")
    for idx, url in enumerate(urls, 1):
        payload = {
            'url': url,
            'type': 'URL_UPDATED'
        }
        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload)
            if response.status_code == 200:
                print(f"[{idx}/{len(urls)}] SUCCESS: {url}")
                success_count += 1
            else:
                print(f"[{idx}/{len(urls)}] ERROR {response.status_code}: {url}")
                try:
                    print("Detail:", response.json())
                except:
                    pass
                error_count += 1
            
            # Rate limit mitigation
            time.sleep(0.5)
        except Exception as e:
            print(f"[{idx}/{len(urls)}] FAILED Request for {url}: {e}")
            error_count += 1

    print("\n--- Summary ---")
    print(f"Successfully pushed: {success_count}")
    print(f"Errors: {error_count}")

if __name__ == '__main__':
    try:
        urls = get_urls_from_sitemap(SITEMAP_FILE)
        notify_google(urls)
    except Exception as e:
        print(f"Fatal error: {e}")
