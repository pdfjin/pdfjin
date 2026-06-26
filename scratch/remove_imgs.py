import re

def remove_imgs(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Matches <a href="blog/..."><img src="..." ...></a>
    pattern = r'<a href="blog/[^"]+">\s*<img[^>]+>\s*</a>\s*'
    new_content = re.sub(pattern, "", content)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Cleaned {file_path}")

remove_imgs(r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog.html")
remove_imgs(r"c:\Users\ADMIN\Desktop\pdfjin\backend\static_frontend\pages\blog.html")
