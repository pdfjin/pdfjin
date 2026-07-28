# Absolute final cleanup - remove ALL remaining non-ASCII garble
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

        # Remaining patterns from sign-pdf debug:
        # 1. &#128196; followed by garble: EFBFBDE2809AC2ACC382C2B9 (partial ✍️ remnant)
        #    followed by: 20C2AFC383E2809AC382C2B8C383E2809AC382C28F
        # Full: 26233132383139363BEFBFBDE2809AC2ACC382C2B920C2AFC383E2809AC382C2B8C383E2809AC382C28F
        # This should just be &#9997; (✍) instead of &#128196; + garble
        $hex = $hex.Replace("26233132383139363BEFBFBDE2809AC2ACC382C2B920C2AFC383E2809AC382C2B8C383E2809AC382C28F", (ToHex "&#9997;"))

        # 2. Any remaining EFBFBD (U+FFFD replacement char) followed by garble bytes
        # These are all remnants of partial fixes - remove them
        # EFBFBD + E2809A + C2AC + C382 + C2B9 = leftover
        $hex = $hex.Replace("EFBFBDE2809AC2ACC382C2B9", "")
        
        # 3. Orphan C2AF + C383 + E2809A + C382 + C2B8 + C383 + E2809A + C382 + C28F
        # This is the second half of the garbled ✍️
        $hex = $hex.Replace("C2AFC383E2809AC382C2B8C383E2809AC382C28F", "")
        
        # 4. Any remaining C383E2809A sequences (double-encoded continuation bytes)
        $hex = $hex.Replace("C383E2809AC382C2B8C383E2809AC382C28F", "")
        $hex = $hex.Replace("C383E2809AC382C2B3", "")  # garbled part of ⏳
        $hex = $hex.Replace("C383E2809AC382C28F", "")  # variation selector garble
        $hex = $hex.Replace("C383E2809AC382C290", "")  # garbled arrow part
        
        # 5. Remaining C383C2A2 (double a-circumflex prefix)
        $hex = $hex.Replace("C383C2A2C3A2E2809AC2ACC382C2A0", (ToHex "&larr;"))
        $hex = $hex.Replace("C383C2A2C3A2E2809AC2ACC3A2E2809EC2A2", (ToHex "&rarr;"))
        
        # 6. C383E280A6 sequences (double-encoded ... part)
        $hex = $hex.Replace("C383E280A6C3A2E282ACC593", "")
        
        # 7. C382C2B9 orphan (double-encoded superscript)
        $hex = $hex.Replace("C382C2B9", "")
        
        # 8. C2AF orphan
        $hex = $hex.Replace("20C2AF20", "20")
        
        # 9. EFBFBD (replacement character) - remove any remaining
        $hex = $hex.Replace("EFBFBD", "")
        
        # 10. C281 orphan after entity
        $hex = $hex.Replace("26233132383139363BC281", "26233132383139363B")
        $hex = $hex.Replace("26233132383139363BC28D", "26233132383139363B")
        
        # 11. Any remaining C383 followed by various garble - nuclear option
        # Match C383 + next 2-8 bytes until we hit a normal ASCII byte
        while ($hex.Contains("C383")) {
            $idx = $hex.IndexOf("C383")
            # Find extent of garble sequence
            $endIdx = $idx + 4
            while ($endIdx + 2 -le $hex.Length) {
                $nextByte = $hex.Substring($endIdx, 2)
                # If next byte is normal ASCII (20-7E), stop
                $byteVal = [Convert]::ToInt32($nextByte, 16)
                if ($byteVal -ge 0x20 -and $byteVal -le 0x7E) { break }
                $endIdx += 2
            }
            # Replace entire garble sequence with a space
            $hex = $hex.Substring(0, $idx) + $hex.Substring($endIdx)
        }
        
        # 12. Clean up remaining C2xx orphans (non-ASCII Latin continuation bytes)
        # Only remove if they're clearly garble (between ASCII chars)
        # C2AC, C2B9, C2AF, C2B8, C28F, C281, C28D
        foreach ($orphan in @("C2AC", "C2B9", "C2AF", "C2B8", "C28F", "C281", "C28D")) {
            # Only remove if preceded and followed by ASCII or entity
            $hex = $hex.Replace("3B" + $orphan + "3C", "3B3C")  # between ; and <
            $hex = $hex.Replace("3B" + $orphan + "20", "3B20")  # between ; and space
            $hex = $hex.Replace("20" + $orphan + "20", "20")     # between spaces
            $hex = $hex.Replace("20" + $orphan + "3C", "203C")   # between space and <
        }
        
        # 13. Clean up double/triple spaces
        while ($hex.Contains("202020")) { $hex = $hex.Replace("202020", "20") }

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
Write-Host "ABSOLUTE FINAL pass fixed $fixedCount files." -ForegroundColor Cyan
