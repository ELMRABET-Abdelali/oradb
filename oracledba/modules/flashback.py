"""
Flashback Manager
"""

from rich.console import Console
from rich import print as rprint
import subprocess

console = Console()


class FlashbackManager:
    def __init__(self):
        pass
    
    def _run_sql(self, sql):
        """Execute SQL"""
        cmd = f"echo \"{sql}\" | sqlplus -S / as sysdba"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    
    def enable(self, retention_minutes=2880):
        """Enable Flashback Database"""
        console.print(f"\n[bold cyan]Enabling Flashback Database[/bold cyan]")
        console.print(f"Retention: {retention_minutes} minutes ({retention_minutes//60} hours)\n")
        
        sql = f"""
        ALTER SYSTEM SET DB_FLASHBACK_RETENTION_TARGET={retention_minutes} SCOPE=BOTH;
        SHUTDOWN IMMEDIATE;
        STARTUP MOUNT;
        ALTER DATABASE FLASHBACK ON;
        ALTER DATABASE OPEN;
        """
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint("[green]✓[/green] Flashback Database enabled")
            return True
        else:
            rprint(f"[red]✗ Failed:[/red] {stderr}")
            return False
    
    def disable(self):
        """Disable Flashback Database"""
        console.print("\n[bold cyan]Disabling Flashback Database[/bold cyan]\n")
        
        sql = """
        ALTER DATABASE FLASHBACK OFF;
        """
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint("[green]✓[/green] Flashback Database disabled")
            return True
        else:
            rprint(f"[red]✗ Failed:[/red] {stderr}")
            return False
    
    def restore(self, point_in_time=None, scn=None):
        """Restore with Flashback"""
        console.print("\n[bold red]⚠️  Flashback Database Restore[/bold red]\n")
        
        if point_in_time:
            sql = f"""
            SHUTDOWN IMMEDIATE;
            STARTUP MOUNT;
            FLASHBACK DATABASE TO TIMESTAMP TO_TIMESTAMP('{point_in_time}', 'YYYY-MM-DD HH24:MI:SS');
            ALTER DATABASE OPEN RESETLOGS;
            """
        elif scn:
            sql = f"""
            SHUTDOWN IMMEDIATE;
            STARTUP MOUNT;
            FLASHBACK DATABASE TO SCN {scn};
            ALTER DATABASE OPEN RESETLOGS;
            """
        else:
            rprint("[red]Error: Specify point_in_time or scn[/red]")
            return False
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint("[green]✓[/green] Database restored with Flashback")
            return True
        else:
            rprint(f"[red]✗ Restore failed:[/red] {stderr}")
            return False
