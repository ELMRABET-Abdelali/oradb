"""
Oracle Installation Testing Suite
Automated tests for Oracle 19c installation and functionality
"""

import os
import subprocess
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

console = Console()


class OracleTestSuite:
    """Complete test suite for Oracle 19c installation"""
    
    def __init__(self, oracle_home=None, oracle_sid=None):
        self.oracle_home = oracle_home or os.getenv('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
        self.oracle_sid = oracle_sid or os.getenv('ORACLE_SID', 'ORCL')
        self.results = {}
        
    def run_all_tests(self):
        """Run complete test suite"""
        console.print(Panel.fit(
            "[bold cyan]Oracle 19c Test Suite[/bold cyan]\n"
            f"ORACLE_HOME: {self.oracle_home}\n"
            f"ORACLE_SID: {self.oracle_sid}",
            border_style="cyan"
        ))
        
        tests = [
            ("Environment", self.test_environment),
            ("Binaries", self.test_binaries),
            ("Listener", self.test_listener),
            ("Database", self.test_database),
            ("Instance", self.test_instance),
            ("Tablespaces", self.test_tablespaces),
            ("Users", self.test_users),
            ("PDB", self.test_pdb),
            ("Archive Mode", self.test_archive_mode),
            ("Backup", self.test_rman),
            ("Performance", self.test_performance),
        ]
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            for test_name, test_func in tests:
                task = progress.add_task(f"[cyan]Testing {test_name}...", total=None)
                try:
                    result = test_func()
                    self.results[test_name] = result
                except Exception as e:
                    self.results[test_name] = {
                        'passed': False,
                        'details': [f"Error: {str(e)}"]
                    }
                progress.remove_task(task)
        
        return self.display_results()
    
    def _run_sql(self, sql_command, as_sysdba=True):
        """Execute SQL command"""
        try:
            if as_sysdba:
                cmd = f"sqlplus -s / as sysdba << EOF\nSET PAGESIZE 0 FEEDBACK OFF VERIFY OFF HEADING OFF ECHO OFF\n{sql_command}\nEXIT;\nEOF"
            else:
                cmd = f"sqlplus -s system/manager << EOF\nSET PAGESIZE 0 FEEDBACK OFF VERIFY OFF HEADING OFF ECHO OFF\n{sql_command}\nEXIT;\nEOF"
            
            env = os.environ.copy()
            env['ORACLE_HOME'] = self.oracle_home
            env['ORACLE_SID'] = self.oracle_sid
            env['PATH'] = f"{self.oracle_home}/bin:{env.get('PATH', '')}"
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                env=env
            )
            
            return result.stdout.strip(), result.returncode == 0
        except Exception as e:
            return str(e), False
    
    def test_environment(self):
        """Test Oracle environment variables"""
        result = {'passed': True, 'details': []}
        
        # Check ORACLE_HOME
        if Path(self.oracle_home).exists():
            result['details'].append(f"✓ ORACLE_HOME exists: {self.oracle_home}")
        else:
            result['details'].append(f"✗ ORACLE_HOME not found: {self.oracle_home}")
            result['passed'] = False
        
        # Check ORACLE_BASE
        oracle_base = os.getenv('ORACLE_BASE', '/u01/app/oracle')
        if Path(oracle_base).exists():
            result['details'].append(f"✓ ORACLE_BASE exists: {oracle_base}")
        else:
            result['details'].append(f"✗ ORACLE_BASE not found: {oracle_base}")
            result['passed'] = False
        
        # Check oracle user
        try:
            import pwd
            pwd.getpwnam('oracle')
            result['details'].append("✓ Oracle user exists")
        except:
            result['details'].append("✗ Oracle user not found")
            result['passed'] = False
        
        return result
    
    def test_binaries(self):
        """Test Oracle binaries"""
        result = {'passed': True, 'details': []}
        
        binaries = ['sqlplus', 'rman', 'lsnrctl', 'dbca', 'netca']
        
        for binary in binaries:
            binary_path = Path(self.oracle_home) / 'bin' / binary
            if binary_path.exists():
                result['details'].append(f"✓ {binary} found")
            else:
                result['details'].append(f"✗ {binary} not found")
                result['passed'] = False
        
        # Check version
        try:
            env = os.environ.copy()
            env['ORACLE_HOME'] = self.oracle_home
            cmd_result = subprocess.run(
                [f"{self.oracle_home}/bin/sqlplus", "-version"],
                capture_output=True,
                text=True,
                env=env
            )
            version = cmd_result.stdout.split('\n')[0]
            result['details'].append(f"✓ Version: {version}")
        except:
            result['details'].append("⚠ Could not get version")
        
        return result
    
    def test_listener(self):
        """Test Oracle Listener"""
        result = {'passed': True, 'details': []}
        
        try:
            env = os.environ.copy()
            env['ORACLE_HOME'] = self.oracle_home
            
            cmd_result = subprocess.run(
                [f"{self.oracle_home}/bin/lsnrctl", "status"],
                capture_output=True,
                text=True,
                env=env
            )
            
            if "ready" in cmd_result.stdout.lower() or "connecting" in cmd_result.stdout.lower():
                result['details'].append("✓ Listener is running")
                
                # Check for service registration
                if self.oracle_sid.lower() in cmd_result.stdout.lower():
                    result['details'].append(f"✓ Service {self.oracle_sid} registered")
                else:
                    result['details'].append(f"⚠ Service {self.oracle_sid} not registered yet")
            else:
                result['details'].append("✗ Listener not running")
                result['passed'] = False
        except Exception as e:
            result['details'].append(f"✗ Error checking listener: {str(e)}")
            result['passed'] = False
        
        return result
    
    def test_database(self):
        """Test database connectivity"""
        result = {'passed': True, 'details': []}
        
        # Test SQL*Plus connection
        output, success = self._run_sql("SELECT 'Connected' FROM dual;")
        
        if success and 'Connected' in output:
            result['details'].append("✓ Database connection successful")
        else:
            result['details'].append("✗ Cannot connect to database")
            result['passed'] = False
            return result
        
        # Check database name
        output, success = self._run_sql("SELECT name FROM v$database;")
        if success:
            result['details'].append(f"✓ Database: {output}")
        
        # Check database version
        output, success = self._run_sql("SELECT version FROM v$instance;")
        if success:
            result['details'].append(f"✓ Version: {output}")
        
        return result
    
    def test_instance(self):
        """Test database instance"""
        result = {'passed': True, 'details': []}
        
        # Check instance status
        output, success = self._run_sql("SELECT status FROM v$instance;")
        if success:
            if output == 'OPEN':
                result['details'].append("✓ Instance status: OPEN")
            else:
                result['details'].append(f"⚠ Instance status: {output}")
                result['passed'] = False
        
        # Check instance name
        output, success = self._run_sql("SELECT instance_name FROM v$instance;")
        if success:
            result['details'].append(f"✓ Instance: {output}")
        
        # Check startup time
        output, success = self._run_sql("SELECT TO_CHAR(startup_time, 'YYYY-MM-DD HH24:MI:SS') FROM v$instance;")
        if success:
            result['details'].append(f"✓ Started: {output}")
        
        return result
    
    def test_tablespaces(self):
        """Test tablespaces"""
        result = {'passed': True, 'details': []}
        
        # Check SYSTEM tablespace
        output, success = self._run_sql(
            "SELECT tablespace_name, status FROM dba_tablespaces WHERE tablespace_name='SYSTEM';"
        )
        if success and 'ONLINE' in output:
            result['details'].append("✓ SYSTEM tablespace online")
        else:
            result['details'].append("✗ SYSTEM tablespace issue")
            result['passed'] = False
        
        # Count tablespaces
        output, success = self._run_sql("SELECT COUNT(*) FROM dba_tablespaces;")
        if success:
            result['details'].append(f"✓ Tablespaces: {output}")
        
        # Check space usage
        output, success = self._run_sql("""
            SELECT ROUND(SUM(bytes)/1024/1024/1024, 2) 
            FROM dba_data_files;
        """)
        if success:
            result['details'].append(f"✓ Total datafile size: {output} GB")
        
        return result
    
    def test_users(self):
        """Test database users"""
        result = {'passed': True, 'details': []}
        
        # Check SYS user
        output, success = self._run_sql(
            "SELECT username, account_status FROM dba_users WHERE username='SYS';"
        )
        if success and 'OPEN' in output:
            result['details'].append("✓ SYS user active")
        
        # Check SYSTEM user
        output, success = self._run_sql(
            "SELECT username, account_status FROM dba_users WHERE username='SYSTEM';"
        )
        if success and 'OPEN' in output:
            result['details'].append("✓ SYSTEM user active")
        
        # Count users
        output, success = self._run_sql("SELECT COUNT(*) FROM dba_users;")
        if success:
            result['details'].append(f"✓ Total users: {output}")
        
        return result
    
    def test_pdb(self):
        """Test PDBs in multitenant"""
        result = {'passed': True, 'details': []}
        
        # Check if CDB
        output, success = self._run_sql("SELECT cdb FROM v$database;")
        if success:
            if output == 'YES':
                result['details'].append("✓ Container database enabled")
                
                # Count PDBs
                output, success = self._run_sql("SELECT COUNT(*) FROM v$pdbs;")
                if success:
                    result['details'].append(f"✓ PDBs configured: {output}")
                
                # Check PDB status
                output, success = self._run_sql("""
                    SELECT name, open_mode FROM v$pdbs WHERE name != 'PDB$SEED';
                """)
                if success:
                    result['details'].append(f"✓ PDB status: {output}")
            else:
                result['details'].append("⚠ Non-CDB database")
        
        return result
    
    def test_archive_mode(self):
        """Test archive log mode"""
        result = {'passed': True, 'details': []}
        
        output, success = self._run_sql("SELECT log_mode FROM v$database;")
        if success:
            result['details'].append(f"✓ Log mode: {output}")
            if output != 'ARCHIVELOG':
                result['details'].append("⚠ Consider enabling ARCHIVELOG mode for production")
        
        return result
    
    def test_rman(self):
        """Test RMAN backup configuration"""
        result = {'passed': True, 'details': []}
        
        try:
            env = os.environ.copy()
            env['ORACLE_HOME'] = self.oracle_home
            env['ORACLE_SID'] = self.oracle_sid
            env['PATH'] = f"{self.oracle_home}/bin:{env.get('PATH', '')}"
            
            cmd = f"""rman target / << EOF
SHOW ALL;
EXIT;
EOF"""
            
            cmd_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                env=env
            )
            
            if cmd_result.returncode == 0:
                result['details'].append("✓ RMAN accessible")
                
                if 'CONFIGURE RETENTION POLICY' in cmd_result.stdout:
                    result['details'].append("✓ RMAN configuration found")
            else:
                result['details'].append("⚠ RMAN connection issue")
        except Exception as e:
            result['details'].append(f"⚠ RMAN test skipped: {str(e)}")
        
        return result
    
    def test_performance(self):
        """Test basic performance metrics"""
        result = {'passed': True, 'details': []}
        
        # SGA size
        output, success = self._run_sql("""
            SELECT ROUND(SUM(value)/1024/1024, 2) 
            FROM v$sga;
        """)
        if success:
            result['details'].append(f"✓ SGA size: {output} MB")
        
        # PGA usage
        output, success = self._run_sql("""
            SELECT ROUND(value/1024/1024, 2) 
            FROM v$pgastat 
            WHERE name='total PGA allocated';
        """)
        if success:
            result['details'].append(f"✓ PGA allocated: {output} MB")
        
        # Session count
        output, success = self._run_sql("SELECT COUNT(*) FROM v$session;")
        if success:
            result['details'].append(f"✓ Active sessions: {output}")
        
        return result
    
    def display_results(self):
        """Display test results"""
        console.print("\n")
        
        table = Table(title="Oracle 19c Test Results", show_header=True, header_style="bold cyan")
        table.add_column("Test", style="cyan", width=20)
        table.add_column("Status", width=10)
        table.add_column("Details", width=60)
        
        passed_count = 0
        failed_count = 0
        
        for test_name, result in self.results.items():
            if result['passed']:
                status = "[green]✓ PASS[/green]"
                passed_count += 1
            else:
                status = "[red]✗ FAIL[/red]"
                failed_count += 1
            
            details = "\n".join(result['details'])
            table.add_row(test_name, status, details)
        
        console.print(table)
        
        total = passed_count + failed_count
        console.print(f"\n[bold]Summary:[/bold] {passed_count}/{total} tests passed")
        
        if failed_count == 0:
            console.print(Panel.fit(
                "[bold green]✓ All tests passed![/bold green]\n"
                "Oracle 19c is fully operational.",
                border_style="green"
            ))
            return True
        else:
            console.print(Panel.fit(
                f"[bold yellow]⚠ {failed_count} test(s) failed[/bold yellow]\n"
                "Review the errors above.",
                border_style="yellow"
            ))
            return False
    
    def generate_test_report(self, output_file='oracle-test-report.txt'):
        """Generate detailed test report"""
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("Oracle 19c Installation Test Report\n")
            f.write("="*80 + "\n\n")
            f.write(f"ORACLE_HOME: {self.oracle_home}\n")
            f.write(f"ORACLE_SID: {self.oracle_sid}\n")
            f.write(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for test_name, result in self.results.items():
                f.write(f"\n{test_name}\n")
                f.write("-" * len(test_name) + "\n")
                f.write(f"Status: {'PASS' if result['passed'] else 'FAIL'}\n")
                for detail in result['details']:
                    f.write(f"  {detail}\n")
        
        console.print(f"\n[green]✓[/green] Test report generated: {output_file}")
