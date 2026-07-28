$blogDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
$fixes = @(
    @('<scan', '<span'),
    @('paragraphis', 'paragraphs'),
    @('paragraphi', 'paragraphs'),
    @('changeis', 'changes'),
    @('happenis', 'happens'),
    @('fontis', 'fonts'),
    @('imageis', 'images'),
    @('proceis', 'process'),
    @('secondis', 'seconds'),
    @('layoutis', 'layouts'),
    @('tableis', 'tables'),
    @('juis', 'just'),
    @('uis ', 'use '),
    @(' uis', ' use'),
    @('boundarieis', 'boundaries'),
    @('Matteris', 'Matters'),
    @('eais ', 'easy '),
    @('miis ', 'miss '),
    @('thois', 'those'),
    @('liss', 'lists'),
    @('stting', 'setting'),
    @('sngle', 'single'),
    @('\.xlis', '.xlsx'),
    @('headleis', 'headless'),
    @('physcal', 'physical'),
    @('preirved', 'preserved'),
    @('presntation', 'presentation'),
    @('profeisonal', 'professional'),
    @('remaisin', 'remains in'),
    @('remaisp', 'remains p'),
    @('remainsp', 'remains p'),
    @('sddingly', 'suddenly'),
    @('fruserat', 'frustrat'),
    @('guest ', 'guess '),
    @('ishow ', 'is how '),
    @('isfine-tuned', 'is fine-tuned'),
    @('fresly', 'freshly'),
    @('wasee', 'waste'),
    @('insde', 'inside'),
    @('Images/h3>', 'Images</h3>'),
    @('isBetter', 'is Better'),
    @('isdesigned', 'is designed'),
    @('isour', 'is our'),
    @('isjuis', 'is just'),
    @('isas ', 'is as '),
    @('simple ais', 'simple as'),
    @('we', 'we'),
    @('It ''s', "It's"),
    @('Word ''sediting', "Word's editing"),
    @('&mdas;', '&mdash;'),
    @('containis', 'contains'),
    @('nightmare for', 'nightmare for'),
    @('houris', 'hours'),
    @('minute is', 'minute'),
    @('secondsright', 'seconds right'),
    @('incredbly', 'incredibly'),
    @('expensave', 'expensive'),
    @('Tutorial</span>', 'Tutorial</span>'),
    @('<scan class="category-badge">', '<span class="category-badge">'),
    @('<scan class="meta-divider">', '<span class="meta-divider">'),
    @('converterswill', 'converters will'),
    @('PDFsare', 'PDFs are'),
    @('containsimportant', 'contains important'),
    @('saysin', 'stays in'),
    @('sop ', 'stop '),
    @('hourstyping', 'hours typing'),
    @('ensuresthat', 'ensures that'),
    @('concluson', 'conclusion')
)

Get-ChildItem -Path $blogDir -Filter "*.html" | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    
    foreach ($fix in $fixes) {
        $content = $content -replace [regex]::Escape($fix[0]), $fix[1]
    }
    
    # Custom quote fix logic
    $content = $content -replace "we've", "we've"
    $content = $content -replace "'sincredibly", "it's incredibly"
    $content = $content -replace "'sediting", "s editing"
    
    [IO.File]::WriteAllText($_.FullName, $content, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "Healed: $($_.Name)"
}
