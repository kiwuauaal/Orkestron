# Push to GitHub - Quick Script
# Run this after creating your GitHub repository

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Orkestron - Push to GitHub" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Ask for GitHub username
$githubUsername = Read-Host "Enter your GitHub username"

if (-not $githubUsername) {
    Write-Host "Error: Username cannot be empty" -ForegroundColor Red
    exit 1
}

$repoUrl = "https://github.com/$githubUsername/orkestron.git"

Write-Host ""
Write-Host "Setting up remote: $repoUrl" -ForegroundColor Green

# Add remote
git remote add origin $repoUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Remote added successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to add remote. It might already exist." -ForegroundColor Yellow
    Write-Host "Removing old remote and adding new one..." -ForegroundColor Yellow
    git remote remove origin
    git remote add origin $repoUrl
}

Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Green
Write-Host "(You'll be asked for your GitHub credentials)" -ForegroundColor Yellow
Write-Host ""

# Push to GitHub
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "✓ SUCCESS!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository is now live at:" -ForegroundColor Cyan
    Write-Host "https://github.com/$githubUsername/orkestron" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Add topics to your repository" -ForegroundColor White
    Write-Host "2. Share with the community!" -ForegroundColor White
    Write-Host "3. Start accepting contributions!" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "✗ Push failed" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. You need a Personal Access Token (not password)" -ForegroundColor White
    Write-Host "   Create one at: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Repository doesn't exist on GitHub" -ForegroundColor White
    Write-Host "   Create it at: https://github.com/new" -ForegroundColor White
    Write-Host ""
}

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
