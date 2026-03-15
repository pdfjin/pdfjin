import os

path = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\sign-pdf.html'

replacements = {
    'ðŸ–‹ï¸ ': '🖋️',
    'ðŸ“ ': '📁',
    'â ³': '⏳',
    'âœ¨': '✨',
    'ðŸ“„': '📄'
}

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in replacements.items():
    content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fix complete.")
