"""
Database Manager - Core database operations
"""

import os
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


class DatabaseManager:
    def __init__(self):
        self.oracle_home = os.getenv('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
        self.oracle_sid = os.getenv('ORACLE_SID', 'GDCPROD')
        self.sqlplus = f"{self.oracle_home}/bin/sqlplus"
    
    def _run_sql(self, sql, as_sysdba=True):
        """Execute SQL command"""
        try:
            connect_str = "/ as sysdba" if as_sysdba else "/"
            cmd = f"echo \"{sql}\" | {self.sqlplus} -S {connect_str}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def show_status(self):
        """Show database status"""
        console.print("\n[bold cyan]Oracle Database Status[/bold cyan]\n")
        
        # Database status
        sql = "SELECT instance_name, status, database_status FROM v$instance;"
        success, stdout, _ = self._run_sql(sql)
        
        if success:
            console.print("[green]Database is accessible[/green]")
            console.print(stdout)
        else:
            console.print("[red]Database is not accessible[/red]")
        
        # Tablespaces
        sql = "SELECT tablespace_name, status FROM dba_tablespaces;"
        success, stdout, _ = self._run_sql(sql)
        if success:
            console.print("\n[bold]Tablespaces:[/bold]")
            console.print(stdout)
        
        # PDBs if CDB
        sql = "SELECT name, open_mode FROM v$pdbs;"
        success, stdout, _ = self._run_sql(sql)
        if success and stdout.strip():
            console.print("\n[bold]Pluggable Databases:[/bold]")
            console.print(stdout)
    
    def start(self):
        """Start database"""
        console.print("\n[bold cyan]Starting Oracle Database[/bold cyan]\n")
        
        sql = "STARTUP;"
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint("[green]✓[/green] Database started successfully")
            console.print(stdout)
            return True
        else:
            rprint(f"[red]✗ Failed to start database:[/red] {stderr}")
            return False
    
    def stop(self):
        """Stop database"""
        console.print("\n[bold cyan]Stopping Oracle Database[/bold cyan]\n")
        
        sql = "SHUTDOWN IMMEDIATE;"
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint("[green]✓[/green] Database stopped successfully")
            return True
        else:
            rprint(f"[red]✗ Failed to stop database:[/red] {stderr}")
            return False
    
    def restart(self):
        """Restart database"""
        console.print("\n[bold cyan]Restarting Oracle Database[/bold cyan]\n")
        
        sql = "SHUTDOWN IMMEDIATE;\nSTARTUP;"
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint("[green]✓[/green] Database restarted successfully")
            return True
        else:
            rprint(f"[red]✗ Failed to restart database:[/red] {stderr}")
            return False
    
    def sqlplus(self, as_sysdba=False, pdb=None):
        """Connect to SQL*Plus"""
        console.print("\n[bold cyan]Connecting to SQL*Plus[/bold cyan]\n")
        
        connect_str = "/ as sysdba" if as_sysdba else "/"
        
        if pdb:
            # Connect to PDB
            os.system(f"{self.sqlplus} {connect_str} <<< 'ALTER SESSION SET CONTAINER={pdb};'")
        
        os.system(f"{self.sqlplus} {connect_str}")
    
    def exec_script(self, script_path, as_sysdba=True):
        """Execute SQL or shell script"""
        script = Path(script_path)
        
        if not script.exists():
            rprint(f"[red]Error:[/red] Script {script_path} not found")
            return False
        
        console.print(f"\n[bold cyan]Executing {script.name}[/bold cyan]\n")
        
        if script.suffix == '.sql':
            connect_str = "/ as sysdba" if as_sysdba else "/"
            cmd = f"{self.sqlplus} {connect_str} @{script}"
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0
        elif script.suffix == '.sh':
            cmd = f"bash {script}"
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0
        else:
            rprint(f"[red]Error:[/red] Unsupported script type: {script.suffix}")
            return False
    
    def view_alert_log(self, tail=50):
        """View alert log"""
        alert_log = Path(f"{self.oracle_home}/../diag/rdbms/{self.oracle_sid.lower()}/{self.oracle_sid}/trace/alert_{self.oracle_sid}.log")
        
        if alert_log.exists():
            os.system(f"tail -n {tail} {alert_log}")
        else:
            rprint(f"[red]Alert log not found:[/red] {alert_log}")
    
    def view_listener_log(self, tail=50):
        """View listener log"""
        listener_log = Path(f"{self.oracle_home}/../diag/tnslsnr/{os.uname().nodename}/listener/trace/listener.log")
        
        if listener_log.exists():
            os.system(f"tail -n {tail} {listener_log}")
        else:
            rprint(f"[red]Listener log not found:[/red] {listener_log}")
    
    def monitor_tablespaces(self):
        """Monitor tablespace usage"""
        console.print("\n[bold cyan]Tablespace Usage[/bold cyan]\n")
        
        sql = """
        SELECT 
            tablespace_name,
            ROUND(used_space * 8192 / 1024 / 1024, 2) AS used_mb,
            ROUND(tablespace_size * 8192 / 1024 / 1024, 2) AS total_mb,
            ROUND(used_percent, 2) AS used_pct
        FROM dba_tablespace_usage_metrics
        ORDER BY used_percent DESC;
        """
        
        success, stdout, _ = self._run_sql(sql)
        
        if success:
            console.print(stdout)
        else:
            rprint("[red]Failed to retrieve tablespace information[/red]")
    
    def monitor_sessions(self, active_only=False):
        """Monitor database sessions"""
        console.print("\n[bold cyan]Active Sessions[/bold cyan]\n")
        
        where_clause = "WHERE status = 'ACTIVE'" if active_only else ""
        
        sql = f"""
        SELECT 
            username,
            status,
            program,
            machine,
            logon_time
        FROM v$session
        {where_clause}
        ORDER BY logon_time DESC;
        """
        
        success, stdout, _ = self._run_sql(sql)
        
        if success:
            console.print(stdout)
        else:
            rprint("[red]Failed to retrieve session information[/red]")
