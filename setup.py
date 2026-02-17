#!/usr/bin/env python3
"""
OracleDBA - Complete Oracle Database Administration Package
Installation and Management Tool for Oracle 19c on Rocky Linux 8/9
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="oracledba",
    version="1.0.0",
    author="DBA Formation Team",
    author_email="dba@formation.com",
    description="Complete Oracle 19c DBA package with installation, backup, tuning, ASM, RAC and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ELMRABET-Abdelali/oracledba",
    packages=find_packages(exclude=["tests", "docs"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Topic :: Database :: Database Engines/Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    keywords="oracle oracle19c dba database rman dataguard asm rac rocky-linux automation",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "colorama>=0.4.6",
        "pyyaml>=6.0.1",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "paramiko>=3.4.0",
        "jinja2>=3.1.3",
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.8.0",
        ],
        "oracle": [
            "cx_Oracle>=8.3.0",
            "oracledb>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "oradba=oracledba.cli:main",
            "oradba-setup=oracledba.setup_wizard:main",
        ],
    },
    include_package_data=True,
    package_data={
        "oracledba": [
            "scripts/*.sh",
            "scripts/*.sql",
            "configs/*.yaml",
            "configs/*.yml",
            "templates/*.j2",
            "templates/*.sql",
        ],
    },
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/ELMRABET-Abdelali/oracledba/issues",
        "Documentation": "https://github.com/ELMRABET-Abdelali/oracledba/wiki",
        "Source": "https://github.com/ELMRABET-Abdelali/oracledba",
    },
)
