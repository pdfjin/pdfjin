$rootDir = "c:\Users\ADMIN\Desktop\pdfjin\frontend"
$targetDirs = @("$rootDir\js", "$rootDir\pages")

$replacements = @{
    "JSON.parseeeee"         = "JSON.parse"
    "loadsript"              = "loadScript"
    "ssc: ="                 = "s.src ="
    "sonload: ="             = "s.onload ="
    "reslve\(\)"             = "resolve()"
    "Promis\("               = "Promise("
    "applyPersnalization"    = "applyPersonalization"
    "stupDeveloperdashboard" = "setupDeveloperDashboard"
    "verson"                 = "version"
    "sat-"                   = "stat-"
    "sat_"                   = "stat_"
    "prousers"               = "proUsers"
    "entusers"               = "entUsers"
    "allUsersfilter"         = "allUsers.filter"
    "allUsersfind"           = "allUsers.find"
    "allUserslength"         = "allUsers.length"
    "userslength"            = "users.length"
    "keyslength"             = "keys.length"
    "itemslength"            = "items.length"
    "generatesles"           = "generateSales"
    "resltspus"              = "results.push"
    "slesmap"                = "sales.map"
    "generateusers"          = "generateUsers"
    "generateActivity"       = "generateActivity"
    "generateLogs"           = "generateLogs"
    "toLocaleDatesring"      = "toLocaleDateString"
    "toLocaleTimesring"      = "toLocaleTimeString"
    "input.focus\)\;"        = "input.focus();"
    "btnsave"                = "btnSave"
    "btnsve"                 = "btnSave"
    "disount"                = "discount"
    "pasword"                = "password"
    "pas"                    = "pass"
    "sre"                    = "sure"
    "sve"                    = "save"
    "sncsession"             = "syncSession"
    "loadDasData"            = "loadDashboardData"
    "updatePricingdisplay"   = "updatePricingDisplay"
    "api-keystoken"          = "api-keys?token"
    "api-keysgenerate"       = "api-keys/generate"
    "apiKeysuccess"          = "apiKeySuccess"
    "newKeydisplay"          = "newKeyDisplay"
    "copystatus"             = "copyStatus"
    "apiUsgeCount"           = "apiUsageCount"
    "apiUsgeBar"             = "apiUsageBar"
    "smple"                  = "simple"
    "sctions"                = "sections"
    "sction"                 = "section"
    "sdebar"                 = "sidebar"
    "sitch"                  = "switch"
    "stTool"                 = "setTool"
    "st-"                    = "set-"
    "closs"                  = "closest"
    "parseeeee"              = "parse"
    ": ="                    = "="
}

$regexReplacements = @(
    @("link: \.", "link."),
    @("link \.", "link."),
    @("s \.background", "s.style.background"),
    @("l \.classList", "l.classList"),
    @("l \.toggle", "l.classList.toggle"),
    @("s \.opacity", "s.style.opacity"),
    @("link: \.pointerEvents", "link.style.pointerEvents"),
    @("link: \.cursor", "link.style.cursor"),
    @("link \.opacity", "link.style.opacity"),
    @("([a-zA-Z0-9]+)forEach", '$1.forEach'),
    @("([a-zA-Z0-9]+)map", '$1.map'),
    @("([a-zA-Z0-9]+)filter", '$1.filter'),
    @("([a-zA-Z0-9]+)find", '$1.find'),
    @("([a-zA-Z0-9]+)split", '$1.split'),
    @("([a-zA-Z0-9]+)join", '$1.join'),
    @("([a-zA-Z0-9]+)slice", '$1.slice'),
    @("([a-zA-Z0-9]+)toLowerCase", '$1.toLowerCase'),
    @("([a-zA-Z0-9]+)toUpperCase", '$1.toUpperCase'),
    @("([a-zA-Z0-9]+)trim", '$1.trim'),
    @("([a-zA-Z0-9]+)push", '$1.push'),
    @("([a-zA-Z0-9]+)addEventListener", '$1.addEventListener')
)

function Fix-File($path) {
    Write-Host "Fixing: $path"
    $content = Get-Content -Path $path -Raw -Encoding UTF8
    
    foreach ($key in $replacements.Keys) {
        $content = $content -replace $key, $replacements[$key]
    }
    
    foreach ($reg in $regexReplacements) {
        $content = [regex]::Replace($content, $reg[0], $reg[1])
    }

    if ($path -like "*index.html") {
        $content = $content -replace 'class="dashboard-body"', 'class="landing-page"'
    }

    Set-Content -Path $path -Value $content -Encoding UTF8
}

foreach ($dir in $targetDirs) {
    if (Test-Path $dir) {
        Get-ChildItem -Path $dir -Recurse -Include *.html, *.js, *.css | ForEach-Object {
            Fix-File $_.FullName
        }
    }
}

Fix-File "$rootDir\index.html"
