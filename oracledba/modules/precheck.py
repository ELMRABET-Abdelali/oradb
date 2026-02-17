"""
Pre-Installation Checker for Oracle 19c
Validates system requirements before installation
"""

import os
import subprocess
import platform
import psutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


class PreInstallChecker:
    """Checks system requirements for Oracle 19c installation"""
    
    # Oracle 19c Minimum Requirements
    REQUIREMENTS = {
        'min_ram_gb': 8,
        'min_swap_gb': 8,
        'min_disk_gb': 50,
        'min_tmp_gb': 2,
        'supported_os': ['rocky', 'centos', 'rhel', 'oracle'],
        'supported_versions': ['8', '9'],
        'required_packages': [
            'bc', 'binutils', 'compat-openssl10', 'elfutils-libelf',
            'glibc', 'glibc-devel', 'ksh', 'libaio', 'libaio-devel',
            'libXrender', 'libX11', 'libXau', 'libXi', 'libXtst',
            'libgcc', 'libnsl', 'libstdc++', 'libxcb', 'make',
            'policycoreutils', 'policycoreutils-python-utils',
            'smartmontools', 'sysstat', 'unixODBC', 'unixODBC-devel',
        ],
        'required_kernel_params': {
            'fs.file-max': 6815744,
            'kernel.sem': '250 32000 100 128',
            'kernel.shmmni': 4096,
            'kernel.shmall': 1073741824,
            'kernel.shmmax': 4398046511104,
            'net.core.rmem_default': 262144,
            'net.core.rmem_max': 4194304,
            'net.core.wmem_default': 262144,
            'net.core.wmem_max': 1048576,
            'fs.aio-max-nr': 1048576,
            'net.ipv4.ip_local_port_range': '9000 65500',
        }
    }
    
    def __init__(self):
        self.results = {
            'os': {'passed': False, 'details': []},
            'hardware': {'passed': False, 'details': []},
            'packages': {'passed': False, 'details': []},
            'kernel': {'passed': False, 'details': []},
            'network': {'passed': False, 'details': []},
            'filesystem': {'passed': False, 'details': []},
        }
    
    def check_all(self):
        """Run all pre-installation checks"""
        console.print(Panel.fit(
            "[bold cyan]Oracle 19c Pre-Installation Checker[/bold cyan]\n"
            "Validating system requirements...",
            border_style="cyan"
        ))
        
        self.check_os()
        self.check_hardware()
        self.check_packages()
        self.check_kernel_params()
        self.check_network()
        self.check_filesystem()
        
        return self.display_results()
    
    def check_os(self):
        """Check OS compatibility"""
        console.print("\n[yellow]→[/yellow] Checking Operating System...")
        
        try:
            # Read OS release
            if Path('/etc/os-release').exists():
                with open('/etc/os-release', 'r') as f:
                    os_info = f.read().lower()
                
                # Check distribution
                supported = False
                for dist in self.REQUIREMENTS['supported_os']:
                    if dist in os_info:
                        self.results['os']['details'].append(f"✓ Distribution: {dist.upper()}")
                        supported = True
                        break
                
                if not supported:
                    self.results['os']['details'].append("✗ Unsupported distribution")
                    return
                
                # Check version
                version_found = False
                for ver in self.REQUIREMENTS['supported_versions']:
                    if f'VERSION_ID="{ver}' in os_info or f"VERSION_ID='{ver}" in os_info:
                        self.results['os']['details'].append(f"✓ Version: {ver}")
                        version_found = True
                        break
                
                if not version_found:
                    self.results['os']['details'].append("⚠ Version might not be officially supported")
                
                # Check kernel
                kernel = platform.release()
                self.results['os']['details'].append(f"✓ Kernel: {kernel}")
                
                self.results['os']['passed'] = supported
        
        except Exception as e:
            self.results['os']['details'].append(f"✗ Error checking OS: {str(e)}")
    
    def check_hardware(self):
        """Check hardware requirements"""
        console.print("[yellow]→[/yellow] Checking Hardware Resources...")
        
        try:
            # RAM
            ram_gb = psutil.virtual_memory().total / (1024**3)
            if ram_gb >= self.REQUIREMENTS['min_ram_gb']:
                self.results['hardware']['details'].append(f"✓ RAM: {ram_gb:.1f} GB (min: {self.REQUIREMENTS['min_ram_gb']} GB)")
                ram_ok = True
            else:
                self.results['hardware']['details'].append(f"✗ RAM: {ram_gb:.1f} GB (min: {self.REQUIREMENTS['min_ram_gb']} GB)")
                ram_ok = False
            
            # SWAP
            swap_gb = psutil.swap_memory().total / (1024**3)
            if swap_gb >= self.REQUIREMENTS['min_swap_gb']:
                self.results['hardware']['details'].append(f"✓ SWAP: {swap_gb:.1f} GB (min: {self.REQUIREMENTS['min_swap_gb']} GB)")
                swap_ok = True
            else:
                self.results['hardware']['details'].append(f"✗ SWAP: {swap_gb:.1f} GB (min: {self.REQUIREMENTS['min_swap_gb']} GB)")
                swap_ok = False
            
            # Disk space
            disk = psutil.disk_usage('/')
            disk_gb = disk.free / (1024**3)
            if disk_gb >= self.REQUIREMENTS['min_disk_gb']:
                self.results['hardware']['details'].append(f"✓ Disk: {disk_gb:.1f} GB free (min: {self.REQUIREMENTS['min_disk_gb']} GB)")
                disk_ok = True
            else:
                self.results['hardware']['details'].append(f"✗ Disk: {disk_gb:.1f} GB free (min: {self.REQUIREMENTS['min_disk_gb']} GB)")
                disk_ok = False
            
            # /tmp space
            if Path('/tmp').exists():
                tmp_disk = psutil.disk_usage('/tmp')
                tmp_gb = tmp_disk.free / (1024**3)
                if tmp_gb >= self.REQUIREMENTS['min_tmp_gb']:
                    self.results['hardware']['details'].append(f"✓ /tmp: {tmp_gb:.1f} GB free (min: {self.REQUIREMENTS['min_tmp_gb']} GB)")
                    tmp_ok = True
                else:
                    self.results['hardware']['details'].append(f"✗ /tmp: {tmp_gb:.1f} GB free (min: {self.REQUIREMENTS['min_tmp_gb']} GB)")
                    tmp_ok = False
            else:
                tmp_ok = True
            
            # CPU
            cpu_count = psutil.cpu_count()
            self.results['hardware']['details'].append(f"✓ CPUs: {cpu_count}")
            
            self.results['hardware']['passed'] = ram_ok and swap_ok and disk_ok and tmp_ok
        
        except Exception as e:
            self.results['hardware']['details'].append(f"✗ Error checking hardware: {str(e)}")
    
    def check_packages(self):
        """Check required packages"""
        console.print("[yellow]→[/yellow] Checking Required Packages...")
        
        try:
            missing = []
            installed = []
            
            for pkg in self.REQUIREMENTS['required_packages']:
                result = subprocess.run(
                    ['rpm', '-q', pkg],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    installed.append(pkg)
                else:
                    missing.append(pkg)
            
            if installed:
                self.results['packages']['details'].append(f"✓ Installed: {len(installed)}/{len(self.REQUIREMENTS['required_packages'])}")
            
            if missing:
                self.results['packages']['details'].append(f"✗ Missing: {', '.join(missing[:5])}")
                if len(missing) > 5:
                    self.results['packages']['details'].append(f"  ... and {len(missing)-5} more")
            
            self.results['packages']['passed'] = len(missing) == 0
        
        except Exception as e:
            self.results['packages']['details'].append(f"✗ Error checking packages: {str(e)}")
    
    def check_kernel_params(self):
        """Check kernel parameters"""
        console.print("[yellow]→[/yellow] Checking Kernel Parameters...")
        
        try:
            incorrect = []
            correct = 0
            
            for param, expected in self.REQUIREMENTS['required_kernel_params'].items():
                try:
                    result = subprocess.run(
                        ['sysctl', param],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        current = result.stdout.split('=')[1].strip()
                        if str(expected) in current or current in str(expected):
                            correct += 1
                        else:
                            incorrect.append(f"{param}: {current} (expected: {expected})")
                except:
                    incorrect.append(f"{param}: not set")
            
            total = len(self.REQUIREMENTS['required_kernel_params'])
            if correct > 0:
                self.results['kernel']['details'].append(f"✓ Correct: {correct}/{total}")
            
            if incorrect:
                self.results['kernel']['details'].append(f"✗ Need adjustment: {len(incorrect)}")
                for item in incorrect[:3]:
                    self.results['kernel']['details'].append(f"  • {item}")
            
            self.results['kernel']['passed'] = len(incorrect) == 0
        
        except Exception as e:
            self.results['kernel']['details'].append(f"✗ Error checking kernel params: {str(e)}")
    
    def check_network(self):
        """Check network configuration"""
        console.print("[yellow]→[/yellow] Checking Network Configuration...")
        
        try:
            # Hostname
            hostname = platform.node()
            self.results['network']['details'].append(f"✓ Hostname: {hostname}")
            
            # Check /etc/hosts
            if Path('/etc/hosts').exists():
                with open('/etc/hosts', 'r') as f:
                    hosts_content = f.read()
                    if hostname in hosts_content:
                        self.results['network']['details'].append("✓ Hostname in /etc/hosts")
                        hosts_ok = True
                    else:
                        self.results['network']['details'].append("✗ Hostname not in /etc/hosts")
                        hosts_ok = False
            else:
                hosts_ok = False
            
            # Check DNS
            try:
                import socket
                socket.gethostbyname(hostname)
                self.results['network']['details'].append("✓ DNS resolution working")
                dns_ok = True
            except:
                self.results['network']['details'].append("⚠ DNS resolution failed")
                dns_ok = False
            
            self.results['network']['passed'] = hosts_ok
        
        except Exception as e:
            self.results['network']['details'].append(f"✗ Error checking network: {str(e)}")
    
    def check_filesystem(self):
        """Check filesystem requirements"""
        console.print("[yellow]→[/yellow] Checking Filesystem...")
        
        try:
            # Check /u01 directory
            u01_exists = Path('/u01').exists()
            if u01_exists:
                self.results['filesystem']['details'].append("✓ /u01 directory exists")
            else:
                self.results['filesystem']['details'].append("⚠ /u01 directory does not exist (will be created)")
            
            # Check SELinux
            try:
                result = subprocess.run(
                    ['getenforce'],
                    capture_output=True,
                    text=True
                )
                selinux = result.stdout.strip()
                if selinux in ['Permissive', 'Disabled']:
                    self.results['filesystem']['details'].append(f"✓ SELinux: {selinux}")
                    selinux_ok = True
                else:
                    self.results['filesystem']['details'].append(f"✗ SELinux: {selinux} (should be Permissive or Disabled)")
                    selinux_ok = False
            except:
                selinux_ok = True
            
            # Check firewall
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', 'firewalld'],
                    capture_output=True,
                    text=True
                )
                firewall = result.stdout.strip()
                if firewall == 'active':
                    self.results['filesystem']['details'].append("⚠ Firewall is active (port 1521 must be open)")
                else:
                    self.results['filesystem']['details'].append("✓ Firewall is inactive")
            except:
                pass
            
            self.results['filesystem']['passed'] = selinux_ok
        
        except Exception as e:
            self.results['filesystem']['details'].append(f"✗ Error checking filesystem: {str(e)}")
    
    def display_results(self):
        """Display check results"""
        console.print("\n")
        
        table = Table(title="Pre-Installation Check Results", show_header=True, header_style="bold cyan")
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Status", width=10)
        table.add_column("Details", width=60)
        
        overall_passed = True
        
        for category, result in self.results.items():
            status = "[green]✓ PASS[/green]" if result['passed'] else "[red]✗ FAIL[/red]"
            details = "\n".join(result['details'])
            table.add_row(category.upper(), status, details)
            
            if not result['passed']:
                overall_passed = False
        
        console.print(table)
        
        if overall_passed:
            console.print(Panel.fit(
                "[bold green]✓ All checks passed![/bold green]\n"
                "System is ready for Oracle 19c installation.",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                "[bold yellow]⚠ Some checks failed[/bold yellow]\n"
                "Please fix the issues before installing Oracle 19c.\n"
                "Run: [cyan]oradba install system[/cyan] to fix most issues automatically.",
                border_style="yellow"
            ))
        
        return overall_passed
    
    def generate_fix_script(self, output_file='fix-precheck-issues.sh'):
        """Generate a script to fix common issues"""
        script_content = """#!/bin/bash
# Auto-generated script to fix Oracle 19c pre-installation issues

set -e

echo "Fixing Oracle 19c pre-installation issues..."

# Install missing packages
missing_packages=("""
        
        # Add missing packages logic
        script_content += """
)

if [ ${#missing_packages[@]} -gt 0 ]; then
    echo "Installing missing packages..."
    dnf install -y "${missing_packages[@]}"
fi

# Fix kernel parameters
cat >> /etc/sysctl.conf << 'EOF'
fs.file-max = 6815744
kernel.sem = 250 32000 100 128
kernel.shmmni = 4096
kernel.shmall = 1073741824
kernel.shmmax = 4398046511104
net.core.rmem_default = 262144
net.core.rmem_max = 4194304
net.core.wmem_default = 262144
net.core.wmem_max = 1048576
fs.aio-max-nr = 1048576
net.ipv4.ip_local_port_range = 9000 65500
EOF

sysctl -p

# Disable SELinux
sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
setenforce 0

# Create /u01 if needed
if [ ! -d /u01 ]; then
    mkdir -p /u01
    chmod 755 /u01
fi

echo "✓ Fixes applied successfully!"
"""
        
        with open(output_file, 'w') as f:
            f.write(script_content)
        
        os.chmod(output_file, 0o755)
        console.print(f"\n[green]✓[/green] Fix script generated: {output_file}")
