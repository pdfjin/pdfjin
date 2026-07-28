# ============================================================
#  PDFjin - Fix Triple/Double Encoding (Byte-Level Pass 2)
#  Targets the exact hex patterns found in corrupted files
# ============================================================

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
        
        # === TRIPLE-ENCODED PATTERNS (exact bytes from debug output) ===
        
        # Triple ← (left arrow): C383C692C382C2A2C383C2A2C3A2E2809AC2ACC382C2A0C383E2809AC382C290
        $hex = $hex.Replace("C383C692C382C2A2C383C2A2C3A2E2809AC2ACC382C2A0C383E2809AC382C290", "266C6172723B")
        
        # Triple → (right arrow): C383C692C382C2A2C383C2A2C3A2E2809AC2ACC382C2A0C383C2A2C3A2E2809AC2ACC3A2E2809EC2A2
        $hex = $hex.Replace("C383C692C382C2A2C383C2A2C3A2E2809AC2ACC382C2A0C383C2A2C3A2E2809AC2ACC3A2E2809EC2A2", "26726172723B")
        # Triple → alternate
        $hex = $hex.Replace("C383C692C382C2A2C383C2A2C3A2E2809AC2ACC3A2E280A0C383C2A2C3A2E2809AC2ACC3A2E2809EC2A2", "26726172723B")
        
        # Triple 📄 (file emoji): starts with C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C284
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C284", "2623313238313936 3B")
        
        # Triple 📤 (upload):
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383C2A2C3A2E2809AC2ACC382C2B0", "26233132383232383B")
        
        # Triple 📦 (package/compress): C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C2A6
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C2A6", "26233132383233303B")
        
        # Triple ✂ (scissors): 
        $hex = $hex.Replace("C383C692C382C2A2C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C2A2", "2623393938363B")
        
        # Triple 📬 (compass/icons that start with F09F93):
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383C2A2C3A2E2809AC2ACC382C2B0", "26233132383232383B")
        
        # Triple © : C383C692C382C2A9
        $hex = $hex.Replace("C383C692C382C2A9", "26636F70793B")
        
        # Triple · : C383C692C382C2B7
        $hex = $hex.Replace("C383C692C382C2B7", "266D6964646F743B")
        
        # Triple — (em dash):
        $hex = $hex.Replace("C383C692C382C2A2C383C2A2C3A2E2809AC2ACC3A2E280A0C383C2A2C3A2E2809AC2ACC382C2A0", "266D646173683B")
        
        # Triple ❤ :
        $hex = $hex.Replace("C383C692C382C2A2C383C2A2C3A2E2809AC2ACC382C2A0C383C2A2C3A2E2809AC2ACC384C2A4", "266865617274733B")
        
        # === DOUBLE-ENCODED PATTERNS ===        
        # Double ← : C383C2A2C3A2E2809AC2ACC382C2A0C383E2809AC382C290
        $hex = $hex.Replace("C383C2A2C3A2E2809AC2ACC382C2A0C383E2809AC382C290", "266C6172723B")
        # Double ← alternate: C383C2A2C3A2E2809AC2ACC382C2A0
        $hex = $hex.Replace("C383C2A2C3A2E280A0C382C2A0", "266C6172723B")
        
        # Double → : C383C2A2C3A2E2809AC2ACC382C2A0C383C2A2C3A2E2809AC2ACC3A2E2809EC2A2
        $hex = $hex.Replace("C383C2A2C3A2E280A0C3A2E2809EC2A2", "26726172723B")
        
        # Double 📄: C383C2B0C385C2B8C3A2E2809CC3A2E2809E
        $hex = $hex.Replace("C383C2B0C385C2B8C3A2E2809CC3A2E2809E", "2623313238313936 3B")
        
        # Double ©: C382C2A9 (already handled in pass 1)
        # Double ·: C382C2B7 (already handled in pass 1)
        
        # === Remaining garble cleanup ===
        # Any remaining C383C692 prefix (triple-encode marker for Latin chars)
        # C383C692 = triple encode of C3xx byte
        
        # Clean up spaces in hex entities we inserted
        $hex = $hex.Replace("2623313238313936 3B", "26233132383139363B")
        
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
Write-Host "Pass 2 fixed $fixedCount files." -ForegroundColor Cyan
