# ============================================================
#  PDFjin - FINAL Encoding Fix (Pass 3)
#  Targets ALL remaining garbled hex byte patterns
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

        # Helper: string to hex
        function ToHex($str) { 
            return ([BitConverter]::ToString([System.Text.Encoding]::UTF8.GetBytes($str))) -replace '-', ''
        }
        
        # === REMAINING SINGLE-GARBLE patterns (from navbar/footer templates) ===
        # X logo: C3B0C29DE280A2C28F -> &#120143; (was garbled 𝕏)
        $hex = $hex.Replace("C3B0C29DE280A2C28F", (ToHex "&#120143;"))
        # Option key: C3A2C28CC2A5 -> &#8997; (was garbled ⌥)
        $hex = $hex.Replace("C3A2C28CC2A5", (ToHex "&#8997;"))
        # Heart: C3A2C29DC2A4C3AFC2B8C28F -> &hearts; (was garbled ❤️)
        $hex = $hex.Replace("C3A2C29DC2A4C3AFC2B8C28F", (ToHex "&amp;hearts;"))
        # Heart without VS16: C3A2C29DC2A4 -> &hearts;
        $hex = $hex.Replace("C3A2C29DC2A4", (ToHex "&amp;hearts;"))

        # === TRIPLE-ENCODED blog patterns ===
        # Triple bullet/dot (•): C383C692C382C2A2C383C2A2C3A2E282ACC5A1C382C2ACC383E2809AC382C2A2
        $hex = $hex.Replace("C383C692C382C2A2C383C2A2C3A2E282ACC5A1C382C2ACC383E2809AC382C2A2", (ToHex "&amp;bull;"))
        
        # Triple apostrophe/right single quote ('): C383C692C382C2A2C383C2A2C3A2E282ACC5BEC382C2A2
        $hex = $hex.Replace("C383C692C382C2A2C383C2A2C3A2E282ACC5BEC382C2A2", (ToHex "&amp;rsquo;"))
        
        # Triple em dash (—): C383C692C382C2A2C383C2A2C3A2E282ACC5A1C382C2ACC383C2A2C3A2E2809AC2ACC382C29D
        $hex = $hex.Replace("C383C692C382C2A2C383C2A2C3A2E282ACC5A1C382C2ACC383C2A2C3A2E2809AC2ACC382C29D", (ToHex "&amp;mdash;"))
        
        # Triple em dash alternate: C383C692C382C2A2C383C2A2C3A2E282ACC5A1C382C2ACC383C2A2C3A2E280A0C382C29D (was different end byte)
        # Actually let me match the real hex from debug: for "—" in blog content
        # From scan: Ã¢â€šÂ¬Ã¢â‚¬Â = em dash in blog text
        $hex = $hex.Replace("C383C2A2C3A2E282ACC5A1C382C2ACC383C2A2C3A2E2809AC2ACC382C29D", (ToHex "&amp;mdash;"))

        # === DOUBLE-ENCODED patterns still remaining ===
        # Double bullet: C3A2E282ACC2A2 -> &bull;
        $hex = $hex.Replace("C3A2E282ACC2A2", (ToHex "&amp;bull;"))
        # Double apostrophe: C3A2E282ACC2A2 (same as bullet sometimes)
        # Double right single quote: C3A2E280B0C2A2
        $hex = $hex.Replace("C3A2E280B0C2A2", (ToHex "&amp;rsquo;"))
        
        # === FIX double-escaped &amp;amp; patterns ===
        # &amp;amp;middot; -> &amp;middot;
        $hex = $hex.Replace((ToHex "&amp;amp;middot;"), (ToHex "&amp;middot;"))
        $hex = $hex.Replace((ToHex "&amp;amp;hearts;"), (ToHex "&amp;hearts;"))
        $hex = $hex.Replace((ToHex "&amp;amp;copy;"), (ToHex "&amp;copy;"))
        $hex = $hex.Replace((ToHex "&amp;amp;larr;"), (ToHex "&amp;larr;"))
        $hex = $hex.Replace((ToHex "&amp;amp;rarr;"), (ToHex "&amp;rarr;"))
        $hex = $hex.Replace((ToHex "&amp;amp;mdash;"), (ToHex "&amp;mdash;"))
        $hex = $hex.Replace((ToHex "&amp;amp;bull;"), (ToHex "&amp;bull;"))
        $hex = $hex.Replace((ToHex "&amp;amp;rsquo;"), (ToHex "&amp;rsquo;"))
        
        # === FIX triple+ &amp;amp;amp; patterns ===
        $hex = $hex.Replace((ToHex "&amp;amp;amp;"), (ToHex "&amp;amp;"))
        
        # === word-to-pdf.html specific: icon-box garbled emoji ===
        # Triple 📄→📄 pattern (arrow between icons)
        # From scan: ÃƒÂ°Ã…Â¸Ã¢â‚¬Å"Ã‚Â→ÃƒÂ°Ã…Â¸Ã¢â‚¬Å"Ã¢â‚¬Å¾
        # The triple 📄: C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C284
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C284", (ToHex "&#128196;"))
        # Triple 📄 alternate (ending C2B4 or other):
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383C2A2C3A2E2809AC2ACC385C2BE", (ToHex "&#128196;"))
        
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
Write-Host "Pass 3 fixed $fixedCount files." -ForegroundColor Cyan
