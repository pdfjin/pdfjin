"""
PDFjin - Fix Encoding Issues
Repairs mojibake caused by multiple PowerShell sync runs
"""
import os
import glob

DIRS = [
    r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages",
    r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog",
]

# Mojibake replacement map: corrupted string -> correct HTML entity
# Ordered from longest patterns to shortest to prevent partial matches
REPLACEMENTS = [
    # === TRIPLE-ENCODED patterns (worst case, 3+ sync runs) ===
    ("\u00c3\u0192\u00c2\u00b0\u00c3\u2026\u00c2\u00b8\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u201e\u00a2\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u009c", "&#128196;"),  # triple 📄
    ("\u00c3\u0192\u00c2\u00b0\u00c3\u2026\u00c2\u00b8\u00c3\u00a2\u00e2\u201a\u00ac\u2026\u201c\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u00b0", "&#128228;"),  # triple 📤
    ("\u00c3\u0192\u00c2\u00b0\u00c3\u2026\u00c2\u00b8\u00c3\u00a2\u00e2\u201a\u00ac\u2026\u201c\u00c3\u0192\u00c2\u00a6", "&#128230;"),  # triple compress icon
    ("\u00c3\u0192\u00c2\u00a2\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u0178\u00c3\u0192\u00c2\u00a0", "&larr;"),  # triple ←  
    ("\u00c3\u0192\u00c2\u00a2\u00c3\u00a2\u00e2\u201a\u00ac\u00c2\u00a0\u00c3\u0192\u00c2\u00a0", "&larr;"),  # triple ← alt
    ("\u00c3\u0192\u00c2\u00a2\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u0178\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u201e\u00a2", "&rarr;"),  # triple →
    ("\u00c3\u0192\u00c2\u00a2\u00c3\u00a2\u00e2\u201a\u00ac\u00c2\u00a0\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u201e\u00a2", "&rarr;"),  # triple → alt
]

# Build comprehensive replacement list programmatically
# These are the common patterns found in the files
SIMPLE_REPLACEMENTS = [
    # Double-encoded emoji (from 2 sync runs)
    ("\u00c3\u00b0\u00c5\u00b8\u00e2\u20ac\u0153\u00e2\u20ac\u017e", "&#128196;"),   # 📄
    ("\u00c3\u00b0\u00c5\u00b8\u00e2\u20ac\u0153\u00c2\u00a4", "&#128228;"),        # 📤
    ("\u00c3\u00b0\u00c5\u00b8\u00e2\u20ac\u0153\u00c2\u00a6", "&#128230;"),        # 📦 (compress)
    ("\u00c3\u00a2\u00e2\u20ac\u0160\u00c2\u00a0", "&larr;"),                       # ←
    ("\u00c3\u00a2\u00e2\u20ac\u0160\u00e2\u20ac\u2122", "&rarr;"),                 # →
    ("\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u0153", "&mdash;"),                # —
    ("\u00c3\u0082\u00c2\u00a9", "&copy;"),                                          # ©
    ("\u00c3\u0082\u00c2\u00b7", "&middot;"),                                        # ·
    
    # Single-encoded garble (from template emoji in PS)
    ("\u00c3\u00b0\u00c5\u00b8\u00e2\u20ac\u009c\u00e2\u20ac\u0161", "&#128196;"),
    ("\u00c3\u00b0\u00c5\u00b8\u00e2\u20ac\u201c\u00e2\u20ac\u017e", "&#128196;"),
]

