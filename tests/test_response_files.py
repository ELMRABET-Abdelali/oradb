"""
Tests for Response Files Generator
"""

import pytest
from pathlib import Path
from oracledba.modules.response_files import (
    generate_response_file,
    generate_all_response_files,
    DEFAULT_CONFIG
)


class TestResponseFileGeneration:
    """Test response file generation"""
    
    def test_generate_db_install_default(self, tmp_path):
        """Test DB install response file with defaults"""
        output_file = tmp_path / "db_install.rsp"
        content = generate_response_file('DB_INSTALL', output_file=str(output_file))
        
        assert output_file.exists()
        assert 'oracle.install.responseFileVersion' in content
        assert 'ORACLE_HOME' in content
        assert 'ORACLE_BASE' in content
    
    def test_generate_dbca_default(self, tmp_path):
        """Test DBCA response file with defaults"""
        output_file = tmp_path / "dbca.rsp"
        content = generate_response_file('DBCA', output_file=str(output_file))
        
        assert output_file.exists()
        assert 'gdbName' in content
        assert 'sid' in content
        assert 'characterSet' in content
    
    def test_generate_netca_default(self, tmp_path):
        """Test NETCA response file with defaults"""
        output_file = tmp_path / "netca.rsp"
        content = generate_response_file('NETCA', output_file=str(output_file))
        
        assert output_file.exists()
        assert 'LISTENER' in content
        assert 'RESPONSEFILE_VERSION' in content
    
    def test_generate_with_custom_config(self, tmp_path):
        """Test generation with custom configuration"""
        custom_config = {
            'oracle_home': '/custom/oracle/home',
            'oracle_base': '/custom/oracle',
        }
        
        output_file = tmp_path / "custom.rsp"
        content = generate_response_file('DB_INSTALL', custom_config, str(output_file))
        
        assert '/custom/oracle/home' in content
        assert '/custom/oracle' in content
    
    def test_unknown_template_raises_error(self):
        """Test that unknown template raises ValueError"""
        with pytest.raises(ValueError):
            generate_response_file('UNKNOWN_TEMPLATE')
    
    def test_generate_all_files(self, tmp_path):
        """Test generating all response files"""
        files = generate_all_response_files(output_dir=str(tmp_path))
        
        assert 'db_install' in files
        assert 'dbca' in files
        assert 'netca' in files
        
        # Check all files exist
        for file_path in files.values():
            assert Path(file_path).exists()
    
    def test_db_install_required_fields(self, tmp_path):
        """Test DB install file contains required fields"""
        output_file = tmp_path / "db_install.rsp"
        content = generate_response_file('DB_INSTALL', output_file=str(output_file))
        
        required_fields = [
            'INVENTORY_LOCATION',
            'UNIX_GROUP_NAME',
            'ORACLE_HOME',
            'ORACLE_BASE',
            'oracle.install.db.InstallEdition',
        ]
        
        for field in required_fields:
            assert field in content, f"Missing required field: {field}"
    
    def test_dbca_multitenant_config(self, tmp_path):
        """Test DBCA with multitenant configuration"""
        config = {
            'is_cdb': 'true',
            'pdb_count': '2',
            'pdb_name': 'TESTPDB',
        }
        
        output_file = tmp_path / "dbca_mt.rsp"
        content = generate_response_file('DBCA', config, str(output_file))
        
        assert 'createAsContainerDatabase=true' in content
        assert 'numberOfPDBs=2' in content
        assert 'pdbName=TESTPDB' in content
    
    def test_dbca_non_cdb_config(self, tmp_path):
        """Test DBCA with non-CDB configuration"""
        config = {
            'is_cdb': 'false',
        }
        
        output_file = tmp_path / "dbca_non_cdb.rsp"
        content = generate_response_file('DBCA', config, str(output_file))
        
        assert 'createAsContainerDatabase=false' in content


class TestDefaultConfiguration:
    """Test default configuration values"""
    
    def test_default_config_structure(self):
        """Test default config has all sections"""
        assert 'DB_INSTALL' in DEFAULT_CONFIG
        assert 'DBCA' in DEFAULT_CONFIG
        assert 'NETCA' in DEFAULT_CONFIG
    
    def test_db_install_defaults(self):
        """Test DB install default values"""
        config = DEFAULT_CONFIG['DB_INSTALL']
        
        assert config['oracle_group'] == 'oinstall'
        assert config['dba_group'] == 'dba'
        assert config['edition'] in ['EE', 'SE2']
    
    def test_dbca_defaults(self):
        """Test DBCA default values"""
        config = DEFAULT_CONFIG['DBCA']
        
        assert config['charset'] == 'AL32UTF8'
        assert config['storage_type'] in ['FS', 'ASM']
        assert config['auto_memory_mgmt'] in ['true', 'false']
    
    def test_netca_defaults(self):
        """Test NETCA default values"""
        config = DEFAULT_CONFIG['NETCA']
        
        assert 'listener_number' in config
        assert 'listener_port' not in config or config.get('listener_port', 1521) == 1521


class TestResponseFileContent:
    """Test response file content validity"""
    
    def test_no_jinja_syntax_in_output(self, tmp_path):
        """Test that Jinja2 syntax is properly rendered"""
        output_file = tmp_path / "test.rsp"
        content = generate_response_file('DB_INSTALL', output_file=str(output_file))
        
        # Should not contain Jinja2 syntax
        assert '{{' not in content
        assert '}}' not in content
        assert '{%' not in content
        assert '%}' not in content
    
    def test_all_variables_substituted(self, tmp_path):
        """Test that all variables are substituted"""
        output_file = tmp_path / "test.rsp"
        content = generate_response_file('DBCA', output_file=str(output_file))
        
        # Check for proper substitution
        assert 'AL32UTF8' in content  # charset
        assert 'ORCL' in content  # default db name
    
    def test_file_is_writable(self, tmp_path):
        """Test that generated files are writable"""
        output_file = tmp_path / "writable.rsp"
        generate_response_file('DB_INSTALL', output_file=str(output_file))
        
        # Try to write to it
        with open(output_file, 'a') as f:
            f.write('\n# Test comment\n')
        
        # Verify content was added
        content = output_file.read_text()
        assert '# Test comment' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
