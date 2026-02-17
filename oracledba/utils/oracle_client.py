"""
Oracle Client utility for database connections
"""

import os
import subprocess


class OracleClient:
    """Simple Oracle client wrapper"""
    
    def __init__(self, oracle_home=None, oracle_sid=None):
        self.oracle_home = oracle_home or os.getenv('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
        self.oracle_sid = oracle_sid or os.getenv('ORACLE_SID', 'GDCPROD')
        self.sqlplus = f"{self.oracle_home}/bin/sqlplus"
    
    def execute_sql(self, sql, as_sysdba=True):
        """Execute SQL command"""
        connect_str = "/ as sysdba" if as_sysdba else "/"
        
        cmd = f"echo \"{sql}\" | {self.sqlplus} -S {connect_str}"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                env={**os.environ, 'ORACLE_HOME': self.oracle_home, 'ORACLE_SID': self.oracle_sid}
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def execute_script(self, script_path, as_sysdba=True):
        """Execute SQL script"""
        connect_str = "/ as sysdba" if as_sysdba else "/"
        
        cmd = f"{self.sqlplus} {connect_str} @{script_path}"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                env={**os.environ, 'ORACLE_HOME': self.oracle_home, 'ORACLE_SID': self.oracle_sid}
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
