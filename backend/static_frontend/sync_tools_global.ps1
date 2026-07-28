# ============================================================
#  PDFjin - Global Sync Script (Encoding-Safe Version)
#  Uses ONLY HTML entities - zero raw emoji characters
# ============================================================

$targetDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend\pages"
$blogDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"

# ALL templates use HTML entities only - pure ASCII, impossible to corrupt
$navbarTemplate = @"
    <nav class="navbar scrolled" role="navigation" aria-label="Main navigation">
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
            <li class="user-only">
                <div class="nav-user-wrapper">
                    <a href="dashboard.html" class="user-profile-btn" title="Go to Dashboard">
                        <span class="user-bubble" id="navUserBubble">U</span>
                        <span class="user-status-dot"></span>
                    </a>
                    <a href="#" class="logout-link-simple" id="navLogout">Logout</a>
                </div>
            </li>
            <li><a href="../index.html#services" class="nav-cta" id="mainCTA">Get Started Free &rarr;</a></li>
        </ul>

        <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation" aria-expanded="false">
            <span></span><span></span><span></span>
        </button>
    </nav>
"@

$footerTemplate = @"
    <footer class="footer">
        <div class="footer-grid">
            <div class="footer-brand">
                <a href="../index.html" class="nav-logo" style="display:inline-flex;">
                    <div class="logo-icon">&#128196;</div>
                    PDF<span>jin</span>
                </a>
                <p>The complete PDF toolkit built on open-source technology.</p>
                <div class="footer-social">
                  <a href="#" class="social-btn" aria-label="X">&#120143;</a>
                  <a href="#" class="social-btn" aria-label="GitHub">&#8997;</a>
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
                <h4>AI Studio</h4>
                <ul>
                    <li><a href="ai-pdf-chat.html">AI Chat</a></li>
                    <li><a href="ai-pdf-extraction.html">AI Extract</a></li>
                    <li><a href="ai-smart-rewrite.html">AI Rewrite</a></li>
                    <li><a href="ai-pdf-podcast.html">AI Podcast</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Company</h4>
                <ul>
                    <li><a href="../about.html">About Us</a></li>
                    <li><a href="blog.html">Blog</a></li>
                    <li><a href="api-docs.html">API Docs</a></li>
                    <li><a href="../privacy.html">Privacy Policy</a></li>
                </ul>
            </div>
        </div>

        <div class="footer-bottom">
            <span>&copy; 2026 PDFjin. <a href="../privacy.html" style="color: inherit; text-decoration: underline;">Privacy Policy</a> | <a href="../terms.html" style="color: inherit; text-decoration: underline;">Terms</a> | <a href="../contact.html" style="color: inherit; text-decoration: underline;">Contact</a></span>
            <span>Made with &hearts; using open-source tools &middot; Hosted on <a href="https://cloud.google.com" target="_blank" rel="noopener">Google Cloud</a></span>
        </div>
    </footer>
"@

$backLinkHtml = @"
                <div style="text-align: left; margin-bottom: 25px;">
                    <a href="dashboard.html" class="back-link" style="text-decoration: none; color: #64748b; font-weight: 600; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 8px; transition: color 0.2s;">
                        &larr; Back to Dashboard
                    </a>
                </div>
"@

$loginCheckTemplate = @"
    <script>
        // PDFjin: Global API configuration v3.3
        (function () {
            const targetApi = "https://pdfjin-api-d33mroeryq-as.a.run.app";
            window.PDFJIN_API_URL = targetApi;
            
            // Force fix stale localStorage that blocks requests
            try {
                const config = JSON.parse(localStorage.getItem('adminApiConfig') || '{}');
                if (config.apiUrl && (config.apiUrl.includes('97530578628') || config.apiUrl.includes('asia-southeast1'))) {
                    console.log("PDFjin: Fixing stale API configuration...");
                    config.apiUrl = targetApi;
                    localStorage.setItem('adminApiConfig', JSON.stringify(config));
                }
            } catch(e) {}

            // Critical: Instant Login Check
            const logged = localStorage.getItem('isLoggedIn') === 'true' || sessionStorage.getItem('isLoggedIn') === 'true';
            if (logged) {
                document.documentElement.classList.add('is-logged-in');
                window.isUserLoggedIn = true;
            }
        })();
    </script>
"@

