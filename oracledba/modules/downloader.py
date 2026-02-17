"""
Oracle Software Downloader
Handles downloading Oracle 19c binaries and patches
"""

import os
import requests
import hashlib
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, DownloadColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich import print as rprint

console = Console()


class OracleDownloader:
    """Download Oracle software from various sources"""
    
    # Oracle 19c Software Information
    ORACLE_19C = {
        'version': '19.3.0.0.0',
        'linux_x64': {
            'filename': 'LINUX.X64_193000_db_home.zip',
            'size': 2889184573,  # bytes
            'md5': 'ba8329c757133da313ed3b6d7f86c5ac',
        },
        'grid_19c': {
            'filename': 'LINUX.X64_193000_grid_home.zip',
            'size': 2989041158,
            'md5': 'e96ec0427e8514856e5e0333e07e097f',
        }
    }
    
    def __init__(self, download_dir='/opt/oracle/install'):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_from_url(self, url, filename=None, verify_md5=None):
        """
        Download file from direct URL
        
        Args:
            url: Direct download URL
            filename: Output filename (optional)
            verify_md5: Expected MD5 hash for verification
        
        Returns:
            Path to downloaded file
        """
        if not filename:
            filename = url.split('/')[-1]
        
        output_path = self.download_dir / filename
        
        # Check if already downloaded
        if output_path.exists():
            if verify_md5:
                console.print(f"[yellow]File exists, verifying...[/yellow]")
                if self._verify_md5(output_path, verify_md5):
                    console.print(f"[green]✓[/green] File already downloaded and verified: {output_path}")
                    return output_path
                else:
                    console.print(f"[yellow]MD5 mismatch, re-downloading...[/yellow]")
                    output_path.unlink()
            else:
                console.print(f"[yellow]File exists:[/yellow] {output_path}")
                return output_path
        
        # Download with progress bar
        console.print(f"\n[cyan]Downloading:[/cyan] {filename}")
        console.print(f"[cyan]URL:[/cyan] {url}")
        
        try:
            with requests.get(url, stream=True, timeout=30) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                
                with Progress(
                    "[progress.description]{task.description}",
                    BarColumn(),
                    TaskProgressColumn(),
                    DownloadColumn(),
                    TimeRemainingColumn(),
                ) as progress:
                    task = progress.add_task(f"[cyan]Downloading...", total=total_size)
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                progress.update(task, advance=len(chunk))
            
            console.print(f"[green]✓[/green] Download complete: {output_path}")
            
            # Verify MD5 if provided
            if verify_md5:
                if self._verify_md5(output_path, verify_md5):
                    console.print(f"[green]✓[/green] MD5 verification passed")
                else:
                    console.print(f"[red]✗[/red] MD5 verification failed!")
                    output_path.unlink()
                    return None
            
            return output_path
        
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗[/red] Download failed: {str(e)}")
            if output_path.exists():
                output_path.unlink()
            return None
    
    def download_oracle_19c(self, component='database', custom_url=None):
        """
        Download Oracle 19c software
        
        Args:
            component: 'database' or 'grid'
            custom_url: Custom download URL (if not using Oracle.com)
        
        Returns:
            Path to downloaded file
        """
        if component == 'database':
            info = self.ORACLE_19C['linux_x64']
        elif component == 'grid':
            info = self.ORACLE_19C['grid_19c']
        else:
            console.print(f"[red]✗[/red] Unknown component: {component}")
            return None
        
        filename = info['filename']
        md5_hash = info['md5']
        
        if custom_url:
            # Use custom URL
            return self.download_from_url(custom_url, filename, md5_hash)
        else:
            # Show instructions for Oracle.com download
            self._show_oracle_download_instructions(component)
            
            # Check if user already placed the file
            file_path = self.download_dir / filename
            if file_path.exists():
                console.print(f"\n[green]✓[/green] Found: {file_path}")
                if self._verify_md5(file_path, md5_hash):
                    console.print(f"[green]✓[/green] MD5 verification passed")
                    return file_path
                else:
                    console.print(f"[red]✗[/red] MD5 verification failed!")
                    return None
            else:
                console.print(f"\n[yellow]⚠[/yellow] File not found: {file_path}")
                return None
    
    def _show_oracle_download_instructions(self, component):
        """Show instructions for downloading from Oracle.com"""
        console.print("\n" + "="*80)
        console.print("[bold cyan]Oracle Software Download Instructions[/bold cyan]")
        console.print("="*80 + "\n")
        
        console.print("Due to Oracle licensing, you must download the software manually:\n")
        
        console.print("[bold]Step 1:[/bold] Go to Oracle Technology Network:")
        console.print("  https://www.oracle.com/database/technologies/oracle-database-software-downloads.html\n")
        
        console.print("[bold]Step 2:[/bold] Accept the license agreement\n")
        
        if component == 'database':
            console.print("[bold]Step 3:[/bold] Download:")
            console.print(f"  • Oracle Database 19c (19.3) for Linux x86-64")
            console.print(f"  • File: {self.ORACLE_19C['linux_x64']['filename']}")
        elif component == 'grid':
            console.print("[bold]Step 3:[/bold] Download:")
            console.print(f"  • Oracle Grid Infrastructure 19c (19.3) for Linux x86-64")
            console.print(f"  • File: {self.ORACLE_19C['grid_19c']['filename']}")
        
        console.print(f"\n[bold]Step 4:[/bold] Place the downloaded file here:")
        console.print(f"  {self.download_dir}/")
        
        console.print("\n[bold]Alternative:[/bold] Use wget with Oracle SSO credentials:")
        console.print(f"  wget --user=YOUR_EMAIL --ask-password \\")
        console.print(f"    --output-document={self.download_dir}/{self.ORACLE_19C['linux_x64']['filename']} \\")
        console.print(f"    'DOWNLOAD_URL_FROM_ORACLE'\n")
        
        console.print("="*80 + "\n")
    
    def _verify_md5(self, file_path, expected_md5):
        """Verify MD5 checksum of file"""
        console.print(f"[yellow]→[/yellow] Verifying MD5 checksum...")
        
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5_hash.update(chunk)
        
        calculated_md5 = md5_hash.hexdigest()
        
        if calculated_md5 == expected_md5:
            return True
        else:
            console.print(f"[red]Expected:[/red] {expected_md5}")
            console.print(f"[red]Got:[/red]      {calculated_md5}")
            return False
    
    def download_patches(self, patch_numbers=None):
        """
        Download Oracle patches
        
        Args:
            patch_numbers: List of patch numbers to download
        
        Note: Requires My Oracle Support (MOS) access
        """
        console.print("\n[bold yellow]Patch Download[/bold yellow]")
        console.print("\nTo download Oracle patches, you need:")
        console.print("1. My Oracle Support (MOS) account")
        console.print("2. Use the official patch download tool\n")
        
        if patch_numbers:
            console.print("Requested patches:")
            for patch in patch_numbers:
                console.print(f"  • {patch}")
                console.print(f"    URL: https://updates.oracle.com/ARULink/PatchDetails/process_form?patch_num={patch}")
        
        console.print("\n[bold]Alternative:[/bold] Use getMOSPatch.sh script")
        console.print("  https://github.com/MarisElsins/getMOSPatch\n")
    
    def extract_oracle_zip(self, zip_file, extract_to=None):
        """
        Extract Oracle ZIP file to ORACLE_HOME
        
        Args:
            zip_file: Path to ZIP file
            extract_to: Target directory (defaults to ORACLE_HOME)
        
        Returns:
            Path to extracted location
        """
        import zipfile
        
        if not extract_to:
            extract_to = os.getenv('ORACLE_HOME', '/u01/app/oracle/product/19.3.0/dbhome_1')
        
        extract_path = Path(extract_to)
        extract_path.mkdir(parents=True, exist_ok=True)
        
        console.print(f"\n[cyan]Extracting:[/cyan] {zip_file}")
        console.print(f"[cyan]To:[/cyan] {extract_path}")
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Get total number of files
                total_files = len(zip_ref.namelist())
                
                with Progress(
                    "[progress.description]{task.description}",
                    BarColumn(),
                    TaskProgressColumn(),
                ) as progress:
                    task = progress.add_task("[cyan]Extracting...", total=total_files)
                    
                    for file in zip_ref.namelist():
                        zip_ref.extract(file, extract_path)
                        progress.update(task, advance=1)
            
            console.print(f"[green]✓[/green] Extraction complete: {extract_path}")
            return extract_path
        
        except Exception as e:
            console.print(f"[red]✗[/red] Extraction failed: {str(e)}")
            return None
    
    def prepare_installation(self, component='database'):
        """
        Complete preparation: download and extract
        
        Args:
            component: 'database' or 'grid'
        
        Returns:
            Path to ORACLE_HOME ready for installation
        """
        console.print(Panel.fit(
            f"[bold cyan]Preparing Oracle 19c {component.title()} Installation[/bold cyan]",
            border_style="cyan"
        ))
        
        # Download
        zip_file = self.download_oracle_19c(component)
        
        if not zip_file:
            console.print("\n[red]✗[/red] Cannot proceed without Oracle software")
            return None
        
        # Extract
        oracle_home = self.extract_oracle_zip(zip_file)
        
        if oracle_home:
            console.print(Panel.fit(
                f"[bold green]✓ Ready for Installation[/bold green]\n"
                f"ORACLE_HOME: {oracle_home}\n"
                f"Next: Run installation script",
                border_style="green"
            ))
        
        return oracle_home


def download_from_oci_bucket(bucket_url, filename, output_dir='/opt/oracle/install'):
    """
    Download Oracle software from OCI Object Storage bucket
    
    Args:
        bucket_url: Pre-authenticated URL from OCI bucket
        filename: Filename to save as
        output_dir: Output directory
    
    Example:
        download_from_oci_bucket(
            'https://objectstorage.us-phoenix-1.oraclecloud.com/p/xxx/n/xxx/b/oracle-software/o/db19c.zip',
            'LINUX.X64_193000_db_home.zip'
        )
    """
    downloader = OracleDownloader(output_dir)
    return downloader.download_from_url(bucket_url, filename)
