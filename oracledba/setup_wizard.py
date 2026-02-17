#!/usr/bin/env python3
"""
OracleDBA Setup Wizard
Interactive installation wizard
"""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint
import yaml
from pathlib import Path

console = Console()


def main():
    """Main setup wizard"""
    console.print(Panel.fit(
        "[bold cyan]OracleDBA Setup Wizard[/bold cyan]\n\n"
        "This wizard will guide you through Oracle 19c installation configuration",
        title="🚀 Welcome"
    ))
    
    config = {}
    
    # System configuration
    console.print("\n[bold]System Configuration[/bold]")
    config['system'] = {
        'os': Prompt.ask("Operating System", default="Rocky Linux 8"),
        'min_ram_gb': int(Prompt.ask("Minimum RAM (GB)", default="4")),
        'min_disk_gb': int(Prompt.ask("Minimum Disk Space (GB)", default="50")),
    }
    
    # Oracle configuration
    console.print("\n[bold]Oracle Configuration[/bold]")
    config['oracle'] = {
        'version': Prompt.ask("Oracle Version", default="19.3.0.0.0"),
        'edition': Prompt.ask("Edition", choices=["EE", "SE2"], default="EE"),
        'oracle_base': Prompt.ask("ORACLE_BASE", default="/u01/app/oracle"),
        'oracle_home': Prompt.ask("ORACLE_HOME", default="/u01/app/oracle/product/19.3.0/dbhome_1"),
    }
    
    # Database configuration
    console.print("\n[bold]Database Configuration[/bold]")
    config['database'] = {
        'db_name': Prompt.ask("Database Name", default="GDCPROD"),
        'sid': Prompt.ask("SID", default="GDCPROD"),
        'cdb': Confirm.ask("Enable Container Database (CDB)?", default=True),
        'sys_password': Prompt.ask("SYS Password", password=True),
        'system_password': Prompt.ask("SYSTEM Password", password=True),
    }
    
    # PDBs if CDB
    if config['database']['cdb']:
        console.print("\n[bold]Pluggable Databases (PDB)[/bold]")
        num_pdbs = int(Prompt.ask("Number of PDBs to create", default="1"))
        config['database']['pdbs'] = []
        
        for i in range(num_pdbs):
            pdb_name = Prompt.ask(f"PDB #{i+1} Name", default=f"PDB{i+1}")
            pdb_admin_password = Prompt.ask(f"PDB #{i+1} Admin Password", password=True)
            config['database']['pdbs'].append({
                'name': pdb_name,
                'admin_user': f'{pdb_name.lower()}admin',
                'admin_password': pdb_admin_password
            })
    
    # Backup configuration
    console.print("\n[bold]Backup Configuration (RMAN)[/bold]")
    if Confirm.ask("Configure RMAN backup?", default=True):
        config['backup'] = {
            'location': Prompt.ask("Backup Location", default="/u01/backup"),
            'retention_days': int(Prompt.ask("Retention (days)", default="7")),
            'compression': Confirm.ask("Enable compression?", default=True),
            'parallelism': int(Prompt.ask("Backup parallelism", default="2")),
        }
    
    # ASM configuration
    console.print("\n[bold]ASM Configuration[/bold]")
    if Confirm.ask("Configure ASM?", default=False):
        config['asm'] = {
            'grid_home': Prompt.ask("Grid Home", default="/u01/app/19.3.0/grid"),
            'diskgroups': []
        }
        
        num_dgs = int(Prompt.ask("Number of disk groups", default="1"))
        for i in range(num_dgs):
            dg_name = Prompt.ask(f"Diskgroup #{i+1} Name", default=f"DATA{i+1}")
            redundancy = Prompt.ask(f"Redundancy", choices=["EXTERNAL", "NORMAL", "HIGH"], default="NORMAL")
            config['asm']['diskgroups'].append({
                'name': dg_name,
                'redundancy': redundancy
            })
    
    # Data Guard
    console.print("\n[bold]Data Guard Configuration[/bold]")
    if Confirm.ask("Configure Data Guard?", default=False):
        config['dataguard'] = {
            'standby_host': Prompt.ask("Standby Host"),
            'standby_db_name': Prompt.ask("Standby DB Name"),
        }
    
    # NFS
    console.print("\n[bold]NFS Configuration[/bold]")
    if Confirm.ask("Configure NFS?", default=False):
        role = Prompt.ask("NFS Role", choices=["server", "client"], default="client")
        if role == "server":
            config['nfs'] = {
                'role': 'server',
                'export_path': Prompt.ask("Export Path", default="/u01/shared"),
            }
        else:
            config['nfs'] = {
                'role': 'client',
                'server': Prompt.ask("NFS Server IP/Hostname"),
                'remote_path': Prompt.ask("Remote Path", default="/u01/shared"),
                'mount_point': Prompt.ask("Mount Point", default="/u01/nfs"),
            }
    
    # Save configuration
    console.print("\n[bold green]Configuration Summary[/bold green]")
    console.print_json(data=config)
    
    if Confirm.ask("\nSave this configuration?", default=True):
        config_file = Prompt.ask("Configuration filename", default="oradba-config.yml")
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        console.print(f"\n✅ [green]Configuration saved to[/green] [cyan]{config_file}[/cyan]")
        
        if Confirm.ask("\nStart installation now?", default=True):
            console.print("\n[yellow]Starting installation...[/yellow]")
            from .modules.install import InstallManager
            mgr = InstallManager(config_file)
            mgr.install_full()
        else:
            console.print(f"\n[cyan]To install later, run:[/cyan] [bold]oradba install --config {config_file}[/bold]")
    else:
        console.print("\n[yellow]Configuration not saved[/yellow]")


if __name__ == '__main__':
    main()