function Sync-File($filePath, $isBlog) {
    if ($filePath -match "index.html" -or $filePath -match "admin.html" -or $filePath -match "blog-admin.html" -or $filePath -match "dashboard.html" -or $filePath -match "auth.html" -or $filePath -match "register.html" -or $filePath -match "social-callback.html" -or $filePath -match "checkout.html") { 
        return 
    }
    
    # Read with explicit UTF8 encoding
    $content = Get-Content -Path $filePath -Raw -Encoding UTF8
    
    # Remove leading junk
    $content = $content.TrimStart([char]0xFEFF, '?', ' ')
    
    $nav = $navbarTemplate
    $foot = $footerTemplate

    if ($isBlog) {
        $nav = $nav.Replace('../index.html', '../../index.html')
        $nav = $nav.Replace('blog.html', '../blog.html')
        $nav = $nav.Replace('api-docs.html', '../api-docs.html')
        $nav = $nav.Replace('auth.html', '../auth.html')
        $nav = $nav.Replace('dashboard.html', '../dashboard.html')
        
        $foot = $foot.Replace('../index.html', '../../index.html')
        $foot = $foot.Replace('pdf-to-word.html', '../pdf-to-word.html')
        $foot = $foot.Replace('word-to-pdf.html', '../word-to-pdf.html')
        $foot = $foot.Replace('pdf-to-jpg.html', '../pdf-to-jpg.html')
        $foot = $foot.Replace('jpg-to-pdf.html', '../jpg-to-pdf.html')
        $foot = $foot.Replace('merge-pdf.html', '../merge-pdf.html')
        $foot = $foot.Replace('split-pdf.html', '../split-pdf.html')
        $foot = $foot.Replace('compress-pdf.html', '../compress-pdf.html')
        $foot = $foot.Replace('sign-pdf.html', '../sign-pdf.html')
        $foot = $foot.Replace('ai-pdf-chat.html', '../ai-pdf-chat.html')
        $foot = $foot.Replace('ai-pdf-extraction.html', '../ai-pdf-extraction.html')
        $foot = $foot.Replace('ai-smart-rewrite.html', '../ai-smart-rewrite.html')
        $foot = $foot.Replace('ai-pdf-podcast.html', '../ai-pdf-podcast.html')
        $foot = $foot.Replace('../about.html', '../../about.html')
        $foot = $foot.Replace('blog.html', '../blog.html')
        $foot = $foot.Replace('education.html', '../education.html')
        $foot = $foot.Replace('api-docs.html', '../api-docs.html')
        $foot = $foot.Replace('../privacy.html', '../../privacy.html')
        $foot = $foot.Replace('../terms.html', '../../terms.html')
        $foot = $foot.Replace('../contact.html', '../../contact.html')
    }

    # Clean up multiple duplicated script blocks BEFORE injecting the new one
    $loginBlockPattern = "(?s)\s*<script>.*?// Critical: Instant Login Check.*?</script>"
    $content = [regex]::Replace($content, $loginBlockPattern, "")
    
    # Inject one clean block into head
    $content = $content.Replace("</head>", "$loginCheckTemplate`n</head>")

    # Restore missing meta tags
    if (-not $content.Contains("<meta charset=`"UTF-8`">") -and -not $content.Contains('<meta charset="UTF-8">')) {
        $content = $content.Replace("<head>", "<head>`n    <meta charset=`"UTF-8`">")
    }

    # Sync Navbar and Footer
    $content = [regex]::Replace($content, "<nav.*?>.*?</nav>", $nav, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    $content = [regex]::Replace($content, "<footer.*?>.*?</footer>", $foot, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    
    # Sync main.js and inject if missing
    $jsProjectVersion = "3.3"
    $jsPathWithVersion = if ($isBlog) { "../../js/main.js?v=$jsProjectVersion" } else { "../js/main.js?v=$jsProjectVersion" }
    
    if ($content.Contains("main.js")) {
        $content = [regex]::Replace($content, '<script src=".*?js/main\.js.*?"></script>', "<script src=`"$jsPathWithVersion`"></script>")
    } else {
        $content = $content.Replace("</body>", "<script src=`"$jsPathWithVersion`"></script>`n</body>")
    }

    # Final cleanup: ensure only one DOCTYPE and trim
    if ($content.Contains("<!DOCTYPE html>")) {
        $idx = $content.IndexOf("<!DOCTYPE html>")
        if ($idx -gt 0) { $content = $content.Substring($idx) }
    }

    # Write back as UTF8 (No BOM)
    $utf8NoBOM = New-Object System.Text.UTF8Encoding $false
    [IO.File]::WriteAllText($filePath, $content, $utf8NoBOM)
    Write-Host "Cleaned and Synced: $filePath"
}

# Run
Get-ChildItem -Path $targetDir -Filter "*.html" | ForEach-Object { Sync-File $_.FullName $false }
Get-ChildItem -Path $blogDir -Filter "*.html" | ForEach-Object { Sync-File $_.FullName $true }

Write-Host ""
Write-Host "Global sync complete (encoding-safe version)!" -ForegroundColor Green
