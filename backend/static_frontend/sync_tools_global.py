import os
import re

# Configuration
target_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages"
blog_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"

# Navbar Template (Relative to pages/ directory)
navbar_template = """    <nav class="navbar scrolled" role="navigation" aria-label="Main navigation">
        <a href="../index.html" class="nav-logo" aria-label="PDFjin Home">
            <div class="logo-icon" aria-hidden="true">&#128196;</div>
            PDF<span>jin</span>
        </a>

        <ul class="nav-links" id="navMenu">
            <li><a href="../index.html#services">Tools</a></li>
            <li><a href="blog.html">Blog</a></li>
            <li><a href="../index.html#how-it-works">How It Works</a></li>
            <li><a href="../index.html#features">Features</a></li>
            <li><a href="../index.html#pricing">Pricing</a></li>
            <li><a href="api-docs.html">API Docs</a></li>
            <li class="guest-only"><a href="auth.html">Sign In</a></li>
            <li class="guest-only"><a href="register.html" class="nav-register">Register</a></li>
            <li class="user-only">
                <div class="nav-user-wrapper">
                    <a href="dashboard.html" class="user-profile-btn" title="Go to Dashboard">
                        <span class="user-bubble" id="navUserBubble">U</span>
                        <span class="user-status-dot"></span>
                    </a>
                    <a href="#" class="logout-link-simple" id="navLogout">Logout</a>
                </div>
            </li>
            <li><a href="../index.html#services" class="nav-cta" id="mainCTA" onclick="handleMainCTAClick(event)">Get Started Free &rarr;</a></li>
        </ul>

        <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation" aria-expanded="false">
            <span></span><span></span><span></span>
        </button>
    </nav>"""

# Footer Template (Relative to pages/ directory)
footer_template = """    <footer class="footer">
        <div class="footer-grid">
            <div class="footer-brand">
                <a href="../index.html" class="nav-logo" style="display:inline-flex;">
                    <div class="logo-icon">📄</div>
                    PDF<span>jin</span>
                </a>
                <p>The complete PDF toolkit built on open-source technology. Fast, free, and privacy-first. Powered by Google Cloud.</p>
                <div class="footer-social">
                  <a href="#" class="social-btn" aria-label="Twitter">𝕏</a>
                  <a href="#" class="social-btn" aria-label="GitHub">⌥</a>
                  <a href="#" class="social-btn" aria-label="LinkedIn">in</a>
                </div>
            </div>

            <div class="footer-col">
                <h4>Convert</h4>
                <ul>
                    <li><a href="pdf-to-word.html">PDF to Word</a></li>
                    <li><a href="word-to-pdf.html">Word to PDF</a></li>
                    <li><a href="pdf-to-jpg.html">PDF to JPG</a></li>
                    <li><a href="jpg-to-pdf.html">JPG to PDF</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Tools</h4>
                <ul>
                    <li><a href="merge-pdf.html">Merge PDF</a></li>
                    <li><a href="split-pdf.html">Split PDF</a></li>
                    <li><a href="compress-pdf.html">Compress PDF</a></li>
                    <li><a href="sign-pdf.html">Sign PDF</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Company</h4>
                <ul>
                    <li><a href="../about.html">About Us</a></li>
                    <li><a href="blog.html">Blog</a></li>
                    <li><a href="education.html">Education & Grant</a></li>
                    <li><a href="api-docs.html">API Docs</a></li>
                    <li><a href="../privacy.html">Privacy Policy</a></li>
                    <li><a href="../terms.html">Terms of Service</a></li>
                    <li><a href="../contact.html">Contact</a></li>
                </ul>
            </div>
        </div>

        <div class="footer-bottom">
            <span>© 2026 PDFjin. <a href="../privacy.html" style="color: inherit; text-decoration: underline;">Privacy Policy</a> | <a href="../terms.html" style="color: inherit; text-decoration: underline;">Terms</a> | <a href="../contact.html" style="color: inherit; text-decoration: underline;">Contact</a></span>
            <span>Made with ❤️ using open-source tools · Hosted on <a href="https://cloud.google.com" target="_blank" rel="noopener">Google Cloud</a></span>
        </div>
    </footer>"""

