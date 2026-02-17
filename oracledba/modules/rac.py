"""
RAC Manager - Real Application Clusters
"""

from pathlib import Path
from rich.console import Console
from rich import print as rprint
import subprocess

console = Console()


class RACManager:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
    
    def setup(self, nodes, vips):
        """Setup RAC"""
        console.print("\n[bold cyan]Setting up RAC Cluster[/bold cyan]\n")
        console.print(f"Nodes: {', '.join(nodes)}")
        console.print(f"VIPs: {', '.join(vips)}\n")
        
        script = self.scripts_dir / "tp15-asm-rac-concepts.sh"
        if script.exists():
            result = subprocess.run(['bash', str(script)], capture_output=True, text=True)
            if result.returncode == 0:
                rprint("[green]✓[/green] RAC configured")
                return True
        
        rprint("[red]✗ RAC setup failed[/red]")
        return False
    
    def add_node(self, hostname, vip):
        """Add RAC node"""
        console.print(f"\n[bold cyan]Adding RAC Node[/bold cyan]")
        console.print(f"Hostname: {hostname}")
        console.print(f"VIP: {vip}\n")
        
        rprint("[yellow]This requires Grid Infrastructure to be installed[/yellow]")
        # Implement node addition logic
        return True
    
    def status(self):
        """Check RAC status"""
        console.print("\n[bold cyan]RAC Cluster Status[/bold cyan]\n")
        
        # Check cluster status
        result = subprocess.run(['crsctl', 'stat', 'res', '-t'], capture_output=True, text=True)
        console.print(result.stdout)
        
        # Check database instances
        result = subprocess.run(['srvctl', 'status', 'database', '-d', 'GDCPROD'], 
                              capture_output=True, text=True)
        console.print(result.stdout)
