# Fix exact remaining garble bytes: A2E2809AC2AC and C2A2
$dirs = @(
    "c:\Users\ADMIN\Desktop\pdfjin\frontend\pages",
    "c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
)

$fixedCount = 0

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) { continue }
    Get-ChildItem -Path $dir -Filter "*.html" | ForEach-Object {
        $filePath = $_.FullName
        $bytes = [IO.File]::ReadAllBytes($filePath)
        
        $sb = New-Object System.Text.StringBuilder($bytes.Length * 2)
        foreach ($b in $bytes) { [void]$sb.Append($b.ToString("X2")) }
        $hex = $sb.ToString()
        $originalHex = $hex

        # Remove: A2E2809AC2AC (orphan garble after emoji entities)
        $hex = $hex.Replace("A2E2809AC2AC", "")
        
        # Remove: C2A2 when between > and space or space and < (orphan ¢)
        $hex = $hex.Replace("3E20C2A2200D", "3E200D")
        $hex = $hex.Replace("20C2A220", "20")
        
        # Remove standalone E2809A (‚ garble)
        $hex = $hex.Replace("3BE2809A3C", "3B3C")
        $hex = $hex.Replace("3BE2809A20", "3B20")

        if ($hex -ne $originalHex) {
            $newBytes = New-Object byte[] ($hex.Length / 2)
            for ($i = 0; $i -lt $hex.Length; $i += 2) {
                $newBytes[$i / 2] = [Convert]::ToByte($hex.Substring($i, 2), 16)
            }
            [IO.File]::WriteAllBytes($filePath, $newBytes)
            Write-Host "  FIXED: $filePath" -ForegroundColor Green
            $fixedCount++
        }
        else {
            Write-Host "  ok: $filePath" -ForegroundColor Gray
        }
    }
}

Write-Host "`nFixed $fixedCount files." -ForegroundColor Cyan
