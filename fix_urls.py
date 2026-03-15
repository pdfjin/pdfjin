import os

old_url = "pdfjin-api-97530578628.asia-southeast1.run.app"
new_url = "pdfjin-api-d33mroeryq-as.a.run.app"
root_dir = "c:/Users/ADMIN/Desktop/pdfjin/frontend"

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith((".html", ".js")):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if old_url in content:
                    print(f"Updating {filepath}")
                    new_content = content.replace(old_url, new_url)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
