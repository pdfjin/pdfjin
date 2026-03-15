# Fix encoding - byte-level approach
# No garbled strings in source code at all

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
        
        # Convert bytes to hex string for reliable pattern matching
        $hex = [BitConverter]::ToString($bytes) -replace '-', ''
        $originalHex = $hex
        
        # Replace corrupted byte sequences with their HTML entity equivalents
        # Each replacement: corrupted hex bytes -> ASCII hex of HTML entity
        
        # Helper to convert string to hex
        function ToHex($str) { 
            $b = [System.Text.Encoding]::UTF8.GetBytes($str)
            return ([BitConverter]::ToString($b) -replace '-', '')
        }
        
        # --- Fix garbled emoji bytes ---
        # C3 B0 C5 B8 E2 80 9C E2 80 9E = garbled file emoji -> &#128196;
        $hex = $hex.Replace("C3B0C5B8E28099E2809C", (ToHex "&#128196;"))
        $hex = $hex.Replace("C3B0C5B8E2809CE2809E", (ToHex "&#128196;"))
        $hex = $hex.Replace("C3B0C5B8E2809CE2809C", (ToHex "&#128196;"))
        # garbled upload emoji -> &#128228;
        $hex = $hex.Replace("C3B0C5B8E2809CC2A4", (ToHex "&#128228;"))
        $hex = $hex.Replace("C3B0C5B8E2809CE280B0", (ToHex "&#128228;"))
        # garbled compress emoji -> &#128230;
        $hex = $hex.Replace("C3B0C5B8E2809CC2A6", (ToHex "&#128230;"))
        
        # garbled scissors -> &#9986;
        $hex = $hex.Replace("C3A2C593E2809A", (ToHex "&#9986;"))
        $hex = $hex.Replace("C3A2C593E280AC", (ToHex "&#9986;"))
        
        # garbled lock emoji
        $hex = $hex.Replace("C3B0C5B8E28099E28098", (ToHex "&#128274;"))
        
        # --- Fix garbled arrows ---
        # garbled left arrow -> &larr;
        $hex = $hex.Replace("C3A2E280A0C2A0", (ToHex "&amp;larr;"))
        $hex = $hex.Replace("C3A2E280A0E28099", (ToHex "&amp;rarr;"))
        
        # --- Fix garbled special chars ---
        # garbled copyright -> &copy;
        $hex = $hex.Replace("C382C2A9", (ToHex "&amp;copy;"))
        # garbled middle dot -> &middot;
        $hex = $hex.Replace("C382C2B7", (ToHex "&amp;middot;"))
        # garbled em dash -> &mdash;
        $hex = $hex.Replace("C3A2E282ACE2809C", (ToHex "&amp;mdash;"))
        $hex = $hex.Replace("C3A2E282ACE28093", (ToHex "&amp;mdash;"))
        
        # --- Fix actual UTF-8 emoji (4-byte sequences that display wrong) ---
        # These are CORRECT UTF-8 bytes but display as garble because of encoding mismatch
        # F0 9F 93 84 = file emoji 📄 -> &#128196;
        $hex = $hex.Replace("F09F9384", (ToHex "&#128196;"))
        # F0 9F 93 A4 = upload emoji 📤 -> &#128228;
        $hex = $hex.Replace("F09F93A4", (ToHex "&#128228;"))
        # F0 9F 93 A6 = 📦 -> &#128230;
        $hex = $hex.Replace("F09F93A6", (ToHex "&#128230;"))
        # F0 9F 94 92 = 🔒 -> &#128274;
        $hex = $hex.Replace("F09F9492", (ToHex "&#128274;"))
        # F0 9F 96 8A = 🖊 -> &#128394;
        $hex = $hex.Replace("F09F968A", (ToHex "&#128394;"))
        # F0 9F 96 8B = 🖋 -> &#128395;
        $hex = $hex.Replace("F09F968B", (ToHex "&#128395;"))
        # F0 9F 97 A3 = 🗣 -> &#128483;
        $hex = $hex.Replace("F09F97A3", (ToHex "&#128483;"))
        # F0 9F A7 A0 = 🧠 -> &#129504;
        $hex = $hex.Replace("F09FA7A0", (ToHex "&#129504;"))
        # F0 9F 93 8A = 📊 -> &#128202;
        $hex = $hex.Replace("F09F938A", (ToHex "&#128202;"))
        # F0 9F 93 88 = 📈 -> &#128200;
        $hex = $hex.Replace("F09F9388", (ToHex "&#128200;"))
        # F0 9F 94 8D = 🔍 -> &#128269;
        $hex = $hex.Replace("F09F948D", (ToHex "&#128269;"))
        # F0 9F 96 BC = 🖼 -> &#128444;
        $hex = $hex.Replace("F09F96BC", (ToHex "&#128444;"))
        # F0 9F 93 83 = 📃 -> &#128195;
        $hex = $hex.Replace("F09F9383", (ToHex "&#128195;"))
        
        # E2 9C 82 = ✂ -> &#9986;
        $hex = $hex.Replace("E29C82", (ToHex "&#9986;"))
        # E2 86 90 = ← -> &larr;
        $hex = $hex.Replace("E28690", (ToHex "&amp;larr;"))
        # E2 86 92 = → -> &rarr;
        $hex = $hex.Replace("E28692", (ToHex "&amp;rarr;"))
        # E2 80 94 = — -> &mdash;
        $hex = $hex.Replace("E28094", (ToHex "&amp;mdash;"))
        # E2 9D A4 EF B8 8F = ❤️ -> &hearts;
        $hex = $hex.Replace("E29DA4EFB88F", (ToHex "&amp;hearts;"))
        # E2 9D A4 = ❤ -> &hearts;
        $hex = $hex.Replace("E29DA4", (ToHex "&amp;hearts;"))
        # C2 A9 = © -> &copy;
        $hex = $hex.Replace("C2A9", (ToHex "&amp;copy;"))
        # C2 B7 = · -> &middot;
        $hex = $hex.Replace("C2B7", (ToHex "&amp;middot;"))
        
        # F0 9F 95 B6 = ▶ play -> &#128310;
        $hex = $hex.Replace("F09F95B6", (ToHex "&#128310;"))
        # F0 9F 94 A7 = 🔧 -> &#128295;
        $hex = $hex.Replace("F09F94A7", (ToHex "&#128295;"))
        # F0 9F 93 9D = 📝 -> &#128221;
        $hex = $hex.Replace("F09F939D", (ToHex "&#128221;"))
        # F0 9F 93 B0 = 📰 -> &#128240;
        $hex = $hex.Replace("F09F93B0", (ToHex "&#128240;"))
        # F0 9F 8E A4 = 🎤 -> &#127908;
        $hex = $hex.Replace("F09F8EA4", (ToHex "&#127908;"))
        # F0 9F 8E 99 = 🎙 -> &#127897;
        $hex = $hex.Replace("F09F8E99", (ToHex "&#127897;"))
        # F0 9F 93 91 = 📑 -> &#128209;
        $hex = $hex.Replace("F09F9391", (ToHex "&#128209;"))
        # F0 9F 93 9C = 📜 -> &#128220;
        $hex = $hex.Replace("F09F939C", (ToHex "&#128220;"))
        # F0 9F 94 84 = 🔄 -> &#128260;
        $hex = $hex.Replace("F09F9484", (ToHex "&#128260;"))
        # EF B8 8F = variation selector 16 (remove)
        $hex = $hex.Replace("EFB88F", "")
        
        if ($hex -ne $originalHex) {
            # Convert hex back to bytes
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
Write-Host "Fixed $fixedCount files." -ForegroundColor Cyan
