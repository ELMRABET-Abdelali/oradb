"""
Oracle Installation Manager
Single-command Oracle 19c installation with real-time terminal output.

Usage (CLI):
    oradba install              # Full install with live output
    oradba install --yes        # Skip confirmation
    oradba install system       # Just system prep (TP01)
    oradba install binaries     # Just download+extract (TP02)
    oradba install software     # Just runInstaller
    oradba install database     # Just DBCA

Usage (Python):
    from oracledba.modules.install import InstallManager
    mgr = InstallManager()
    mgr.install_all(auto_yes=True)
"""

import os
import sys
import subprocess
import yaml
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


class InstallManager:
    def __init__(self, config_file=None):
        self.config = self._load_config(config_file)
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
        self._log_handle = None
        try:
            self.log_dir = Path("/var/log/oracledba")
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            self.log_dir = Path("/tmp/oracledba-logs")
            self.log_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_file):
        """Load configuration from YAML file"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return self._default_config()

    def _default_config(self):
        """Return default configuration"""
        return {
            'oracle': {
                'oracle_base': '/u01/app/oracle',
                'oracle_home': '/u01/app/oracle/product/19.3.0/dbhome_1',
                'oracle_sid': 'GDCPROD',
            },
            'database': {
                'db_name': 'GDCPROD',
                'sid': 'GDCPROD',
                'pdb_name': 'GDCPDB',
                'sys_password': 'Oracle123',
            },
            'google_drive': {
                'file_id': '1Mi7B2HneMBIyxJ01tnA-ThQ9hr2CAsns'
            }
        }

    # =========================================================================
    # OUTPUT — everything goes to stdout + log file simultaneously
    # =========================================================================

    def _out(self, text, end='\n'):
        """Write text to stdout and log file"""
        sys.stdout.write(text + end)
        sys.stdout.flush()
        if self._log_handle:
            self._log_handle.write(text + end)
            self._log_handle.flush()

    def _step_header(self, step_num, total, title):
        """Print a visible step header"""
        self._out("")
        self._out("\u2501" * 60)
        self._out(f"  Step {step_num}/{total} \u2500 {title}")
        self._out("\u2501" * 60)
        self._out("")

    def _step_result(self, step_num, success, elapsed_seconds):
        """Print step result with timing"""
        mins = int(elapsed_seconds // 60)
        secs = int(elapsed_seconds % 60)
        if success:
            self._out(f"\n\u2713 Step {step_num} complete ({mins}m {secs}s)")
        else:
            self._out(f"\n\u2717 Step {step_num} FAILED ({mins}m {secs}s)")

    def _open_log(self, name):
        """Open a log file for writing"""
        log_file = self.log_dir / f"{name}.log"
        self._log_handle = open(log_file, 'w')
        return log_file

    def _close_log(self):
        """Close the log file"""
        if self._log_handle:
            self._log_handle.close()
            self._log_handle = None

    # =========================================================================
    # PROCESS EXECUTION — always streams output live
    # =========================================================================

    def _build_env(self, extra_vars=None):
        """Build environment with Oracle-specific vars"""
        env = os.environ.copy()
        env['CV_ASSUME_DISTID'] = 'OEL7.8'
        if extra_vars:
            env.update(extra_vars)
        return env

    def _get_euid(self):
        """Get effective user ID (safe for Windows)"""
        try:
            return os.geteuid()
        except AttributeError:
            return -1

    def _build_cmd(self, command_str, as_user='root'):
        """Build command array. Wraps in su - oracle if needed."""
        euid = self._get_euid()
        if as_user == 'oracle' and euid == 0:
            return ['su', '-', 'oracle', '-c',
                    f'source ~/.bash_profile 2>/dev/null && {command_str}']
        else:
            return ['bash', '-c', command_str]

    def _stream_cmd(self, cmd, env=None):
        """Execute command, stream every line to _out(). Returns exit code."""
        if env is None:
            env = self._build_env()
        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                env=env, text=True, bufsize=1
            )
            for line in process.stdout:
                self._out(line, end='')
            process.wait()
            return process.returncode
        except Exception as e:
            self._out(f"Error running command: {e}")
            return 1

    def _stream_cmd_capture(self, cmd, env=None):
        """Like _stream_cmd but also returns full output for post-checking."""
        if env is None:
            env = self._build_env()
        output_lines = []
        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                env=env, text=True, bufsize=1
            )
            for line in process.stdout:
                self._out(line, end='')
                output_lines.append(line)
            process.wait()
            return process.returncode, ''.join(output_lines)
        except Exception as e:
            self._out(f"Error running command: {e}")
            return 1, str(e)

    def _run_script(self, script_name, as_user='root', env_vars=None, show_output=True):
        """Execute a bash script with live output streaming.

        show_output is kept for backward compat but output always streams now.
        """
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            self._out(f"\u2717 Error: Script {script_name} not found at {script_path}")
            return False

        env = self._build_env(env_vars)
        cmd = self._build_cmd(f'bash {script_path}', as_user)

        log_file = self.log_dir / f"{script_name}.log"
        self._out(f"  Script: {script_name}")
        self._out(f"  Log:    {log_file}")
        self._out("")

        returncode = self._stream_cmd(cmd, env)

        if returncode == 0:
            self._out(f"\n\u2713 {script_name} completed successfully")
            return True
        else:
            self._out(f"\n\u2717 {script_name} failed (exit code: {returncode})")
            return False

    # =========================================================================
    # BOOTSTRAP — ensure runtime dependencies are available
    # =========================================================================

    def _bootstrap(self):
        """Self-heal: upgrade pip and ensure critical tools are installed.

        This runs BEFORE any installation step so that gdown, flask, etc.
        are guaranteed to work regardless of the system's initial state.
        """
        self._out("Bootstrapping environment...\n")

        # 1. Upgrade pip / setuptools / wheel (old distro pip can't install modern packages)
        py = sys.executable or 'python3'
        upgrade_cmd = f'{py} -m pip install --upgrade pip setuptools wheel 2>/dev/null || true'
        self._out("  Upgrading pip, setuptools, wheel...")
        self._stream_cmd(['bash', '-c', upgrade_cmd])

        # 2. Ensure gdown is available (needed for Google Drive download in step 2)
        try:
            import gdown  # noqa: F401
            self._out("  \u2713 gdown available")
        except ImportError:
            self._out("  Installing gdown (Google Drive downloader)...")
            self._stream_cmd(['bash', '-c', f'{py} -m pip install gdown 2>/dev/null || pip3 install gdown || true'])

        # 3. Ensure flask is available (needed for GUI)
        try:
            import flask  # noqa: F401
            self._out("  \u2713 flask available")
        except ImportError:
            self._out("  Installing flask (needed for GUI)...")
            self._stream_cmd(['bash', '-c', f'{py} -m pip install flask flask-cors 2>/dev/null || true'])

        # 4. Ensure gdown is on PATH for oracle user too
        gdown_paths = [
            os.path.expanduser('~/.local/bin/gdown'),
            '/usr/local/bin/gdown',
            '/usr/bin/gdown',
        ]
        gdown_found = any(os.path.exists(p) for p in gdown_paths)
        if not gdown_found:
            # Install for oracle user as well (tp02 runs as oracle)
            self._out("  Installing gdown for oracle user...")
            self._stream_cmd(['bash', '-c',
                'su - oracle -c "pip3 install --user gdown 2>/dev/null || '
                'python3 -m pip install --user gdown 2>/dev/null || true"'])

        self._out("\n\u2713 Bootstrap complete\n")

    # =========================================================================
    # INSTALLATION STEPS — each one does ONE thing with full live output
    # =========================================================================

    def _step_system(self):
        """Step 1: System readiness — users, groups, kernel, packages (TP01)"""
        return self._run_script('tp01-system-readiness.sh', 'root')

    def _step_binaries(self):
        """Step 2: Download and extract Oracle binaries (TP02)"""
        return self._run_script('tp02-installation-binaire.sh', 'oracle')

    def _step_software(self):
        """Step 3: Install Oracle software with runInstaller + root scripts"""
        oracle_home = self.config['oracle']['oracle_home']
        oracle_base = self.config['oracle']['oracle_base']

        # --- Create response file ---
        self._out("Creating response file for silent install...")
        response_file = "/tmp/db_install.rsp"
        response_content = (
            "oracle.install.responseFileVersion="
            "/oracle/install/rspfmt_dbinstall_response_schema_v19.0.0\n"
            "oracle.install.option=INSTALL_DB_SWONLY\n"
            "UNIX_GROUP_NAME=oinstall\n"
            "INVENTORY_LOCATION=/u01/app/oraInventory\n"
            f"ORACLE_HOME={oracle_home}\n"
            f"ORACLE_BASE={oracle_base}\n"
            "oracle.install.db.InstallEdition=EE\n"
            "oracle.install.db.OSDBA_GROUP=dba\n"
            "oracle.install.db.OSOPER_GROUP=oper\n"
            "oracle.install.db.OSBACKUPDBA_GROUP=backupdba\n"
            "oracle.install.db.OSDGDBA_GROUP=dgdba\n"
            "oracle.install.db.OSKMDBA_GROUP=kmdba\n"
            "oracle.install.db.OSRACDBA_GROUP=racdba\n"
            "SECURITY_UPDATES_VIA_MYORACLESUPPORT=false\n"
            "DECLINE_SECURITY_UPDATES=true\n"
        )
        with open(response_file, 'w') as f:
            f.write(response_content)
        self._out(f"\u2713 Response file: {response_file}\n")

        # --- Run installer ---
        self._out("Running Oracle runInstaller (this takes ~10 minutes)...")
        self._out(f"  ORACLE_HOME: {oracle_home}\n")

        install_cmd = (
            f'export CV_ASSUME_DISTID=OEL7.8 && '
            f'cd {oracle_home} && '
            f'./runInstaller -silent '
            f'-responseFile {response_file} '
            f'-waitforcompletion -ignorePrereq'
        )
        cmd = self._build_cmd(install_cmd, 'oracle')
        returncode, output = self._stream_cmd_capture(cmd)

        # runInstaller returns 6 for "Successfully Setup Software with warnings"
        if "Successfully Setup Software" in output or returncode in (0, 6):
            self._out("\n\u2713 Oracle software installed successfully")
        else:
            self._out(f"\n\u2717 Oracle software installation failed (exit code: {returncode})")
            return False

        # --- Run root scripts ---
        self._out("\nRunning root configuration scripts...\n")

        orainstRoot = '/u01/app/oraInventory/orainstRoot.sh'
        root_sh = f'{oracle_home}/root.sh'

        if os.path.exists(orainstRoot):
            self._out(f"\u2192 {orainstRoot}")
            rc = self._stream_cmd(['bash', orainstRoot])
            if rc == 0:
                self._out("\u2713 orainstRoot.sh completed")
            else:
                self._out(f"\u26a0 orainstRoot.sh returned {rc} (continuing)")
        else:
            self._out(f"\u26a0 {orainstRoot} not found, skipping")

        if os.path.exists(root_sh):
            self._out(f"\n\u2192 {root_sh}")
            rc = self._stream_cmd(['bash', root_sh])
            if rc == 0:
                self._out("\u2713 root.sh completed")
            else:
                self._out(f"\u26a0 root.sh returned {rc} (continuing)")
        else:
            self._out(f"\u26a0 {root_sh} not found, skipping")

        return True

    def _step_database(self):
        """Step 4: Create database — listener + DBCA"""
        db_config = self.config['database']
        oracle_home = self.config['oracle']['oracle_home']
        oracle_base = self.config['oracle']['oracle_base']

        # --- Write listener.ora from Python (we are root) ---
        self._out("Setting up Oracle Listener...\n")

        listener_dir = Path(f"{oracle_home}/network/admin")
        try:
            listener_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            pass

        listener_content = (
            "LISTENER =\n"
            "  (DESCRIPTION_LIST =\n"
            "    (DESCRIPTION =\n"
            "      (ADDRESS = (PROTOCOL = TCP)(HOST = 0.0.0.0)(PORT = 1521))\n"
            "      (ADDRESS = (PROTOCOL = IPC)(KEY = EXTPROC1521))\n"
            "    )\n"
            "  )\n\n"
            "SID_LIST_LISTENER =\n"
            "  (SID_LIST =\n"
            "    (SID_DESC =\n"
            f"      (GLOBAL_DBNAME = {db_config['db_name']})\n"
            f"      (ORACLE_HOME = {oracle_home})\n"
            f"      (SID_NAME = {db_config['sid']})\n"
            "    )\n"
            "  )\n\n"
            f"ADR_BASE_LISTENER = {oracle_base}\n"
        )

        listener_path = listener_dir / 'listener.ora'
        try:
            listener_path.write_text(listener_content)
            subprocess.run(['chown', '-R', 'oracle:oinstall', str(listener_dir)],
                           capture_output=True, check=False)
            self._out(f"\u2713 listener.ora written to {listener_path}")
        except (PermissionError, OSError) as e:
            self._out(f"\u26a0 Could not write listener.ora directly: {e}")
            self._out("  Trying via su - oracle...")
            lsn_cmd = (
                f"mkdir -p {oracle_home}/network/admin && "
                f"cat > {listener_path} << 'LSNEOF'\n{listener_content}LSNEOF"
            )
            self._stream_cmd(self._build_cmd(lsn_cmd, 'oracle'))

        # Start listener as oracle
        cmd = self._build_cmd('lsnrctl start', 'oracle')
        rc = self._stream_cmd(cmd)
        if rc == 0:
            self._out("\n\u2713 Listener started")
        else:
            self._out("\n\u26a0 Listener start had issues (may already be running), continuing...")

        # --- DBCA ---
        self._out(f"\nCreating database {db_config['db_name']} with DBCA...")
        self._out("This takes 10-15 minutes. Watch the progress below.\n")

        dbca_cmd = (
            f"export CV_ASSUME_DISTID=OEL7.8 && "
            f"dbca -silent -createDatabase "
            f"-templateName General_Purpose.dbc "
            f"-gdbName {db_config['db_name']} "
            f"-sid {db_config['sid']} "
            f"-createAsContainerDatabase true "
            f"-numberOfPDBs 1 "
            f"-pdbName {db_config['pdb_name']} "
            f"-sysPassword {db_config['sys_password']} "
            f"-systemPassword {db_config['sys_password']} "
            f"-pdbAdminPassword {db_config['sys_password']} "
            f"-datafileDestination {oracle_base}/oradata "
            f"-recoveryAreaDestination {oracle_base}/fast_recovery_area "
            f"-storageType FS "
            f"-characterSet AL32UTF8 "
            f"-nationalCharacterSet AL16UTF16 "
            f"-totalMemory 2048 "
            f"-emConfiguration NONE"
        )

        cmd = self._build_cmd(dbca_cmd, 'oracle')
        returncode, output = self._stream_cmd_capture(cmd)

        if returncode == 0 or "100% complete" in output.lower():
            self._out("\n\u2713 Database created successfully!")

            # Verify database
            self._out("\nVerifying database...\n")
            verify_cmd = (
                "sqlplus -s / as sysdba << 'EOF'\n"
                "SET PAGESIZE 0 FEEDBACK OFF\n"
                "SELECT 'DB: ' || name || ' - ' || open_mode FROM v$database;\n"
                "SELECT 'PDB: ' || name || ' - ' || open_mode FROM v$pdbs "
                "WHERE name != 'PDB$SEED';\n"
                "EXIT\nEOF"
            )
            cmd = self._build_cmd(verify_cmd, 'oracle')
            self._stream_cmd(cmd)

            # Add to /etc/oratab
            oratab_line = f"{db_config['sid']}:{oracle_home}:Y"
            try:
                existing = ''
                if os.path.exists('/etc/oratab'):
                    with open('/etc/oratab', 'r') as f:
                        existing = f.read()
                if db_config['sid'] not in existing:
                    with open('/etc/oratab', 'a') as f:
                        f.write(f"\n{oratab_line}\n")
                    self._out(f"\u2713 Added {db_config['sid']} to /etc/oratab")
            except Exception:
                self._out(f"\u26a0 Could not update /etc/oratab (add: {oratab_line})")

            return True
        else:
            self._out(f"\n\u2717 Database creation failed (exit code: {returncode})")
            return False

    # =========================================================================
    # MAIN INSTALL — single command, 4 steps, full live output
    # =========================================================================

    def install_all(self, skip_system=False, skip_binaries=False,
                    skip_db_creation=False, verbose=False, auto_yes=False,
                    run_all_tps=False):
        """Complete Oracle 19c installation - one command, live output.

        This is the main entry point for: oradba install
        When run_all_tps=True, also runs TP04-TP15 after the base install.
        """
        log_file = self._open_log("install-all")

        try:
            # Banner
            self._out("\u2554" + "\u2550" * 53 + "\u2557")
            self._out("\u2551   Oracle 19c \u2500 Complete Automated Installation     \u2551")
            self._out("\u2551   oradba install                                   \u2551")
            self._out("\u255a" + "\u2550" * 53 + "\u255d")
            self._out("")

            # Bootstrap — ensure pip, gdown, flask are ready
            self._bootstrap()

            # Build step list
            steps = []
            if not skip_system:
                steps.append(('System Readiness',
                              'Users, groups, kernel params, 50+ packages',
                              self._step_system))
            if not skip_binaries:
                steps.append(('Download & Extract Binaries',
                              'Download 3GB from Google Drive, extract to ORACLE_HOME',
                              self._step_binaries))
                steps.append(('Install Oracle Software',
                              'runInstaller (silent) + root scripts',
                              self._step_software))
            if not skip_db_creation:
                steps.append(('Create Database',
                              'Listener + DBCA \u2192 GDCPROD (CDB) + GDCPDB (PDB)',
                              self._step_database))

            # Show plan
            self._out(f"  {len(steps)} steps to execute:\n")
            for i, (title, desc, _) in enumerate(steps, 1):
                self._out(f"    {i}. {title}")
                self._out(f"       {desc}")
            self._out(f"\n  Log file: {log_file}")
            self._out("")

            # Confirmation
            if not auto_yes:
                self._out("Press Enter to start, Ctrl+C to cancel...")
                try:
                    input()
                except KeyboardInterrupt:
                    self._out("\n\u2717 Installation cancelled by user")
                    return False

            total_start = time.time()

            # Execute steps
            for i, (title, _desc, func) in enumerate(steps, 1):
                self._step_header(i, len(steps), title)
                step_start = time.time()

                success = func()

                elapsed = time.time() - step_start
                self._step_result(i, success, elapsed)

                if not success:
                    self._out(f"\n\u2717 Installation FAILED at step {i}: {title}")
                    self._out(f"  Check log: {log_file}")
                    return False

            # Success
            total_elapsed = time.time() - total_start
            total_mins = int(total_elapsed // 60)
            total_secs = int(total_elapsed % 60)

            db = self.config['database']
            self._out("")
            self._out("\u2550" * 60)
            self._out("  \u2713 Oracle 19c Installation Complete!")
            self._out(f"  Total Time: {total_mins}m {total_secs}s")
            self._out("\u2550" * 60)
            self._out("")
            self._out(f"  Database: {db['db_name']}")
            self._out(f"  SID:      {db['sid']}")
            self._out(f"  PDB:      {db['pdb_name']}")
            self._out(f"  Home:     {self.config['oracle']['oracle_home']}")
            self._out(f"  Listener: port 1521")
            self._out("")
            self._out("  Connect:")
            self._out("    sqlplus / as sysdba")
            self._out(f"    sqlplus sys/{db['sys_password']}@//localhost/{db['pdb_name']} as sysdba")
            self._out("")
            self._out(f"  Log: {log_file}")
            self._out("\u2550" * 60)

            # Run post-install TPs if --all flag was set
            if run_all_tps:
                self._out("")
                self._out("\u2550" * 60)
                self._out("  Running post-install configuration labs (TP04-TP15)...")
                self._out("\u2550" * 60)
                post_labs = ['04', '05', '06', '07', '08', '09',
                             '10', '11', '12', '13', '14', '15']
                failed = []
                for i, lab_num in enumerate(post_labs, 1):
                    self._step_header(i, len(post_labs),
                                      f"Post-Config Lab TP{lab_num}")
                    lab_start = time.time()
                    try:
                        success = self.run_lab(lab_num, show_output=True)
                    except Exception as exc:
                        self._out(f"  Lab TP{lab_num} error: {exc}")
                        success = False
                    elapsed = time.time() - lab_start
                    self._step_result(i, success, elapsed)
                    if not success:
                        failed.append(lab_num)
                self._out("")
                if failed:
                    self._out(f"  \u26a0 Labs with issues: {', '.join(failed)}")
                else:
                    self._out("  \u2713 All post-install labs completed!")
                grand_total = time.time() - total_start
                gm = int(grand_total // 60)
                gs = int(grand_total % 60)
                self._out(f"  Grand Total: {gm}m {gs}s")
                self._out("\u2550" * 60)

            return True

        finally:
            self._close_log()

    def install_full(self, skip_system=False, skip_binaries=False,
                     skip_db_creation=False):
        """Alias for install_all with verbose=True (backward compat)"""
        return self.install_all(skip_system, skip_binaries, skip_db_creation,
                                verbose=True, auto_yes=False)

    # =========================================================================
    # INDIVIDUAL INSTALL COMMANDS — for CLI subcommands
    # =========================================================================

    def install_system(self):
        """Install system prerequisites only (TP01)"""
        log_file = self._open_log("install-system")
        try:
            self._out("\u2550\u2550\u2550 Installing System Prerequisites \u2550\u2550\u2550\n")
            return self._step_system()
        finally:
            self._close_log()

    def install_binaries(self):
        """Download and extract Oracle binaries only (TP02)"""
        log_file = self._open_log("install-binaries")
        try:
            self._out("\u2550\u2550\u2550 Installing Oracle Binaries \u2550\u2550\u2550\n")
            success = self._step_binaries()
            if success:
                self._out("\nNext step: oradba install software")
            return success
        finally:
            self._close_log()

    def install_software(self):
        """Install Oracle software only (runInstaller + root scripts)"""
        log_file = self._open_log("install-software")
        try:
            self._out("\u2550\u2550\u2550 Installing Oracle Software \u2550\u2550\u2550\n")
            return self._step_software()
        finally:
            self._close_log()

    def create_database(self, db_name=None):
        """Create Oracle database only (Listener + DBCA)"""
        if db_name:
            self.config['database']['sid'] = db_name
            self.config['database']['db_name'] = db_name
        log_file = self._open_log("install-database")
        try:
            self._out("\u2550\u2550\u2550 Creating Oracle Database \u2550\u2550\u2550\n")
            return self._step_database()
        finally:
            self._close_log()

    # =========================================================================
    # LAB RUNNER — run TP04-TP15 configuration labs
    # =========================================================================

    def run_lab(self, lab_number, show_output=True):
        """Run a specific configuration lab script"""
        lab_map = {
            '01': ('tp01-system-readiness.sh', 'root', 'System Readiness'),
            '02': ('tp02-installation-binaire.sh', 'oracle', 'Binary Installation'),
            '03': ('tp03-creation-instance.sh', 'oracle', 'Instance Creation'),
            '04': ('tp04-fichiers-critiques.sh', 'oracle', 'Critical Files Multiplexing'),
            '05': ('tp05-gestion-stockage.sh', 'oracle', 'Storage Management'),
            '06': ('tp06-securite-acces.sh', 'oracle', 'Security and Access'),
            '07': ('tp07-flashback.sh', 'oracle', 'Flashback Technologies'),
            '08': ('tp08-rman.sh', 'oracle', 'RMAN Backup'),
            '09': ('tp09-dataguard.sh', 'oracle', 'Data Guard Setup'),
            '10': ('tp10-tuning.sh', 'oracle', 'Performance Tuning'),
            '11': ('tp11-patching.sh', 'oracle', 'Patching and Maintenance'),
            '12': ('tp12-multitenant.sh', 'oracle', 'Multitenant Architecture'),
            '13': ('tp13-ai-foundations.sh', 'oracle', 'AI/ML Foundations'),
            '14': ('tp14-mobilite-concurrence.sh', 'oracle', 'Data Mobility'),
            '15': ('tp15-asm-rac-concepts.sh', 'oracle', 'ASM and RAC Concepts'),
        }

        if lab_number not in lab_map:
            rprint(f"[red]Error:[/red] Lab {lab_number} not found")
            rprint(f"[yellow]Available labs:[/yellow] {', '.join(sorted(lab_map.keys()))}")
            return False

        script, user, description = lab_map[lab_number]
        rprint(f"\n[bold cyan]Running Lab {lab_number}: {description}[/bold cyan]\n")
        return self._run_script(script, user)

    def list_labs(self):
        """List all available configuration labs"""
        table = Table(title="Oracle DBA Configuration Labs",
                      show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Name", style="white")
        table.add_column("Description", style="dim")
        table.add_column("Category", style="yellow")

        labs = [
            ("01", "System Readiness", "User, groups, packages, kernel params", "Installation"),
            ("02", "Binary Installation", "Download and extract Oracle 19c", "Installation"),
            ("03", "Database Creation", "Create database with DBCA", "Installation"),
            ("04", "Critical Files", "Multiplex control files, redo logs", "Configuration"),
            ("05", "Storage Management", "Tablespaces, datafiles, OMF", "Configuration"),
            ("06", "Security", "Users, roles, profiles, privileges", "Security"),
            ("07", "Flashback", "Flashback query, table, database", "Protection"),
            ("08", "RMAN Backup", "Backup strategies and recovery", "Protection"),
            ("09", "Data Guard", "High availability with standby", "HA"),
            ("10", "Performance Tuning", "AWR, SQL tuning, optimization", "Performance"),
            ("11", "Patching", "Apply patches and updates", "Maintenance"),
            ("12", "Multitenant", "CDB/PDB management", "Architecture"),
            ("13", "AI/ML", "Oracle Machine Learning", "Advanced"),
            ("14", "Data Mobility", "Data Pump, transportable tablespaces", "Advanced"),
            ("15", "ASM/RAC", "Clustering and ASM concepts", "Advanced"),
        ]

        for lab_num, name, desc, category in labs:
            table.add_row(lab_num, name, desc, category)

        console.print(table)
        console.print("\n[cyan]Usage:[/cyan]")
        console.print("  oradba configure multiplexing    # Lab 04")
        console.print("  oradba configure storage         # Lab 05")
        console.print("  oradba configure backup          # Lab 08")
        console.print("  oradba maintenance tune          # Lab 10")
        console.print("  oradba advanced multitenant      # Lab 12")

    def run_all_labs(self, start_from='01', end_at='15'):
        """Run multiple labs sequentially"""
        console.print("\n[bold cyan]Running Oracle DBA Configuration Labs[/bold cyan]\n")

        all_labs = ['01', '02', '03', '04', '05', '06', '07',
                    '08', '09', '10', '11', '12', '13', '14', '15']

        try:
            start_idx = all_labs.index(start_from)
            end_idx = all_labs.index(end_at) + 1
            labs = all_labs[start_idx:end_idx]
            rprint(f"[yellow]Running labs {start_from} to {end_at}[/yellow]")
        except ValueError:
            rprint(f"[red]Invalid lab range: {start_from} to {end_at}[/red]")
            return False

        failed_labs = []
        for lab_num in labs:
            success = self.run_lab(lab_num)
            if not success:
                failed_labs.append(lab_num)
                rprint(f"\n[red]\u2717 Lab {lab_num} failed. Continue? (y/N)[/red]")
                response = input().strip().lower()
                if response != 'y':
                    break

        console.print("\n[bold cyan]\u2550\u2550\u2550 Configuration Summary \u2550\u2550\u2550[/bold cyan]")
        if failed_labs:
            rprint(f"[yellow]Failed labs:[/yellow] {', '.join(failed_labs)}")
        else:
            rprint("[green]\u2713 All labs completed successfully![/green]")

        return len(failed_labs) == 0

    def vm_init(self, role, node_number=None):
        """Initialize VM for Oracle"""
        console.print(f"\n[bold cyan]Initializing VM as {role}[/bold cyan]\n")
        if role == 'database':
            return self.install_system()
        elif role == 'rac-node':
            rprint(f"[cyan]Setting up RAC node {node_number}[/cyan]")
            return self._run_script("tp15-asm-rac-concepts.sh", "root")
        elif role == 'dataguard-standby':
            rprint("[cyan]Setting up Data Guard standby[/cyan]")
            return self._run_script("tp09-dataguard.sh", "oracle")
        return False
