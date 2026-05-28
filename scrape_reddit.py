import requests
import json

SUBREDDITS = ['pdf', 'software', 'techsupport']
KEYWORDS = ['merge', 'split', 'edit', 'combine', 'password', 'compress', 'convert']

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

found_posts = []

for sub in SUBREDDITS:
    url = f'https://www.reddit.com/r/{sub}/new.json?limit=25'
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            for child in data.get('data', {}).get('children', []):
                post = child.get('data', {})
                title = post.get('title', '')
                text = post.get('selftext', '')
                combined = f'{title} {text}'.lower()
                
                if 'pdf' in combined:
                    for kw in KEYWORDS:
                        if kw in combined:
                            link = post.get('permalink', '')
                            found_posts.append({
                                'title': title,
                                'text': text[:200] + '...',
                                'url': f'https://www.reddit.com{link}'
                            })
                            break
    except Exception as e:
        print(f'Error on {sub}: {e}')

if found_posts:
    for i, p in enumerate(found_posts[:3]):
        print(f'--- POST {i+1} ---')
        print(f"Title: {p['title']}")
        print(f"URL: {p['url']}")
        print(f"Preview: {p['text']}\n")
else:
    print('No relevant PDF posts found right now.')
