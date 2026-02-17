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
        listener_ports = []
        listeners = []
        try:
            result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
            listener_running = 'tnslsnr' in result.stdout
            if listener_running:
                listeners = ['LISTENER']
                listener_ports = [1521]
        except:
            pass
        
        # Check ASM
        asm_running = False
        asm_installed = False
        try:
            result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
            asm_running = 'asm_pmon_' in result.stdout
            asm_installed = os.path.exists('/u01/app/grid') or os.path.exists('/u01/app/19.3.0/grid')
        except:
            pass
        
        # Check Grid/Cluster
        grid_installed = os.path.exists('/u01/app/grid') or os.path.exists('/u01/app/19.3.0/grid')
        grid_running = False
        cluster_configured = False
        try:
            if os.path.exists('/etc/oracle/olr.loc'):
                cluster_configured = True
            result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
            grid_running = 'ohasd' in result.stdout or 'crsd' in result.stdout
        except:
            pass
        
        # Get current SID from environment
        current_sid = os.environ.get('ORACLE_SID', running_dbs[0] if running_dbs else 'Not Set')
        
        # Count individual background processes
        db_processes = {'pmon': 0, 'smon': 0, 'dbwr': 0, 'lgwr': 0, 'ckpt': 0, 'arch': 0, 'reco': 0}
        try:
            result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
            ps_lines = result.stdout.split('\n')
            for line in ps_lines:
                if 'ora_pmon_' in line: db_processes['pmon'] += 1
                if 'ora_smon_' in line: db_processes['smon'] += 1
                if 'ora_dbw' in line: db_processes['dbwr'] += 1
                if 'ora_lgwr_' in line: db_processes['lgwr'] += 1
                if 'ora_ckpt_' in line: db_processes['ckpt'] += 1
                if 'ora_arc' in line and 'grep' not in line: db_processes['arch'] += 1
                if 'ora_reco_' in line: db_processes['reco'] += 1
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
                'count': len(running_dbs),
                'current_sid': current_sid,
                'processes': db_processes
            },
            'listener': {
                'running': listener_running,
                'status': 'Running' if listener_running else 'Stopped',
                'listeners': listeners,
                'ports': listener_ports
            },
            'cluster': {
                'configured': cluster_configured,
                'type': 'RAC' if cluster_configured else 'Single Instance',
                'nodes': []
            },
            'grid': {
                'installed': grid_installed,
                'running': grid_running,
                'status': 'Running' if grid_running else ('Installed' if grid_installed else 'Not Installed'),
                'grid_home': '/u01/app/19.3.0/grid' if grid_installed else ''
            },
            'asm': {
                'running': asm_running,
                'installed': asm_installed,
                'status': 'Running' if asm_running else 'Not Running',
                'disk_groups': []
            },
            'features': {
                'archivelog': False,
                'flashback': False,
                'dataguard': False,
                'rman': oracle_installed
            }
        }
    
    def _run_sql(self, sql, timeout=30):
        """Run SQL via sqlplus and return raw output (uses stdin pipe to preserve $ in view names)"""
        full_sql = f"SET PAGESIZE 1000\nSET LINESIZE 1000\nSET FEEDBACK OFF\nSET HEADING ON\nSET COLSEP '|'\nSET TRIMSPOOL ON\nSET TRIMOUT ON\n{sql}\nEXIT;\n"
        try:
            uid = os.getuid() if hasattr(os, 'getuid') else -1
            if uid == 0:
                cmd = ['su', '-', 'oracle', '-c',
                       f'{self.oracle_home}/bin/sqlplus -s "/ as sysdba"']
            else:
                cmd = [f'{self.oracle_home}/bin/sqlplus', '-s', '/ as sysdba']
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, _ = proc.communicate(input=full_sql, timeout=timeout)
            return stdout.strip()
        except Exception as e:
            return f"SQL Error: {e}"

    def _parse_sql_rows(self, output):
        """Parse pipe-delimited sqlplus output into list of dicts.
        Finds header line by looking for first line with '|' separators."""
        rows = []
        lines = [l.strip() for l in output.split('\n') if l.strip()]
        # Find header line: first line with '|' that isn't all dashes
        header_idx = -1
        for i, line in enumerate(lines):
            if '|' in line:
                stripped = line.replace(' ', '').replace('|', '')
                if stripped and not set(stripped) <= {'-'}:
                    header_idx = i
                    break
        if header_idx < 0:
            return rows
        headers = [h.strip() for h in lines[header_idx].split('|')]
        for line in lines[header_idx + 1:]:
            if '|' not in line:
                continue
            stripped = line.replace(' ', '').replace('|', '')
            if not stripped or set(stripped) <= {'-'}:
                continue
            vals = [v.strip() for v in line.split('|')]
            if len(vals) >= len(headers):
                rows.append(dict(zip(headers, vals[:len(headers)])))
        return rows

    def get_oracle_metrics(self):
        """Get Oracle performance metrics — SGA, PGA, sessions, tablespaces"""
        metrics = {
            'sga': {},
            'pga': {},
            'memory': {'total_sga_mb': 0, 'total_pga_mb': 0},
            'processes': {'count': 0},
            'sessions': {'count': 0},
            'datafiles': 0,
            'tempfiles': 0,
            'tablespaces': []
        }

        # Check if Oracle is running first
        running_dbs = self.get_running_databases()
        if not running_dbs:
            return metrics

        try:
            # SGA components
            sga_out = self._run_sql(
                "COL COMPONENT FORMAT A40\n"
                "SELECT component, ROUND(current_size/1024/1024, 2) AS size_mb "
                "FROM v$sga_dynamic_components WHERE current_size > 0;"
            )
            for row in self._parse_sql_rows(sga_out):
                try:
                    name = row.get('COMPONENT', '')
                    size = float(row.get('SIZE_MB', 0))
                    if name:
                        metrics['sga'][name] = size
                        metrics['memory']['total_sga_mb'] += size
                except (ValueError, TypeError):
                    pass
        except Exception:
            pass

        try:
            # PGA stats
            pga_out = self._run_sql(
                "COL NAME FORMAT A40\n"
                "SELECT name, ROUND(value/1024/1024, 2) AS size_mb FROM v$pgastat "
                "WHERE name IN ('total PGA allocated','total PGA inuse','maximum PGA allocated');"
            )
            for row in self._parse_sql_rows(pga_out):
                try:
                    name = row.get('NAME', '')
                    size = float(row.get('SIZE_MB', 0))
                    if name:
                        metrics['pga'][name] = size
                        if 'allocated' in name.lower() and 'max' not in name.lower():
                            metrics['memory']['total_pga_mb'] = size
                except (ValueError, TypeError):
                    pass
        except Exception:
            pass

        try:
            # Processes & sessions
            proc_out = self._run_sql("SELECT COUNT(*) AS cnt FROM v$process;")
            for row in self._parse_sql_rows(proc_out):
                try: metrics['processes']['count'] = int(row.get('CNT', 0))
                except: pass

            sess_out = self._run_sql("SELECT COUNT(*) AS cnt FROM v$session;")
            for row in self._parse_sql_rows(sess_out):
                try: metrics['sessions']['count'] = int(row.get('CNT', 0))
                except: pass
        except Exception:
            pass

        try:
            # Datafiles & tempfiles
            df_out = self._run_sql("SELECT COUNT(*) AS cnt FROM v$datafile;")
            for row in self._parse_sql_rows(df_out):
                try: metrics['datafiles'] = int(row.get('CNT', 0))
                except: pass

            tf_out = self._run_sql("SELECT COUNT(*) AS cnt FROM v$tempfile;")
            for row in self._parse_sql_rows(tf_out):
                try: metrics['tempfiles'] = int(row.get('CNT', 0))
                except: pass
        except Exception:
            pass

        try:
            # Tablespace usage
            ts_out = self._run_sql(
                "COL NAME FORMAT A30\n"
                "SELECT df.tablespace_name AS name, "
                "ROUND(df.bytes/1024/1024,2) AS total_mb, "
                "ROUND((df.bytes - NVL(fs.bytes,0))/1024/1024,2) AS used_mb, "
                "ROUND(NVL(fs.bytes,0)/1024/1024,2) AS free_mb, "
                "ROUND((df.bytes - NVL(fs.bytes,0))/df.bytes * 100, 1) AS pct_used "
                "FROM (SELECT tablespace_name, SUM(bytes) bytes FROM dba_data_files GROUP BY tablespace_name) df "
                "LEFT JOIN (SELECT tablespace_name, SUM(bytes) bytes FROM dba_free_space GROUP BY tablespace_name) fs "
                "ON df.tablespace_name = fs.tablespace_name ORDER BY df.tablespace_name;"
            )
            for row in self._parse_sql_rows(ts_out):
                try:
                    metrics['tablespaces'].append({
                        'name': row.get('NAME', ''),
                        'total_mb': float(row.get('TOTAL_MB', 0)),
                        'used_mb': float(row.get('USED_MB', 0)),
                        'free_mb': float(row.get('FREE_MB', 0)),
                        'pct_used': float(row.get('PCT_USED', 0))
                    })
                except (ValueError, TypeError):
                    pass
        except Exception:
            pass

        return metrics

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
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not new_password or not confirm_password:
            flash('Please fill in all password fields', 'error')
            return render_template('change_password.html',
                                   must_change=config_manager.load_users()[session['user']].get('must_change_password', False))
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('change_password.html',
                                   must_change=config_manager.load_users()[session['user']].get('must_change_password', False))
        
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
    # Return metrics at top level so JS can access metrics.sga, metrics.processes, etc.
    return jsonify(metrics)


