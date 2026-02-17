"""
Oracle Response File Templates
For silent installation of Oracle 19c
"""

# Database Software Installation Response File
DB_INSTALL_RSP = """####################################################################
## Oracle Database 19c - Silent Installation Response File
####################################################################

oracle.install.responseFileVersion=/oracle/install/rspfmt_dbinstall_response_schema_v19.0.0

# Inventory directory location
INVENTORY_LOCATION={{ inventory_location }}

# Oracle base directory
UNIX_GROUP_NAME={{ oracle_group }}

# Oracle Home directory
ORACLE_HOME={{ oracle_home }}

# Oracle Base directory
ORACLE_BASE={{ oracle_base }}

# Installation Edition
oracle.install.db.InstallEdition={{ edition }}

# Database type: GENERAL_PURPOSE/DATA_WAREHOUSE/HIGH_PERFORMANCE
oracle.install.db.OSDBA_GROUP={{ dba_group }}
oracle.install.db.OSOPER_GROUP={{ oper_group }}
oracle.install.db.OSBACKUPDBA_GROUP={{ backupdba_group }}
oracle.install.db.OSDGDBA_GROUP={{ dgdba_group }}
oracle.install.db.OSKMDBA_GROUP={{ kmdba_group }}
oracle.install.db.OSRACDBA_GROUP={{ racdba_group }}

# Root script execution configuration (true/false)
oracle.install.db.rootconfig.executeRootScript=false

# Automatic Security Updates
oracle.installer.autoupdates.option=SKIP_UPDATES

# Decline Security Updates
DECLINE_SECURITY_UPDATES=true
"""

# Database Creation Response File (DBCA)
DBCA_RSP = """####################################################################
## Oracle Database 19c - DBCA Response File
####################################################################

responseFileVersion=/oracle/assistants/dbca/dbca_19.0.0

# Database General Options
gdbName={{ db_name }}
sid={{ sid }}
databaseConfigType={{ db_type }}
templateName={{ template }}

# Database Storage
storageType={{ storage_type }}
datafileDestination={{ data_file_dest }}
recoveryAreaDestination={{ fra_dest }}
recoveryAreaSize={{ fra_size }}

# Database Memory
totalMemory={{ total_memory }}
memoryPercentage={{ memory_percentage }}

# Database Character Set
characterSet={{ charset }}
nationalCharacterSet={{ ncharset }}

# Database Listener
listeners={{ listener }}

# Database Variables
variables={{ variables }}

# Init Parameters
initParams={{ init_params }}

# Sample Schemas
sampleSchema={{ sample_schema }}

# Database Creation Options
createAsContainerDatabase={{ is_cdb }}

{% if is_cdb == "true" %}
numberOfPDBs={{ pdb_count }}
pdbName={{ pdb_name }}
pdbAdminPassword={{ pdb_admin_pwd }}
{% endif %}

# Database Passwords
sysPassword={{ sys_password }}
systemPassword={{ system_password }}

# Automatic Memory Management
automaticMemoryManagement={{ auto_memory_mgmt }}

# Database Options
datafileJarLocation={ORACLE_HOME}/assistants/dbca/templates/
"""

# Listener Configuration Response File (NETCA)
NETCA_RSP = """####################################################################
## Oracle Database 19c - Listener Configuration Response File
####################################################################

[GENERAL]
RESPONSEFILE_VERSION="{{ responsefile_version }}"
CREATE_TYPE="{{ create_type }}"

[oracle.net.ca]
INSTALLED_COMPONENTS={"server","net8","javavm"}
INSTALL_TYPE="{{ install_type }}"
LISTENER_NUMBER={{ listener_number }}
LISTENER_NAMES={{ listener_names }}
LISTENER_PROTOCOLS={{ listener_protocols }}
LISTENER_START="{{ listener_start }}"
NAMING_METHODS={{ naming_methods }}
NSN_NUMBER=1
NSN_NAMES={{ nsn_names }}
NSN_SERVICE={{ nsn_service }}
NSN_PROTOCOLS={{ nsn_protocols }}
"""

