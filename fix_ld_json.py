import os
import re
import json

blog_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"

for filename in os.listdir(blog_dir):
    if not filename.endswith(".html"):
        continue
    filepath = os.path.join(blog_dir, filename)
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    changed = False

    # 1. Extract meta description
    meta_desc_match = re.search(r'<meta name="description" content="(.*?)" />', content)
    if meta_desc_match:
        meta_desc = meta_desc_match.group(1)
        
        # Replace description in ld+json
        # Find ld+json block
        ld_json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        if ld_json_match:
            ld_json_str = ld_json_match.group(1)
            try:
                # Need to carefully replace description using regex to avoid json parsing issues if malformed
                # The description in json is usually: "description": "...",
                new_ld_json_str = re.sub(r'"description":\s*"[^"]*",', f'"description": "{meta_desc}",', ld_json_str)
                if new_ld_json_str != ld_json_str:
                    content = content.replace(ld_json_str, new_ld_json_str)
                    changed = True
                    ld_json_str = new_ld_json_str
            except Exception as e:
                pass
                
    # 2. Extract hero image from meta property="og:image"
    og_img_match = re.search(r'<meta property="og:image" content="(.*?)" />', content)
    if og_img_match:
        og_img_url = og_img_match.group(1)
        
        # Update ld+json image
        ld_json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        if ld_json_match:
            ld_json_str = ld_json_match.group(1)
            new_ld_json_str = re.sub(r'"image":\s*"[^"]*",', f'"image": "{og_img_url}",', ld_json_str)
            if new_ld_json_str != ld_json_str:
                content = content.replace(ld_json_str, new_ld_json_str)
                changed = True
                
    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filename}")
