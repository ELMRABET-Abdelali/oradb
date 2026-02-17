#!/bin/bash
################################################################################
# OraDB Remote Deployment Script for Rocky 8
# 
# This script deploys and installs the oradb package on a remote Rocky 8 server
# Server: 178.128.10.67
# SSH Key: id_rsa
################################################################################

set -e  # Exit on error

# Configuration
REMOTE_HOST="178.128.10.67"
SSH_KEY="./otherfiles/id_rsa"
REMOTE_USER="root"
REPO_URL="https://github.com/ELMRABET-Abdelali/oradb.git"
INSTALL_DIR="/opt/oradb"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    log_error "SSH key not found at: $SSH_KEY"
    exit 1
fi

# Set correct permissions for SSH key
chmod 600 "$SSH_KEY"
log_info "SSH key permissions set"

# Test SSH connection
log_info "Testing SSH connection to ${REMOTE_HOST}..."
if ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "echo 'Connection successful'" &> /dev/null; then
    log_success "SSH connection successful"
else
    log_error "Cannot connect to ${REMOTE_HOST}"
    exit 1
fi

log_info "Starting remote deployment to ${REMOTE_HOST}..."

# Execute remote installation
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" <<'ENDSSH'

set -e

echo "=========================================="
echo "🚀 OraDB Installation on Rocky 8"
echo "=========================================="

# Step 1: Update system and install prerequisites
echo ""
echo "📦 Step 1/7: Installing prerequisites..."
dnf install -y git python39 python39-pip python39-devel gcc make || yum install -y git python39 python39-pip python39-devel gcc make

# Ensure pip is up to date
python3.9 -m pip install --upgrade pip

echo "✅ Prerequisites installed"

# Step 2: Clone repository
echo ""
echo "📥 Step 2/7: Cloning oradb repository..."
if [ -d "/opt/oradb" ]; then
    echo "⚠️  Directory /opt/oradb already exists. Removing..."
    rm -rf /opt/oradb
fi

cd /opt
git clone https://github.com/ELMRABET-Abdelali/oradb.git
cd oradb

echo "✅ Repository cloned"

# Step 3: Install Python package
echo ""
echo "🔧 Step 3/7: Installing oradb package..."
python3.9 -m pip install -e .

echo "✅ Package installed"

# Step 4: Install GUI dependencies
echo ""
echo "🎨 Step 4/7: Installing GUI dependencies..."
if [ -f "requirements-gui.txt" ]; then
    python3.9 -m pip install -r requirements-gui.txt
    echo "✅ GUI dependencies installed"
else
    echo "⚠️  requirements-gui.txt not found, skipping GUI dependencies"
fi

# Step 5: Verify installation
echo ""
echo "✔️  Step 5/7: Verifying installation..."
python3.9 -m oracledba.cli --version

# Add oradba to PATH (create symlink)
if [ ! -L "/usr/local/bin/oradba" ]; then
    cat > /usr/local/bin/oradba << 'EOF'
#!/bin/bash
python3.9 -m oracledba.cli "$@"
EOF
    chmod +x /usr/local/bin/oradba
    echo "✅ oradba command created in /usr/local/bin"
fi

# Test command
oradba --version

echo "✅ Installation verified"

# Step 6: Display available commands
echo ""
echo "📚 Step 6/7: Available installation commands..."
echo ""
echo "To see all available commands:"
echo "  oradba --help"
echo ""
echo "To install Oracle Database 19c:"
echo "  oradba install --help"
echo ""
echo "  oradba install all         # Complete installation (recommended)"
echo "  oradba install full        # Same as 'all'"
echo "  oradba install system      # System preparation only"
echo "  oradba install binaries    # Download Oracle binaries"
echo "  oradba install software    # Install Oracle software"
echo "  oradba install database    # Create database"
echo ""
echo "To start the Web GUI:"
echo "  oradba install gui                # Start on 0.0.0.0:5000"
echo "  oradba install gui --port 8080    # Start on custom port"
echo ""

# Step 7: Display next steps
echo ""
echo "=========================================="
echo "✅ OraDB Installation Complete!"
echo "=========================================="
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Run system precheck:"
echo "   oradba precheck"
echo ""
echo "2. Install Oracle 19c database:"
echo "   oradba install all"
echo "   (This will take 30-45 minutes)"
echo ""
echo "3. Or use step-by-step installation:"
echo "   oradba install system     # Prepare system"
echo "   oradba install binaries   # Download Oracle"
echo "   oradba install software   # Install software"
echo "   oradba install database   # Create database"
echo ""
echo "4. Start Web GUI (optional):"
echo "   oradba install gui"
echo "   Access at: http://178.128.10.67:5000"
echo ""
echo "📖 Documentation: /opt/oradb/guide/"
echo ""

ENDSSH

log_success "Remote deployment completed successfully!"
echo ""
echo "=========================================="
echo "📝 Summary"
echo "=========================================="
echo "✅ Package installed on ${REMOTE_HOST}"
echo "✅ Package location: /opt/oradb"
echo "✅ Command available: oradba"
echo ""
echo "🔗 To connect to the server:"
echo "   ssh -i ${SSH_KEY} ${REMOTE_USER}@${REMOTE_HOST}"
echo ""
echo "🚀 To start Oracle installation on the server:"
echo "   ssh -i ${SSH_KEY} ${REMOTE_USER}@${REMOTE_HOST}"
echo "   oradba install all"
echo ""
echo "🌐 To start Web GUI on the server:"
echo "   ssh -i ${SSH_KEY} ${REMOTE_USER}@${REMOTE_HOST}"
echo "   oradba install gui"
echo ""
