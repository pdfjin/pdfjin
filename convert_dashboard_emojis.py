
import os

entities = {
    '🖋️': '&#x1F58B;&#xFE0F;',
    '📸': '&#x1F4F8;',
    '📄→📝': '&#x1F4C4;&#x2192;&#x1F4DD;',
    '📝→📄': '&#x1F4DD;&#x2192;&#x1F4C4;',
    '📊→📄': '&#x1F4CA;&#x2192;&#x1F4C4;',
    '📈→📄': '&#x1F4C8;&#x2192;&#x1F4C4;',
    '📄→🖼️': '&#x1F4C4;&#x2192;&#x1F5BC;&#xFE0F;',
    '🖼️→📄': '&#x1F5BC;&#xFE0F;&#x2192;&#x1F4C4;',
    '📄→📊': '&#x1F4C4;&#x2192;&#x1F4CA;',
    '🌐→📄': '&#x1F310;&#x2192;&#x1F4C4;',
    '🔀': '&#x1F500;',
    '✂️': '&#x2702;&#xFE0F;',
    '🔄': '&#x1F504;',
    '📋': '&#x1F4CB;',
    '🔢': '&#x1F522;',
    '📦': '&#x1F4E6;',
    '🩹': '&#x1FA79;',
    '🔒': '&#x1F512;',
    '🔓': '&#x1F513;',
    '🌐': '&#x1F310;',
    '✍️': '&#x270D;&#xFE0F;',
    '🔍': '&#x1F50D;',
    '🖊️': '&#x1F58A;&#xFE0F;',
    '✨': '&#x2728;',
    '🤖': '&#x1F916;',
    '🎓': '&#x1F393;',
    '🎙️': '&#x1F399;&#xFE0F;',
    '⚖️': '&#x2696;&#xFE0F;',
    '📊': '&#x1F4CA;',
    '🛡️': '&#x1F6E1;&#xFE0F;',
    '🧬': '&#x1F9EC;',
    '🎧': '&#x1F3A7;',
    '📄': '&#x1F4C4;',
    '🚀': '&#x1F680;',
    '⚡': '&#x26A1;',
    '🔐': '&#x1F510;',
    '→</span>': '&rarr;</span>'
}

path = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

for k, v in entities.items():
    content = content.replace(k, v)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully converted emojis to HTML entities in dashboard.html")
