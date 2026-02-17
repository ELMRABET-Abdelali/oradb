@echo off
REM Script pour pousser les nouveaux modules vers GitHub
cd /d C:\Users\DELL\Desktop\DBA\dbadministration\digitalocean-setup\oracledba

echo ============================================
echo Push vers GitHub - OracleDBA
echo ============================================
echo.

REM Vérifier que nous sommes dans le bon dossier
if not exist "oracledba\modules\precheck.py" (
    echo ERREUR: Fichiers manquants!
    pause
    exit /b 1
)

echo Fichiers a pusher:
echo   - precheck.py (16 KB)
echo   - testing.py (17 KB)
echo   - downloader.py (12 KB)
echo   - response_files.py (8 KB)
echo   - cli.py (mis a jour)
echo   - pyproject.toml (corrige)
echo.

REM Ajouter les fichiers modifiés
echo [1/4] Ajout des fichiers...
git add oracledba/modules/precheck.py
git add oracledba/modules/testing.py
git add oracledba/modules/downloader.py
git add oracledba/modules/response_files.py
git add oracledba/cli.py
git add pyproject.toml
git add requirements.txt

REM Ajouter aussi les documentations
git add docs/INSTALLATION_GUIDE.md
git add TESTING.md
git add WHAT_IS_NEW.md
git add QUICK_INSTALL.md
git add install.sh

echo [2/4] Status...
git status --short

echo.
echo [3/4] Commit...
git commit -m "feat: Add precheck, testing, downloader, response_files modules

- Added PreInstallChecker for system validation (16 KB)
- Added OracleTestSuite for post-install testing (17 KB)
- Added OracleDownloader for software management (12 KB)
- Added Response file generator for silent install (8 KB)
- Updated cli.py with 10 new commands (precheck, test, download, genrsp)
- Fixed pyproject.toml to include all sub-packages
- Added psutil>=5.9.0 dependency
- Created comprehensive documentation
- Installation now fully automated with install.sh

This makes OracleDBA a complete auto-sufficient Oracle 19c DBA package.
"

echo.
echo [4/4] Push vers GitHub...
git push origin main

echo.
echo ============================================
echo Push termine avec succes!
echo ============================================
echo.
echo Verifiez sur GitHub:
echo https://github.com/ELMRABET-Abdelali/oracledba
echo.
pause
