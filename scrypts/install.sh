#!/bin/bash
################################################################################
# OracleDBA - Installation Script
# Installation automatique et simple pour Rocky Linux 8/9
# Usage: bash install.sh
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "═══════════════════════════════════════════════════════"
    echo "  🗄️  OracleDBA Installation"
    echo "  Oracle Database Administration Toolkit"
    echo "═══════════════════════════════════════════════════════"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_warning "Running as root. Will install system-wide."
    INSTALL_USER="root"
else
    print_info "Running as regular user. Will install for current user."
    INSTALL_USER=$(whoami)
fi

print_header

# Step 1: Check Python version
print_info "Checking Python version..."
if ! command -v python3.9 &> /dev/null; then
    print_error "Python 3.9 not found!"
    echo ""
    echo "Install Python 3.9 first:"
    echo "  sudo dnf module enable python39 -y"
    echo "  sudo dnf install -y python39 python39-pip"
    exit 1
fi

PYTHON_VERSION=$(python3.9 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Step 2: Check/Install pip
print_info "Checking pip..."
if ! python3.9 -m pip --version &> /dev/null; then
    print_warning "pip not found, installing..."
    curl -fsSL https://bootstrap.pypa.io/get-pip.py | python3.9
    print_success "pip installed"
else
    PIP_VERSION=$(python3.9 -m pip --version | awk '{print $2}')
    print_success "pip $PIP_VERSION found"
fi

# Step 3: Upgrade pip and setuptools
print_info "Upgrading pip and setuptools..."
python3.9 -m pip install --upgrade pip setuptools wheel --quiet
print_success "Tools upgraded"

# Step 4: Check if we're in the oracledba directory
if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ]; then
    print_warning "Not in oracledba directory"
    
    if [ -d "oracledba" ]; then
        print_info "Found oracledba subdirectory, entering..."
        cd oracledba
    else
        print_info "Cloning from GitHub..."
        if ! command -v git &> /dev/null; then
            print_error "git not found! Install it first: sudo dnf install -y git"
            exit 1
        fi
        git clone https://github.com/ELMRABET-Abdelali/oracledba.git
        cd oracledba
        print_success "Repository cloned"
    fi
fi

# Step 5: Clean previous installations
print_info "Cleaning previous installations..."
python3.9 -m pip uninstall oracledba -y &> /dev/null || true
rm -rf build/ dist/ *.egg-info &> /dev/null || true
print_success "Cleaned"

# Step 6: Install dependencies first
print_info "Installing dependencies..."
python3.9 -m pip install --quiet \
    'click>=8.1.0' \
    'colorama>=0.4.6' \
    'pyyaml>=6.0.1' \
    'requests>=2.31.0' \
    'rich>=13.7.0' \
    'paramiko>=3.4.0' \
    'jinja2>=3.1.3' \
    'psutil>=5.9.0'
print_success "Dependencies installed"

# Step 7: Install the package
print_info "Installing OracleDBA package..."
python3.9 -m pip install . --no-cache-dir --quiet
print_success "Package installed"

# Step 8: Configure PATH
print_info "Configuring PATH..."
if [ "$INSTALL_USER" = "root" ]; then
    BIN_PATH="/usr/local/bin"
else
    BIN_PATH="$HOME/.local/bin"
    
    if [[ ":$PATH:" != *":$BIN_PATH:"* ]]; then
        echo "export PATH=\$PATH:\$HOME/.local/bin" >> ~/.bashrc
        export PATH=$PATH:$HOME/.local/bin
        print_success "PATH updated in ~/.bashrc"
    fi
fi
print_success "PATH configured"

# Step 9: Verify installation
print_info "Verifying installation..."

# Test import
if ! python3.9 -c "import oracledba" 2>/dev/null; then
    print_error "Import test FAILED"
    exit 1
fi
print_success "Import test passed"

# Test modules
if ! python3.9 -c "from oracledba.modules import install, precheck, testing, downloader, response_files" 2>/dev/null; then
    print_error "Module import test FAILED"
    exit 1
fi
print_success "Module import test passed"

# Test CLI
if command -v oradba &> /dev/null; then
    CLI_VERSION=$(oradba --version 2>&1 | head -1)
    print_success "CLI test passed: $CLI_VERSION"
else
    print_warning "CLI not in PATH directly"
    if python3.9 -m oracledba.cli --version &> /dev/null; then
        CLI_VERSION=$(python3.9 -m oracledba.cli --version 2>&1 | head -1)
        print_success "CLI works via python module: $CLI_VERSION"
        
        # Create alias
        if ! grep -q "alias oradba=" ~/.bashrc 2>/dev/null; then
            echo "alias oradba='python3.9 -m oracledba.cli'" >> ~/.bashrc
            print_info "Alias 'oradba' added to ~/.bashrc"
        fi
    else
        print_error "CLI test FAILED"
        exit 1
    fi
fi

# Step 10: Success message
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Installation Successful!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "📝 Quick Start:"
echo ""
echo "  # Check version"
echo "  oradba --version"
echo ""
echo "  # Check system requirements"
echo "  oradba precheck"
echo ""
echo "  # Fix system issues automatically"
echo "  oradba precheck --fix"
echo "  sudo bash fix-precheck-issues.sh"
echo ""
echo "  # Generate response files"
echo "  oradba genrsp all"
echo ""
echo "  # Install Oracle 19c (after downloading Oracle ZIP)"
echo "  sudo oradba install full --installer-zip /tmp/oracle.zip --sid PRODDB"
echo ""
echo "  # Test installation"
echo "  oradba test --report"
echo ""
echo "📚 Documentation:"
echo "  https://github.com/ELMRABET-Abdelali/oracledba"
echo ""
echo "⚠️  Important: Source your bashrc or restart shell:"
echo "  source ~/.bashrc"
echo ""
