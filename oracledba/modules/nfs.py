"""
NFS Manager - Network File System Management
"""

from rich.console import Console
from rich import print as rprint
import subprocess
from pathlib import Path

console = Console()


class NFSManager:
    def __init__(self):
        pass
    
    def setup_server(self, export_path, clients=None):
        """Setup NFS server"""
        console.print("\n[bold cyan]Setting up NFS Server[/bold cyan]\n")
        
        # Install NFS server
        rprint("[cyan]Installing NFS server packages...[/cyan]")
        subprocess.run(['yum', 'install', '-y', 'nfs-utils'], check=False)
        
        # Create export directory
        Path(export_path).mkdir(parents=True, exist_ok=True)
        
        # Configure exports
        client_spec = " ".join(clients) if clients else "*"
        export_line = f"{export_path} {client_spec}(rw,sync,no_root_squash,no_all_squash)\n"
        
        with open('/etc/exports', 'a') as f:
            f.write(export_line)
        
        # Export filesystems
        subprocess.run(['exportfs', '-ra'])
        
        # Enable and start NFS
        subprocess.run(['systemctl', 'enable', 'nfs-server'])
        subprocess.run(['systemctl', 'start', 'nfs-server'])
        
        rprint(f"[green]✓[/green] NFS server configured - exporting {export_path}")
        return True
    
    def setup_client(self, server, remote_path, mount_point):
        """Setup NFS client"""
        console.print("\n[bold cyan]Setting up NFS Client[/bold cyan]\n")
        
        # Install NFS client
        rprint("[cyan]Installing NFS client packages...[/cyan]")
        subprocess.run(['yum', 'install', '-y', 'nfs-utils'], check=False)
        
        # Create mount point
        Path(mount_point).mkdir(parents=True, exist_ok=True)
        
        # Mount NFS
        result = subprocess.run(
            ['mount', '-t', 'nfs', f'{server}:{remote_path}', mount_point],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            # Add to /etc/fstab for persistence
            fstab_line = f"{server}:{remote_path} {mount_point} nfs defaults 0 0\n"
            with open('/etc/fstab', 'a') as f:
                f.write(fstab_line)
            
            rprint(f"[green]✓[/green] NFS mounted at {mount_point}")
            return True
        else:
            rprint(f"[red]✗ Mount failed:[/red] {result.stderr}")
            return False
    
    def mount(self, server, remote_path, mount_point):
        """Mount NFS share"""
        console.print(f"\n[bold cyan]Mounting NFS Share[/bold cyan]")
        console.print(f"{server}:{remote_path} -> {mount_point}\n")
        
        Path(mount_point).mkdir(parents=True, exist_ok=True)
        
        result = subprocess.run(
            ['mount', '-t', 'nfs', f'{server}:{remote_path}', mount_point],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            rprint("[green]✓[/green] NFS share mounted")
            return True
        else:
            rprint(f"[red]✗ Mount failed:[/red] {result.stderr}")
            return False
    
    def share(self, directory, clients=None):
        """Share directory via NFS"""
        console.print(f"\n[bold cyan]Sharing {directory} via NFS[/bold cyan]\n")
        
        client_spec = " ".join(clients) if clients else "*"
        export_line = f"{directory} {client_spec}(rw,sync,no_root_squash)\n"
        
        with open('/etc/exports', 'a') as f:
            f.write(export_line)
        
        subprocess.run(['exportfs', '-ra'])
        
        rprint(f"[green]✓[/green] Directory {directory} shared via NFS")
        return True
