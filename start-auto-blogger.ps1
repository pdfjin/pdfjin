# start-auto-blogger.ps1
# This script runs in the background and checks the time every minute.
# At 9:00 AM, it triggers the auto_blogger.py script.

Write-Host "PDFjin Auto-Blogger Scheduler Started."
Write-Host "It will automatically write and publish posts at 09:00."
Write-Host "Leave this window open in the background."

while ($true) {
    $now = Get-Date
    if ($now.Hour -eq 9 -and $now.Minute -eq 0) {
        Write-Host "[$($now.ToString())] Triggering Auto-Blogger..."
        
        # Run the python script
        python auto_blogger.py
        
        # Sleep for 65 seconds so it doesn't trigger multiple times in the same minute
        Start-Sleep -Seconds 65
    } else {
        # Sleep for 30 seconds before checking again
        Start-Sleep -Seconds 30
    }
}
