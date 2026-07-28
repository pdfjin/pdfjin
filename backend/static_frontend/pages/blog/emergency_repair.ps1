$blogDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"

Get-ChildItem -Path $blogDir -Filter "*.html" | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    
    # 1. Undo the catastrophic 's' -> "'s" replacement
    # We target "'s" specifically. 
    $content = $content -replace "'s", "s"
    
    # 2. Undo the disastrous word splitting (e.g., "d is play" -> "display")
    # This targets " is " and " and " where they were inserted into words.
    # We use regex to find these patterns.
    $content = $content -replace " is ", "is"
    $content = $content -replace " and ", "and"
    
    # 3. Fix the broken HTML tags that were corrupted by the single quotes
    $content = $content -replace "<'script", "<script"
    $content = $content -replace "<'span", "<span"
    $content = $content -replace "<'nav", "<nav"
    $content = $content -replace "'src", "src"
    $content = $content -replace "cla's's", "class"
    
    # 4. Correct legitimate contractions that were broken by step 1
    # "it s" -> "it's", "we ve" -> "we've", etc.
    $content = $content -replace "it s", "it's"
    $content = $content -replace "we ve", "we've"
    $content = $content -replace "Don t", "Don't"
    $content = $content -replace "you ll", "you'll"
    $content = $content -replace "Word s", "Word's"
    
    # 5. Clean up duplicate "we"
    $content = $content -replace "we we've", "we've"
    
    # 6. Final tag cleanup
    $content = $content -replace "<'/", "</"
    
    [IO.File]::WriteAllText($_.FullName, $content, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "Emergency Repair: $($_.Name)"
}
