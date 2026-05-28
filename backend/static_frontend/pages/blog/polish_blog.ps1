$blogDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"

Get-ChildItem -Path $blogDir -Filter "*.html" | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    
    # 1. Fix programming terms (Case sensitivity restoration)
    $content = $content -replace "JsON", "JSON"
    $content = $content -replace "localstorage", "localStorage"
    $content = $content -replace "sessionstorage", "sessionStorage"
    $content = $content -replace "classlist", "classList"
    $content = $content -replace "navbar scrolled", "navbar scrolled"
    
    # 2. Fix fused words (Surgical restoration)
    $content = $content -replace "sharingandviewing", "sharing and viewing"
    $content = $content -replace "WordisBetter", "Word is Better"
    $content = $content -replace "Thisisa", "This is a"
    $content = $content -replace "Nightmare is", "Nightmare for"
    $content = $content -replace "tablesandindented", "tables and indented"
    $content = $content -replace "fontis", "fonts"
    $content = $content -replace "images stay", "images stay"
    $content = $content -replace "PDFjinisdesigned", "PDFjin is designed"
    $content = $content -replace "Hereishow", "Here is how"
    $content = $content -replace "structureandmap", "structure and map"
    $content = $content -replace "engineisfine-tuned", "engine is fine-tuned"
    $content = $content -replace "columnsandnested", "columns and nested"
    $content = $content -replace "nowandstart", "now and start"
    $content = $content -replace "PitfallsandHow", "Pitfalls and How"
    $content = $content -replace "rowandcolumn", "row and column"
    $content = $content -replace "Mattersisit'safe", "Matters Is it safe"
    $content = $content -replace "privacyisour", "privacy is our"
    $content = $content -replace "free,andprivacy", "free, and privacy"
    $content = $content -replace "display:", "display:"
    
    # 3. Fix Case in text
    $content = $content -replace "step-by-step", "Step-by-step"
    $content = $content -replace "sign In", "Sign In"
    $content = $content -replace "Get started", "Get Started"
    
    # 4. Remove any remaining weird replacement chars  if they survived
    $content = $content -replace "", ""
    
    [IO.File]::WriteAllText($_.FullName, $content, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "Polished: $($_.Name)"
}
