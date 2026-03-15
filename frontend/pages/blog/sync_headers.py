import os
import re

files = [
    r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog\digitally-sign-pdf-guide.html",
    r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog\edit-pdf-text-online-guide.html",
    r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog\excel-to-pdf-guide.html",
    r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog\merge-multiple-pdfs-guide.html",
    r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog\pdf-to-editable-word-guide.html",
    r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog\reduce-pdf-size-email-guide.html"
]

navbar_template = """    <nav class="navbar scrolled" role="navigation" aria-label="Main navigation">
        <a href="../../index.html" class="nav-logo" aria-label="PDFjin Home">
            <div class="logo-icon" aria-hidden="true">📄</div>
            PDF<span>jin</span>
        </a>

        <ul class="nav-links" id="navMenu">
            <li><a href="../../index.html#services">Tools</a></li>
            <li><a href="../blog.html">Blog</a></li>
            <li><a href="../../index.html#how-it-works">How It Works</a></li>
            <li><a href="../../index.html#features">Features</a></li>
            <li><a href="../../index.html#pricing">Pricing</a></li>
            <li><a href="../api-docs.html">API Docs</a></li>
            <li class="guest-only"><a href="../auth.html">Sign In</a></li>
            <li class="guest-only"><a href="../register.html" class="nav-register">Register</a></li>
            <li class="user-only">
                <div class="nav-user-wrapper">
                    <a href="../dashboard.html" class="user-profile-btn" title="Go to Dashboard">
                        <span class="user-bubble" id="navUserBubble">U</span>
                        <span class="user-status-dot"></span>
                    </a>
                    <a href="#" class="logout-link-simple" id="navLogout">Logout</a>
                </div>
            </li>
            <li><a href="../../index.html#services" class="nav-cta" id="mainCTA">Get Started Free →</a>
            </li>
        </ul>

        <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation" aria-expanded="false">
            <span></span><span></span><span></span>
        </button>
    </nav>"""

login_check_script = """    <script>
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

for file_path in files:
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}, not found.")
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace navbar - matches <nav class="navbar">...</nav> or <nav class="navbar scrolled">...</nav>
    # Handle the ones with div.nav-container too
    content = re.sub(r'<nav.*?>.*?</nav>', navbar_template, content, flags=re.DOTALL)
    
    # Add login check script if not present
    if "Instant Login Check" not in content:
        content = content.replace('</head>', login_check_script)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {file_path}")
