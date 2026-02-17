"""
RMAN Manager - Backup and Recovery Management
"""

import subprocess
from pathlib import Path
from rich.console import Console
from rich import print as rprint
from datetime import datetime

console = Console()


class RMANManager:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
    
    def _run_rman(self, commands):
        """Execute RMAN commands"""
        try:
            cmd = f"rman target / << EOF\n{commands}\nEOF"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def setup(self, retention_days=7, compression=True):
        """Configure RMAN"""
        console.print("\n[bold cyan]Configuring RMAN[/bold cyan]\n")
        
        commands = f"""
        CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF {retention_days} DAYS;
        CONFIGURE CONTROLFILE AUTOBACKUP ON;
        CONFIGURE CONTROLFILE AUTOBACKUP FORMAT FOR DEVICE TYPE DISK TO '/u01/backup/cf_%F';
        CONFIGURE DEVICE TYPE DISK PARALLELISM 2 BACKUP TYPE TO BACKUPSET;
        """
        
        if compression:
            commands += "CONFIGURE COMPRESSION ALGORITHM 'MEDIUM' AS OF RELEASE DEFAULT OPTIMIZE FOR LOAD TRUE;\n"
        
        commands += "SHOW ALL;"
        
        success, stdout, stderr = self._run_rman(commands)
        
        if success:
            rprint("[green]✓[/green] RMAN configured successfully")
            console.print(stdout)
            return True
        else:
            rprint(f"[red]✗ RMAN configuration failed:[/red] {stderr}")
            return False
    
    def backup(self, backup_type='full', tag=None):
        """Perform RMAN backup"""
        console.print(f"\n[bold cyan]Starting {backup_type} backup[/bold cyan]\n")
        
        if not tag:
            tag = f"{backup_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if backup_type == 'full':
            commands = f"""
            BACKUP AS COMPRESSED BACKUPSET 
            TAG '{tag}'
            DATABASE PLUS ARCHIVELOG DELETE INPUT;
            """
        elif backup_type == 'incremental':
            commands = f"""
            BACKUP AS COMPRESSED BACKUPSET 
            INCREMENTAL LEVEL 1 
            TAG '{tag}'
            DATABASE PLUS ARCHIVELOG DELETE INPUT;
            """
        elif backup_type == 'archive':
            commands = f"""
            BACKUP AS COMPRESSED BACKUPSET 
            TAG '{tag}'
            ARCHIVELOG ALL DELETE INPUT;
            """
        else:
            rprint(f"[red]Unknown backup type:[/red] {backup_type}")
            return False
        
        success, stdout, stderr = self._run_rman(commands)
        
        if success:
            rprint(f"[green]✓[/green] {backup_type} backup completed successfully")
            return True
        else:
            rprint(f"[red]✗ Backup failed:[/red] {stderr}")
            return False
    
    def restore(self, point_in_time=None):
        """Restore database"""
        console.print("\n[bold red]⚠️  WARNING: Database restore operation[/bold red]\n")
        
        commands = "RESTORE DATABASE;\nRECOVER DATABASE;"
        
        if point_in_time:
            commands = f"RESTORE DATABASE UNTIL TIME \"{point_in_time}\";\nRECOVER DATABASE UNTIL TIME \"{point_in_time}\";"
        
        commands += "\nALTER DATABASE OPEN RESETLOGS;"
        
        success, stdout, stderr = self._run_rman(commands)
        
        if success:
            rprint("[green]✓[/green] Database restored successfully")
            return True
        else:
            rprint(f"[red]✗ Restore failed:[/red] {stderr}")
            return False
    
    def list_backups(self, backup_type='backup'):
        """List RMAN backups"""
        console.print(f"\n[bold cyan]Listing {backup_type}s[/bold cyan]\n")
        
        if backup_type == 'backup':
            commands = "LIST BACKUP SUMMARY;"
        elif backup_type == 'archivelog':
            commands = "LIST ARCHIVELOG ALL;"
        else:
            commands = "LIST BACKUP SUMMARY;\nLIST ARCHIVELOG ALL;"
        
        success, stdout, stderr = self._run_rman(commands)
        
        if success:
            console.print(stdout)
            return True
        else:
            rprint(f"[red]Error:[/red] {stderr}")
            return False
