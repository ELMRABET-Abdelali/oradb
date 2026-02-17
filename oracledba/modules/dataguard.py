"""
Data Guard Manager
"""

from pathlib import Path
from rich.console import Console
from rich import print as rprint
import subprocess

console = Console()


class DataGuardManager:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
    
    def setup(self, primary_host, standby_host, db_name):
        """Setup Data Guard"""
        console.print(f"\n[bold cyan]Setting up Data Guard[/bold cyan]")
        console.print(f"Primary: {primary_host}")
        console.print(f"Standby: {standby_host}\n")
        
        script = self.scripts_dir / "tp09-dataguard.sh"
        if script.exists():
            result = subprocess.run(['bash', str(script)], capture_output=True, text=True)
            if result.returncode == 0:
                rprint("[green]✓[/green] Data Guard configured")
                return True
        
        rprint("[red]✗ Data Guard setup failed[/red]")
        return False
    
    def status(self):
        """Check Data Guard status"""
        console.print("\n[bold cyan]Data Guard Status[/bold cyan]\n")
        
        sql = """
        SELECT database_role, protection_mode, protection_level 
        FROM v$database;
        
        SELECT process, status, sequence# 
        FROM v$managed_standby;
        """
        
        cmd = f"echo \"{sql}\" | sqlplus -S / as sysdba"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        console.print(result.stdout)
    
    def switchover(self):
        """Perform switchover"""
        console.print("\n[bold cyan]Performing Switchover[/bold cyan]\n")
        rprint("[yellow]This is a critical operation![/yellow]")
        # Implement switchover logic
        return True
    
    def failover(self):
        """Perform failover"""
        console.print("\n[bold red]⚠️  Performing Failover[/bold red]\n")
        rprint("[yellow]Emergency operation - Primary database unavailable[/yellow]")
        # Implement failover logic
        return True
