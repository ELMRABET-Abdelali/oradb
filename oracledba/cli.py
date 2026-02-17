#!/usr/bin/env python3
"""
OracleDBA CLI - Main Command Line Interface
Complete Oracle Database Administration Tool
"""

import os
import sys
import subprocess
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

console = Console()

# Note: module imports are lazy (inside command functions) to avoid
# import errors when optional dependencies are not installed.
from .modules import flashback
from .modules import security
from .modules import nfs
from .modules import database
from .utils import logger

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version')
@click.pass_context
def main(ctx, version):
    """
    🗄️  OracleDBA - Complete Oracle Database Administration Tool
    
    Installation, backup, tuning, ASM, RAC, and more for Oracle 19c
    """
    if version:
        from . import __version__
        rprint(f"[bold green]OracleDBA[/bold green] version [cyan]{__version__}[/cyan]")
        return
    
    if ctx.invoked_subcommand is None:
        show_banner()
        rprint("\n[yellow]Use[/yellow] [cyan]oradba --help[/cyan] [yellow]for available commands[/yellow]\n")


def show_banner():
    """Display banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     🗄️   OracleDBA - Database Administration Tool    ║
    ║                                                       ║
    ║     Complete package for Oracle 19c on Rocky Linux   ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold blue"))


# ============================================================================
# INSTALLATION COMMANDS
# ============================================================================

@main.group(invoke_without_command=True)
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompts')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.pass_context
def install(ctx, yes, config):
    """📦 Install and configure Oracle Database

    Run without subcommand for complete one-shot installation:
      oradba install          # full install with live output
      oradba install --yes    # skip confirmation
    """
    ctx.ensure_object(dict)
    ctx.obj['yes'] = yes
    ctx.obj['config'] = config
    if ctx.invoked_subcommand is None:
        from .modules.install import InstallManager
        mgr = InstallManager(config)
        success = mgr.install_all(auto_yes=yes)
        sys.exit(0 if success else 1)


@install.command('all')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--skip-system', is_flag=True, help='Skip system setup')
@click.option('--skip-binaries', is_flag=True, help='Skip binary installation')
@click.option('--skip-db', is_flag=True, help='Skip database creation')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def install_all(config, skip_system, skip_binaries, skip_db, yes):
    """🚀 Complete Oracle 19c installation from scratch"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.install_all(skip_system, skip_binaries, skip_db, auto_yes=yes)
    sys.exit(0 if success else 1)


@install.command('full')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def install_full(config, yes):
    """🚀 ONE-BUTTON Complete Oracle 19c installation"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.install_all(auto_yes=yes)
    sys.exit(0 if success else 1)


@install.command('system')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
def install_system(config):
    """Prepare system - users, groups, kernel params, packages"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.install_system()
    sys.exit(0 if success else 1)


@install.command('binaries')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
def install_binaries(config):
    """Download Oracle binaries - 3GB download from Google Drive"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.install_binaries()
    sys.exit(0 if success else 1)


@install.command('software')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
def install_software(config):
    """Install Oracle software - runs runInstaller + root scripts"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.install_software()
    sys.exit(0 if success else 1)