# Default Configuration Values
DEFAULT_CONFIG = {
    'DB_INSTALL': {
        'inventory_location': '/u01/app/oraInventory',
        'oracle_group': 'oinstall',
        'oracle_home': '/u01/app/oracle/product/19.3.0/dbhome_1',
        'oracle_base': '/u01/app/oracle',
        'edition': 'EE',  # EE/SE2
        'dba_group': 'dba',
        'oper_group': 'oper',
        'backupdba_group': 'backupdba',
        'dgdba_group': 'dgdba',
        'kmdba_group': 'kmdba',
        'racdba_group': 'racdba',
    },
    'DBCA': {
        'db_name': 'ORCL',
        'sid': 'ORCL',
        'db_type': 'MULTIPURPOSE',  # MULTIPURPOSE/DATA_WAREHOUSING/OLTP
        'template': 'General_Purpose.dbc',
        'storage_type': 'FS',  # FS/ASM
        'data_file_dest': '/u01/app/oracle/oradata',
        'fra_dest': '/u01/app/oracle/fast_recovery_area',
        'fra_size': '10240',  # MB
        'total_memory': '2048',  # MB
        'memory_percentage': '40',
        'charset': 'AL32UTF8',
        'ncharset': 'AL16UTF16',
        'listener': 'LISTENER',
        'variables': 'ORACLE_BASE_HOME={ORACLE_BASE}/homes/OraDB19Home1,DB_UNIQUE_NAME={DB_UNIQUE_NAME},ORACLE_HOME={ORACLE_HOME},PDB_NAME=,DB_NAME={DB_NAME},ORACLE_BASE={ORACLE_BASE},SID={SID}',
        'init_params': 'undo_tablespace=UNDOTBS1,sga_target=1536MB,db_block_size=8192BYTES,pga_aggregate_target=512MB,nls_language=AMERICAN,dispatchers=(PROTOCOL=TCP) (SERVICE={SID}XDB),diagnostic_dest={ORACLE_BASE},control_files=("{ORACLE_BASE}/oradata/{DB_UNIQUE_NAME}/control01.ctl","{ORACLE_BASE}/oradata/{DB_UNIQUE_NAME}/control02.ctl"),audit_file_dest={ORACLE_BASE}/admin/{DB_UNIQUE_NAME}/adump,processes=320,audit_trail=db,db_name={DB_NAME},open_cursors=300,compatible=19.0.0,db_recovery_file_dest_size=10240MB,db_recovery_file_dest={ORACLE_BASE}/fast_recovery_area/{DB_UNIQUE_NAME},remote_login_passwordfile=EXCLUSIVE',
        'sample_schema': 'false',
        'is_cdb': 'true',
        'pdb_count': '1',
        'pdb_name': 'ORCLPDB',
        'pdb_admin_pwd': 'Oracle123',
        'sys_password': 'Oracle123',
        'system_password': 'Oracle123',
        'auto_memory_mgmt': 'true',
    },
    'NETCA': {
        'responsefile_version': '19.0',
        'create_type': 'LISTENER',
        'install_type': 'typical',
        'listener_number': '1',
        'listener_names': '{"LISTENER"}',
        'listener_protocols': '{"TCP;1521"}',
        'listener_start': 'LISTENER',
        'naming_methods': '{"TNSNAMES","ONAMES","HOSTNAME"}',
        'nsn_names': '{"EXTPROC_CONNECTION_DATA"}',
        'nsn_service': '{"PLSExtProc"}',
        'nsn_protocols': '{"TCP;HOSTNAME;1521"}',
    }
}


def generate_response_file(template_name, config=None, output_file=None):
    """
    Generate response file from template
    
    Args:
        template_name: 'DB_INSTALL', 'DBCA', or 'NETCA'
        config: Dictionary with configuration values
        output_file: Output file path (optional)
    
    Returns:
        Generated response file content
    """
    from jinja2 import Template
    
    # Get template
    templates = {
        'DB_INSTALL': DB_INSTALL_RSP,
        'DBCA': DBCA_RSP,
        'NETCA': NETCA_RSP,
    }
    
    if template_name not in templates:
        raise ValueError(f"Unknown template: {template_name}")
    
    # Merge with defaults
    final_config = DEFAULT_CONFIG.get(template_name, {}).copy()
    if config:
        final_config.update(config)
    
    # Render template
    template = Template(templates[template_name])
    content = template.render(**final_config)
    
    # Write to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(content)
    
    return content


def generate_all_response_files(config_file=None, output_dir='/tmp'):
    """
    Generate all response files needed for Oracle installation
    
    Args:
        config_file: YAML config file with custom values
        output_dir: Directory to write response files
    
    Returns:
        Dictionary with file paths
    """
    import yaml
    from pathlib import Path
    
    # Load config
    config = {}
    if config_file and Path(config_file).exists():
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    
    # Generate files
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files = {}
    
    # DB Install
    db_install_file = output_dir / 'db_install.rsp'
    generate_response_file(
        'DB_INSTALL',
        config.get('oracle', {}),
        str(db_install_file)
    )
    files['db_install'] = str(db_install_file)
    
    # DBCA
    dbca_file = output_dir / 'dbca.rsp'
    generate_response_file(
        'DBCA',
        config.get('database', {}),
        str(dbca_file)
    )
    files['dbca'] = str(dbca_file)
    
    # NETCA
    netca_file = output_dir / 'netca.rsp'
    generate_response_file(
        'NETCA',
        config.get('network', {}),
        str(netca_file)
    )
    files['netca'] = str(netca_file)
    
    return files
