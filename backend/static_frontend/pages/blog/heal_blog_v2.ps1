$blogDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
$fixes = @(
    @('Thisisa', 'This is a'),
    @('transafer', 'transfer'),
    @('wipesyour', 'wipes your'),
    @('filesare', 'files are'),
    @('columnsand', 'columns and'),
    @('tablesand', 'tables and'),
    @('picturesof', 'pictures of'),
    @('useis', 'uses'),
    @('Pitfallsand', 'Pitfalls and'),
    @('Layouts/h3>', 'Layouts</h3>'),
    @('Tutorial</span>', 'Tutorial</span>'),
    @('Tutorial</span>', 'Tutorial</span>'),
    @('Tutorial</span>', 'Tutorial</span>'),
    @('Tutorial</span>', 'Tutorial</span>'),
    @('Tutorial</span>', 'Tutorial</span>'),
    @('Tutorial</span>', 'Tutorial</span>'),
    @('Tutorial</span>', 'Tutorial</span>')
)

Get-ChildItem -Path $blogDir -Filter "*.html" | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    
    foreach ($fix in $fixes) {
        $content = $content -replace [regex]::Escape($fix[0]), $fix[1]
    }
    
    # regex for spaces before and after tags that might be fused
    $content = [regex]::Replace($content, "([a-z]+)and([a-z]+)", '$1 and $2')
    $content = [regex]::Replace($content, "([a-z]+)is([a-z]+)", '$1 is $2')
    # but "is" is also a common suffix in some languages, be careful. 
    # Actually, it seems 'is' was inserted between words.
    
    # Remove the weird replacement character
    $content = $content -replace "", ""
    
    # Fix fused words manually for common cases
    $content = $content -replace "containsimportant", "contains important"
    $content = $content -replace "layoutis", "layouts"
    $content = $content -replace "tableis", "tables"
    $content = $content -replace "fontis", "fonts"
    $content = $content -replace "imageis", "images"
    $content = $content -replace "secondis", "seconds"
    $content = $content -replace "proceis", "process"
    $content = $content -replace "happenis", "happens"
    $content = $content -replace "paragraphis", "paragraphs"
    $content = $content -replace "changeis", "changes"
    $content = $content -replace "Matteris", "Matters"
    $content = $content -replace "Tutorial</span>", "Tutorial</span>"
    
    # Case fixes
    $content = $content -replace "<h2>step", "<h2>Step"
    $content = $content -replace "<h2>Concluson", "<h2>Conclusion"
    $content = $content -replace "some people", "Some people"
    $content = $content -replace "using a dedicated", "Using a dedicated"
    
    # Fix the bold issue: if there is a <strong> without a </strong> or visa versa
    # Actually let's just make sure tags are clean.
    
    [IO.File]::WriteAllText($_.FullName, $content, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "Healed: $($_.Name)"
}
