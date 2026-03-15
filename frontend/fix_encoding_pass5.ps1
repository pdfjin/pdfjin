# Pass 5 - Final cleanup of remaining two patterns
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
        $hex = ([BitConverter]::ToString($bytes)) -replace '-', ''
        $originalHex = $hex

        function ToHex($str) { 
            return ([BitConverter]::ToString([System.Text.Encoding]::UTF8.GetBytes($str))) -replace '-', ''
        }
        
        # 1. Fix remaining garbled ⌥ (option key icon): C3A2C28CC2A5
        # Actually check what bytes are present
        # From viewer: âŒ¥ = UTF-8 bytes E2 8C A5 which is garbled as C3A2 C28C C2A5
        $hex = $hex.Replace("C3A2C28CC2A5", (ToHex "&#8997;"))
        
        # 2. Fix remaining partial apostrophe: ÃƒÂ¢' 
        # ÃƒÂ¢ = C383C2A2 followed by ' (27) = right single quote remnant
        $hex = $hex.Replace("C383C2A227", (ToHex "'"))
        
        # 3. Fix remaining Ã patterns that are partial garble
        # ÃƒÂ¢ followed by various chars
        # This is a double-encoded â (C3A2) which then got partially fixed
        # C383C2A2 = double-encoded â, need to check what follows
        
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

Write-Host ""
Write-Host "Pass 5 fixed $fixedCount files." -ForegroundColor Cyan
