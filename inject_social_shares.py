import os
import glob

BLOG_DIR = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"

SOCIAL_SHARE_HTML = """
            <div class="post-action-bar">
                <span class="share-label">Share:</span>
                <a href="#" class="action-icon-link facebook" aria-label="Share on Facebook" onclick="window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(window.location.href), '_blank'); return false;">
                    <svg viewBox="0 0 24 24"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path></svg>
                </a>
                <a href="#" class="action-icon-link twitter" aria-label="Share on X" onclick="window.open('https://twitter.com/intent/tweet?url=' + encodeURIComponent(window.location.href) + '&text=' + encodeURIComponent(document.title), '_blank'); return false;">
                    <svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"></path></svg>
                </a>
                <a href="#" class="action-icon-link linkedin" aria-label="Share on LinkedIn" onclick="window.open('https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(window.location.href), '_blank'); return false;">
                    <svg viewBox="0 0 24 24"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>
                </a>
                <a href="#" class="action-icon-link whatsapp" aria-label="Share on WhatsApp" onclick="window.open('https://api.whatsapp.com/send?text=' + encodeURIComponent(document.title + ' ' + window.location.href), '_blank'); return false;">
                    <svg viewBox="0 0 24 24"><path d="M20.52 3.449A11.91 11.91 0 0 0 12 .002a11.96 11.96 0 0 0-10.22 17.84L.27 24l6.3-1.654A11.91 11.91 0 0 0 12 23.948a11.96 11.96 0 0 0 11.99-12c.002-3.197-1.24-6.205-3.47-8.499zM12 21.94c-2.58 0-5.11-1.04-6.95-2.88l-4.42 1.16 1.18-4.3C.44 14.12-.03 12.08.03 9.97.13 4.54 4.63.15 10.06.02a12.03 12.03 0 0 1 3.52 23.9z"></path><path d="M16.81 14.61c-.39-.2-2.31-1.14-2.67-1.27-.36-.13-.62-.2-.88.2-.26.39-1.01 1.27-1.24 1.53-.23.26-.47.3-.86.1-.39-.2-1.65-.61-3.14-1.95-1.16-1.04-1.94-2.33-2.17-2.73-.23-.39-.02-.6.18-.8.19-.19.39-.46.59-.69.19-.23.26-.39.39-.65.13-.26.06-.5-.03-.7-.1-.2-.88-2.12-1.21-2.9-.32-.76-.64-.66-.88-.67-.23-.01-.5-.01-.76-.01-.26 0-.69.1-1.05.49-.36.39-1.37 1.34-1.37 3.27 0 1.93 1.41 3.8 1.6 4.06.2.26 2.76 4.22 6.69 5.92.94.41 1.67.65 2.24.83.94.3 1.79.26 2.47.16.76-.11 2.31-.95 2.64-1.86.33-.91.33-1.69.23-1.86-.1-.17-.36-.27-.75-.47z"></path></svg>
                </a>
                <a href="#" class="action-icon-link instagram" aria-label="Copy link for Instagram" onclick="copyBlogLink(); return false;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
                </a>
                <a href="#" class="action-icon-link tiktok" aria-label="Copy link for TikTok" onclick="copyBlogLink(); return false;">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 0h1.98c.144.715.54 1.617 1.235 2.512C12.895 3.389 13.797 4 15 4v2c-1.753 0-3.07-.814-4-1.829V11a5 5 0 1 1-5-5v2a3 3 0 1 0 3 3V0Z"></path></svg>
                </a>
            </div>"""

TOAST_SCRIPT_HTML = """
    <div id="toast-container"></div>
    <script>
        function copyBlogLink() {
            navigator.clipboard.writeText(window.location.href).then(function() {
                showToast("Link copied to clipboard!");
            });
        }
        function showToast(message) {
            const container = document.getElementById("toast-container");
            const toast = document.createElement("div");
            toast.className = "toast";
            toast.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg> ${message}`;
            container.appendChild(toast);
            
            // Trigger reflow
            void toast.offsetWidth;
            toast.classList.add("show");
            
            setTimeout(() => {
                toast.classList.remove("show");
                setTimeout(() => toast.remove(), 400);
            }, 3000);
        }
    </script>
</body>"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already injected
    if 'class="post-action-bar"' in content:
        print(f"Skipping {os.path.basename(filepath)} - already has social share")
        return

    # Find the injection point for the share bar
    # We want it at the end of the <header class="blog-pos-header">
    header_end_tag = "</header>"
    if header_end_tag in content:
        content = content.replace(header_end_tag, SOCIAL_SHARE_HTML + "\n        " + header_end_tag, 1)
    else:
        print(f"WARNING: Could not find <header> end tag in {os.path.basename(filepath)}")
        return

    # Inject toast script before </body>
    body_end_tag = "</body>"
    if body_end_tag in content:
        content = content.replace(body_end_tag, TOAST_SCRIPT_HTML)
    else:
        print(f"WARNING: Could not find </body> end tag in {os.path.basename(filepath)}")
        # We try to append to the end
        content += TOAST_SCRIPT_HTML

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully injected into {os.path.basename(filepath)}")

def main():
    search_pattern = os.path.join(BLOG_DIR, "*.html")
    html_files = glob.glob(search_pattern)
    
    if not html_files:
        print("No HTML files found in the blog directory.")
        return

    for filepath in html_files:
        process_file(filepath)

    print(f"Finished processing {len(html_files)} files.")

if __name__ == "__main__":
    main()
