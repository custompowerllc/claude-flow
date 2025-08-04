Write-Host "Listing files in logs directory"
$csvFiles = Get-ChildItem -Path "logs\*.csv"
Write-Host "Found $($csvFiles.Count) files"
foreach ($file in $csvFiles) {
    Write-Host $file.Name
}