def fix_file(filepath):
    """Read file, fix encoding issues, write back."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    original = content
    
    # Apply all replacements
    for corrupted, correct in REPLACEMENTS + SIMPLE_REPLACEMENTS:
        content = content.replace(corrupted, correct)
    
    # Also fix by scanning for common multi-byte garble patterns
    # These are the raw byte patterns that appear in the view
    byte_fixes = {
        # Navbar/footer emoji garble patterns (as they appear in the file)
        b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xe2\x80\x9e': b'&#128196;',      # 📄 
        b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xa4': b'&#128228;',          # 📤
        b'\xc3\xa2\xe2\x80\xa0\xc2\xa0': b'&larr;',                       # ←
        b'\xc3\xa2\xe2\x80\xa0\xe2\x80\x99': b'&rarr;',                   # →
        b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c': b'&mdash;',                  # —
        b'\xc2\xa9': b'&copy;',                                            # ©
        b'\xc2\xb7': b'&middot;',                                          # ·
        b'\xc3\xa2\xc5\x93\xe2\x80\x9a': b'&#9986;',                      # ✂
    }
    
    # Read raw bytes for byte-level fixes
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    raw_original = raw
    for bad_bytes, good_bytes in byte_fixes.items():
        raw = raw.replace(bad_bytes, good_bytes)
    
    # Decode back and do string-level fixes
    content = raw.decode('utf-8', errors='replace')
    
    # Fix remaining known garble strings that appear in the actual files
    garble_map = {
        'ðŸ"„': '&#128196;',       # 📄
        'ðŸ"¤': '&#128228;',       # 📤  
        'â¤ï¸': '&hearts;',        # ❤️
        'âœ‚ï¸': '&#9986;',        # ✂️
        'âœ‚': '&#9986;',          # ✂
        'â†': '&larr;',            # ←
        'â†'': '&rarr;',           # →
        'â€"': '&mdash;',          # —
        'Â©': '&copy;',            # ©
        'Â·': '&middot;',          # ·
        'ð•': '&#120143;',         # 𝕏
        'âŒ¥': '&#8997;',          # ⌥
        'ðŸ–Š': '&#128394;',       # 🖊
        'ðŸ–‹': '&#128395;',       # 🖋
        'ðŸ"'': '&#128274;',       # 🔒
        'ðŸ"ƒ': '&#128195;',       # 📃
        'ðŸ"': '&#128209;',        # 📑
        'ðŸ—£': '&#128483;',        # 🗣
        'ðŸ§ ': '&#129504;',        # 🧠
        'ðŸ"Š': '&#128202;',       # 📊
        'ðŸ"': '&#128269;',        # 🔍
        'ðŸ–¼': '&#128444;',       # 🖼
        'ðŸ"ˆ': '&#128200;',       # 📈
        'ðŸ"„': '&#128196;',       # 📄 alt
        'ðŸ"': '&#128240;',        # 📰
    }
    
    for garbled, entity in garble_map.items():
        content = content.replace(garbled, entity)
    
    # Triple-encoded specific patterns found in the files
    triple_patterns = {
        'ÃƒÂ°Ã…Â¸Ã¢â‚¬Å"Ã‚Â„': '&#128196;',        # 📄 triple
        'ÃƒÂ°Ã…Â¸Ã¢â‚¬Å"Ã¢â‚¬Â°': '&#128228;',        # 📤 triple
        'ÃƒÂ°Ã…Â¸Ã¢â‚¬Å"Ã‚Â¦': '&#128230;',        # 📦 triple
        'ÃƒÂ¢Ã¢â‚¬Â Ã‚Â': '&larr;',                 # ← triple
        'ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢': '&rarr;',              # → triple
        'ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â': '&mdash;',              # — triple
        'ÃƒÂ°Ã…Â¸Ã¢â‚¬Å"Ã¢â‚¬Â¬': '&#128236;',        # generic emoji triple
    }
    
    for garbled, entity in triple_patterns.items():
        content = content.replace(garbled, entity)
    
    # Double-encoded patterns
    double_patterns = {
        'Ã°Å¸â€œâ€ž': '&#128196;',    # 📄 double
        'Ã°Å¸â€œÂ¤': '&#128228;',    # 📤 double
        'Ã¢â€ Â': '&larr;',          # ← double
        'Ã¢â€ â€™': '&rarr;',        # → double
        'Ã¢â‚¬â€"': '&mdash;',        # — double
        'Ã‚Â©': '&copy;',            # © double
        'Ã‚Â·': '&middot;',          # · double  
        'Ã¢Å"â€š': '&#9986;',         # ✂ double
    }
    
    for garbled, entity in double_patterns.items():
        content = content.replace(garbled, entity)
    
    # Clean up any remaining Ã-prefix double encoding artifacts
    # These are the telltale sign of UTF-8 read as Latin-1
    
    if content != original or raw != raw_original:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  FIXED: {filepath}")
        return True
    else:
        print(f"  clean: {filepath}")
        return False

# Main
fixed_count = 0
for d in DIRS:
    if not os.path.exists(d):
        continue
    for html_file in glob.glob(os.path.join(d, "*.html")):
        if fix_file(html_file):
            fixed_count += 1

print(f"\nDone! Fixed {fixed_count} files.")