@app.route('/api/installation-status')
@login_required
def api_installation_status():
    """API: Get what's installed and what can be activated"""
    try:
        detection = detector.detect_all()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
    binaries_val = detection.get('oracle', {}).get('binaries', False)
    binaries_installed = binaries_val if isinstance(binaries_val, bool) else binaries_val.get('lsnrctl', False) if isinstance(binaries_val, dict) else False
    
    installation_status = {
        'components': {
            'oracle_database': {
                'installed': detection.get('oracle', {}).get('installed', False),
                'version': detection.get('oracle', {}).get('version', 'Unknown'),
                'can_activate': detection.get('oracle', {}).get('installed', False) and not detection.get('database', {}).get('running', False),
                'active': detection.get('database', {}).get('running', False),
                'binaries': binaries_val
            },
            'listener': {
                'installed': binaries_installed,
                'can_activate': detection.get('oracle', {}).get('installed', False) and not detection.get('listener', {}).get('running', False),
                'active': detection.get('listener', {}).get('running', False),
                'ports': detection.get('listener', {}).get('ports', [])
            },
            'grid_infrastructure': {
                'installed': detection.get('grid', {}).get('installed', False),
                'can_activate': detection.get('grid', {}).get('installed', False) and not detection.get('grid', {}).get('running', False),
                'active': detection.get('grid', {}).get('running', False),
                'grid_home': detection.get('grid', {}).get('grid_home', '')
            },
            'asm': {
                'installed': detection.get('asm', {}).get('installed', False),
                'can_activate': detection.get('asm', {}).get('installed', False) and not detection.get('asm', {}).get('running', False),
                'active': detection.get('asm', {}).get('running', False),
                'disk_groups': detection.get('asm', {}).get('disk_groups', [])
            }
        },
        'features': detection.get('features', {}),
        'summary': {
            'total_components': 4,
            'installed': sum([
                detection.get('oracle', {}).get('installed', False),
                binaries_installed,
                detection.get('grid', {}).get('installed', False),
                detection.get('asm', {}).get('installed', False)
            ]),
            'active': sum([
                detection.get('database', {}).get('running', False),
                detection.get('listener', {}).get('running', False),
                detection.get('grid', {}).get('running', False),
                detection.get('asm', {}).get('running', False)
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
        if feature == 'archivelog':
            if action == 'enable':
                result = run_sqlplus("SHUTDOWN IMMEDIATE;\nSTARTUP MOUNT;\nALTER DATABASE ARCHIVELOG;\nALTER DATABASE OPEN;")
            else:
                result = run_sqlplus("SHUTDOWN IMMEDIATE;\nSTARTUP MOUNT;\nALTER DATABASE NOARCHIVELOG;\nALTER DATABASE OPEN;")
        elif feature == 'fra':
            if action == 'enable':
                result = run_sqlplus("ALTER SYSTEM SET db_recovery_file_dest_size = 10G SCOPE=BOTH;\nALTER SYSTEM SET db_recovery_file_dest = '/u01/app/oracle/fast_recovery_area' SCOPE=BOTH;")
            else:
                result = run_sqlplus("ALTER SYSTEM SET db_recovery_file_dest = '' SCOPE=BOTH;")
        elif feature == 'flashback':
            if action == 'enable':
                result = run_sqlplus("ALTER DATABASE FLASHBACK ON;")
            else:
                result = run_sqlplus("ALTER DATABASE FLASHBACK OFF;")
        elif feature == 'rman':
            oracle_home = os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
            if action == 'enable':
                rman_cmd = "CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 7 DAYS;\nCONFIGURE CONTROLFILE AUTOBACKUP ON;"
                result = run_shell_command(f'source ~/.bash_profile 2>/dev/null; echo "{rman_cmd}" | {oracle_home}/bin/rman target /', as_oracle=True)
            else:
                result = 'RMAN cannot be disabled.'
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
            'installation_valid': detection['oracle']['binaries'] if isinstance(detection['oracle']['binaries'], bool) else all(detection['oracle']['binaries'].values())
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
    """API: List all databases (CDB + PDBs) as structured JSON"""
    try:
        instance_info = run_sqlplus(
            "SELECT INSTANCE_NAME, STATUS, DATABASE_STATUS FROM V$INSTANCE;"
        )
        pdb_info = run_sqlplus(
            "SELECT NAME, OPEN_MODE, CON_ID FROM V$PDBS ORDER BY CON_ID;"
        )
        cdb_rows = parse_sql_rows(instance_info)
        pdb_rows = parse_sql_rows(pdb_info)
        cdb = {}
        if cdb_rows:
            cdb = {
                'instance_name': cdb_rows[0].get('INSTANCE_NAME', ''),
                'status': cdb_rows[0].get('STATUS', ''),
                'database_status': cdb_rows[0].get('DATABASE_STATUS', '')
            }
        pdbs = []
        for row in pdb_rows:
            pdbs.append({
                'name': row.get('NAME', ''),
                'open_mode': row.get('OPEN_MODE', ''),
                'con_id': row.get('CON_ID', '')
            })
        return jsonify({'success': True, 'cdb': cdb, 'pdbs': pdbs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/databases/create', methods=['POST'])
@login_required
def api_databases_create():
    """API: Create a new Pluggable Database"""
    data = request.json
    sid = data.get('sid', 'PRODDB').upper()
    memory = data.get('memory', 2048)
    
    # Sanitize SID name (alphanumeric + underscore only)
    import re as _re
    if not _re.match(r'^[A-Z][A-Z0-9_]{0,29}$', sid):
        return jsonify({'success': False, 'error': 'Invalid SID name. Use uppercase letters, digits, underscore (max 30 chars).'})
    
    try:
        sql = f"""CREATE PLUGGABLE DATABASE {sid} ADMIN USER {sid}_admin IDENTIFIED BY Oracle123
  FILE_NAME_CONVERT = ('/u01/app/oracle/oradata/GDCPROD/pdbseed/', '/u01/app/oracle/oradata/GDCPROD/{sid}/');
ALTER PLUGGABLE DATABASE {sid} OPEN;
ALTER PLUGGABLE DATABASE {sid} SAVE STATE;"""
        result = run_sqlplus(sql)
        return jsonify({'success': True, 'output': f'PDB {sid} created successfully.\n{result}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/databases/pdb/<name>/open', methods=['POST'])
@login_required
@admin_required
def api_databases_pdb_open(name):
    """API: Open a PDB"""
    import re as _re
    if not _re.match(r'^[A-Za-z][A-Za-z0-9_$#]{0,29}$', name):
        return jsonify({'success': False, 'error': 'Invalid PDB name.'})
    result = run_sqlplus(f"ALTER PLUGGABLE DATABASE {name.upper()} OPEN;\nALTER PLUGGABLE DATABASE {name.upper()} SAVE STATE;")
    return jsonify({'success': True, 'output': result})


@app.route('/api/databases/pdb/<name>/close', methods=['POST'])
@login_required
@admin_required
def api_databases_pdb_close(name):
    """API: Close a PDB"""
    import re as _re
    if not _re.match(r'^[A-Za-z][A-Za-z0-9_$#]{0,29}$', name):
        return jsonify({'success': False, 'error': 'Invalid PDB name.'})
    result = run_sqlplus(f"ALTER PLUGGABLE DATABASE {name.upper()} CLOSE IMMEDIATE;")
    return jsonify({'success': True, 'output': result})


@app.route('/api/databases/pdb/<name>/drop', methods=['POST'])
@login_required
@admin_required
def api_databases_pdb_drop(name):
    """API: Drop a PDB"""
    import re as _re
    if not _re.match(r'^[A-Za-z][A-Za-z0-9_$#]{0,29}$', name):
        return jsonify({'success': False, 'error': 'Invalid PDB name.'})
    result = run_sqlplus(f"ALTER PLUGGABLE DATABASE {name.upper()} CLOSE IMMEDIATE;\nDROP PLUGGABLE DATABASE {name.upper()} INCLUDING DATAFILES;")
    return jsonify({'success': True, 'output': result})


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
    """API: List tablespaces with size info as structured JSON"""
    try:
        sql = """SELECT df.tablespace_name AS "TABLESPACE_NAME",
       ROUND(df.bytes/1024/1024) AS "SIZE_MB",
       ROUND(NVL(fs.bytes,0)/1024/1024) AS "FREE_MB",
       ROUND((df.bytes - NVL(fs.bytes,0))/1024/1024) AS "USED_MB",
       df.autoextensible AS "AUTOEXT"
FROM (SELECT tablespace_name, SUM(bytes) bytes, MAX(autoextensible) autoextensible
      FROM dba_data_files GROUP BY tablespace_name) df
LEFT JOIN (SELECT tablespace_name, SUM(bytes) bytes
      FROM dba_free_space GROUP BY tablespace_name) fs
  ON df.tablespace_name = fs.tablespace_name
ORDER BY df.tablespace_name;"""
        result = run_sqlplus(sql)
        rows = parse_sql_rows(result)
        tablespaces = []
        for row in rows:
            try:
                size = float(row.get('SIZE_MB', 0))
                free = float(row.get('FREE_MB', 0))
                used = float(row.get('USED_MB', 0))
                pct = round((used / size * 100) if size > 0 else 0, 1)
            except (ValueError, TypeError, ZeroDivisionError):
                size = free = used = pct = 0
            tablespaces.append({
                'name': row.get('TABLESPACE_NAME', ''),
                'size_mb': size, 'free_mb': free, 'used_mb': used,
                'pct_used': pct, 'autoext': row.get('AUTOEXT', 'NO')
            })
        return jsonify({'success': True, 'tablespaces': tablespaces})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/storage/tablespace/create', methods=['POST'])
@login_required
def api_storage_tablespace_create():
    """API: Create tablespace"""
    data = request.json
    name = data.get('name', '').upper()
    size = data.get('size', '500M').upper()
    autoextend = data.get('autoextend', True)
    
    import re as _re
    if not name or not _re.match(r'^[A-Z][A-Z0-9_]{0,29}$', name):
        return jsonify({'success': False, 'error': 'Invalid tablespace name.'})
    
    try:
        autoext_clause = ' AUTOEXTEND ON NEXT 100M MAXSIZE UNLIMITED' if autoextend else ''
        sql = f"""CREATE TABLESPACE {name}
  DATAFILE '/u01/app/oracle/oradata/GDCPROD/{name.lower()}01.dbf' SIZE {size}{autoext_clause};"""
        result = run_sqlplus(sql)
        return jsonify({'success': True, 'output': f'Tablespace {name} created.\n{result}'})
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
    """API: ARCHIVELOG status - returns structured JSON"""
    try:
        result = run_sqlplus("SELECT LOG_MODE, FLASHBACK_ON FROM V$DATABASE;")
        rows = parse_sql_rows(result)
        log_mode = rows[0].get('LOG_MODE', 'UNKNOWN') if rows else 'UNKNOWN'
        flashback_on = rows[0].get('FLASHBACK_ON', 'NO') if rows else 'NO'
        return jsonify({'success': True, 'log_mode': log_mode, 'flashback_on': flashback_on})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/protection/archivelog/enable', methods=['POST'])
@login_required
def api_protection_archivelog_enable():
    """API: Enable ARCHIVELOG"""
    try:
        result = run_sqlplus("SHUTDOWN IMMEDIATE;\nSTARTUP MOUNT;\nALTER DATABASE ARCHIVELOG;\nALTER DATABASE OPEN;")
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
        oracle_home = os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
        if backup_type == 'incremental':
            rman_cmd = "BACKUP INCREMENTAL LEVEL 1 DATABASE PLUS ARCHIVELOG;"
        else:
            rman_cmd = "BACKUP DATABASE PLUS ARCHIVELOG;"
        
        # Run RMAN in background since backups take time
        log_file = '/tmp/rman-backup.log'
        cmd = f'source ~/.bash_profile 2>/dev/null; echo "{rman_cmd}" | {oracle_home}/bin/rman target / > {log_file} 2>&1'
        run_shell_command(f'nohup bash -c \'{cmd}\' &', as_oracle=True, timeout=10)
        return jsonify({'success': True, 'output': f'RMAN {backup_type} backup started. Check log: {log_file}'})
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
    """API: List database users as structured JSON"""
    try:
        sql = """COL "USERNAME" FORMAT A30
COL "ACCOUNT_STATUS" FORMAT A30
COL "DEFAULT_TABLESPACE" FORMAT A30
SELECT username AS "USERNAME", account_status AS "ACCOUNT_STATUS",
       default_tablespace AS "DEFAULT_TABLESPACE", profile AS "PROFILE",
       TO_CHAR(created, 'YYYY-MM-DD') AS "CREATED"
FROM dba_users ORDER BY username FETCH FIRST 50 ROWS ONLY;"""
        result = run_sqlplus(sql)
        rows = parse_sql_rows(result)
        users = []
        for row in rows:
            users.append({
                'username': row.get('USERNAME', ''),
                'account_status': row.get('ACCOUNT_STATUS', ''),
                'default_tablespace': row.get('DEFAULT_TABLESPACE', ''),
                'profile': row.get('PROFILE', ''),
                'created': row.get('CREATED', '')
            })
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/security/user/create', methods=['POST'])
@login_required
def api_security_user_create():
    """API: Create database user"""
    data = request.json
    username = data.get('username', '').upper()
    password = data.get('password', '')
    default_ts = data.get('defaultTs', 'USERS').upper()
    profile = data.get('profile', 'DEFAULT').upper()
    
    import re as _re
    if not username or not _re.match(r'^[A-Z][A-Z0-9_]{0,29}$', username):
        return jsonify({'success': False, 'error': 'Invalid username.'})
    if not password or len(password) < 4:
        return jsonify({'success': False, 'error': 'Password must be at least 4 characters.'})
    
    try:
        sql = f"""CREATE USER {username} IDENTIFIED BY \"{password}\"
  DEFAULT TABLESPACE {default_ts}
  TEMPORARY TABLESPACE TEMP
  PROFILE {profile};
GRANT CONNECT, RESOURCE TO {username};
ALTER USER {username} QUOTA UNLIMITED ON {default_ts};"""
        result = run_sqlplus(sql)
        return jsonify({'success': True, 'output': f'User {username} created.\n{result}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/security/user/<name>/lock', methods=['POST'])
@login_required
@admin_required
def api_security_user_lock(name):
    """API: Lock a database user"""
    result = run_sqlplus(f"ALTER USER {name.upper()} ACCOUNT LOCK;")
    return jsonify({'success': True, 'output': result})


@app.route('/api/security/user/<name>/unlock', methods=['POST'])
@login_required
@admin_required
def api_security_user_unlock(name):
    """API: Unlock a database user"""
    result = run_sqlplus(f"ALTER USER {name.upper()} ACCOUNT UNLOCK;")
    return jsonify({'success': True, 'output': result})


@app.route('/api/security/user/<name>/drop', methods=['POST'])
@login_required
@admin_required
def api_security_user_drop(name):
    """API: Drop a database user"""
    result = run_sqlplus(f"DROP USER {name.upper()} CASCADE;")
    return jsonify({'success': True, 'output': result})


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
        result = run_shell_command('crsctl stat res -t 2>/dev/null || echo "Cluster not configured. Single-instance mode."', as_oracle=False)
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
    
    return jsonify({
        'success': False, 
        'error': f'RAC node addition requires Grid Infrastructure. Configure NFS/SSH first, then run TP15 from the Labs page.'
    })


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
    """API: Create sample HR schema"""
    try:
        sql = """-- Create HR user for sample schema
CREATE USER HR IDENTIFIED BY hr123 DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE TEMP;
GRANT CONNECT, RESOURCE, CREATE VIEW TO HR;
ALTER USER HR QUOTA UNLIMITED ON USERS;

-- Create sample tables as HR
ALTER SESSION SET CURRENT_SCHEMA = HR;

CREATE TABLE departments (
    department_id NUMBER(4) PRIMARY KEY,
    department_name VARCHAR2(30) NOT NULL
);

CREATE TABLE employees (
    employee_id NUMBER(6) PRIMARY KEY,
    first_name VARCHAR2(20),
    last_name VARCHAR2(25) NOT NULL,
    email VARCHAR2(25) NOT NULL UNIQUE,
    hire_date DATE NOT NULL,
    salary NUMBER(8,2),
    department_id NUMBER(4) REFERENCES departments(department_id)
);

INSERT INTO departments VALUES (10, 'Administration');
INSERT INTO departments VALUES (20, 'Marketing');
INSERT INTO departments VALUES (30, 'IT');
INSERT INTO departments VALUES (40, 'Human Resources');
INSERT INTO departments VALUES (50, 'Finance');

INSERT INTO employees VALUES (100, 'Steven', 'King', 'SKING', SYSDATE-3650, 24000, 10);
INSERT INTO employees VALUES (101, 'Neena', 'Kochhar', 'NKOCHHAR', SYSDATE-3000, 17000, 10);
INSERT INTO employees VALUES (102, 'Lex', 'De Haan', 'LDEHAAN', SYSDATE-2800, 17000, 30);
INSERT INTO employees VALUES (103, 'Alexander', 'Hunold', 'AHUNOLD', SYSDATE-2500, 9000, 30);
INSERT INTO employees VALUES (104, 'Bruce', 'Ernst', 'BERNST', SYSDATE-2200, 6000, 30);
INSERT INTO employees VALUES (105, 'Diana', 'Lorentz', 'DLORENTZ', SYSDATE-2000, 4200, 30);
INSERT INTO employees VALUES (106, 'Daniel', 'Faviet', 'DFAVIET', SYSDATE-1800, 9000, 50);
INSERT INTO employees VALUES (107, 'John', 'Chen', 'JCHEN', SYSDATE-1600, 8200, 50);

COMMIT;"""
        result = run_sqlplus(sql)
        return jsonify({'success': True, 'output': f'Sample HR schema created with departments and employees tables.\n{result}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sample/test', methods=['POST'])
@login_required
def api_sample_test():
    """API: Test sample database queries"""
    try:
        sql = """SELECT 'Departments: ' || COUNT(*) AS result FROM hr.departments
UNION ALL
SELECT 'Employees: ' || COUNT(*) FROM hr.employees
UNION ALL
SELECT 'Avg Salary: $' || TO_CHAR(ROUND(AVG(salary),2)) FROM hr.employees;

SELECT department_name, COUNT(e.employee_id) AS emp_count, ROUND(AVG(e.salary),0) AS avg_sal
FROM hr.departments d LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY department_name ORDER BY department_name;"""
        result = run_sqlplus(sql)
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
    """API: Execute command in terminal - supports oradba, sqlplus, lsnrctl, rman, and basic shell"""
    data = request.json
    command = data.get('command', '')
    
    if not command:
        return jsonify({'success': False, 'error': 'No command provided'})
    
    # Whitelist of allowed command prefixes for DBA operations
    ALLOWED_PREFIXES = [
        'oradba ',       # Our CLI tool
        'sqlplus ',      # SQL*Plus
        'lsnrctl ',      # Listener control
        'rman ',         # RMAN backup/recovery
        'asmcmd ',       # ASM commands
        'srvctl ',       # Server control for RAC
        'crsctl ',       # Cluster control
        'dbca ',         # Database Configuration Assistant
        'emctl ',        # Enterprise Manager
        'expdp ',        # Data Pump Export
        'impdp ',        # Data Pump Import
        'adrci ',        # ADR Command Interpreter
        'opatch ',       # Oracle patch utility
        'datapatch ',    # SQL patch utility
    ]
    
    # Also allow these exact commands (no prefix)
    ALLOWED_EXACT = [
        'id oracle', 'hostname', 'uname -a', 'df -h', 'free -h',
        'uptime', 'nproc', 'cat /etc/os-release', 'cat /etc/oratab',
        'ps aux | grep ora_', 'ps aux | grep tnslsnr',
        'echo $ORACLE_HOME', 'echo $ORACLE_SID', 'echo $ORACLE_BASE',
        'ls $ORACLE_HOME', 'ls /u01/app/oracle/oradata',
    ]
    
    # Reject shell metacharacters to prevent command injection
    # Allow pipes only in pre-approved ALLOWED_EXACT commands
    DANGEROUS_CHARS = [';', '&&', '||', '$(', '`', '>', '<', '\n', '\r']
    has_pipe = '|' in command
    
    # Security check
    is_exact = command.strip() in ALLOWED_EXACT
    if not is_exact:
        # For non-exact commands, reject ALL shell metacharacters including pipes
        if has_pipe or any(ch in command for ch in DANGEROUS_CHARS):
            return jsonify({
                'success': False,
                'error': 'Shell metacharacters (;, &&, ||, |, $(), `, >, <) are not allowed in commands.'
            })
    
    allowed = any(command.startswith(prefix) for prefix in ALLOWED_PREFIXES)
    if not allowed:
        allowed = is_exact
    if not allowed:
        # Allow commands starting with common safe utilities
        SAFE_STARTS = ['cat /etc/', 'ls /u01/', 'ls /home/oracle', 'tail ', 'head ', 'grep ']
        allowed = any(command.startswith(s) for s in SAFE_STARTS)
    
    if not allowed:
        return jsonify({
            'success': False, 
            'error': 'Command not allowed. Allowed: oradba, sqlplus, lsnrctl, rman, asmcmd, srvctl, crsctl, dbca, expdp, impdp, opatch, and basic system commands.'
        })
    
    try:
        if command.startswith('oradba '):
            result = execute_cli_command(command.split())
        else:
            # Run as oracle user with Oracle environment
            result = run_shell_command(
                f'source ~/.bash_profile 2>/dev/null; export CV_ASSUME_DISTID=OEL7.8; {command}',
                as_oracle=True,
                timeout=120
            )
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


@app.route('/api/installation/detect', methods=['GET'])
@login_required
@admin_required
def api_installation_detect():
    """Detailed detection of Oracle installation state for the installation wizard"""
    import subprocess
    checks = {}

    # 1. Oracle user exists?
    try:
        result = subprocess.run(['id', 'oracle'], capture_output=True, text=True)
        checks['oracle_user'] = result.returncode == 0
    except Exception:
        checks['oracle_user'] = False

    # 2. Required groups (oinstall, dba)
    try:
        result = subprocess.run(['getent', 'group', 'oinstall'], capture_output=True, text=True)
        oinstall = result.returncode == 0
        result = subprocess.run(['getent', 'group', 'dba'], capture_output=True, text=True)
        dba = result.returncode == 0
        checks['groups'] = oinstall and dba
    except Exception:
        checks['groups'] = False

    # 3. Oracle zip downloaded?
    zip_paths = [
        '/u01/app/oracle/LINUX.X64_193000_db_home.zip',
        '/tmp/LINUX.X64_193000_db_home.zip',
        '/home/oracle/LINUX.X64_193000_db_home.zip',
        os.path.join(detector.oracle_home, 'LINUX.X64_193000_db_home.zip'),
    ]
    checks['zip_downloaded'] = any(os.path.exists(p) for p in zip_paths)
    checks['zip_path'] = next((p for p in zip_paths if os.path.exists(p)), None)

    # 4. ORACLE_HOME directory exists?
    checks['oracle_home_exists'] = os.path.isdir(detector.oracle_home)
    checks['oracle_home'] = detector.oracle_home

    # 5. Key binaries present?
    binaries = {}
    for b in ['sqlplus', 'lsnrctl', 'dbca', 'rman', 'emctl']:
        binaries[b] = os.path.exists(os.path.join(detector.oracle_home, 'bin', b))
    checks['binaries'] = binaries
    checks['binaries_installed'] = binaries.get('sqlplus', False) and binaries.get('lsnrctl', False)

    # 6. /etc/oratab exists and has entries?
    checks['oratab'] = False
    checks['oratab_entries'] = []
    if os.path.exists('/etc/oratab'):
        try:
            with open('/etc/oratab', 'r') as f:
                entries = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            checks['oratab'] = len(entries) > 0
            checks['oratab_entries'] = entries
        except Exception:
            pass

    # 7. Running database processes?
    running_dbs = detector.get_running_databases()
    checks['database_running'] = len(running_dbs) > 0
    checks['running_instances'] = running_dbs

    # 8. Listener running?
    try:
        result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
        checks['listener_running'] = 'tnslsnr' in result.stdout
    except Exception:
        checks['listener_running'] = False

    # 9. Kernel parameters set?
    checks['kernel_params'] = False
    try:
        if os.path.exists('/etc/sysctl.d/97-oracle-database-sysctl.conf'):
            checks['kernel_params'] = True
        elif os.path.exists('/etc/sysctl.conf'):
            with open('/etc/sysctl.conf', 'r') as f:
                checks['kernel_params'] = 'shmmax' in f.read().lower()
    except Exception:
        pass

    # 10. Disk space on /u01
    checks['disk_space'] = None
    try:
        result = subprocess.run(['df', '-BG', '/u01'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    checks['disk_space'] = {
                        'total': parts[1],
                        'used': parts[2],
                        'available': parts[3]
                    }
    except Exception:
        pass

    # Compute overall step status
    steps = {
        'step1_download': checks['zip_downloaded'],
        'step2_system': checks['oracle_user'] and checks['groups'] and checks['kernel_params'],
        'step3_binaries': checks['binaries_installed'],
        'step4_database': checks['database_running']
    }
    checks['steps'] = steps

    # Overall readiness
    checks['fully_installed'] = all(steps.values())

    return jsonify({'success': True, 'checks': checks})


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
    python3 -m pip install --upgrade pip 2>/dev/null || true
    python3 -m pip install --user gdown 2>/dev/null || pip3 install --user gdown
    export PATH=$PATH:~/.local/bin
fi

# Download Oracle 19c from Google Drive
echo ""
echo "=== Downloading Oracle 19c (3.06 GB) ==="
echo "This may take 10-20 minutes depending on your connection..."
echo ""

cd {oracle_home}
export PATH=$HOME/.local/bin:$PATH
gdown {file_id} -O {download_path}

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
    """Install system prerequisites - runs TP01 directly"""
    try:
        result = run_tp_script('01', background=True, as_user='root')
        if result.get('success'):
            result['message'] = 'System prerequisites installation started (TP01)'
            result['log_file'] = '/tmp/tp01.log'
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/installation/binaries', methods=['POST'])
@login_required
@admin_required
def api_installation_binaries():
    """Install Oracle binaries - runs TP02 directly"""
    try:
        result = run_tp_script('02', background=True, as_user='oracle')
        if result.get('success'):
            result['message'] = 'Oracle binaries installation started (TP02)'
            result['log_file'] = '/tmp/tp02.log'
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/installation/database', methods=['POST'])
@login_required
@admin_required
def api_installation_database():
    """Create Oracle database - runs TP03 directly"""
    try:
        result = run_tp_script('03', background=True, as_user='oracle')
        if result.get('success'):
            result['message'] = 'Database creation started (TP03)'
            result['log_file'] = '/tmp/tp03.log'
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/installation/quick', methods=['POST'])
@login_required
@admin_required
def api_installation_quick():
    """One-click installation — runs oradba install --yes (same code path as CLI)"""
    try:
        log_file = '/tmp/oracle-install-all.log'

        # Use the unified CLI command so both CLI and GUI share identical logic.
        # oradba install --yes  →  InstallManager.install_all(auto_yes=True)
        # stdout is redirected to the log file; install.py also writes its own
        # log under /var/log/oracledba/install-all.log.
        cmd = f"nohup oradba install --yes > {log_file} 2>&1 &"
        subprocess.Popen(cmd, shell=True)

        return jsonify({
            'success': True,
            'message': 'Automated installation started (oradba install --yes). This will take 30-60 minutes.',
            'log_file': log_file,
            'steps': [
                {'step': 1, 'name': 'System Readiness', 'status': 'running'},
                {'step': 2, 'name': 'Download & Extract Binaries', 'status': 'pending'},
                {'step': 3, 'name': 'Install Oracle Software', 'status': 'pending'},
                {'step': 4, 'name': 'Create Database', 'status': 'pending'}
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/installation/logs/<log_type>')
@login_required
@admin_required
def api_installation_logs(log_type):
    """Get installation logs with step-progress detection"""
    import subprocess
    try:
        log_files = {
            'download': '/tmp/oracle-download.log',
            'system': '/tmp/tp01.log',
            'binaries': '/tmp/tp02.log',
            'database': '/tmp/tp03.log',
            'quick': '/tmp/oracle-install-all.log'
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
                'size': 0,
                'is_running': True,
                'current_step': 0
            })
        
        # Get file size
        file_size = os.path.getsize(log_file)
        
        # Read all content
        with open(log_file, 'r', errors='replace') as f:
            content = f.read()
        
        # Check if process is still running
        is_running = False
        if log_type == 'quick':
            # For unified install, check for the oradba install process
            proc = subprocess.run(['pgrep', '-f', 'oradba install'], capture_output=True)
            is_running = proc.returncode == 0
        else:
            script_file = log_file.replace('.log', '.sh')
            if os.path.exists(script_file):
                proc = subprocess.run(['pgrep', '-f', script_file], capture_output=True)
                is_running = proc.returncode == 0
        
        # Parse step progress from log content (from InstallManager step markers)
        current_step = 0
        total_steps = 4
        step_statuses = {}
        if content:
            import re
            # Detect "Step X/Y" headers from install.py _step_header()
            step_matches = re.findall(r'Step (\d+)/(\d+)', content)
            if step_matches:
                current_step = int(step_matches[-1][0])
                total_steps = int(step_matches[-1][1])
            # Detect completed steps from _step_result()
            completed = re.findall(r'[✓✓] Step (\d+) complete', content)
            for s in completed:
                step_statuses[int(s)] = 'complete'
            # Detect failed steps
            failed = re.findall(r'[✗✗] Step (\d+) FAILED', content)
            for s in failed:
                step_statuses[int(s)] = 'failed'
            # Detect overall completion
            if 'Installation Complete' in content:
                current_step = total_steps
        
        return jsonify({
            'success': True,
            'logs': content,
            'size': file_size,
            'is_running': is_running,
            'current_step': current_step,
            'total_steps': total_steps,
            'step_statuses': step_statuses
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
    """Execute OracleDBA CLI command with proper PATH"""
    oracle_home = os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
    env = os.environ.copy()
    env['PATH'] = f"{oracle_home}/bin:/usr/local/bin:/usr/bin:/bin:" + env.get('PATH', '')
    env['ORACLE_HOME'] = oracle_home
    env['ORACLE_SID'] = os.environ.get('ORACLE_SID', 'GDCPROD')
    env['CV_ASSUME_DISTID'] = 'OEL7.8'
    
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n\nErrors:\n{result.stderr}"
        
        return output
    except subprocess.TimeoutExpired:
        return "Command timed out after 5 minutes"
    except FileNotFoundError:
        return f"Command not found: {args[0]}. Make sure package is installed (pip install -e .)"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def run_sqlplus(sql, as_sysdba=True, timeout=60):
    """Run SQL command via sqlplus and return output (uses stdin pipe to preserve $ in V$ view names)"""
    oracle_home = os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
    oracle_sid = os.environ.get('ORACLE_SID', 'GDCPROD')
    
    connect_str = '/ as sysdba' if as_sysdba else '/'
    
    full_sql = f"SET PAGESIZE 1000\nSET LINESIZE 1000\nSET FEEDBACK OFF\nSET HEADING ON\nSET COLSEP '|'\nSET TRIMSPOOL ON\nSET TRIMOUT ON\n{sql}\nEXIT;\n"
    
    try:
        uid = os.getuid() if hasattr(os, 'getuid') else -1
        if uid == 0:
            cmd = ['su', '-', 'oracle', '-c',
                   f'{oracle_home}/bin/sqlplus -s "{connect_str}"']
        else:
            cmd = [f'{oracle_home}/bin/sqlplus', '-s', connect_str]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, _ = proc.communicate(input=full_sql, timeout=timeout)
        return stdout.strip()
    except Exception as e:
        return f"SQL Error: {str(e)}"


def parse_sql_rows(output):
    """Parse pipe-delimited sqlplus output into list of dicts.
    Finds header line by looking for the first line with '|' separators.
    Skips wrapped lines (no '|') and separator lines (all dashes)."""
    rows = []
    lines = [l.strip() for l in output.split('\n') if l.strip()]
    # Find header line: first line with '|' that isn't all dashes
    header_idx = -1
    for i, line in enumerate(lines):
        if '|' in line:
            stripped = line.replace(' ', '').replace('|', '')
            if stripped and not set(stripped) <= {'-'}:
                header_idx = i
                break
    if header_idx < 0:
        return rows
    headers = [h.strip() for h in lines[header_idx].split('|')]
    for line in lines[header_idx + 1:]:
        if '|' not in line:
            continue
        stripped = line.replace(' ', '').replace('|', '')
        if not stripped or set(stripped) <= {'-'}:
            continue
        vals = [v.strip() for v in line.split('|')]
        if len(vals) >= len(headers):
            rows.append(dict(zip(headers, vals[:len(headers)])))
    return rows


def run_tp_script(tp_number, background=True, as_user='oracle'):
    """Run a TP script from the scripts directory"""
    scripts_dir = Path(__file__).parent / 'scripts'
    
    tp_map = {
        '01': ('tp01-system-readiness.sh', 'root'),
        '02': ('tp02-installation-binaire.sh', 'oracle'),
        '03': ('tp03-creation-instance.sh', 'oracle'),
        '04': ('tp04-fichiers-critiques.sh', 'oracle'),
        '05': ('tp05-gestion-stockage.sh', 'oracle'),
        '06': ('tp06-securite-acces.sh', 'oracle'),
        '07': ('tp07-flashback.sh', 'oracle'),
        '08': ('tp08-rman.sh', 'oracle'),
        '09': ('tp09-dataguard.sh', 'oracle'),
        '10': ('tp10-tuning.sh', 'oracle'),
        '11': ('tp11-patching.sh', 'oracle'),
        '12': ('tp12-multitenant.sh', 'oracle'),
        '13': ('tp13-ai-foundations.sh', 'oracle'),
        '14': ('tp14-mobilite-concurrence.sh', 'oracle'),
        '15': ('tp15-asm-rac-concepts.sh', 'oracle'),
    }
    
    if tp_number not in tp_map:
        return {'success': False, 'error': f'Unknown TP: {tp_number}'}
    
    script_name, default_user = tp_map[tp_number]
    script_path = scripts_dir / script_name
    
    if not script_path.exists():
        return {'success': False, 'error': f'Script not found: {script_path}'}
    
    log_file = f'/tmp/tp{tp_number}.log'
    run_user = as_user or default_user
    
    env_setup = 'source ~/.bash_profile 2>/dev/null; export CV_ASSUME_DISTID=OEL7.8;'
    
    is_root = False
    try:
        is_root = os.getuid() == 0
    except AttributeError:
        pass
    
    if background:
        if run_user == 'oracle' and is_root:
            cmd = f'nohup su - oracle -c "{env_setup} bash {script_path}" > {log_file} 2>&1 &'
        else:
            cmd = f'nohup bash {script_path} > {log_file} 2>&1 &'
        
        subprocess.Popen(cmd, shell=True)
        return {
            'success': True,
            'message': f'TP{tp_number} ({script_name}) started in background',
            'log_file': log_file,
            'script': script_name
        }
    else:
        try:
            if run_user == 'oracle' and is_root:
                cmd = ['su', '-', 'oracle', '-c', f'{env_setup} bash {script_path}']
            else:
                cmd = ['bash', str(script_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            # Also write to log file
            with open(log_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write('\n--- STDERR ---\n')
                    f.write(result.stderr)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout + ('\n' + result.stderr if result.stderr else ''),
                'log_file': log_file
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Script timed out (>60 min)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


def run_shell_command(command, as_oracle=True, timeout=120):
    """Run a shell command and return output"""
    try:
        uid = -1
        try:
            uid = os.getuid()
        except AttributeError:
            uid = -1
        
        if as_oracle and uid == 0:
            cmd = ['su', '-', 'oracle', '-c', command]
        else:
            cmd = ['bash', '-c', command]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout + (result.stderr if result.stderr else '')
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# LABS - RUN ANY TP SCRIPT FROM GUI
# ============================================================================

@app.route('/labs')
@login_required
def labs():
    """Labs management page - run any TP script"""
    return render_template('labs.html')


@app.route('/api/labs/list')
@login_required
def api_labs_list():
    """API: List all available TP labs"""
    labs_info = [
        {'number': '01', 'name': 'System Readiness', 'description': 'Users, groups, packages, kernel params', 'category': 'Installation', 'user': 'root', 'duration': '5-10 min'},
        {'number': '02', 'name': 'Binary Installation', 'description': 'Download Oracle 19c binaries (3GB)', 'category': 'Installation', 'user': 'oracle', 'duration': '10-20 min'},
        {'number': '03', 'name': 'Database Creation', 'description': 'runInstaller + DBCA database', 'category': 'Installation', 'user': 'oracle', 'duration': '15-30 min'},
        {'number': '04', 'name': 'Critical Files', 'description': 'Multiplex control files, redo logs', 'category': 'Configuration', 'user': 'oracle', 'duration': '5 min'},
        {'number': '05', 'name': 'Storage Management', 'description': 'Tablespaces, datafiles, OMF', 'category': 'Configuration', 'user': 'oracle', 'duration': '5 min'},
        {'number': '06', 'name': 'Security & Access', 'description': 'Users, roles, profiles, privileges', 'category': 'Security', 'user': 'oracle', 'duration': '5 min'},
        {'number': '07', 'name': 'Flashback', 'description': 'Flashback query, table, database', 'category': 'Protection', 'user': 'oracle', 'duration': '5 min'},
        {'number': '08', 'name': 'RMAN Backup', 'description': 'Backup strategies and recovery', 'category': 'Protection', 'user': 'oracle', 'duration': '10 min'},
        {'number': '09', 'name': 'Data Guard', 'description': 'High availability standby setup', 'category': 'HA', 'user': 'oracle', 'duration': '10 min'},
        {'number': '10', 'name': 'Performance Tuning', 'description': 'AWR, SQL tuning, optimization', 'category': 'Performance', 'user': 'oracle', 'duration': '5 min'},
        {'number': '11', 'name': 'Patching', 'description': 'Oracle patches and updates', 'category': 'Maintenance', 'user': 'oracle', 'duration': '5 min'},
        {'number': '12', 'name': 'Multitenant', 'description': 'CDB/PDB management', 'category': 'Architecture', 'user': 'oracle', 'duration': '10 min'},
        {'number': '13', 'name': 'AI/ML Foundations', 'description': 'Oracle Machine Learning', 'category': 'Advanced', 'user': 'oracle', 'duration': '10 min'},
        {'number': '14', 'name': 'Data Mobility', 'description': 'Data Pump, transportable tablespaces', 'category': 'Advanced', 'user': 'oracle', 'duration': '10 min'},
        {'number': '15', 'name': 'ASM/RAC Concepts', 'description': 'Clustering and ASM architecture', 'category': 'Advanced', 'user': 'oracle', 'duration': '5 min'},
    ]
    
    # Check which scripts exist
    scripts_dir = Path(__file__).parent / 'scripts'
    for lab in labs_info:
        tp_map = {
            '01': 'tp01-system-readiness.sh', '02': 'tp02-installation-binaire.sh',
            '03': 'tp03-creation-instance.sh', '04': 'tp04-fichiers-critiques.sh',
            '05': 'tp05-gestion-stockage.sh', '06': 'tp06-securite-acces.sh',
            '07': 'tp07-flashback.sh', '08': 'tp08-rman.sh',
            '09': 'tp09-dataguard.sh', '10': 'tp10-tuning.sh',
            '11': 'tp11-patching.sh', '12': 'tp12-multitenant.sh',
            '13': 'tp13-ai-foundations.sh', '14': 'tp14-mobilite-concurrence.sh',
            '15': 'tp15-asm-rac-concepts.sh',
        }
        script_file = tp_map.get(lab['number'], '')
        lab['script'] = script_file
        lab['exists'] = (scripts_dir / script_file).exists() if script_file else False
        
        # Check if log exists
        log_file = f"/tmp/tp{lab['number']}.log"
        lab['has_log'] = os.path.exists(log_file)
    
    return jsonify({'success': True, 'labs': labs_info})


@app.route('/api/labs/run', methods=['POST'])
@login_required
@admin_required
def api_labs_run():
    """API: Run a TP lab script"""
    data = request.json or {}
    tp_number = data.get('tp_number', '')
    background = data.get('background', True)
    
    if not tp_number:
        return jsonify({'success': False, 'error': 'No TP number provided'})
    
    result = run_tp_script(tp_number, background=background)
    return jsonify(result)


@app.route('/api/labs/log/<tp_number>')
@login_required
def api_labs_log(tp_number):
    """API: Get TP lab log"""
    log_file = f'/tmp/tp{tp_number}.log'
    
    if not os.path.exists(log_file):
        return jsonify({'success': True, 'logs': f'No log yet for TP{tp_number}. Run the lab first.\n', 'size': 0, 'is_running': False})
    
    try:
        file_size = os.path.getsize(log_file)
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Check if script is still running
        is_running = False
        scripts_dir = Path(__file__).parent / 'scripts'
        try:
            proc = subprocess.run(['pgrep', '-f', f'tp{tp_number}'], capture_output=True)
            is_running = proc.returncode == 0
        except:
            pass
        
        return jsonify({'success': True, 'logs': content, 'size': file_size, 'is_running': is_running})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/labs/run-sequence', methods=['POST'])
@login_required
@admin_required
def api_labs_run_sequence():
    """API: Run a sequence of TP labs (e.g., 01-03 for full install)"""
    data = request.json or {}
    start_tp = data.get('start', '01')
    end_tp = data.get('end', '03')
    
    all_tps = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']
    
    try:
        start_idx = all_tps.index(start_tp)
        end_idx = all_tps.index(end_tp) + 1
        tps_to_run = all_tps[start_idx:end_idx]
    except ValueError:
        return jsonify({'success': False, 'error': f'Invalid range: {start_tp} to {end_tp}'})
    
    # Create a master script that runs all TPs in sequence
    scripts_dir = Path(__file__).parent / 'scripts'
    log_file = f'/tmp/tp-sequence-{start_tp}-{end_tp}.log'
    
    tp_map = {
        '01': 'tp01-system-readiness.sh', '02': 'tp02-installation-binaire.sh',
        '03': 'tp03-creation-instance.sh', '04': 'tp04-fichiers-critiques.sh',
        '05': 'tp05-gestion-stockage.sh', '06': 'tp06-securite-acces.sh',
        '07': 'tp07-flashback.sh', '08': 'tp08-rman.sh',
        '09': 'tp09-dataguard.sh', '10': 'tp10-tuning.sh',
        '11': 'tp11-patching.sh', '12': 'tp12-multitenant.sh',
        '13': 'tp13-ai-foundations.sh', '14': 'tp14-mobilite-concurrence.sh',
        '15': 'tp15-asm-rac-concepts.sh',
    }
    
    script_lines = ['#!/bin/bash', 'set -e', f'echo "=== Running TPs {start_tp} to {end_tp} ==="', f'echo "Started: $(date)"', '']
    
    for tp in tps_to_run:
        script_name = tp_map.get(tp, '')
        script_path = scripts_dir / script_name
        if script_path.exists():
            script_lines.append(f'echo ""')
            script_lines.append(f'echo "============================================="')
            script_lines.append(f'echo "=== TP{tp}: {script_name} ==="')
            script_lines.append(f'echo "============================================="')
            script_lines.append(f'bash {script_path}')
            script_lines.append(f'echo "=== TP{tp} completed ==="')
    
    script_lines.append('')
    script_lines.append('echo ""')
    script_lines.append(f'echo "=== All TPs {start_tp} to {end_tp} completed ==="')
    script_lines.append(f'echo "Finished: $(date)"')
    
    master_script = '/tmp/tp-sequence.sh'
    with open(master_script, 'w') as f:
        f.write('\n'.join(script_lines))
    
    os.chmod(master_script, 0o755)
    
    cmd = f'nohup bash {master_script} > {log_file} 2>&1 &'
    subprocess.Popen(cmd, shell=True)
    
    return jsonify({
        'success': True,
        'message': f'Running TPs {start_tp} to {end_tp} in sequence',
        'tps': tps_to_run,
        'log_file': log_file
    })


@app.route('/api/labs/sequence-log')
@login_required
def api_labs_sequence_log():
    """API: Get the sequence run log"""
    # Find the most recent sequence log
    import glob
    log_files = glob.glob('/tmp/tp-sequence-*.log')
    
    if not log_files:
        return jsonify({'success': True, 'logs': 'No sequence log found.\n', 'size': 0, 'is_running': False})
    
    log_file = max(log_files, key=os.path.getmtime)
    
    try:
        file_size = os.path.getsize(log_file)
        with open(log_file, 'r') as f:
            content = f.read()
        
        is_running = False
        try:
            proc = subprocess.run(['pgrep', '-f', 'tp-sequence.sh'], capture_output=True)
            is_running = proc.returncode == 0
        except:
            pass
        
        return jsonify({'success': True, 'logs': content, 'size': file_size, 'is_running': is_running})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# MISSING STORAGE API ROUTES (referenced by storage.html)
# ============================================================================

@app.route('/api/storage/controlfile/multiplex', methods=['POST'])
@login_required
@admin_required
def api_storage_controlfile_multiplex():
    """API: Multiplex control files (runs TP04)"""
    result = run_tp_script('04', background=True)
    return jsonify(result)


@app.route('/api/storage/controlfile/list')
@login_required
def api_storage_controlfile_list():
    """API: List control files as structured JSON"""
    sql = """COL \"NAME\" FORMAT A100
SELECT name AS \"NAME\", NVL(status, 'OK') AS \"STATUS\" FROM v$controlfile;"""
    output = run_sqlplus(sql)
    rows = parse_sql_rows(output)
    controlfiles = [{'name': r.get('NAME', ''), 'status': r.get('STATUS', '')} for r in rows]
    return jsonify({'success': True, 'controlfiles': controlfiles})


@app.route('/api/storage/redolog/multiplex', methods=['POST'])
@login_required
@admin_required
def api_storage_redolog_multiplex():
    """API: Multiplex redo logs (runs TP04)"""
    result = run_tp_script('04', background=True)
    return jsonify(result)


@app.route('/api/storage/redolog/list')
@login_required
def api_storage_redolog_list():
    """API: List redo log files with group info as structured JSON"""
    sql = """COL "MEMBER" FORMAT A100
SELECT f.group# AS "GROUP#", f.member AS "MEMBER", f.type AS "TYPE",
       l.status AS "STATUS", ROUND(l.bytes/1024/1024) AS "SIZE_MB", l.members AS "MEMBERS"
FROM v$logfile f JOIN v$log l ON f.group# = l.group#
ORDER BY f.group#, f.member;"""
    output = run_sqlplus(sql)
    rows = parse_sql_rows(output)
    redologs = []
    for r in rows:
        redologs.append({
            'group': r.get('GROUP#', ''), 'member': r.get('MEMBER', ''),
            'type': r.get('TYPE', ''), 'status': r.get('STATUS', ''),
            'size_mb': r.get('SIZE_MB', ''), 'members': r.get('MEMBERS', '')
        })
    return jsonify({'success': True, 'redologs': redologs})


@app.route('/api/storage/redolog/add', methods=['POST'])
@login_required
@admin_required
def api_storage_redolog_add():
    """API: Add a new redo log group"""
    data = request.json or {}
    size = data.get('size', '200M')
    result = run_sqlplus(f"ALTER DATABASE ADD LOGFILE SIZE {size};")
    return jsonify({'success': True, 'output': result})


@app.route('/api/storage/tablespace/<name>/drop', methods=['POST'])
@login_required
@admin_required
def api_storage_tablespace_drop(name):
    """API: Drop tablespace"""
    result = run_sqlplus(f"DROP TABLESPACE {name.upper()} INCLUDING CONTENTS AND DATAFILES;")
    return jsonify({'success': True, 'output': result})


# ============================================================================
# MISSING PROTECTION API ROUTES (referenced by protection.html)
# ============================================================================

@app.route('/api/protection/fra/status')
@login_required
def api_protection_fra_status():
    """API: FRA (Fast Recovery Area) status as structured JSON"""
    output = run_sqlplus("COL \"NAME\" FORMAT A80\nSELECT name AS \"NAME\", ROUND(space_limit/1024/1024) AS \"SIZE_MB\", ROUND(space_used/1024/1024) AS \"USED_MB\" FROM v$recovery_file_dest;")
    rows = parse_sql_rows(output)
    if rows:
        try:
            return jsonify({'success': True, 'configured': True, 'name': rows[0].get('NAME', ''),
                            'size_mb': float(rows[0].get('SIZE_MB', 0)), 'used_mb': float(rows[0].get('USED_MB', 0))})
        except (ValueError, TypeError):
            return jsonify({'success': True, 'configured': True, 'name': rows[0].get('NAME', ''), 'size_mb': 0, 'used_mb': 0})
    return jsonify({'success': True, 'configured': False, 'name': '', 'size_mb': 0, 'used_mb': 0})


@app.route('/api/protection/fra/enable', methods=['POST'])
@login_required
@admin_required
def api_protection_fra_enable():
    """API: Enable FRA"""
    sql = """
ALTER SYSTEM SET db_recovery_file_dest_size = 10G SCOPE=BOTH;
ALTER SYSTEM SET db_recovery_file_dest = '/u01/app/oracle/fast_recovery_area' SCOPE=BOTH;
"""
    output = run_sqlplus(sql)
    return jsonify({'success': True, 'output': output})


@app.route('/api/protection/flashback/status')
@login_required
def api_protection_flashback_status():
    """API: Flashback Database status as structured JSON"""
    output = run_sqlplus("SELECT flashback_on AS \"FLASHBACK_ON\", log_mode AS \"LOG_MODE\" FROM v$database;")
    rows = parse_sql_rows(output)
    flashback_on = rows[0].get('FLASHBACK_ON', 'NO') if rows else 'NO'
    log_mode = rows[0].get('LOG_MODE', 'UNKNOWN') if rows else 'UNKNOWN'
    return jsonify({'success': True, 'flashback_on': flashback_on, 'log_mode': log_mode})


@app.route('/api/protection/flashback/enable', methods=['POST'])
@login_required
@admin_required
def api_protection_flashback_enable():
    """API: Enable Flashback Database"""
    sql = """
ALTER DATABASE FLASHBACK ON;
"""
    output = run_sqlplus(sql)
    return jsonify({'success': True, 'output': output})


@app.route('/api/rman/configure', methods=['POST'])
@login_required
@admin_required
def api_rman_configure():
    """API: Configure RMAN"""
    data = request.json or {}
    retention = data.get('retention', 7)
    
    oracle_home = os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
    rman_cmds = f"""
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF {retention} DAYS;
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE DEVICE TYPE DISK PARALLELISM 2;
CONFIGURE BACKUP OPTIMIZATION ON;
"""
    
    cmd = f'source ~/.bash_profile 2>/dev/null; echo "{rman_cmds}" | {oracle_home}/bin/rman target /'
    output = run_shell_command(cmd, as_oracle=True)
    return jsonify({'success': True, 'output': output})


@app.route('/api/flashback/database', methods=['POST'])
@login_required
@admin_required
def api_flashback_database():
    """API: Flashback Database"""
    data = request.json or {}
    scn = data.get('scn', '')
    timestamp = data.get('timestamp', '')
    
    if timestamp:
        sql = f"FLASHBACK DATABASE TO TIMESTAMP TO_TIMESTAMP('{timestamp}', 'YYYY-MM-DD HH24:MI:SS');"
    elif scn:
        sql = f"FLASHBACK DATABASE TO SCN {scn};"
    else:
        return jsonify({'success': False, 'error': 'Provide SCN or timestamp'})
    
    output = run_sqlplus(sql)
    return jsonify({'success': True, 'output': output})


@app.route('/api/flashback/table', methods=['POST'])
@login_required
@admin_required
def api_flashback_table():
    """API: Flashback Table"""
    data = request.json or {}
    table_name = data.get('table', '')
    timestamp = data.get('timestamp', '')
    
    if not table_name or not timestamp:
        return jsonify({'success': False, 'error': 'Provide table name and timestamp'})
    
    sql = f"""
ALTER TABLE {table_name} ENABLE ROW MOVEMENT;
FLASHBACK TABLE {table_name} TO TIMESTAMP TO_TIMESTAMP('{timestamp}', 'YYYY-MM-DD HH24:MI:SS');
"""
    output = run_sqlplus(sql)
    return jsonify({'success': True, 'output': output})


# ============================================================================
# MISSING SECURITY API ROUTES (referenced by security.html)
# ============================================================================

@app.route('/api/security/grant', methods=['POST'])
@login_required
@admin_required
def api_security_grant():
    """API: Grant privileges"""
    data = request.json or {}
    username = data.get('username', '')
    privilege = data.get('privilege', '')
    
    if not username or not privilege:
        return jsonify({'success': False, 'error': 'Provide username and privilege'})
    
    output = run_sqlplus(f"GRANT {privilege} TO {username};")
    return jsonify({'success': True, 'output': output})


@app.route('/api/security/profile/create', methods=['POST'])
@login_required
@admin_required
def api_security_profile_create():
    """API: Create password profile"""
    data = request.json or {}
    name = data.get('name', '')
    
    if not name:
        return jsonify({'success': False, 'error': 'Provide profile name'})
    
    sql = f"""
CREATE PROFILE {name} LIMIT
    SESSIONS_PER_USER 5
    FAILED_LOGIN_ATTEMPTS 3
    PASSWORD_LOCK_TIME 1/24
    PASSWORD_LIFE_TIME 90
    PASSWORD_GRACE_TIME 7
    PASSWORD_REUSE_TIME 365
    PASSWORD_REUSE_MAX 12;
"""
    output = run_sqlplus(sql)
    return jsonify({'success': True, 'output': output})


@app.route('/api/security/audit/configure', methods=['POST'])
@login_required
@admin_required
def api_security_audit_configure():
    """API: Configure auditing"""
    data = request.json or {}
    action = data.get('action', 'enable')
    
    if action == 'enable':
        sql = """
ALTER SYSTEM SET audit_trail = DB,EXTENDED SCOPE=SPFILE;
AUDIT CREATE SESSION;
AUDIT ALTER SYSTEM;
AUDIT CREATE USER;
AUDIT DROP USER;
AUDIT ALTER USER;
AUDIT GRANT;
AUDIT REVOKE;
"""
    else:
        sql = "NOAUDIT ALL;"
    
    output = run_sqlplus(sql)
    return jsonify({'success': True, 'output': output})


@app.route('/api/security/audit/view')
@login_required
def api_security_audit_view():
    """API: View audit records as structured JSON"""
    sql = """SELECT username AS "USERNAME", action_name AS "ACTION_NAME",
       TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS "TIMESTAMP",
       returncode AS "RETURNCODE"
FROM dba_audit_trail WHERE timestamp > SYSDATE - 7
ORDER BY timestamp DESC FETCH FIRST 50 ROWS ONLY;"""
    output = run_sqlplus(sql)
    rows = parse_sql_rows(output)
    records = []
    for row in rows:
        records.append({
            'username': row.get('USERNAME', ''),
            'action_name': row.get('ACTION_NAME', ''),
            'timestamp': row.get('TIMESTAMP', ''),
            'returncode': row.get('RETURNCODE', '')
        })
    return jsonify({'success': True, 'records': records})


# ============================================================================
# MISSING CLUSTER API ROUTES (referenced by cluster.html)
# ============================================================================

@app.route('/api/cluster/nfs/configure', methods=['POST'])
@login_required
@admin_required
def api_cluster_nfs_configure():
    """API: Configure NFS"""
    data = request.json or {}
    server_ip = data.get('server_ip', '')
    export_path = data.get('export_path', '/shared/oracle')
    mount_point = data.get('mount_point', '/mnt/oracle_shared')
    
    script = f"""#!/bin/bash
set -e
echo "=== NFS Configuration ==="

# Install NFS
dnf install -y nfs-utils 2>/dev/null || yum install -y nfs-utils

# Create export directory
mkdir -p {export_path}
chown oracle:oinstall {export_path}

# Configure exports
echo "{export_path} *(rw,sync,no_root_squash,no_subtree_check)" >> /etc/exports

# Start NFS
systemctl enable --now nfs-server
exportfs -ra

echo "NFS server configured: {export_path}"
echo "Clients can mount with: mount {server_ip}:{export_path} {mount_point}"
"""
    
    script_path = '/tmp/nfs-setup.sh'
    with open(script_path, 'w') as f:
        f.write(script)
    os.chmod(script_path, 0o755)
    
    log_file = '/tmp/nfs-setup.log'
    cmd = f'nohup bash {script_path} > {log_file} 2>&1 &'
    subprocess.Popen(cmd, shell=True)
    
    return jsonify({'success': True, 'message': 'NFS configuration started', 'log_file': log_file})


@app.route('/api/cluster/nfs/test')
@login_required
def api_cluster_nfs_test():
    """API: Test NFS status"""
    output = run_shell_command('exportfs -v 2>/dev/null; echo "---"; showmount -e localhost 2>/dev/null || echo "NFS not configured"', as_oracle=False)
    return jsonify({'success': True, 'output': output})


@app.route('/api/cluster/grid/install', methods=['POST'])
@login_required
@admin_required
def api_cluster_grid_install():
    """API: Install Grid Infrastructure"""
    result = run_tp_script('15', background=True)
    return jsonify(result)


@app.route('/api/cluster/grid/status')
@login_required
def api_cluster_grid_status():
    """API: Grid Infrastructure status"""
    output = run_shell_command('crsctl stat res -t 2>/dev/null || echo "Grid Infrastructure not installed"', as_oracle=False)
    return jsonify({'success': True, 'output': output})


@app.route('/api/cluster/asm/configure', methods=['POST'])
@login_required
@admin_required
def api_cluster_asm_configure():
    """API: Configure ASM"""
    result = run_tp_script('15', background=True)
    return jsonify(result)


@app.route('/api/cluster/asm/status')
@login_required
def api_cluster_asm_status():
    """API: ASM status"""
    output = run_shell_command('asmcmd lsdg 2>/dev/null || echo "ASM not configured"', as_oracle=True)
    return jsonify({'success': True, 'output': output})


@app.route('/api/cluster/start', methods=['POST'])
@login_required
@admin_required
def api_cluster_start():
    """API: Start cluster services"""
    output = run_shell_command('crsctl start has 2>/dev/null || echo "Grid not installed"', as_oracle=False)
    return jsonify({'success': True, 'output': output})


@app.route('/api/cluster/stop', methods=['POST'])
@login_required
@admin_required
def api_cluster_stop():
    """API: Stop cluster services"""
    output = run_shell_command('crsctl stop has 2>/dev/null || echo "Grid not installed"', as_oracle=False)
    return jsonify({'success': True, 'output': output})


@app.route('/api/cluster/ssh/setup', methods=['POST'])
@login_required
@admin_required
def api_cluster_ssh_setup():
    """API: Setup SSH equivalence"""
    data = request.json or {}
    target_hosts = data.get('hosts', [])
    
    if not target_hosts:
        return jsonify({'success': False, 'error': 'No target hosts provided'})
    
    script = f"""#!/bin/bash
echo "=== SSH Equivalence Setup ==="

# Generate SSH key if not exists
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q
    echo "SSH key generated"
fi

# Copy key to target hosts
for HOST in {' '.join(target_hosts)}; do
    echo "Setting up SSH to $HOST..."
    ssh-copy-id -o StrictHostKeyChecking=no oracle@$HOST 2>/dev/null || echo "Could not connect to $HOST"
done

echo "=== SSH Setup Complete ==="
"""
    
    script_path = '/tmp/ssh-setup.sh'
    with open(script_path, 'w') as f:
        f.write(script)
    os.chmod(script_path, 0o755)
    
    output = run_shell_command(f'bash {script_path}', as_oracle=True)
    return jsonify({'success': True, 'output': output})


@app.route('/api/cluster/ssh/test')
@login_required
def api_cluster_ssh_test():
    """API: Test SSH connectivity"""
    output = run_shell_command('cat ~/.ssh/authorized_keys 2>/dev/null | wc -l; echo " authorized keys"; ssh -o BatchMode=yes localhost echo "SSH to localhost: OK" 2>/dev/null || echo "SSH to localhost: FAILED"', as_oracle=True)
    return jsonify({'success': True, 'output': output})


@app.route('/api/cluster/ssh/distribute', methods=['POST'])
@login_required
@admin_required
def api_cluster_ssh_distribute():
    """API: Distribute SSH keys"""
    data = request.json or {}
    hosts = data.get('hosts', [])
    
    output = ''
    for host in hosts:
        result = run_shell_command(f'ssh-copy-id -o StrictHostKeyChecking=no oracle@{host} 2>&1 || echo "Failed for {host}"', as_oracle=True)
        output += f"Host {host}: {result}\n"
    
    return jsonify({'success': True, 'output': output})


# ============================================================================
# MISSING SAMPLE DB API ROUTES (referenced by sample.html)
# ============================================================================

@app.route('/api/sample/status')
@login_required
def api_sample_status():
    """API: Check sample database status"""
    output = run_sqlplus("SELECT table_name, num_rows FROM all_tables WHERE owner = 'HR' ORDER BY table_name;")
    return jsonify({'success': True, 'output': output})


@app.route('/api/sample/remove', methods=['POST'])
@login_required
@admin_required
def api_sample_remove():
    """API: Remove sample database objects"""
    sql = """
DROP USER hr CASCADE;
"""
    output = run_sqlplus(sql)
    return jsonify({'success': True, 'output': output})


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