@install.command('database')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--name', help='Database name')
def install_database(config, name):
    """Create Oracle database - runs DBCA with CDB/PDB"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.create_database(name)
    sys.exit(0 if success else 1)


@install.command('gui')
@click.option('--host', default='0.0.0.0', help='Host to bind (default: 0.0.0.0 for all interfaces)')
@click.option('--port', default=5000, type=int, help='Port to listen on (default: 5000)')
@click.option('--debug', is_flag=True, help='Run in debug mode')
def install_gui(host, port, debug):
    """🌐 Start Web GUI - Browser-based database management interface"""
    try:
        from .web_server import app, config_manager
        
        # Update config with provided options
        gui_config = config_manager.load_config()
        gui_config['host'] = host
        gui_config['port'] = port
        gui_config['debug'] = debug
        config_manager.save_config(gui_config)
        
        console.print("\n[bold green]🌐 Starting OracleDBA Web GUI...[/bold green]\n")
        console.print(f"[cyan]→ URL:[/cyan] http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
        console.print(f"[cyan]→ Default credentials:[/cyan] admin / admin123")
        console.print(f"[yellow]⚠️  You will be forced to change password on first login[/yellow]\n")
        
        # Start Flask server
        app.run(host=host, port=port, debug=debug)
        
    except ImportError as e:
        console.print("[bold red]❌ Web GUI dependencies not installed![/bold red]")
        console.print(f"[dim]Error: {e}[/dim]")
        console.print("\n[yellow]Install with:[/yellow]")
        console.print("[cyan]pip install oracledba[gui][/cyan]")
        console.print("[yellow]or:[/yellow]")
        console.print("[cyan]pip install flask flask-cors[/cyan]\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Error starting web server:[/bold red] {e}")
        sys.exit(1)


@install.command('check')
def install_check():
    """🔍 Check what's installed - detect Oracle, database, listener status"""
    console.print("\n[bold cyan]Oracle Installation Status Check[/bold cyan]\n")
    
    checks = {}
    
    # Check oracle user
    try:
        result = subprocess.run(['id', 'oracle'], capture_output=True, text=True)
        checks['oracle_user'] = result.returncode == 0
    except:
        checks['oracle_user'] = False
    
    # Check ORACLE_HOME exists
    oracle_home = os.environ.get('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
    checks['oracle_home_exists'] = os.path.exists(oracle_home)
    
    # Check Oracle binaries
    checks['sqlplus'] = os.path.exists(os.path.join(oracle_home, 'bin', 'sqlplus'))
    checks['lsnrctl'] = os.path.exists(os.path.join(oracle_home, 'bin', 'lsnrctl'))
    checks['dbca'] = os.path.exists(os.path.join(oracle_home, 'bin', 'dbca'))
    
    # Check running processes
    try:
        result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
        ps_output = result.stdout
        checks['db_running'] = 'ora_pmon_' in ps_output
        checks['listener_running'] = 'tnslsnr' in ps_output
        
        # Get running SIDs
        running_sids = [line.split('ora_pmon_')[1].strip() for line in ps_output.split('\n') if 'ora_pmon_' in line]
        checks['running_sids'] = running_sids
    except:
        checks['db_running'] = False
        checks['listener_running'] = False
        checks['running_sids'] = []
    
    # Check /etc/oratab
    checks['oratab'] = os.path.exists('/etc/oratab')
    
    # Display results
    table = Table(title="Installation Detection", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="white")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")
    
    def status_icon(val):
        return "[green]✓ YES[/green]" if val else "[red]✗ NO[/red]"
    
    table.add_row("Oracle User", status_icon(checks['oracle_user']), "id oracle")
    table.add_row("ORACLE_HOME", status_icon(checks['oracle_home_exists']), oracle_home)
    table.add_row("sqlplus Binary", status_icon(checks['sqlplus']), f"{oracle_home}/bin/sqlplus")
    table.add_row("lsnrctl Binary", status_icon(checks['lsnrctl']), f"{oracle_home}/bin/lsnrctl")
    table.add_row("DBCA Binary", status_icon(checks['dbca']), f"{oracle_home}/bin/dbca")
    table.add_row("Database Running", status_icon(checks['db_running']), 
                  ', '.join(checks.get('running_sids', [])) or 'No instances')
    table.add_row("Listener Running", status_icon(checks['listener_running']), "tnslsnr process")
    table.add_row("/etc/oratab", status_icon(checks['oratab']), "Database registry")
    
    console.print(table)
    
    # Recommendations
    console.print("\n[bold cyan]Recommendations:[/bold cyan]")
    if not checks['oracle_user']:
        console.print("  [yellow]→ Run:[/yellow] oradba install system  [dim](TP01: create oracle user & groups)[/dim]")
    elif not checks['sqlplus']:
        console.print("  [yellow]→ Run:[/yellow] oradba install binaries  [dim](TP02: download & extract Oracle 19c)[/dim]")
    elif not checks['db_running']:
        console.print("  [yellow]→ Run:[/yellow] oradba install database  [dim](TP03: create database with DBCA)[/dim]")
    else:
        console.print("  [green]✓ Oracle 19c is fully installed and running![/green]")
        console.print("  [dim]Next steps: oradba configure multiplexing | oradba configure storage | oradba install gui[/dim]")
    
    console.print("")


# ============================================================================
# CONFIGURATION COMMANDS
# ============================================================================

@main.group()
def configure():
    """⚙️  Configure Oracle Database features"""
    pass


@configure.command('multiplexing')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def configure_multiplexing(config):
    """Multiplex critical files - control files and redo logs"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('04')
    sys.exit(0 if success else 1)


@configure.command('storage')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def configure_storage(config):
    """Configure storage - tablespaces, datafiles, quotas"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('05')
    sys.exit(0 if success else 1)


@configure.command('users')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def configure_users(config):
    """Configure security - users, roles, profiles, privileges"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('06')
    sys.exit(0 if success else 1)


@configure.command('flashback')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def configure_flashback(config):
    """Setup Flashback - query, table, and database recovery"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('07')
    sys.exit(0 if success else 1)


@configure.command('backup')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def configure_backup(config):
    """Setup RMAN backup strategy"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('08')
    sys.exit(0 if success else 1)


@configure.command('dataguard')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def configure_dataguard(config):
    """Setup Data Guard for high availability"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('09')
    sys.exit(0 if success else 1)


@configure.command('all')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def configure_all(config):
    """Run all post-installation configuration steps"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_all_labs(start_from='04', end_at='09')
    sys.exit(0 if success else 1)


# ============================================================================
# MAINTENANCE COMMANDS
# ============================================================================

@main.group()
def maintenance():
    """🔧 Database maintenance operations"""
    pass


@maintenance.command('tune')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def maintenance_tune(config):
    """Performance tuning - AWR, SQL optimization"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('10')
    sys.exit(0 if success else 1)


@maintenance.command('patch')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def maintenance_patch(config):
    """Apply Oracle patches and updates"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('11')
    sys.exit(0 if success else 1)


# ============================================================================
# ADVANCED FEATURES
# ============================================================================

@main.group()
def advanced():
    """🚀 Advanced Oracle features"""
    pass


@advanced.command('multitenant')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def advanced_multitenant(config):
    """Configure multitenant architecture - CDB/PDB management"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('12')
    sys.exit(0 if success else 1)


@advanced.command('ai-ml')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def advanced_ai_ml(config):
    """Setup Oracle AI and Machine Learning features"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('13')
    sys.exit(0 if success else 1)


@advanced.command('data-mobility')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def advanced_data_mobility(config):
    """Data mobility - Data Pump, transportable tablespaces"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('14')
    sys.exit(0 if success else 1)


@advanced.command('asm-rac')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
def advanced_asm_rac(config):
    """Setup ASM and RAC clustering concepts"""
    from .modules.install import InstallManager
    mgr = InstallManager(config)
    success = mgr.run_lab('15')
    sys.exit(0 if success else 1)


# ============================================================================
# LABS LIST COMMAND
# ============================================================================

@main.command('labs')
def labs_list():
    """📚 List all available configuration and advanced labs"""
    from .modules.install import InstallManager
    mgr = InstallManager()
    mgr.list_labs()


# ============================================================================
# PRE-INSTALLATION CHECK
# ============================================================================

@main.command('precheck')
@click.option('--fix', is_flag=True, help='Generate fix script')
def precheck(fix):
    """🔍 Check system requirements before installation"""
    from .modules.precheck import PreInstallChecker
    checker = PreInstallChecker()
    result = checker.check_all()
    
    if fix or not result:
        checker.generate_fix_script()
        console.print("\n[cyan]Run:[/cyan] sudo bash fix-precheck-issues.sh")


# ============================================================================
# TESTING COMMANDS
# ============================================================================

@main.command('test')
@click.option('--oracle-home', help='ORACLE_HOME path')
@click.option('--oracle-sid', help='ORACLE_SID name')
@click.option('--report', is_flag=True, help='Generate detailed report')
def test(oracle_home, oracle_sid, report):
    """🧪 Test Oracle installation"""
    from .modules.testing import OracleTestSuite
    tester = OracleTestSuite(oracle_home, oracle_sid)
    result = tester.run_all_tests()
    
    if report:
        tester.generate_test_report()


# ============================================================================
# DOWNLOAD ORACLE SOFTWARE
# ============================================================================

@main.group()
def download():
    """📥 Download Oracle software"""
    pass


@download.command('database')
@click.option('--url', help='Custom download URL')
@click.option('--dir', default='/opt/oracle/install', help='Download directory')
def download_database(url, dir):
    """Download Oracle 19c Database software"""
    from .modules.downloader import OracleDownloader
    downloader = OracleDownloader(dir)
    downloader.download_oracle_19c('database', url)


@download.command('grid')
@click.option('--url', help='Custom download URL')
@click.option('--dir', default='/opt/oracle/install', help='Download directory')
def download_grid(url, dir):
    """Download Oracle Grid Infrastructure software"""
    from .modules.downloader import OracleDownloader
    downloader = OracleDownloader(dir)
    downloader.download_oracle_19c('grid', url)


@download.command('extract')
@click.argument('zip-file')
@click.option('--to', 'extract_to', help='Extract to directory (ORACLE_HOME)')
def download_extract(zip_file, extract_to):
    """Extract Oracle ZIP file"""
    from .modules.downloader import OracleDownloader
    downloader = OracleDownloader()
    downloader.extract_oracle_zip(zip_file, extract_to)


# ============================================================================
# RESPONSE FILE GENERATION
# ============================================================================

@main.group()
def genrsp():
    """📝 Generate Oracle response files"""
    pass


@genrsp.command('all')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--output-dir', default='/tmp', help='Output directory')
def genrsp_all(config, output_dir):
    """Generate all response files (DB, DBCA, NETCA)"""
    from .modules.response_files import generate_all_response_files
    files = generate_all_response_files(config, output_dir)
    
    console.print("\n[green]✓[/green] Response files generated:")
    for name, path in files.items():
        console.print(f"  • {name}: {path}")


@genrsp.command('db-install')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--output', default='/tmp/db_install.rsp', help='Output file')
def genrsp_db(config, output):
    """Generate DB installation response file"""
    from .modules.response_files import generate_response_file
    import yaml
    
    cfg = {}
    if config:
        with open(config) as f:
            cfg = yaml.safe_load(f).get('oracle', {})
    
    generate_response_file('DB_INSTALL', cfg, output)
    console.print(f"[green]✓[/green] Generated: {output}")


@genrsp.command('dbca')
@click.option('--config', type=click.Path(exists=True), help='Configuration YAML file')
@click.option('--output', default='/tmp/dbca.rsp', help='Output file')
def genrsp_dbca(config, output):
    """Generate DBCA response file"""
    from .modules.response_files import generate_response_file
    import yaml
    
    cfg = {}
    if config:
        with open(config) as f:
            cfg = yaml.safe_load(f).get('database', {})
    
    generate_response_file('DBCA', cfg, output)
    console.print(f"[green]✓[/green] Generated: {output}")


# ============================================================================
# RMAN COMMANDS
# ============================================================================

@main.group()
def rman():
    """💾 RMAN Backup and Recovery"""
    pass


@rman.command('setup')
@click.option('--retention', default=7, help='Retention policy in days')
@click.option('--compression', is_flag=True, default=True, help='Enable compression')
def rman_setup(retention, compression):
    """Configure RMAN"""
    from .modules.rman import RMANManager
    mgr = RMANManager()
    mgr.setup(retention, compression)


@rman.command('backup')
@click.option('--type', type=click.Choice(['full', 'incremental', 'archive']), default='full')
@click.option('--tag', help='Backup tag')
def rman_backup(type, tag):
    """Perform RMAN backup"""
    from .modules.rman import RMANManager
    mgr = RMANManager()
    mgr.backup(type, tag)


@rman.command('restore')
@click.option('--point-in-time', help='Point in time (YYYY-MM-DD HH:MI:SS)')
def rman_restore(point_in_time):
    """Restore database with RMAN"""
    from .modules.rman import RMANManager
    mgr = RMANManager()
    mgr.restore(point_in_time)


@rman.command('list')
@click.option('--type', type=click.Choice(['backup', 'archivelog', 'all']), default='backup')
def rman_list(type):
    """List RMAN backups"""
    from .modules.rman import RMANManager
    mgr = RMANManager()
    mgr.list_backups(type)


# ============================================================================
# DATA GUARD COMMANDS
# ============================================================================

@main.group()
def dataguard():
    """🔄 Data Guard Management"""
    pass


@dataguard.command('setup')
@click.option('--primary-host', required=True, help='Primary database host')
@click.option('--standby-host', required=True, help='Standby database host')
@click.option('--db-name', required=True, help='Database name')
def dataguard_setup(primary_host, standby_host, db_name):
    """Configure Data Guard"""
    from .modules.dataguard import DataGuardManager
    mgr = DataGuardManager()
    mgr.setup(primary_host, standby_host, db_name)


@dataguard.command('status')
def dataguard_status():
    """Check Data Guard status"""
    from .modules.dataguard import DataGuardManager
    mgr = DataGuardManager()
    mgr.status()


@dataguard.command('switchover')
def dataguard_switchover():
    """Perform switchover"""
    from .modules.dataguard import DataGuardManager
    mgr = DataGuardManager()
    mgr.switchover()


@dataguard.command('failover')
def dataguard_failover():
    """Perform failover"""
    from .modules.dataguard import DataGuardManager
    mgr = DataGuardManager()
    mgr.failover()


# ============================================================================
# TUNING COMMANDS
# ============================================================================

@main.group()
def tuning():
    """⚡ Performance Tuning"""
    pass


@tuning.command('analyze')
@click.option('--deep', is_flag=True, help='Deep analysis')
def tuning_analyze(deep):
    """Analyze database performance"""
    from .modules.tuning import TuningManager
    mgr = TuningManager()
    mgr.analyze(deep)


@tuning.command('awr')
@click.option('--begin-snap', type=int, help='Begin snapshot ID')
@click.option('--end-snap', type=int, help='End snapshot ID')
def tuning_awr(begin_snap, end_snap):
    """Generate AWR report"""
    from .modules.tuning import TuningManager
    mgr = TuningManager()
    mgr.generate_awr(begin_snap, end_snap)


@tuning.command('addm')
def tuning_addm():
    """Generate ADDM report"""
    from .modules.tuning import TuningManager
    mgr = TuningManager()
    mgr.generate_addm()


@tuning.command('sql-trace')
@click.option('--session-id', type=int, help='Session ID to trace')
def tuning_sql_trace(session_id):
    """Enable SQL trace"""
    from .modules.tuning import TuningManager
    mgr = TuningManager()
    mgr.sql_trace(session_id)


# ============================================================================
# ASM COMMANDS
# ============================================================================

@main.group()
def asm():
    """💿 Automatic Storage Management"""
    pass


@asm.command('setup')
@click.option('--disks', multiple=True, help='Disk devices')
def asm_setup(disks):
    """Configure ASM"""
    from .modules.asm import ASMManager
    mgr = ASMManager()
    mgr.setup(list(disks))


@asm.command('create-diskgroup')
@click.option('--name', required=True, help='Diskgroup name')
@click.option('--redundancy', type=click.Choice(['EXTERNAL', 'NORMAL', 'HIGH']), default='NORMAL')
@click.option('--disks', multiple=True, required=True, help='Disk paths')
def asm_create_diskgroup(name, redundancy, disks):
    """Create ASM diskgroup"""
    from .modules.asm import ASMManager
    mgr = ASMManager()
    mgr.create_diskgroup(name, redundancy, list(disks))


@asm.command('status')
def asm_status():
    """Check ASM status"""
    from .modules.asm import ASMManager
    mgr = ASMManager()
    mgr.status()


# ============================================================================
# RAC COMMANDS
# ============================================================================

@main.group()
def rac():
    """🔗 Real Application Clusters"""
    pass


@rac.command('setup')
@click.option('--nodes', multiple=True, required=True, help='Node hostnames')
@click.option('--vip', multiple=True, required=True, help='Virtual IPs')
def rac_setup(nodes, vip):
    """Configure RAC"""
    from .modules.rac import RACManager
    mgr = RACManager()
    mgr.setup(list(nodes), list(vip))


@rac.command('add-node')
@click.option('--hostname', required=True, help='New node hostname')
@click.option('--vip', required=True, help='Virtual IP')
def rac_add_node(hostname, vip):
    """Add RAC node"""
    from .modules.rac import RACManager
    mgr = RACManager()
    mgr.add_node(hostname, vip)


@rac.command('status')
def rac_status():
    """Check RAC cluster status"""
    from .modules.rac import RACManager
    mgr = RACManager()
    mgr.status()


# ============================================================================
# MULTITENANT (PDB) COMMANDS
# ============================================================================

@main.group()
def pdb():
    """🏢 Multitenant - PDB Management"""
    pass


@pdb.command('create')
@click.argument('name')
@click.option('--admin-user', default='pdbadmin', help='PDB admin user')
@click.option('--admin-password', prompt=True, hide_input=True, help='Admin password')
def pdb_create(name, admin_user, admin_password):
    """Create new PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.create(name, admin_user, admin_password)


@pdb.command('clone')
@click.argument('source')
@click.argument('destination')
def pdb_clone(source, destination):
    """Clone PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.clone(source, destination)


@pdb.command('list')
def pdb_list():
    """List all PDBs"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.list_pdbs()


@pdb.command('open')
@click.argument('name')
def pdb_open(name):
    """Open PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.open(name)


@pdb.command('close')
@click.argument('name')
def pdb_close(name):
    """Close PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.close(name)


@pdb.command('drop')
@click.argument('name')
@click.option('--including-datafiles', is_flag=True, help='Drop including datafiles')
def pdb_drop(name, including_datafiles):
    """Drop PDB"""
    from .modules.pdb import PDBManager
    mgr = PDBManager()
    mgr.drop(name, including_datafiles)


# ============================================================================
# FLASHBACK COMMANDS
# ============================================================================

@main.group()
def flashback():
    """📊 Flashback Technology"""
    pass


@flashback.command('enable')
@click.option('--retention', default=2880, help='Retention in minutes (default 2 days)')
def flashback_enable(retention):
    """Enable Flashback Database"""
    from .modules.flashback import FlashbackManager
    mgr = FlashbackManager()
    mgr.enable(retention)


@flashback.command('disable')
def flashback_disable():
    """Disable Flashback Database"""
    from .modules.flashback import FlashbackManager
    mgr = FlashbackManager()
    mgr.disable()


@flashback.command('restore')
@click.option('--point-in-time', help='Point in time')
@click.option('--scn', type=int, help='SCN number')
def flashback_restore(point_in_time, scn):
    """Restore database with Flashback"""
    from .modules.flashback import FlashbackManager
    mgr = FlashbackManager()
    mgr.restore(point_in_time, scn)


# ============================================================================
# SECURITY COMMANDS
# ============================================================================

@main.group()
def security():
    """🔐 Security Management"""
    pass


@security.command('audit')
@click.option('--enable', is_flag=True, help='Enable auditing')
def security_audit(enable):
    """Configure auditing"""
    from .modules.security import SecurityManager
    mgr = SecurityManager()
    mgr.configure_audit(enable)


@security.command('encryption')
@click.option('--enable', is_flag=True, help='Enable TDE')
def security_encryption(enable):
    """Configure Transparent Data Encryption"""
    from .modules.security import SecurityManager
    mgr = SecurityManager()
    mgr.configure_tde(enable)


@security.command('users')
@click.option('--create', help='Create user')
@click.option('--drop', help='Drop user')
@click.option('--list', 'list_users', is_flag=True, help='List users')
def security_users(create, drop, list_users):
    """Manage database users"""
    from .modules.security import SecurityManager
    mgr = SecurityManager()
    if create:
        mgr.create_user(create)
    elif drop:
        mgr.drop_user(drop)
    elif list_users:
        mgr.list_users()


# ============================================================================
# NFS COMMANDS
# ============================================================================

@main.group()
def nfs():
    """🌐 NFS Server Management"""
    pass


@nfs.command('setup-server')
@click.option('--export', required=True, help='Export path')
@click.option('--clients', multiple=True, help='Allowed client IPs/networks')
def nfs_setup_server(export, clients):
    """Setup NFS server"""
    from .modules.nfs import NFSManager
    mgr = NFSManager()
    mgr.setup_server(export, list(clients))


@nfs.command('setup-client')
@click.option('--server', required=True, help='NFS server IP')
@click.option('--remote-path', required=True, help='Remote export path')
@click.option('--mount-point', required=True, help='Local mount point')
def nfs_setup_client(server, remote_path, mount_point):
    """Setup NFS client"""
    from .modules.nfs import NFSManager
    mgr = NFSManager()
    mgr.setup_client(server, remote_path, mount_point)


@nfs.command('mount')
@click.option('--server', required=True, help='NFS server')
@click.option('--path', required=True, help='Remote path')
@click.option('--mount-point', required=True, help='Mount point')
def nfs_mount(server, path, mount_point):
    """Mount NFS share"""
    from .modules.nfs import NFSManager
    mgr = NFSManager()
    mgr.mount(server, path, mount_point)


@nfs.command('share')
@click.argument('directory')
@click.option('--clients', multiple=True, help='Allowed clients')
def nfs_share(directory, clients):
    """Share directory via NFS"""
    from .modules.nfs import NFSManager
    mgr = NFSManager()
    mgr.share(directory, list(clients))


# ============================================================================
# DATABASE MANAGEMENT COMMANDS
# ============================================================================

@main.command()
def status():
    """📊 Show database status"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.show_status()


@main.command()
def start():
    """▶️  Start database"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.start()


@main.command()
def stop():
    """⏹️  Stop database"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.stop()


@main.command()
def restart():
    """🔄 Restart database"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.restart()


@main.command()
@click.option('--sysdba', is_flag=True, help='Connect as SYSDBA')
@click.option('--pdb', help='Connect to specific PDB')
def sqlplus(sysdba, pdb):
    """🔌 Connect to SQL*Plus"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.sqlplus(sysdba, pdb)


@main.command()
@click.argument('script', type=click.Path(exists=True))
@click.option('--as-sysdba', is_flag=True, help='Execute as SYSDBA')
def exec(script, as_sysdba):
    """⚙️  Execute SQL or Shell script"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.exec_script(script, as_sysdba)


# ============================================================================
# MONITORING COMMANDS
# ============================================================================

@main.group()
def logs():
    """📝 View logs"""
    pass


@logs.command('alert')
@click.option('--tail', default=50, help='Number of lines to show')
def logs_alert(tail):
    """View alert log"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.view_alert_log(tail)


@logs.command('listener')
@click.option('--tail', default=50, help='Number of lines to show')
def logs_listener(tail):
    """View listener log"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.view_listener_log(tail)


@main.group()
def monitor():
    """📈 Monitor database"""
    pass


@monitor.command('tablespaces')
def monitor_tablespaces():
    """Monitor tablespace usage"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.monitor_tablespaces()


@monitor.command('sessions')
@click.option('--active-only', is_flag=True, help='Show only active sessions')
def monitor_sessions(active_only):
    """Monitor database sessions"""
    from .modules.database import DatabaseManager
    mgr = DatabaseManager()
    mgr.monitor_sessions(active_only)


# ============================================================================
# VM INITIALIZATION
# ============================================================================

@main.command('vm-init')
@click.option('--role', type=click.Choice(['database', 'rac-node', 'dataguard-standby']), required=True)
@click.option('--node-number', type=int, help='Node number for RAC')
def vm_init(role, node_number):
    """🖥️  Initialize new VM for Oracle"""
    from .modules.install import InstallManager
    mgr = InstallManager()
    mgr.vm_init(role, node_number)


if __name__ == '__main__':
    main()
