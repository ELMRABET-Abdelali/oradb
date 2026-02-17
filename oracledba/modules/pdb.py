"""
Multitenant PDB Manager
"""

import subprocess
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


class PDBManager:
    def __init__(self):
        pass
    
    def _run_sql(self, sql):
        """Execute SQL as sysdba"""
        try:
            cmd = f"echo \"{sql}\" | sqlplus -S / as sysdba"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def create(self, pdb_name, admin_user='pdbadmin', admin_password='Oracle123'):
        """Create new PDB"""
        console.print(f"\n[bold cyan]Creating PDB: {pdb_name}[/bold cyan]\n")
        
        sql = f"""
        CREATE PLUGGABLE DATABASE {pdb_name}
        ADMIN USER {admin_user} IDENTIFIED BY {admin_password}
        FILE_NAME_CONVERT=('pdbseed', '{pdb_name.lower()}');
        
        ALTER PLUGGABLE DATABASE {pdb_name} OPEN;
        ALTER PLUGGABLE DATABASE {pdb_name} SAVE STATE;
        """
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint(f"[green]✓[/green] PDB {pdb_name} created successfully")
            return True
        else:
            rprint(f"[red]✗ Failed to create PDB:[/red] {stderr}")
            return False
    
    def clone(self, source_pdb, dest_pdb):
        """Clone PDB"""
        console.print(f"\n[bold cyan]Cloning {source_pdb} to {dest_pdb}[/bold cyan]\n")
        
        sql = f"""
        CREATE PLUGGABLE DATABASE {dest_pdb} FROM {source_pdb}
        FILE_NAME_CONVERT=('{source_pdb.lower()}', '{dest_pdb.lower()}');
        
        ALTER PLUGGABLE DATABASE {dest_pdb} OPEN;
        ALTER PLUGGABLE DATABASE {dest_pdb} SAVE STATE;
        """
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint(f"[green]✓[/green] PDB cloned successfully")
            return True
        else:
            rprint(f"[red]✗ Cloning failed:[/red] {stderr}")
            return False
    
    def list_pdbs(self):
        """List all PDBs"""
        console.print("\n[bold cyan]Pluggable Databases[/bold cyan]\n")
        
        sql = "SELECT name, open_mode, restricted, open_time FROM v$pdbs ORDER BY con_id;"
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            console.print(stdout)
            return True
        else:
            rprint(f"[red]Error:[/red] {stderr}")
            return False
    
    def open(self, pdb_name):
        """Open PDB"""
        console.print(f"\n[bold cyan]Opening PDB: {pdb_name}[/bold cyan]\n")
        
        sql = f"ALTER PLUGGABLE DATABASE {pdb_name} OPEN;"
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint(f"[green]✓[/green] PDB {pdb_name} opened")
            return True
        else:
            rprint(f"[red]✗ Failed:[/red] {stderr}")
            return False
    
    def close(self, pdb_name):
        """Close PDB"""
        console.print(f"\n[bold cyan]Closing PDB: {pdb_name}[/bold cyan]\n")
        
        sql = f"ALTER PLUGGABLE DATABASE {pdb_name} CLOSE IMMEDIATE;"
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint(f"[green]✓[/green] PDB {pdb_name} closed")
            return True
        else:
            rprint(f"[red]✗ Failed:[/red] {stderr}")
            return False
    
    def drop(self, pdb_name, including_datafiles=False):
        """Drop PDB"""
        console.print(f"\n[bold red]⚠️  Dropping PDB: {pdb_name}[/bold red]\n")
        
        datafiles_clause = "INCLUDING DATAFILES" if including_datafiles else ""
        
        sql = f"""
        ALTER PLUGGABLE DATABASE {pdb_name} CLOSE IMMEDIATE;
        DROP PLUGGABLE DATABASE {pdb_name} {datafiles_clause};
        """
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint(f"[green]✓[/green] PDB {pdb_name} dropped")
            return True
        else:
            rprint(f"[red]✗ Failed:[/red] {stderr}")
            return False