# Analytics & Login Check Script (Relative to pages/ directory)
head_scripts = """    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-G4FR9CKVZ0"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() { dataLayer.push(arguments); }
        gtag('js', new Date());
        gtag('config', 'G-G4FR9CKVZ0');
    </script>
    <script>
        // Critical: Instant Login Check
        (function () {
            const logged = localStorage.getItem('isLoggedIn') === 'true' || sessionStorage.getItem('isLoggedIn') === 'true';
            if (logged) {
                document.documentElement.classList.add('is-logged-in');
                window.isUserLoggedIn = true;
            }
        })();
    </script>
</head>"""

def sync_file(file_path, is_blog=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    nav = navbar_template
    foot = footer_template
    head = head_scripts

    if is_blog:
        # Resolve deeper paths for blog pages (../../ vs ../)
        nav = nav.replace('../index.html', '../../index.html')
        nav = nav.replace('blog.html', '../blog.html')
        nav = nav.replace('api-docs.html', '../api-docs.html')
        nav = nav.replace('auth.html', '../auth.html')
        nav = nav.replace('dashboard.html', '../dashboard.html')
        
        foot = foot.replace('../index.html', '../../index.html')
        foot = foot.replace('pdf-to-word.html', '../pdf-to-word.html')
        foot = foot.replace('word-to-pdf.html', '../word-to-pdf.html')
        foot = foot.replace('pdf-to-jpg.html', '../pdf-to-jpg.html')
        foot = foot.replace('jpg-to-pdf.html', '../jpg-to-pdf.html')
        foot = foot.replace('merge-pdf.html', '../merge-pdf.html')
        foot = foot.replace('split-pdf.html', '../split-pdf.html')
        foot = foot.replace('compress-pdf.html', '../compress-pdf.html')
        foot = foot.replace('sign-pdf.html', '../sign-pdf.html')
        foot = foot.replace('../about.html', '../../about.html')
        foot = foot.replace('blog.html', '../blog.html')
        foot = foot.replace('education.html', '../education.html')
        foot = foot.replace('api-docs.html', '../api-docs.html')
        foot = foot.replace('../privacy.html', '../../privacy.html')
        foot = foot.replace('../terms.html', '../../terms.html')
        foot = foot.replace('../contact.html', '../../contact.html')

    # Replace <nav> to </nav>
    content = re.sub(r'<nav class="navbar.*?>.*?</nav>', nav, content, flags=re.DOTALL)
    
    # Replace <footer> to </footer>
    content = re.sub(r'<footer.*?>.*?</footer>', foot, content, flags=re.DOTALL)
    
    # Sync Head (Analytics + Login Check)
    # We look for the closing </head> and replace the scripts before it
    # First we remove old instances of gtag and login check if they exist to avoid duplicates
    content = re.sub(r'<!-- Google tag \(gtag\.js\) -->.*?<script>.*?gtag.*?<\/script>.*?<script>.*?Instant Login Check.*?<\/script>', '', content, flags=re.DOTALL)
    content = content.replace('</head>', head)

    # Ensure correct main.js path
    js_path = "../js/main.js" if not is_blog else "../../js/main.js"
    content = re.sub(r'<script src=".*?js/main\.js.*?"></script>', f'<script src="{js_path}"></script>', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Synced: {file_path}")

def run_sync():
    # Sync Pages
    for file in os.listdir(target_dir):
        if file.endswith(".html") and file not in ["auth-isolated.html", "dashboard.html"]:
            sync_file(os.path.join(target_dir, file))

    # Sync Blog Pages
    for file in os.listdir(blog_dir):
        if file.endswith(".html"):
            sync_file(os.path.join(blog_dir, file), is_blog=True)

if __name__ == "__main__":
    run_sync()
