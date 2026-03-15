$blogDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
$fixes = @(
    @('m is spell', 'misspell'),
    @('m is s', 'miss'),
    @('l is ts', 'lists'),
    @('d is play', 'display'),
    @('exp and ed', 'expanded'),
    @('Tablesare', 'Tables are'),
    @('we', 'we'),
    @('Itit''s', "It's"),
    @('Words editing', "Word's editing"),
    @('we''ve', "we've"),
    @('it''s', "it's"),
    @('s', "'s"),
    @('', ""),
    @('filesfrom', 'files from'),
    @('is Better', 'is Better'),
    @('is how', 'is how'),
    @('is designed', 'is designed'),
    @('is as', 'is as'),
    @('is just', 'is just'),
    @('is our', 'is our')
)

Get-ChildItem -Path $blogDir -Filter "*.html" | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    
    foreach ($fix in $fixes) {
        $content = $content -replace [regex]::Escape($fix[0]), $fix[1]
    }
    
    # Fix the duplicate 'we' if present
    $content = $content -replace "we we've", "we've"
    
    [IO.File]::WriteAllText($_.FullName, $content, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "Cleaned: $($_.Name)"
}
