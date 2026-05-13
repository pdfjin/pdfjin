$frontendDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend"
$htmlFiles = Get-ChildItem -Path $frontendDir -Filter "*.html" -Recurse

foreach ($file in $htmlFiles) {
    if ($file.Name -match "index_restored.html") { continue }
    
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    
    # 1. Replace index.html links with root /
    $content = [regex]::Replace($content, 'href="(\.\./)*index\.html(#\w+)?"', { 
        param($m) 
        if ($m.Groups[2].Success) { "href=`"/$($m.Groups[2].Value)`"" } else { "href=`"/`"" }
    })
    
    # 2. Add or update canonical tag
    $relPath = $file.FullName.Replace($frontendDir + "\", "").Replace("\", "/")
    if ($relPath -eq "index.html") {
        $canonicalUrl = "https://pdfjin.com/"
    } else {
        $canonicalUrl = "https://pdfjin.com/$relPath"
    }
    
    $canonicalTag = "<link rel=`"canonical`" href=`"$canonicalUrl`" />"
    
    if ($content.Contains('<link rel="canonical"')) {
        $content = [regex]::Replace($content, '<link rel="canonical" href="[^"]+" />', $canonicalTag)
    } elseif ($content.Contains('</head>')) {
        $content = $content.Replace('</head>', "    $canonicalTag`n</head>")
    }
    
    [IO.File]::WriteAllText($file.FullName, $content, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "Processed Canonical: $($file.Name)"
}
