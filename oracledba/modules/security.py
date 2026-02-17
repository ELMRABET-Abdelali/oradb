"""
Security Manager
"""

from rich.console import Console
from rich import print as rprint
import subprocess

console = Console()


class SecurityManager:
    def __init__(self):
        pass
    
    def _run_sql(self, sql):
        """Execute SQL"""
        cmd = f"echo \"{sql}\" | sqlplus -S / as sysdba"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    
    def configure_audit(self, enable=True):
        """Configure auditing"""
        console.print("\n[bold cyan]Configuring Database Auditing[/bold cyan]\n")
        
        if enable:
            sql = """
            ALTER SYSTEM SET AUDIT_TRAIL=DB,EXTENDED SCOPE=SPFILE;
            AUDIT ALL BY ACCESS;
            """
            rprint("[green]Auditing enabled (requires restart)[/green]")
        else:
            sql = "ALTER SYSTEM SET AUDIT_TRAIL=NONE SCOPE=SPFILE;"
            rprint("[yellow]Auditing disabled (requires restart)[/yellow]")
        
        success, stdout, stderr = self._run_sql(sql)
        return success
    
    def configure_tde(self, enable=True):
        """Configure Transparent Data Encryption"""
        console.print("\n[bold cyan]Configuring TDE[/bold cyan]\n")
        
        if enable:
            sql = """
            ADMINISTER KEY MANAGEMENT CREATE KEYSTORE '/u01/app/oracle/admin/wallet' IDENTIFIED BY Oracle123;
            ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY Oracle123;
            ADMINISTER KEY MANAGEMENT SET KEY IDENTIFIED BY Oracle123 WITH BACKUP;
            """
            rprint("[green]TDE configured[/green]")
        
        success, stdout, stderr = self._run_sql(sql)
        return success
    
    def create_user(self, username):
        """Create database user"""
        console.print(f"\n[bold cyan]Creating user {username}[/bold cyan]\n")
        
        password = input(f"Password for {username}: ")
        
        sql = f"""
        CREATE USER {username} IDENTIFIED BY {password}
        DEFAULT TABLESPACE USERS
        TEMPORARY TABLESPACE TEMP
        QUOTA UNLIMITED ON USERS;
        
        GRANT CONNECT, RESOURCE TO {username};
        """
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint(f"[green]✓[/green] User {username} created")
            return True
        else:
            rprint(f"[red]✗ Failed:[/red] {stderr}")
            return False
    
    def drop_user(self, username):
        """Drop database user"""
        console.print(f"\n[bold red]Dropping user {username}[/bold red]\n")
        
        sql = f"DROP USER {username} CASCADE;"
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            rprint(f"[green]✓[/green] User {username} dropped")
            return True
        else:
            rprint(f"[red]✗ Failed:[/red] {stderr}")
            return False
    
    def list_users(self):
        """List database users"""
        console.print("\n[bold cyan]Database Users[/bold cyan]\n")
        
        sql = """
        SELECT username, account_status, default_tablespace, created
        FROM dba_users
        WHERE username NOT IN ('SYS','SYSTEM','DBSNMP','SYSMAN','OUTLN')
        ORDER BY created DESC;
        """
        
        success, stdout, stderr = self._run_sql(sql)
        
        if success:
            console.print(stdout)
            return True
        else:
            rprint(f"[red]Error:[/red] {stderr}")
            return False
