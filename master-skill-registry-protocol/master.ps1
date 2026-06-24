# Define the root directory (Current Directory by default)
$rootDir = Get-Location

# Find all "SKILL.md" files exactly one level deep in subdirectories
$skills = Get-ChildItem -Path $rootDir -Filter "SKILL.md" -Recurse -Depth 2 | 
          Where-Object { $_.DirectoryName -ne $rootDir }

if ($skills.Count -eq 0) {
    Write-Host "No surface-level SKILL.md files found to rename." -ForegroundColor Yellow
    return
}

# Loop through and rename each file
foreach ($file in $skills) {
    $folderName = $file.Directory.Name
    $newFileName = "$folderName.md"
    $destinationPath = Join-Path -Path $file.DirectoryName -ChildPath $newFileName
    
    # Check if a file with the folder's name already exists to prevent accidental overwrites
    if (Test-Path -Path $destinationPath) {
        Write-Host "Skipped: '$newFileName' already exists in $($file.DirectoryName)" -ForegroundColor Orange
    } else {
        # Perform the rename operation
        Rename-Item -Path $file.FullName -NewName $newFileName
        Write-Host "Renamed: $($file.FullName.Replace($rootDir.Path, '')) -> $newFileName" -ForegroundColor Green
    }
}