"""
PyTest Configuration and Fixtures
"""

import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_oracle_home(tmp_path):
    """Create a temporary ORACLE_HOME directory structure"""
    oracle_home = tmp_path / "oracle" / "product" / "19c" / "dbhome_1"
    oracle_home.mkdir(parents=True)
    
    # Create bin directory with mock executables
    bin_dir = oracle_home / "bin"
    bin_dir.mkdir()
    
    for binary in ['sqlplus', 'rman', 'lsnrctl', 'dbca', 'netca']:
        binary_path = bin_dir / binary
        binary_path.touch()
        binary_path.chmod(0o755)
    
    return str(oracle_home)


@pytest.fixture
def temp_oracle_base(tmp_path):
    """Create a temporary ORACLE_BASE directory structure"""
    oracle_base = tmp_path / "app" / "oracle"
    oracle_base.mkdir(parents=True)
    
    # Create subdirectories
    (oracle_base / "oradata").mkdir()
    (oracle_base / "fast_recovery_area").mkdir()
    (oracle_base / "admin").mkdir()
    
    return str(oracle_base)


@pytest.fixture
def mock_config_file(tmp_path):
    """Create a mock configuration YAML file"""
    config_content = """
oracle:
  version: "19c"
  edition: "EE"
  base: "/u01/app/oracle"
  home: "/u01/app/oracle/product/19.3.0/dbhome_1"
  oracle_group: "oinstall"
  dba_group: "dba"

database:
  db_name: "TESTDB"
  sid: "TESTDB"
  pdb_name: "TESTPDB"
  charset: "AL32UTF8"
  memory_gb: 2

system:
  oracle_user: "oracle"

network:
  listener_port: 1521
"""
    config_file = tmp_path / "test_config.yml"
    config_file.write_text(config_content)
    return str(config_file)


@pytest.fixture
def mock_oracle_env(temp_oracle_home):
    """Set Oracle environment variables"""
    old_env = os.environ.copy()
    
    os.environ['ORACLE_HOME'] = temp_oracle_home
    os.environ['ORACLE_SID'] = 'TESTDB'
    os.environ['ORACLE_BASE'] = str(Path(temp_oracle_home).parent.parent.parent)
    os.environ['PATH'] = f"{temp_oracle_home}/bin:{os.environ.get('PATH', '')}"
    
    yield
    
    # Restore environment
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def mock_scripts_dir(tmp_path):
    """Create a mock scripts directory"""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    # Create mock scripts
    script_names = [
        'tp01-system-readiness.sh',
        'tp02-installation-binaire.sh',
        'tp03-creation-instance.sh',
    ]
    
    for script_name in script_names:
        script_path = scripts_dir / script_name
        script_path.write_text('#!/bin/bash\necho "Mock script"\nexit 0\n')
        script_path.chmod(0o755)
    
    return str(scripts_dir)


@pytest.fixture
def sample_oracle_zip(tmp_path):
    """Create a sample Oracle ZIP file (empty)"""
    import zipfile
    
    zip_path = tmp_path / "LINUX.X64_193000_db_home.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        # Add some fake files
        zf.writestr('install/oracle_install.sh', '#!/bin/bash\necho "Oracle Install"\n')
        zf.writestr('runInstaller', '#!/bin/bash\necho "Run Installer"\n')
    
    return str(zip_path)


@pytest.fixture(autouse=True)
def reset_env_after_test():
    """Reset environment after each test"""
    yield
    # Cleanup happens automatically


@pytest.fixture
def console_capture(monkeypatch):
    """Capture console output"""
    from io import StringIO
    import sys
    
    captured = StringIO()
    monkeypatch.setattr(sys, 'stdout', captured)
    
    yield captured
    
    # Reset
    sys.stdout = sys.__stdout__


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_oracle: marks tests that require Oracle installation"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    skip_slow = pytest.mark.skip(reason="use --runslow option to run")
    skip_integration = pytest.mark.skip(reason="integration tests not enabled")
    
    for item in items:
        if "slow" in item.keywords and not config.getoption("--runslow", default=False):
            item.add_marker(skip_slow)
        if "integration" in item.keywords and not config.getoption("--integration", default=False):
            item.add_marker(skip_integration)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--integration", action="store_true", default=False, help="run integration tests"
    )
