"""
Oracle Installation Manager
Handles Oracle 19c installation and system setup
"""

import os
import subprocess
import yaml
import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()


class InstallManager:
    def __init__(self, config_file=None):
        self.config = self._load_config(config_file)
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
        self.log_dir = Path("/var/log/oracledba")
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
    
    def _run_script(self, script_name, as_user='root', show_output=False, env_vars=None):
        """Execute a bash script with enhanced logging"""
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            rprint(f"[red]Error:[/red] Script {script_name} not found at {script_path}")
            return False
        
        log_file = self.log_dir / f"{script_name}.log"
        
        try:
            # Prepare environment variables
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Always set CV_ASSUME_DISTID for Oracle compatibility
            env['CV_ASSUME_DISTID'] = 'OEL7.8'
            
            # Build command
            if as_user == 'oracle' and os.geteuid() == 0:
                cmd = ['su', '-', 'oracle', '-c', f'source ~/.bash_profile && bash {script_path}']
            elif as_user == 'root' or os.geteuid() != 0:
                cmd = ['bash', str(script_path)]
            else:
                cmd = ['su', '-', as_user, '-c', f'bash {script_path}']
            
            # Execute with real-time output if requested
            if show_output:
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    env=env,
                    text=True,
                    bufsize=1
                )
                
                with open(log_file, 'w') as log:
                    for line in process.stdout:
                        print(line, end='')
                        log.write(line)
                
                process.wait()
                returncode = process.returncode
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    env=env
                )
                returncode = result.returncode
                
                # Save output to log
                with open(log_file, 'w') as log:
                    log.write(result.stdout)
                    log.write(result.stderr)
            
            if returncode == 0:
                rprint(f"[green]✓[/green] {script_name} completed successfully")
                rprint(f"[dim]  Log: {log_file}[/dim]")
                return True
            else:
                rprint(f"[red]✗[/red] {script_name} failed (exit code: {returncode})")
                rprint(f"[yellow]  Check log:[/yellow] {log_file}")
                if not show_output:
                    rprint("\n[yellow]Last 20 lines of output:[/yellow]")
                    with open(log_file) as log:
                        lines = log.readlines()
                        for line in lines[-20:]:
                            print(line, end='')
                return False
        except Exception as e:
            rprint(f"[red]Error executing {script_name}:[/red] {str(e)}")
            return False
    
    def install_all(self, skip_system=False, skip_binaries=False, skip_db_creation=False, verbose=False):
        """Complete Oracle 19c installation - One button install"""
        console.print(Panel.fit(
            "[bold cyan]Oracle 19c Complete Installation[/bold cyan]\n"
            "This will install Oracle Database 19c on Rocky Linux 8\n"
            "Estimated time: 30-45 minutes",
            border_style="cyan"
        ))
        
        # Define installation steps
        steps = []
        
        if not skip_system:
            steps.append({
                'name': 'System Readiness',
                'script': 'tp01-system-readiness.sh',
                'user': 'root',
                'description': 'Configure system (users, groups, kernel params, packages)',
                'duration': '5-10 min'
            })
        
        if not skip_binaries:
            steps.append({
                'name': 'Binary Installation',
                'script': 'tp02-installation-binaire.sh',
                'user': 'oracle',
                'description': 'Download and extract Oracle 19c binaries (3GB)',
                'duration': '5-10 min'
            })
            
            steps.append({
                'name': 'Software Installation',
                'script': None,  # Will be handled separately
                'user': 'oracle',
                'description': 'Install Oracle software (runInstaller)',
                'duration': '10-15 min'
            })
        
        if not skip_db_creation:
            steps.append({
                'name': 'Database Creation',
                'script': None,  # Will be handled separately
                'user': 'oracle',
                'description': 'Create GDCPROD database with DBCA',
                'duration': '10-15 min'
            })
        
        # Show installation plan
        table = Table(title="Installation Plan", show_header=True, header_style="bold magenta")
        table.add_column("Step", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Duration", style="yellow")
        
        for i, step in enumerate(steps, 1):
            table.add_row(f"{i}. {step['name']}", step['description'], step['duration'])
        
        console.print(table)
        console.print("\n[yellow]Press Ctrl+C to cancel, or wait 5 seconds to continue...[/yellow]")
        
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            rprint("\n[red]Installation cancelled by user[/red]")
            return False
        
        # Execute installation steps
        for i, step in enumerate(steps, 1):
            console.print(f"\n[bold cyan]═══ Step {i}/{len(steps)}: {step['name']} ═══[/bold cyan]")
            
            if step['script']:
                # Standard script execution
                success = self._run_script(step['script'], step['user'], show_output=verbose)
                if not success:
                    rprint(f"\n[red]✗ Installation failed at: {step['name']}[/red]")
                    return False
            else:
                # Special handling for software install and DB creation
                if 'Software Installation' in step['name']:
                    success = self._install_oracle_software()
                elif 'Database Creation' in step['name']:
                    success = self._create_database_dbca()
                
                if not success:
                    rprint(f"\n[red]✗ Installation failed at: {step['name']}[/red]")
                    return False
        
        # Success message
        console.print(Panel.fit(
            "[bold green]✓ Oracle 19c Installation Completed Successfully![/bold green]\n\n"
            "Database Information:\n"
            f"  • Database Name: {self.config['database']['db_name']}\n"
            f"  • SID: {self.config['database']['sid']}\n"
            f"  • PDB Name: {self.config['database']['pdb_name']}\n"
            f"  • ORACLE_HOME: {self.config['oracle']['oracle_home']}\n\n"
            "Login with:\n"
            "  [cyan]sqlplus / as sysdba[/cyan]\n"
            "  [cyan]sqlplus sys/Oracle123@//localhost/GDCPDB as sysdba[/cyan]",
            border_style="green"
        ))
        
        return True
    
    def install_full(self, skip_system=False, skip_binaries=False, skip_db_creation=False):
        """Alias for install_all for backward compatibility"""
        return self.install_all(skip_system, skip_binaries, skip_db_creation, verbose=True)
    
    def _install_oracle_software(self):
        """Install Oracle software using runInstaller"""
        rprint("[cyan]Installing Oracle Database 19c software...[/cyan]")
        
        oracle_home = self.config['oracle']['oracle_home']
        
        # Create response file
        response_file = "/tmp/db_install.rsp"
        response_content = f"""oracle.install.responseFileVersion=/oracle/install/rspfmt_dbinstall_response_schema_v19.0.0
oracle.install.option=INSTALL_DB_SWONLY
UNIX_GROUP_NAME=oinstall
INVENTORY_LOCATION=/u01/app/oraInventory
ORACLE_HOME={oracle_home}
ORACLE_BASE={self.config['oracle']['oracle_base']}
oracle.install.db.InstallEdition=EE
oracle.install.db.OSDBA_GROUP=dba
oracle.install.db.OSOPER_GROUP=oper
oracle.install.db.OSBACKUPDBA_GROUP=backupdba
oracle.install.db.OSDGDBA_GROUP=dgdba
oracle.install.db.OSKMDBA_GROUP=kmdba
oracle.install.db.OSRACDBA_GROUP=racdba
SECURITY_UPDATES_VIA_MYORACLESUPPORT=false
DECLINE_SECURITY_UPDATES=true
"""
        
        with open(response_file, 'w') as f:
            f.write(response_content)
        
        rprint(f"[dim]Response file created: {response_file}[/dim]")
        
        # Run installer
        install_cmd = [
            'su', '-', 'oracle', '-c',
            f'export CV_ASSUME_DISTID=OEL7.8 && cd {oracle_home} && '
            f'./runInstaller -silent -responseFile {response_file} -waitforcompletion -ignorePrereq'
        ]
        
        try:
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            
            if "Successfully Setup Software" in result.stdout:
                rprint("[green]✓[/green] Oracle software installed successfully")
                
                # Run root scripts
                rprint("\n[yellow]Running root configuration scripts...[/yellow]")
                
                subprocess.run(['/u01/app/oraInventory/orainstRoot.sh'], check=True)
                rprint("[green]✓[/green] orainstRoot.sh completed")
                
                subprocess.run([f'{oracle_home}/root.sh'], check=True)
                rprint("[green]✓[/green] root.sh completed")
                
                return True
            else:
                rprint("[red]✗[/red] Oracle software installation failed")
                rprint(result.stdout)
                return False
                
        except Exception as e:
            rprint(f"[red]Error during software installation:[/red] {str(e)}")
            return False
    
    def _create_database_dbca(self):
        """Create database using DBCA"""
        rprint("[cyan]Creating Oracle database with DBCA...[/cyan]")
        rprint("[yellow]This may take 10-15 minutes. Please wait...[/yellow]")
        
        db_config = self.config['database']
        
        # Create listener first
        rprint("\n[cyan]1/2: Setting up Oracle Listener...[/cyan]")
        listener_config = f"""/u01/app/oracle/product/19.3.0/dbhome_1/network/admin/listener.ora"""
        
        listener_cmd = [
            'su', '-', 'oracle', '-c',
            f"""mkdir -p /u01/app/oracle/product/19.3.0/dbhome_1/network/admin && \
cat > /u01/app/oracle/product/19.3.0/dbhome_1/network/admin/listener.ora << 'EOF'
LISTENER =
  (DESCRIPTION_LIST =
    (DESCRIPTION =
      (ADDRESS = (PROTOCOL = TCP)(HOST = 0.0.0.0)(PORT = 1521))
      (ADDRESS = (PROTOCOL = IPC)(KEY = EXTPROC1521))
    )
  )

SID_LIST_LISTENER =
  (SID_LIST =
    (SID_DESC =
      (GLOBAL_DBNAME = {db_config['db_name']})
      (ORACLE_HOME = {self.config['oracle']['oracle_home']})
      (SID_NAME = {db_config['sid']})
    )
  )

ADR_BASE_LISTENER = {self.config['oracle']['oracle_base']}
EOF
lsnrctl start"""
        ]
        
        try:
            subprocess.run(listener_cmd, check=True, shell=True)
            rprint("[green]✓[/green] Listener started successfully")
        except:
            rprint("[yellow]⚠[/yellow] Listener start had issues, continuing...")
        
        # Create database with DBCA
        rprint("\n[cyan]2/2: Creating database with DBCA...[/cyan]")
        
        dbca_cmd = [
            'su', '-', 'oracle', '-c',
            f"""export CV_ASSUME_DISTID=OEL7.8 && \
dbca -silent -createDatabase \
  -gdbName {db_config['db_name']} \
  -sid {db_config['sid']} \
  -createAsContainerDatabase true \
  -numberOfPDBs 1 \
  -pdbName {db_config['pdb_name']} \
  -sysPassword {db_config['sys_password']} \
  -systemPassword {db_config['sys_password']} \
  -pdbAdminPassword {db_config['sys_password']} \
  -datafileDestination {self.config['oracle']['oracle_base']}/oradata \
  -recoveryAreaDestination {self.config['oracle']['oracle_base']}/fast_recovery_area \
  -storageType FS \
  -characterSet AL32UTF8 \
  -nationalCharacterSet AL16UTF16 \
  -memoryPercentage 40 \
  -emConfiguration NONE"""
        ]
        
        try:
            result = subprocess.run(dbca_cmd, capture_output=True, text=True, shell=True, timeout=1800)
            
            if result.returncode == 0 or "100% complete" in result.stdout:
                rprint("[green]✓[/green] Database created successfully!")
                
                # Verify database
                rprint("\n[cyan]Verifying database...[/cyan]")
                verify_cmd = [
                    'su', '-', 'oracle', '-c',
                    "sqlplus -s / as sysdba << 'EOF'\nSET PAGESIZE 0 FEEDBACK OFF\nSELECT 'DB: ' || name || ' - ' || open_mode FROM v\\$database;\nSELECT 'PDB: ' || name || ' - ' || open_mode FROM v\\$pdbs WHERE name != 'PDB\\$SEED';\nEXIT\nEOF"
                ]
                
                verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, shell=True)
                rprint(verify_result.stdout)
                
                return True
            else:
                rprint("[red]✗[/red] Database creation failed")
                rprint(result.stdout)
                rprint(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            rprint("[red]✗[/red] Database creation timed out (>30 min)")
            return False
        except Exception as e:
            rprint(f"[red]Error during database creation:[/red] {str(e)}")
            return False
    
    def install_system(self):
        """Install system prerequisites"""
        console.print("\n[bold cyan]Installing System Prerequisites[/bold cyan]\n")
        return self._run_script("tp01-system-readiness.sh", "root", show_output=True)
    
    def install_binaries(self):
        """Install Oracle binaries"""
        console.print("\n[bold cyan]Installing Oracle Binaries[/bold cyan]\n")
        success = self._run_script("tp02-installation-binaire.sh", "oracle", show_output=True)
        if success:
            rprint("\n[yellow]Now run root scripts:[/yellow]")
            rprint("  sudo /u01/app/oraInventory/orainstRoot.sh")
            rprint("  sudo $ORACLE_HOME/root.sh")
            rprint("\n[yellow]Then install software:[/yellow]")
            rprint("  oradba install software")
        return success
    
    def create_database(self, db_name=None):
        """Create Oracle database"""
        if db_name:
            self.config['database']['sid'] = db_name
            self.config['database']['db_name'] = db_name
        
        console.print("\n[bold cyan]Creating Oracle Database[/bold cyan]\n")
        return self._create_database_dbca()
    
    def run_lab(self, lab_number, show_output=False):
        """Run specific configuration lab script"""
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
        console.print(f"\n[bold cyan]Running Lab: {description}[/bold cyan]\n")
        return self._run_script(script, user, show_output=show_output)
    
    def list_labs(self):
        """List all available configuration labs"""
        table = Table(title="Oracle DBA Configuration Labs", show_header=True, header_style="bold magenta")
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
        console.print("\n[cyan]Usage with CLI commands:[/cyan]")
        console.print("  oradba configure multiplexing    # Run Lab 04")
        console.print("  oradba configure storage         # Run Lab 05")
        console.print("  oradba configure backup          # Run Lab 08")
        console.print("  oradba maintenance tune          # Run Lab 10")
        console.print("  oradba advanced multitenant      # Run Lab 12")
    
    def run_all_labs(self, start_from='01', end_at='15'):
        """Run multiple labs sequentially"""
        console.print("\n[bold cyan]Running Oracle DBA Configuration Labs[/bold cyan]\n")
        
        all_labs = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']
        
        # Filter labs by range
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
            success = self.run_lab(lab_num, show_output=False)
            if not success:
                failed_labs.append(lab_num)
                rprint(f"\n[red]✗ Lab {lab_num} failed. Continue? (y/N)[/red]")
                response = input().strip().lower()
                if response != 'y':
                    break
        
        # Summary
        console.print("\n[bold cyan]═══ Configuration Summary ═══[/bold cyan]")
        if failed_labs:
            rprint(f"[yellow]Failed labs:[/yellow] {', '.join(failed_labs)}")
        else:
            rprint("[green]✓ All labs completed successfully![/green]")
        
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
