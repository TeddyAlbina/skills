# Define the root directory (Current Directory by default)
$rootDir = Get-Location

# Get all immediate subdirectories
$subFolders = Get-ChildItem -Path $rootDir -Directory

$processedCount = 0

foreach ($folder in $subFolders) {
    # Define the target file name based on the folder name
    $targetFileName = "$($folder.Name).md"
    $targetFilePath = Join-Path -Path $folder.FullName -ChildPath $targetFileName
    $destinationPath = Join-Path -Path $folder.FullName -ChildPath "SKILL.md"
    
    # Check if the <SUB_FOLDER_NAME>.md file exists
    if (Test-Path -Path $targetFilePath) {
        
        # Check if a SKILL.md already exists to avoid overwriting conflicts
        if (Test-Path -Path $destinationPath) {
            Write-Host "Skipped: 'SKILL.md' already exists in $($folder.Name). Cannot revert." -ForegroundColor Orange
        } else {
            # Perform the reverse rename operation
            Rename-Item -Path $targetFilePath -NewName "SKILL.md"
            Write-Host "Reverted: $($folder.Name)/$targetFileName -> SKILL.md" -ForegroundColor Green
            $processedCount++
        }
    }
}

if ($processedCount -eq 0) {
    Write-Host "No matching subfolder-named .md files were found to revert." -ForegroundColor Yellow
}