import os

blog_dir = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog'
old_part = "Flat%20design%2C%20highly%20relevant%2C%20clean%2C%20wide%20landscape."
new_part = "Vibrant%20colors%2C%20high%20contrast%2C%20striking%20visuals%2C%20bright%2C%20without%20any%20text%2C%20no%20words%2C%20no%20letters%2C%20wide%20landscape."

for filename in os.listdir(blog_dir):
    if not filename.endswith('.html'): continue
    filepath = os.path.join(blog_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if old_part in content:
        content = content.replace(old_part, new_part)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filename}")
