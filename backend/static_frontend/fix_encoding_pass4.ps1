# Pass 4 - Fix remaining garble patterns
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
        
        # Triple right single quote / apostrophe (')
        $hex = $hex.Replace("C383C2A2C3A2E282ACC5A1C382C2ACC383C2A2C3A2E282ACC5BEC382C2A2", (ToHex "'"))
        
        # Triple em dash in blog content: various forms
        # Ã¢â€šÂ¬Ã¢â‚¬Â pattern
        $hex = $hex.Replace("C383C2A2C3A2E282ACC5A1C382C2ACC383C2A2C3A2E2809AC2ACC382C29D", (ToHex "-"))
        
        # Triple bullet in meta-divider (already caught as &bull; but any remaining)
        $hex = $hex.Replace("C383C2A2C3A2E282ACC5A1C382C2ACC383E2809AC382C2A2", (ToHex "-"))
        
        # Triple left double quote (") 
        $hex = $hex.Replace("C383C2A2C3A2E282ACC5A1C382C2ACC383C2A2C3A2E282ACC5BEC382C29C", (ToHex '"'))
        
        # Triple right double quote (")
        $hex = $hex.Replace("C383C2A2C3A2E282ACC5A1C382C2ACC383C2A2C3A2E282ACC5BEC382C29D", (ToHex '"'))
        
        # Triple 4-byte emoji prefix: C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385
        # This is the start of any triple-encoded 4-byte emoji
        # We need to match the full sequence including the last bytes
        # Let's replace the whole prefix + various endings
        
        # Triple emoji full patterns (with different endings for different emoji)
        # 📄 (file): prefix + E2809CC383E2809AC382C284
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C284", (ToHex "&#128196;"))
        # 📄 alternate ending
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383C2A2C3A2E2809AC2ACC385C2BE", (ToHex "&#128196;"))
        # 📤 (upload)
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383C2A2C3A2E2809AC2ACC382C2A4", (ToHex "&#128228;"))
        # 📝 (memo)
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C29D", (ToHex "&#128221;"))
        # 📦 (package)
        $hex = $hex.Replace("C383C692C382C2B0C383E280A6C382C2B8C383C2A2C3A2E2809AC2ACC385E2809CC383E2809AC382C2A6", (ToHex "&#128230;"))
        
        # Now match the generic triple prefix and replace remaining with a placeholder
        # C383C692C382C2B0C383E280A6C382C2B8 is the triple encoding of F0 9F (emoji prefix)
        # After that comes the category+codepoint bytes
        # Let's catch remaining ones generically and replace with &#128196; (file emoji as fallback)
        while ($hex.Contains("C383C692C382C2B0C383E280A6C382C2B8")) {
            $prefixIdx = $hex.IndexOf("C383C692C382C2B0C383E280A6C382C2B8")
            # Replace the prefix (32 chars) + next 48 chars (typical triple 4-byte emoji)
            $endIdx = $prefixIdx + 32 + 48
            if ($endIdx -le $hex.Length) {
                $hex = $hex.Substring(0, $prefixIdx) + (ToHex "&#128196;") + $hex.Substring($endIdx)
            }
            else {
                break
            }
        }
        
        # Also catch remaining double-level garble with prefix C383C2A2 (garbled C3 A2)
        # These are typically dashes, quotes, etc
        # Triple ← remaining
        $hex = $hex.Replace("C383C2A2C3A2E2809AC2ACC382C2A0C383E2809AC382C290", (ToHex "&larr;"))
        # Triple → remaining
        $hex = $hex.Replace("C383C2A2C3A2E2809AC2ACC382C2A0C383C2A2C3A2E2809AC2ACC3A2E2809EC2A2", (ToHex "&rarr;"))
        
        # Fix &amp; issues - they should just be & in HTML
        # &amp;hearts; -> &hearts;  (entity rendering)
        $hex = $hex.Replace((ToHex "&amp;hearts;"), (ToHex "&hearts;"))
        $hex = $hex.Replace((ToHex "&amp;middot;"), (ToHex "&middot;"))
        $hex = $hex.Replace((ToHex "&amp;copy;"), (ToHex "&copy;"))
        $hex = $hex.Replace((ToHex "&amp;larr;"), (ToHex "&larr;"))
        $hex = $hex.Replace((ToHex "&amp;rarr;"), (ToHex "&rarr;"))
        $hex = $hex.Replace((ToHex "&amp;mdash;"), (ToHex "&mdash;"))
        $hex = $hex.Replace((ToHex "&amp;bull;"), (ToHex "&bull;"))
        $hex = $hex.Replace((ToHex "&amp;rsquo;"), (ToHex "&rsquo;"))
        
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
Write-Host "Pass 4 fixed $fixedCount files." -ForegroundColor Cyan
