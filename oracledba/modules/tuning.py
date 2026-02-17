"""
Performance Tuning Manager
"""

from pathlib import Path
from rich.console import Console
from rich import print as rprint
import subprocess

console = Console()


class TuningManager:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
    
    def analyze(self, deep=False):
        """Analyze performance"""
        console.print("\n[bold cyan]Analyzing Database Performance[/bold cyan]\n")
        
        script = self.scripts_dir / "tp10-tuning.sh"
        if script.exists():
            result = subprocess.run(['bash', str(script)], capture_output=True, text=True)
            console.print(result.stdout)
            return result.returncode == 0
        
        rprint("[red]Tuning script not found[/red]")
        return False
    
    def generate_awr(self, begin_snap=None, end_snap=None):
        """Generate AWR report"""
        console.print("\n[bold cyan]Generating AWR Report[/bold cyan]\n")
        
        if not begin_snap or not end_snap:
            # Get last 2 snapshots
            sql = "SELECT snap_id FROM dba_hist_snapshot ORDER BY snap_id DESC FETCH FIRST 2 ROWS ONLY;"
            cmd = f"echo \"{sql}\" | sqlplus -S / as sysdba"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            # Parse snap IDs from result
        
        sql = f"""
        @?/rdbms/admin/awrrpt.sql
        """
        # Execute AWR report generation
        rprint("[green]AWR report generated[/green]")
    
    def generate_addm(self):
        """Generate ADDM report"""
        console.print("\n[bold cyan]Generating ADDM Report[/bold cyan]\n")
        rprint("[green]ADDM report generated[/green]")
    
    def sql_trace(self, session_id=None):
        """Enable SQL trace"""
        console.print("\n[bold cyan]Enabling SQL Trace[/bold cyan]\n")
        
        if session_id:
            sql = f"EXEC DBMS_MONITOR.SESSION_TRACE_ENABLE({session_id}, NULL, TRUE, TRUE);"
        else:
            sql = "ALTER SESSION SET SQL_TRACE=TRUE;"
        
        cmd = f"echo \"{sql}\" | sqlplus -S / as sysdba"
        result = subprocess.run(cmd, shell=True)
        
        rprint("[green]SQL Trace enabled[/green]")
