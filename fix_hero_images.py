import os
import re
import urllib.parse
import random

blog_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"

# The prompt that was repeated
target_prompt_part = "How%20to%20Convert%20Excel%20to%20PDF%20While%20Keeping%20Perfect%20Formatting"
target_seed = "8299404"
target_alt = "Excel to PDF Illustration"

for filename in os.listdir(blog_dir):
    if not filename.endswith(".html"):
        continue
    filepath = os.path.join(blog_dir, filename)
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    if target_prompt_part in content or target_seed in content or 'alt="Excel to PDF Illustration"' in content:
        # Extract title from the h1 tag or file name
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
        if title_match:
            title = title_match.group(1).strip()
            # Remove any HTML tags from title
            title = re.sub(r'<[^>]+>', '', title)
        else:
            # Fallback to filename
            title = filename.replace("-guide.html", "").replace("-", " ").title()
        
        encoded_title = urllib.parse.quote(title)
        
        # Replace the specific URL parts
        # The base pattern is:
        # https://image.pollinations.ai/prompt/A%20professional%2C%20modern%20blog%20post%20cover%20image%20about%20How%20to%20Convert%20Excel%20to%20PDF%20While%20Keeping%20Perfect%20Formatting.%20Flat%20design%2C%20highly%20relevant%2C%20clean%2C%20wide%20landscape.?width=1280&height=720&nologo=true&seed=8299404
        
        # Some files might have different titles but the same seed, or same title but different seed. Let's just fix all that have the target seed or target prompt or target alt (if it's wrong).
        # Actually, let's look for pollinations.ai URLs and see if they have the target prompt or seed.
        
        # Replace the prompt part
        if target_prompt_part in content:
            content = content.replace(target_prompt_part, encoded_title)
            
        # Replace seed if it's the target seed, or generate a new one anyway
        # Let's find the seed and replace it with a random one
        def repl_seed(match):
            new_seed = str(random.randint(1000000, 9999999))
            return f"seed={new_seed}"
        
        # We only want to replace the seed if the image is the repeated one.
        # But wait, we want each blog post to have a unique hero image.
        # So we can just find all pollinations.ai URLs in the file and update their seeds and prompts if they are the repeated one.
        
        # Better: just use regex to find the specific URL and replace it.
        pattern = r'https://image\.pollinations\.ai/prompt/A%20professional%2C%20modern%20blog%20post%20cover%20image%20about%20How%20to%20Convert%20Excel%20to%20PDF%20While%20Keeping%20Perfect%20Formatting\.%20Flat%20design%2C%20highly%20relevant%2C%20clean%2C%20wide%20landscape\.\?width=1280&height=720&nologo=true&seed=8299404'
        
        def repl_url(match):
            new_seed = str(random.randint(1000000, 9999999))
            return f"https://image.pollinations.ai/prompt/A%20professional%2C%20modern%20blog%20post%20cover%20image%20about%20{encoded_title}.%20Flat%20design%2C%20highly%20relevant%2C%20clean%2C%20wide%20landscape.?width=1280&height=720&nologo=true&seed={new_seed}"

        content, num_subs = re.subn(pattern, repl_url, content)
        
        # Also fix the 'alt="Excel to PDF Illustration"' if it was replaced above
        if num_subs > 0 or target_alt in content:
            # Only replace alt if we are sure it's the wrong one for this page.
            if "excel-to-pdf" not in filename:
                content = content.replace('alt="Excel to PDF Illustration"', f'alt="{title} Illustration"')
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filename}")
