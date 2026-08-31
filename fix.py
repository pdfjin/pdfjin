import os
import glob
import re

dirs = ['c:/Users/ADMIN/Desktop/pdfjin/frontend/pages/*.html', 'c:/Users/ADMIN/Desktop/pdfjin/backend/static_frontend/pages/*.html']
for d in dirs:
    for f in glob.glob(d):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if '<!-- FAQ Preview Component -->' in content and 'class="faq-preview-section section-inner"' in content:
            # We want to move the FAQ component INSIDE the tool-card.
            # The tool-card ends with:
            #         </div>
            # 
            #               </div>
            #         
            #             </div>
            # 
            #         <!-- FAQ Preview Component -->
            
            # Use regex to find the closing tags before the FAQ component
            pattern = re.compile(r'(\s*)\</div>\s*\</div>\s*<!-- FAQ Preview Component -->\s*<div class="faq-preview-section section-inner"[^>]*>')
            
            match = pattern.search(content)
            if match:
                # We want to remove the two closing divs and insert the FAQ component, then add the two closing divs AFTER the FAQ component.
                # Actually, the two closing divs are closing .tool-card and .section-inner.
                
                # Replace the entire FAQ block start
                content = content.replace('<div class="faq-preview-section section-inner" id="faq-preview-accordion" style="margin-top: 4rem; padding-bottom: 4rem;">', 
                                          '<div class="tool-seo-section faq-preview-section" id="faq-preview-accordion" style="border-top: 1px solid #f0f0f0;">')
                content = content.replace('<div class="section-header reveal">', '<div class="section-header">')
                
                # Now we need to move the closing of the tool card and section-inner
                # Let's just find "<!-- FAQ Preview Component -->" and move it BEFORE the closing tags.
                pass

        # Alternative simpler approach: just find the block and rewrite it.
        # Find where tool-seo-section ends.
        
        # Actually, let's just use string replacement if it's consistent.
        if '<!-- FAQ Preview Component -->' in content:
            # We know the FAQ block is outside.
            # It looks like this:
            '''
              </div>
        
            </div>

        <!-- FAQ Preview Component -->
        <div class="faq-preview-section section-inner" id="faq-preview-accordion" style="margin-top: 4rem; padding-bottom: 4rem;">
            <div class="section-header reveal">
            '''
            
            old_block = """
              </div>

        

            </div>

        <!-- FAQ Preview Component -->
        <div class="faq-preview-section section-inner" id="faq-preview-accordion" style="margin-top: 4rem; padding-bottom: 4rem;">
            <div class="section-header reveal">
"""
            # Wait, the spacing might be inconsistent. Let's use regex.
            content = re.sub(
                r'(\s*</div>\s*</div>\s*)<!-- FAQ Preview Component -->\s*<div class="faq-preview-section section-inner" id="faq-preview-accordion"[^>]*>\s*<div class="section-header reveal">',
                r'\n        <!-- FAQ Preview Component -->\n        <div class="tool-seo-section faq-preview-section" id="faq-preview-accordion">\n            <div class="section-header">\n',
                content,
                flags=re.IGNORECASE
            )
            
            # Now we need to append the closing divs at the very end of the FAQ section.
            # The FAQ section ends with:
            #             </script>
            #         </div>
            # 
            # 
            #     </main>
            content = re.sub(
                r'(\s*</script>\s*</div>)\s*</main>',
                r'\1\n              </div>\n            </div>\n\n    </main>',
                content,
                flags=re.IGNORECASE
            )

            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)

print("Done")
