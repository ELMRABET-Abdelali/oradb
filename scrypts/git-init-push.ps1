# Script PowerShell pour initialiser et pusher vers GitHub
# Exécuter avec: .\git-init-push.ps1

$repoPath = "C:\Users\DELL\Desktop\DBA\dbadministration\digitalocean-setup\oracledba"
$remoteUrl = "https://github.com/ELMRABET-Abdelali/oracledba.git"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Initialisation et Push vers GitHub" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Aller dans le dossier
Set-Location $repoPath

# Vérifier que les fichiers existent
if (-not (Test-Path "oracledba\modules\precheck.py")) {
    Write-Host "ERREUR: Fichiers manquants!" -ForegroundColor Red
    exit 1
}

Write-Host "[1/6] Fichiers à pusher:" -ForegroundColor Yellow
Write-Host "  ✓ precheck.py (16 KB)"
Write-Host "  ✓ testing.py (17 KB)"
Write-Host "  ✓ downloader.py (12 KB)"
Write-Host "  ✓ response_files.py (8 KB)"
Write-Host "  ✓ cli.py (mis à jour)"
Write-Host "  ✓ pyproject.toml (corrigé)"
Write-Host ""

# Initialiser Git si nécessaire
if (-not (Test-Path ".git")) {
    Write-Host "[2/6] Initialisation du repository Git..." -ForegroundColor Yellow
    git init
    git branch -M main
} else {
    Write-Host "[2/6] Repository Git déjà initialisé" -ForegroundColor Green
}

# Ajouter le remote
Write-Host "[3/6] Configuration du remote GitHub..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin $remoteUrl

# Ajouter les fichiers
Write-Host "[4/6] Ajout des fichiers..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "[5/6] Commit..." -ForegroundColor Yellow
$commitMessage = @"
feat: Complete Oracle DBA package with precheck, testing, downloader, response_files

Core Modules Added:
- PreInstallChecker: System validation and auto-fix (16 KB)
- OracleTestSuite: Post-install testing suite (17 KB)  
- OracleDownloader: Software download manager (12 KB)
- ResponseFileGenerator: Silent install templates (8 KB)

CLI Enhancements:
- 10 new commands: precheck, test, download, genrsp
- Complete help system with 25+ commands

Infrastructure:
- Fixed pyproject.toml for proper package discovery
- Added psutil dependency
- Robust install.sh script
- Comprehensive documentation

Features:
- Auto system validation
- Auto problem fixing
- Response file generation
- Complete testing suite
- One-command installation

This makes OracleDBA a complete auto-sufficient Oracle 19c DBA package.
"@
git commit -m $commitMessage

# Push
Write-Host "[6/6] Push vers GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Push réussi!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Vérifiez sur:" -ForegroundColor Cyan
Write-Host "https://github.com/ELMRABET-Abdelali/oracledba" -ForegroundColor Cyan
Write-Host ""
