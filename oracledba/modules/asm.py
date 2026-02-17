"""
ASM Manager - Automatic Storage Management
"""

from pathlib import Path
from rich.console import Console
from rich import print as rprint
import subprocess

console = Console()


class ASMManager:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
    
    def setup(self, disks):
        """Setup ASM"""
        console.print("\n[bold cyan]Setting up ASM[/bold cyan]\n")
        
        script = self.scripts_dir / "tp15-asm-rac-concepts.sh"
        if script.exists():
            result = subprocess.run(['bash', str(script)], capture_output=True, text=True)
            if result.returncode == 0:
                rprint("[green]✓[/green] ASM configured")
                return True
        
        rprint("[red]✗ ASM setup failed[/red]")
        return False
    
    def create_diskgroup(self, name, redundancy, disks):
        """Create ASM diskgroup"""
        console.print(f"\n[bold cyan]Creating diskgroup {name}[/bold cyan]\n")
        
        disk_clause = " DISK " + ", ".join([f"'{disk}'" for disk in disks])
        
        sql = f"""
        CREATE DISKGROUP {name} {redundancy} REDUNDANCY
        {disk_clause};
        """
        
        cmd = f"echo \"{sql}\" | sqlplus -S / as sysasm"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            rprint(f"[green]✓[/green] Diskgroup {name} created")
            return True
        else:
            rprint(f"[red]✗ Failed:[/red] {result.stderr}")
            return False
    
    def status(self):
        """Check ASM status"""
        console.print("\n[bold cyan]ASM Status[/bold cyan]\n")
        
        sql = """
        SELECT name, state, type, total_mb, free_mb 
        FROM v$asm_diskgroup;
        
        SELECT name, path, state, total_mb 
        FROM v$asm_disk;
        """
        
        cmd = f"echo \"{sql}\" | sqlplus -S / as sysasm"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        console.print(result.stdout)
