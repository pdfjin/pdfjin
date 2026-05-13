$frontendDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend"
$htmlFiles = Get-ChildItem -Path $frontendDir -Filter "*.html" -Recurse

$existingFiles = @{}
$htmlFiles | ForEach-Object { $existingFiles[$($_.FullName)] = $true }

$brokenLinks = @()

foreach ($file in $htmlFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    # Simple regex for href links
    $matches = [regex]::Matches($content, 'href="([^"#:]+\.html)(#[^"]*)?"')
    
    foreach ($m in $matches) {
        $link = $m.Groups[1].Value
        
        # Combine base dir of file with link path
        $baseDir = Split-Path $file.FullName
        $targetPath = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($baseDir, $link))
        
        if (-not $existingFiles.ContainsKey($targetPath)) {
            $brokenLinks += [PSCustomObject]@{
                Source = $file.FullName.Replace($frontendDir, "")
                Link = $link
                Resolved = $targetPath.Replace($frontendDir, "")
            }
        }
    }
}

if ($brokenLinks.Count -gt 0) {
    Write-Host "Found $($brokenLinks.Count) broken links:" -ForegroundColor Red
    $brokenLinks | Format-Table
} else {
    Write-Host "No broken internal links found." -ForegroundColor Green
}
