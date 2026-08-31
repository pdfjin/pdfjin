$FRONTEND_DIR = "c:\Users\ADMIN\Desktop\pdfjin\frontend"
$OUTPUT_FILE = "$FRONTEND_DIR\sitemap.xml"
$BASE_URL = "https://pdfjin.com"
$TODAY = Get-Date -Format "yyyy-MM-dd"

Write-Host "Generating sitemap..."

$urls = @()

# 1. Homepage
$urls += [PSCustomObject]@{ loc = "$BASE_URL/"; lastmod = $TODAY; priority = "1.0" }

# 2. Main Site Pages (Root)
Get-ChildItem -Path "$FRONTEND_DIR\*.html" -Exclude "index.html", "index_restored.html", "auth.html", "register.html", "dashboard.html", "sitemap_new.xml" | ForEach-Object {
    $urls += [PSCustomObject]@{ loc = "$BASE_URL/$($_.Name)"; lastmod = $TODAY; priority = "0.8" }
}

# 3. Tool Pages
# Excluded: already in root, or utility pages like auth-isolated, social-callback, etc.
Get-ChildItem -Path "$FRONTEND_DIR\pages\*.html" -Exclude "auth.html", "register.html", "dashboard.html", "blog-admin.html", "social-callback.html", "auth-isolated.html", "edit-pdf-isolated.html", "watermark-pdf-clean.html", "admin.html", "checkout.html" | ForEach-Object {
    $priority = "0.9"
    if ($_.Name.StartsWith("ai-")) { $priority = "1.0" }
    $urls += [PSCustomObject]@{ loc = "$BASE_URL/pages/$($_.Name)"; lastmod = $TODAY; priority = $priority }
}

# 4. Blog Posts
Get-ChildItem -Path "$FRONTEND_DIR\pages\blog\*.html" -Exclude "blog.html" | ForEach-Object {
    if ($_.Name -notmatch "heal_|polish_|cleanup_") {
        $urls += [PSCustomObject]@{ loc = "$BASE_URL/pages/blog/$($_.Name)"; lastmod = $TODAY; priority = "0.7" }
    }
}

# 5. FAQ Pages
if (Test-Path "$FRONTEND_DIR\faq") {
    Get-ChildItem -Path "$FRONTEND_DIR\faq\*.html" | ForEach-Object {
        $name_without_ext = $_.Name.Replace(".html", "")
        $urls += [PSCustomObject]@{ loc = "$BASE_URL/faq/$name_without_ext"; lastmod = $TODAY; priority = "0.9" }
    }
}

# Build XML output
$xml = @()
$xml += '<?xml version="1.0" encoding="UTF-8"?>'
$xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

foreach ($u in $urls) {
    $xml += "  <url>"
    $xml += "    <loc>$($u.loc)</loc>"
    $xml += "    <lastmod>$($u.lastmod)</lastmod>"
    $xml += "    <priority>$($u.priority)</priority>"
    $xml += "  </url>"
}

$xml += '</urlset>'

$xml | Out-File -FilePath $OUTPUT_FILE -Encoding UTF8
Write-Host "Success! Sitemap updated at $OUTPUT_FILE"
Write-Host "Found $($urls.Count) URLs."
