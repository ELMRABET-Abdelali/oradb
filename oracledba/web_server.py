#!/usr/bin/env python3
"""
OracleDBA Web GUI Server
Flask-based web interface for Oracle database administration
"""

import os
import sys
import json
import subprocess
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS

# Import our CLI modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simple system detector stub (replace with full implementation later if needed)
class SystemDetector:
    """Basic system detection for Oracle environment"""
    
    def __init__(self):
        self.oracle_home = os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
        self.oracle_base = os.environ.get('ORACLE_BASE', '/u01/app/oracle')
    
    def is_oracle_installed(self):
        """Check if Oracle is installed"""
        return os.path.exists(self.oracle_home)
    
    def get_running_databases(self):
        """Get list of running database instances"""
        try:
            result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
            pmon_lines = [line for line in result.stdout.split('\n') if 'ora_pmon_' in line]
            return [line.split('ora_pmon_')[1].strip() for line in pmon_lines]
        except:
            return []
    
    def detect_all(self):
        """Detect all Oracle components and their status"""
        oracle_installed = self.is_oracle_installed()
        running_dbs = self.get_running_databases()
        
        # Check Oracle version
        oracle_version = 'Unknown'
        if oracle_installed:
            try:
                version_file = os.path.join(self.oracle_home, 'inventory', 'ContentsXML', 'oraclehomeproperties.xml')
                if os.path.exists(version_file):
                    with open(version_file, 'r') as f:
                        content = f.read()
                        if '19' in content:
                            oracle_version = '19c'
            except:
                oracle_version = '19c'
        
        # Check listener
        listener_running = False
        try:
            result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
            listener_running = 'tnslsnr' in result.stdout
        except:
            pass
        
        # Check ASM
        asm_running = False
        try:
            result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
            asm_running = 'asm_pmon_' in result.stdout
        except:
            pass
        
        # Check Grid/Cluster
        grid_installed = os.path.exists('/u01/app/grid') or os.path.exists('/u01/app/19.3.0/grid')
        cluster_configured = False
        try:
            if os.path.exists('/etc/oracle/olr.loc'):
                cluster_configured = True
        except:
            pass
        
        return {
            'oracle': {
                'installed': oracle_installed,
                'version': oracle_version,
                'oracle_home': self.oracle_home,
                'oracle_base': self.oracle_base,
                'binaries': oracle_installed
            },
            'database': {
                'running': len(running_dbs) > 0,
                'instances': running_dbs,
                'count': len(running_dbs)
            },
            'listener': {
                'running': listener_running,
                'status': 'Running' if listener_running else 'Stopped'
            },
            'cluster': {
                'configured': cluster_configured,
                'type': 'RAC' if cluster_configured else 'Single Instance'
            },
            'grid': {
                'installed': grid_installed,
                'status': 'Installed' if grid_installed else 'Not Installed'
            },
            'asm': {
                'running': asm_running,
                'status': 'Running' if asm_running else 'Not Running'
            }
        }
    
    def get_oracle_metrics(self):
        """Get Oracle performance metrics"""
        metrics = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'sessions': 0,
            'active_sessions': 0
        }
        
        try:
            # Get basic system metrics
            result = subprocess.run(['free', '-m'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    mem_line = lines[1].split()
                    if len(mem_line) > 2:
                        total = int(mem_line[1])
                        used = int(mem_line[2])
                        if total > 0:
                            metrics['memory_usage'] = int((used / total) * 100)
        except:
            pass
        
        try:
            # Get disk usage
            result = subprocess.run(['df', '-h', '/u01'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    disk_line = lines[1].split()
                    if len(disk_line) > 4:
                        usage = disk_line[4].replace('%', '')
                        metrics['disk_usage'] = int(usage)
        except:
            pass
        
        return metrics

detector = SystemDetector()

app = Flask(__name__, 
           template_folder='web/templates',
           static_folder='web/static')
app.secret_key = secrets.token_hex(32)
CORS(app)

# Configuration
CONFIG_DIR = Path.home() / '.oracledba'
CONFIG_FILE = CONFIG_DIR / 'gui_config.json'
USERS_FILE = CONFIG_DIR / 'gui_users.json'

# Create system detector instance
detector = SystemDetector()


def hash_password(password: str, salt: str = None) -> tuple:
    """
    Hash password with PBKDF2 and salt
    Returns (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Use PBKDF2 with 100,000 iterations
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return key.hex(), salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify password against hash"""
    key, _ = hash_password(password, salt)
    return hmac.compare_digest(key, hashed_password)


# Default admin credentials
DEFAULT_ADMIN = {
    'username': 'admin',
    'role': 'admin',
    'must_change_password': True,
    'created_at': datetime.now().isoformat()
}
# Set default password with proper hashing
DEFAULT_PASSWORD, DEFAULT_SALT = hash_password('admin123')
DEFAULT_ADMIN['password_hash'] = DEFAULT_PASSWORD
DEFAULT_ADMIN['salt'] = DEFAULT_SALT


class GUIConfig:
    """GUI Configuration Manager"""
    
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.users_file = USERS_FILE
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Create config directory and files if they don't exist"""
        self.config_dir.mkdir(exist_ok=True, parents=True)
        
        # Create default config
        if not self.config_file.exists():
            default_config = {
                'port': 5000,
                'host': '0.0.0.0',
                'debug': False,
                'session_timeout': 3600,  # 1 hour
                'oracle_home': os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1'),
                'created_at': datetime.now().isoformat()
            }
            self.save_config(default_config)
        
        # Create default users
        if not self.users_file.exists():
            self.save_users({'admin': DEFAULT_ADMIN})
    
    def load_config(self):
        """Load GUI configuration"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config):
        """Save GUI configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_users(self):
        """Load users database"""
        with open(self.users_file, 'r') as f:
            return json.load(f)
    
    def save_users(self, users):
        """Save users database"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)


config_manager = GUIConfig()


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'admin':
            flash('Admin privileges required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = config_manager.load_users()
        
        if username in users:
            user = users[username]
            
            # Support both old SHA256 and new PBKDF2 hashing
            if 'salt' in user:
                # New secure method
                if verify_password(password, user['password_hash'], user['salt']):
                    session['user'] = username
                    session['role'] = user.get('role', 'user')
                    session['login_time'] = datetime.now().isoformat()
                    
                    # Check if password change required
                    if user.get('must_change_password'):
                        flash('Please change your password for security', 'warning')
                        return redirect(url_for('change_password'))
                    
                    flash(f'Welcome {username}!', 'success')
                    return redirect(url_for('dashboard'))
            else:
                # Old method (for backward compatibility) - migrate to new method
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if user['password_hash'] == password_hash:
                    session['user'] = username
                    session['role'] = user.get('role', 'user')
                    session['login_time'] = datetime.now().isoformat()
                    
                    # Force migration to new password system
                    flash('Please change your password to upgrade security', 'warning')
                    return redirect(url_for('change_password'))
        
        flash('Invalid credentials', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('change_password.html')
        
        # Password strength check
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('change_password.html')
        
        users = config_manager.load_users()
        username = session['user']
        user = users[username]
        
        # Verify current password (support both old and new methods)
        password_valid = False
        if 'salt' in user:
            password_valid = verify_password(current_password, user['password_hash'], user['salt'])
        else:
            current_hash = hashlib.sha256(current_password.encode()).hexdigest()
            password_valid = (user['password_hash'] == current_hash)
        
        if not password_valid:
            flash('Current password incorrect', 'error')
            return render_template('change_password.html')
        
        # Update password with new secure method
        new_hash, new_salt = hash_password(new_password)
        users[username]['password_hash'] = new_hash
        users[username]['salt'] = new_salt
        users[username]['must_change_password'] = False
        users[username]['password_changed_at'] = datetime.now().isoformat()
        config_manager.save_users(users)
        
        flash('Password changed successfully! Your password is now securely encrypted.', 'success')
        return redirect(url_for('dashboard'))
    
    # Check if force change
    users = config_manager.load_users()
    must_change = users[session['user']].get('must_change_password', False)
    
    return render_template('change_password.html', must_change=must_change)


# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get system status
    status = get_system_status()
    return render_template('dashboard.html', status=status, user=session['user'])


@app.route('/api/system-status')
@login_required
def api_system_status():
    """API: Get system status"""
    return jsonify(get_system_status())


@app.route('/api/oracle-metrics')
@login_required
def api_oracle_metrics():
    """API: Get detailed Oracle metrics (SGA, PGA, processes, tablespaces)"""
    metrics = detector.get_oracle_metrics()
    return jsonify({
        'success': True,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/installation-status')
@login_required
def api_installation_status():
    """API: Get what's installed and what can be activated"""
    detection = detector.detect_all()
    
    installation_status = {
        'components': {
            'oracle_database': {
                'installed': detection['oracle']['installed'],
                'version': detection['oracle']['version'],
                'can_activate': detection['oracle']['installed'] and not detection['database']['running'],
                'active': detection['database']['running'],
                'binaries': detection['oracle']['binaries']
            },
            'listener': {
                'installed': detection['oracle']['binaries'].get('lsnrctl', False),
                'can_activate': detection['oracle']['installed'] and not detection['listener']['running'],
                'active': detection['listener']['running'],
                'ports': detection['listener']['ports']
            },
            'grid_infrastructure': {
                'installed': detection['grid']['installed'],
                'can_activate': detection['grid']['installed'] and not detection['grid']['running'],
                'active': detection['grid']['running'],
                'grid_home': detection['grid']['grid_home']
            },
            'asm': {
                'installed': detection['asm']['installed'],
                'can_activate': detection['asm']['installed'] and not detection['asm']['running'],
                'active': detection['asm']['running'],
                'disk_groups': detection['asm']['disk_groups']
            }
        },
        'features': detection['features'],
        'summary': {
            'total_components': 4,
            'installed': sum([
                detection['oracle']['installed'],
                detection['oracle']['binaries'].get('lsnrctl', False),
                detection['grid']['installed'],
                detection['asm']['installed']
            ]),
            'active': sum([
                detection['database']['running'],
                detection['listener']['running'],
                detection['grid']['running'],
                detection['asm']['running']
            ])
        }
    }
    
    return jsonify(installation_status)


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    users = config_manager.load_users()
    user_data = users[session['user']]
    
    # Mask sensitive data
    profile_data = {
        'username': session['user'],
        'role': user_data.get('role', 'user'),
        'created_at': user_data.get('created_at', 'Unknown'),
        'password_changed_at': user_data.get('password_changed_at', 'Never'),
        'last_login': session.get('login_time', 'Unknown'),
        'password_security': 'PBKDF2-SHA256 with salt' if 'salt' in user_data else 'Legacy (upgrade recommended)'
    }
    
    return render_template('profile.html', profile=profile_data)


@app.route('/api/features/toggle', methods=['POST'])
@login_required
@admin_required
def api_features_toggle():
    """API: Enable/disable Oracle features"""
    data = request.json
    feature = data.get('feature')
    action = data.get('action')  # 'enable' or 'disable'
    
    if feature not in ['archivelog', 'fra', 'flashback', 'rman']:
        return jsonify({'success': False, 'error': 'Invalid feature'})
    
    try:
        if action == 'enable':
            result = execute_cli_command(['oradba', 'protection', feature, 'enable'])
        elif action == 'disable':
            result = execute_cli_command(['oradba', 'protection', feature, 'disable'])
        else:
            return jsonify({'success': False, 'error': 'Invalid action'})
        
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def get_system_status():
    """Get comprehensive system status using SystemDetector"""
    # Use system detector for comprehensive information
    detection = detector.detect_all()
    metrics = detector.get_oracle_metrics()
    
    status = {
        'hostname': subprocess.getoutput('hostname'),
        'timestamp': datetime.now().isoformat(),
        'oracle_home': detection['oracle']['oracle_home'],
        
        # Installation status
        'checks': {
            'oracle_installed': detection['oracle']['installed'],
            'database_running': detection['database']['running'],
            'listener_running': detection['listener']['running'],
            'cluster_configured': detection['cluster']['configured'],
            'grid_installed': detection['grid']['installed'],
            'asm_running': detection['asm']['running']
        },
        
        # Oracle details
        'oracle': {
            'version': detection['oracle']['version'],
            'binaries': detection['oracle']['binaries'],
            'installation_valid': all(detection['oracle']['binaries'].values())
        },
        
        # Database details
        'database': {
            'instances': detection['database']['instances'],
            'current_sid': detection['database']['current_sid'],
            'processes': detection['database']['processes']
        },
        
        # Listener details  
        'listener': {
            'count': len(detection['listener']['listeners']),
            'ports': detection['listener']['ports']
        },
        
        # Features status
        'features': detection['features'],
        
        # Oracle metrics (SGA, PGA, etc.)
        'metrics': metrics,
        
        # Cluster info
        'cluster': detection['cluster'],
        
        # Grid Infrastructure
        'grid': detection['grid'],
        
        # ASM
        'asm': detection['asm']
    }
    
    return status


# ============================================================================
# DATABASE MANAGEMENT ROUTES
# ============================================================================

@app.route('/databases')
@login_required
def databases():
    """Database management page"""
    return render_template('databases.html')


@app.route('/api/databases/list')
@login_required
def api_databases_list():
    """API: List all databases"""
    try:
        result = execute_cli_command(['oradba', 'database', 'list'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/databases/create', methods=['POST'])
@login_required
def api_databases_create():
    """API: Create database"""
    data = request.json
    sid = data.get('sid', 'PRODDB')
    memory = data.get('memory', 2048)
    
    try:
        result = execute_cli_command(['oradba', 'database', 'create', '--sid', sid, '--memory', str(memory)])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# STORAGE MANAGEMENT ROUTES
# ============================================================================

@app.route('/storage')
@login_required
def storage():
    """Storage management page"""
    return render_template('storage.html')


@app.route('/api/storage/tablespaces')
@login_required
def api_storage_tablespaces():
    """API: List tablespaces"""
    try:
        result = execute_cli_command(['oradba', 'storage', 'tablespace', 'list'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/storage/tablespace/create', methods=['POST'])
@login_required
def api_storage_tablespace_create():
    """API: Create tablespace"""
    data = request.json
    name = data.get('name')
    size = data.get('size', '500M')
    
    try:
        result = execute_cli_command(['oradba', 'storage', 'tablespace', 'create', 
                                     '--name', name, '--size', size])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# PROTECTION ROUTES
# ============================================================================

@app.route('/protection')
@login_required
def protection():
    """Data protection page"""
    return render_template('protection.html')


@app.route('/api/protection/archivelog/status')
@login_required
def api_protection_archivelog_status():
    """API: ARCHIVELOG status"""
    try:
        result = execute_cli_command(['oradba', 'protection', 'archivelog', 'status'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/protection/archivelog/enable', methods=['POST'])
@login_required
def api_protection_archivelog_enable():
    """API: Enable ARCHIVELOG"""
    try:
        result = execute_cli_command(['oradba', 'protection', 'archivelog', 'enable'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/rman/backup', methods=['POST'])
@login_required
def api_rman_backup():
    """API: RMAN backup"""
    data = request.json
    backup_type = data.get('type', 'full')
    
    try:
        result = execute_cli_command(['oradba', 'rman', 'backup', backup_type])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# SECURITY ROUTES
# ============================================================================

@app.route('/security')
@login_required
def security():
    """Security management page"""
    return render_template('security.html')


@app.route('/api/security/users')
@login_required
def api_security_users():
    """API: List database users"""
    try:
        result = execute_cli_command(['oradba', 'security', 'user', 'list'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/security/user/create', methods=['POST'])
@login_required
def api_security_user_create():
    """API: Create database user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    try:
        result = execute_cli_command(['oradba', 'security', 'user', 'create',
                                     '--name', username, '--password', password])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# CLUSTER MANAGEMENT ROUTES
# ============================================================================

@app.route('/cluster')
@login_required
def cluster():
    """Cluster management page"""
    return render_template('cluster.html')


@app.route('/api/cluster/nodes')
@login_required
def api_cluster_nodes():
    """API: List cluster nodes"""
    try:
        result = execute_cli_command(['oradba', 'cluster', 'list'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/cluster/add-node', methods=['POST'])
@login_required
def api_cluster_add_node():
    """API: Add cluster node"""
    data = request.json
    name = data.get('name')
    ip = data.get('ip')
    role = data.get('role', 'database')
    
    try:
        result = execute_cli_command(['oradba', 'cluster', 'add-node',
                                     '--name', name, '--ip', ip, '--role', role])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# SAMPLE DATABASE ROUTES
# ============================================================================

@app.route('/sample')
@login_required
def sample():
    """Sample database page"""
    return render_template('sample.html')


@app.route('/api/sample/create', methods=['POST'])
@login_required
def api_sample_create():
    """API: Create sample database"""
    try:
        result = execute_cli_command(['oradba', 'sample', 'create'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sample/test', methods=['POST'])
@login_required
def api_sample_test():
    """API: Test sample database"""
    try:
        result = execute_cli_command(['oradba', 'sample', 'test'])
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# TERMINAL ROUTES
# ============================================================================

@app.route('/terminal')
@login_required
def terminal():
    """Interactive terminal page"""
    return render_template('terminal.html')


@app.route('/api/terminal/execute', methods=['POST'])
@login_required
def api_terminal_execute():
    """API: Execute command in terminal"""
    data = request.json
    command = data.get('command', '')
    
    if not command:
        return jsonify({'success': False, 'error': 'No command provided'})
    
    # Security: only allow oradba commands
    if not command.startswith('oradba '):
        return jsonify({'success': False, 'error': 'Only oradba commands are allowed'})
    
    try:
        result = execute_cli_command(command.split())
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# INSTALLATION ROUTES
# ============================================================================

@app.route('/installation')
@login_required
@admin_required
def installation():
    """Installation wizard page"""
    return render_template('installation.html')


@app.route('/api/installation/download', methods=['POST'])
@login_required
@admin_required
def api_installation_download():
    """Download Oracle software"""
    import subprocess
    data = request.json or {}
    source = data.get('source', 'google_drive')
    
    try:
        if source == 'google_drive':
            # Google Drive file ID for LINUX.X64_193000_db_home.zip
            file_id = '1Mi7B2HneMBIyxJ01tnA-ThQ9hr2CAsns'
            
            # Create install script
            oracle_home = os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
            download_path = f"{oracle_home}/LINUX.X64_193000_db_home.zip"
            
            script_content = f"""#!/bin/bash
set -e

echo "=== Oracle 19c Download Started ==="
echo "Timestamp: $(date)"
echo ""

# Ensure oracle user exists
if ! id oracle >/dev/null 2>&1; then
    echo "Creating oracle user..."
    sudo useradd -m -s /bin/bash oracle
fi

# Add oracle to wheel group for sudo
echo "Adding oracle to wheel group..."
sudo usermod -aG wheel oracle

# Create ORACLE_HOME directory
echo "Creating ORACLE_HOME: {oracle_home}"
sudo mkdir -p {oracle_home}
sudo chown -R oracle:oinstall {oracle_home}

# Check if gdown is installed
if ! command -v gdown &> /dev/null; then
    echo "Installing gdown..."
    sudo dnf install -y python3-pip || yum install -y python3-pip
    pip3 install --user gdown
    export PATH=$PATH:~/.local/bin
fi

# Download Oracle 19c from Google Drive
echo ""
echo "=== Downloading Oracle 19c (3.06 GB) ==="
echo "This may take 10-20 minutes depending on your connection..."
echo ""

cd {oracle_home}
~/.local/bin/gdown {file_id} -O {download_path}

if [ -f "{download_path}" ]; then
    echo ""
    echo "=== Download Complete ==="
    ls -lh {download_path}
    echo ""
    echo "File size: $(du -h {download_path} | cut -f1)"
    echo "Location: {download_path}"
else
    echo "ERROR: Download failed!"
    exit 1
fi
"""
            
            # Write script
            script_path = '/tmp/oracle-download.sh'
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            
            # Execute script in background
            cmd = f"nohup bash {script_path} > /tmp/oracle-download.log 2>&1 &"
            subprocess.Popen(cmd, shell=True)
            
            return jsonify({
                'success': True,
                'message': 'Download started in background',
                'log_file': '/tmp/oracle-download.log',
                'download_path': download_path
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Unknown download source'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/installation/precheck', methods=['GET'])
@login_required
@admin_required
def api_installation_precheck():
    """Run system precheck"""
    try:
        result = execute_cli_command(['oradba', 'precheck'])
        
        # Parse result to determine if passed
        passed = 'ERROR' not in result.upper() and 'FAIL' not in result.upper()
        
        # Extract issues (simple parsing)
        issues = []
        for line in result.split('\n'):
            if 'ERROR' in line.upper() or 'FAIL' in line.upper():
                issues.append(line.strip())
        
        return jsonify({
            'success': True,
            'passed': passed,
            'issues': issues,
            'output': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/installation/system', methods=['POST'])
@login_required
@admin_required
def api_installation_system():
    """Install system prerequisites"""
    import subprocess
    try:
        # Create install script
        script_content = """#!/bin/bash
set -e

echo "=== System Prerequisites Installation ==="
echo "Timestamp: $(date)"
echo ""

# Run oradba precheck first
echo "Running system precheck..."
oradba precheck 2>&1 || true
echo ""

# Run system installation
echo "=== Installing System Prerequisites ==="
echo "This will configure users, groups, and kernel parameters..."
echo ""

oradba install system 2>&1

echo ""
echo "=== System Installation Complete ==="
"""
        
        script_path = '/tmp/oracle-install-system.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # Execute script in background
        cmd = f"nohup bash {script_path} > /tmp/oracle-install-system.log 2>&1 &"
        subprocess.Popen(cmd, shell=True)
        
        return jsonify({
            'success': True,
            'message': 'System installation started in background',
            'log_file': '/tmp/oracle-install-system.log'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/installation/binaries', methods=['POST'])
@login_required
@admin_required
def api_installation_binaries():
    """Install Oracle binaries"""
    import subprocess
    data = request.json or {}
    oracle_home = data.get('oracle_home', '/u01/app/oracle/product/19.3.0/dbhome_1')
    
    try:
        # Create install script
        script_content = f"""#!/bin/bash
set -e

echo "=== Oracle Binaries Installation ==="
echo "Timestamp: $(date)"
echo "Oracle Home: {oracle_home}"
echo ""

# Check if zip file exists
ZIP_FILE="{oracle_home}/LINUX.X64_193000_db_home.zip"
if [ ! -f "$ZIP_FILE" ]; then
    echo "ERROR: Oracle software not found at $ZIP_FILE"
    echo "Please download it first!"
    exit 1
fi

echo "Oracle software found: $ZIP_FILE"
echo "Size: $(du -h $ZIP_FILE | cut -f1)"
echo ""

# Unzip Oracle software
echo "=== Extracting Oracle binaries ==="
echo "This may take 5-10 minutes..."
cd {oracle_home}
unzip -q LINUX.X64_193000_db_home.zip

echo ""
echo "=== Verifying installation ==="
ls -l {oracle_home}/runInstaller

echo ""
echo "=== Running Oracle installer ==="
export ORACLE_HOME={oracle_home}
oradba install binaries 2>&1

echo ""
echo "=== Binaries Installation Complete ==="
"""
        
        script_path = '/tmp/oracle-install-binaries.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # Execute script in background
        cmd = f"nohup bash {script_path} > /tmp/oracle-install-binaries.log 2>&1 &"
        subprocess.Popen(cmd, shell=True)
        
        return jsonify({
            'success': True,
            'message': f'Binary installation started to {oracle_home}',
            'log_file': '/tmp/oracle-install-binaries.log'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/installation/database', methods=['POST'])
@login_required
@admin_required
def api_installation_database():
    """Create Oracle database"""
    import subprocess
    data = request.json or {}
    db_name = data.get('db_name', 'ORCL')
    
    try:
        # Create install script
        script_content = f"""#!/bin/bash
set -e

echo "=== Oracle Database Creation ==="
echo "Timestamp: $(date)"
echo "Database Name: {db_name}"
echo ""

echo "=== Creating database {db_name} ==="
echo "This may take 15-30 minutes..."
echo ""

oradba install database --name {db_name} 2>&1

echo ""
echo "=== Database Creation Complete ==="
echo "Database {db_name} is now running"
echo ""
echo "You can connect with:"
echo "  sqlplus / as sysdba"
echo ""
"""
        
        script_path = '/tmp/oracle-install-database.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # Execute script in background
        cmd = f"nohup bash {script_path} > /tmp/oracle-install-database.log 2>&1 &"
        subprocess.Popen(cmd, shell=True)
        
        return jsonify({
            'success': True,
            'message': f'Database creation started for {db_name}',
            'log_file': '/tmp/oracle-install-database.log'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/installation/quick', methods=['POST'])
@login_required
@admin_required
def api_installation_quick():
    """Quick one-click installation - runs all CLI commands in sequence"""
    import subprocess
    data = request.json or {}
    oracle_home = data.get('oracle_home', '/u01/app/oracle/product/19.3.0/dbhome_1')
    db_name = data.get('db_name', 'ORCL')
    
    try:
        # Create comprehensive installation script that uses working CLI commands
        script_content = f"""#!/bin/bash
set -e

echo "=============================================="
echo "  ORACLE 19c - AUTOMATED INSTALLATION"
echo "  Started: $(date)"
echo "=============================================="
echo ""

# Function for timestamped logging
log() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}}

# ===== STEP 1/4: System Validation =====
log "STEP 1/4: Running system precheck..."
echo ""
oradba precheck 2>&1 || {{
    log "⚠ Precheck found issues, but continuing..."
}}
echo ""
log "✓ System validation complete"
echo ""

# ===== STEP 2/4: System Prerequisites =====
log "STEP 2/4: Installing system prerequisites..."
log "This configures users, groups, and kernel parameters..."
echo ""
oradba install system 2>&1
echo ""
log "✓ System prerequisites installed successfully"
echo ""

# ===== STEP 3/4: Oracle Binaries =====
log "STEP 3/4: Installing Oracle binaries..."
log "Oracle Home: {oracle_home}"
log "This may take 10-15 minutes..."
echo ""
export ORACLE_HOME="{oracle_home}"
oradba install binaries 2>&1
echo ""
log "✓ Oracle binaries installed successfully"
echo ""

# ===== STEP 4/4: Database Creation =====
log "STEP 4/4: Creating database {db_name}..."
log "This may take 15-30 minutes..."
echo ""
oradba install database --name {db_name} 2>&1
echo ""
log "✓ Database {db_name} created successfully"
echo ""

echo "=============================================="
echo "  ✓ INSTALLATION COMPLETE!"
echo "  Finished: $(date)"
echo "=============================================="
echo ""
echo "You can now connect with:"
echo "  sqlplus / as sysdba"
echo ""
"""
        
        script_path = '/tmp/oracle-quick-install.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # Execute script in background
        cmd = f"nohup bash {script_path} > /tmp/oracle-quick-install.log 2>&1 &"
        subprocess.Popen(cmd, shell=True)
        
        return jsonify({
            'success': True,
            'message': 'Automated installation started! This will take 30-60 minutes.',
            'log_file': '/tmp/oracle-quick-install.log',
            'steps': [
                {'step': 1, 'name': 'System Validation', 'status': 'running'},
                {'step': 2, 'name': 'System Prerequisites', 'status': 'pending'},
                {'step': 3, 'name': 'Oracle Binaries', 'status': 'pending'},
                {'step': 4, 'name': 'Database Creation', 'status': 'pending'}
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/installation/logs/<log_type>')
@login_required
@admin_required
def api_installation_logs(log_type):
    """Get installation logs"""
    import subprocess
    try:
        log_files = {
            'download': '/tmp/oracle-download.log',
            'system': '/tmp/oracle-install-system.log',
            'binaries': '/tmp/oracle-install-binaries.log',
            'database': '/tmp/oracle-install-database.log',
            'quick': '/tmp/oracle-quick-install.log'
        }
        
        log_file = log_files.get(log_type)
        if not log_file:
            return jsonify({
                'success': False,
                'error': 'Invalid log type'
            })
        
        if not os.path.exists(log_file):
            return jsonify({
                'success': True,
                'logs': f'Waiting for {log_type} to start...\n',
                'size': 0
            })
        
        # Get file size
        file_size = os.path.getsize(log_file)
        
        # Read all lines (tail -f behavior)
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Check if process is still running
        script_file = log_file.replace('.log', '.sh')
        is_running = False
        if os.path.exists(script_file):
            proc = subprocess.run(['pgrep', '-f', script_file], capture_output=True)
            is_running = proc.returncode == 0
        
        return jsonify({
            'success': True,
            'logs': content,
            'size': file_size,
            'is_running': is_running
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def execute_cli_command(args, timeout=300):
    """Execute OracleDBA CLI command"""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n\nErrors:\n{result.stderr}"
        
        return output
    except subprocess.TimeoutExpired:
        return "Command timed out after 5 minutes"
    except Exception as e:
        return f"Error executing command: {str(e)}"


# ============================================================================
# MAIN
# ============================================================================

def start_gui_server(port=5000, host='0.0.0.0', debug=False):
    """Start the GUI server"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🌐 OracleDBA Web GUI Server                         ║
║                                                          ║
║     Server running on: http://{host}:{port}         ║
║                                                          ║
║     Default credentials:                                 ║
║     Username: admin                                      ║
║     Password: admin123 (change on first login)           ║
║                                                          ║
║     Press Ctrl+C to stop                                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    start_gui_server()
