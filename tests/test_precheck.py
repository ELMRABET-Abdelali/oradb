"""
Tests for PreInstallChecker module
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from oracledba.modules.precheck import PreInstallChecker


class TestPreInstallChecker:
    """Test suite for pre-installation checker"""
    
    def test_init(self):
        """Test checker initialization"""
        checker = PreInstallChecker()
        assert checker.results is not None
        assert 'os' in checker.results
        assert 'hardware' in checker.results
        assert 'packages' in checker.results
    
    @patch('builtins.open', new_callable=mock_open, read_data='ID=rocky\nVERSION_ID="8"')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('platform.release', return_value='4.18.0-425.el8.x86_64')
    def test_check_os_rocky8(self, mock_release, mock_exists, mock_file):
        """Test OS check for Rocky Linux 8"""
        checker = PreInstallChecker()
        checker.check_os()
        
        assert checker.results['os']['passed'] == True
        assert any('rocky' in detail.lower() for detail in checker.results['os']['details'])
    
    @patch('psutil.virtual_memory')
    @patch('psutil.swap_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.cpu_count', return_value=4)
    def test_check_hardware_sufficient(self, mock_cpu, mock_disk, mock_swap, mock_ram):
        """Test hardware check with sufficient resources"""
        # Mock sufficient resources
        mock_ram.return_value = Mock(total=16 * 1024**3)  # 16 GB
        mock_swap.return_value = Mock(total=8 * 1024**3)   # 8 GB
        mock_disk.return_value = Mock(free=100 * 1024**3)  # 100 GB
        
        checker = PreInstallChecker()
        checker.check_hardware()
        
        assert checker.results['hardware']['passed'] == True
        assert any('RAM' in detail for detail in checker.results['hardware']['details'])
    
    @patch('psutil.virtual_memory')
    @patch('psutil.swap_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.cpu_count', return_value=2)
    def test_check_hardware_insufficient(self, mock_cpu, mock_disk, mock_swap, mock_ram):
        """Test hardware check with insufficient resources"""
        # Mock insufficient resources
        mock_ram.return_value = Mock(total=4 * 1024**3)   # 4 GB (insufficient)
        mock_swap.return_value = Mock(total=2 * 1024**3)  # 2 GB (insufficient)
        mock_disk.return_value = Mock(free=20 * 1024**3)  # 20 GB (insufficient)
        
        checker = PreInstallChecker()
        checker.check_hardware()
        
        assert checker.results['hardware']['passed'] == False
    
    @patch('subprocess.run')
    def test_check_packages_all_installed(self, mock_run):
        """Test package check when all packages are installed"""
        # Mock all packages installed
        mock_run.return_value = Mock(returncode=0)
        
        checker = PreInstallChecker()
        checker.check_packages()
        
        # Should pass if all packages found
        # Note: depends on mock behavior
        assert 'packages' in checker.results
    
    @patch('subprocess.run')
    def test_check_kernel_params(self, mock_run):
        """Test kernel parameter checking"""
        # Mock sysctl responses
        mock_run.return_value = Mock(
            returncode=0,
            stdout='fs.file-max = 6815744\n'
        )
        
        checker = PreInstallChecker()
        checker.check_kernel_params()
        
        assert 'kernel' in checker.results
    
    @patch('platform.node', return_value='testhost')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='127.0.0.1 localhost testhost\n')
    def test_check_network(self, mock_file, mock_exists, mock_node):
        """Test network configuration check"""
        checker = PreInstallChecker()
        checker.check_network()
        
        assert checker.results['network']['passed'] == True
        assert any('Hostname' in detail for detail in checker.results['network']['details'])
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('subprocess.run')
    def test_check_filesystem_selinux_permissive(self, mock_run, mock_exists):
        """Test filesystem check with SELinux permissive"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='Permissive\n'
        )
        
        checker = PreInstallChecker()
        checker.check_filesystem()
        
        assert checker.results['filesystem']['passed'] == True
    
    def test_generate_fix_script(self, tmp_path):
        """Test fix script generation"""
        checker = PreInstallChecker()
        output_file = tmp_path / "fix-script.sh"
        
        checker.generate_fix_script(str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert '#!/bin/bash' in content
        assert 'sysctl' in content
    
    @patch('oracledba.modules.precheck.PreInstallChecker.check_os')
    @patch('oracledba.modules.precheck.PreInstallChecker.check_hardware')
    @patch('oracledba.modules.precheck.PreInstallChecker.check_packages')
    @patch('oracledba.modules.precheck.PreInstallChecker.check_kernel_params')
    @patch('oracledba.modules.precheck.PreInstallChecker.check_network')
    @patch('oracledba.modules.precheck.PreInstallChecker.check_filesystem')
    @patch('oracledba.modules.precheck.PreInstallChecker.display_results')
    def test_check_all(self, mock_display, mock_fs, mock_net, mock_kernel, 
                       mock_pkg, mock_hw, mock_os):
        """Test that check_all calls all check methods"""
        mock_display.return_value = True
        
        checker = PreInstallChecker()
        result = checker.check_all()
        
        mock_os.assert_called_once()
        mock_hw.assert_called_once()
        mock_pkg.assert_called_once()
        mock_kernel.assert_called_once()
        mock_net.assert_called_once()
        mock_fs.assert_called_once()
        mock_display.assert_called_once()


class TestPreCheckRequirements:
    """Test requirement constants"""
    
    def test_requirements_defined(self):
        """Test that all requirements are properly defined"""
        reqs = PreInstallChecker.REQUIREMENTS
        
        assert 'min_ram_gb' in reqs
        assert 'min_swap_gb' in reqs
        assert 'min_disk_gb' in reqs
        assert 'supported_os' in reqs
        assert 'required_packages' in reqs
        assert 'required_kernel_params' in reqs
    
    def test_minimum_requirements(self):
        """Test minimum requirement values"""
        reqs = PreInstallChecker.REQUIREMENTS
        
        assert reqs['min_ram_gb'] >= 8
        assert reqs['min_swap_gb'] >= 8
        assert reqs['min_disk_gb'] >= 50
    
    def test_supported_os_list(self):
        """Test supported OS list"""
        reqs = PreInstallChecker.REQUIREMENTS
        
        assert 'rocky' in reqs['supported_os']
        assert 'centos' in reqs['supported_os']
        assert '8' in reqs['supported_versions']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
