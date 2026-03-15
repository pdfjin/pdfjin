$cssDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend\css"
$files = Get-ChildItem -Path $cssDir -Filter "*.css" -Recurse
foreach ($file in $files) {
    $content = Get-Content $file.FullName
    for ($i = 0; $i -lt $content.Length; $i++) {
        $line = $content[$i]
        if ($line -match '^\s*[a-z-]+\s+[^:;]+;\s*$') {
            if ($line -notmatch ':') {
                Write-Host "$($file.Name):$($i+1): $line"
            }
        }
    }
}
