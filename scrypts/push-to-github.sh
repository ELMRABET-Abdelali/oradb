#!/bin/bash
################################################################################
# Script pour pousser la nouvelle version vers GitHub
# Usage: bash push-to-github.sh
################################################################################

set -e

echo "🚀 Préparation push vers GitHub..."

# 1. Status
echo "1️⃣ Status actuel:"
git status --short

# 2. Add all changes
echo ""
echo "2️⃣ Ajout des modifications:"
git add .

# 3. Show what will be committed
echo ""
echo "3️⃣ Fichiers à committer:"
git status --short

# 4. Commit
echo ""
echo "4️⃣ Commit des modifications:"
git commit -m "fix: Fix package structure to include all modules

- Fixed pyproject.toml to use packages.find for auto-discovery
- Added psutil to dependencies
- Created robust install.sh with verification
- Added QUICK_INSTALL.md for simple installation guide
- Installation now works in one command
- All modules (precheck, testing, downloader, response_files) now included

This fixes the ModuleNotFoundError for oracledba.modules
"

# 5. Push
echo ""
echo "5️⃣ Push vers GitHub:"
git push origin main

echo ""
echo "✅ Push réussi!"
echo ""
echo "📝 Prochaines étapes:"
echo "  1. Aller sur une VM vierge"
echo "  2. Exécuter:"
echo "     git clone https://github.com/ELMRABET-Abdelali/oracledba.git"
echo "     cd oracledba"
echo "     bash install.sh"
echo "  3. Tester:"
echo "     oradba --version"
echo "     oradba precheck"
echo ""
