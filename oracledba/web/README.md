# OracleDBA Web GUI - README

## 🌐 Web GUI Added Successfully

The oracledba package now includes a complete Flask-based web interface!

### Quick Start

```bash
# Install GUI dependencies
pip install -r requirements-gui.txt

# Start web server on port 5000
oradba install gui

# Or with custom port
oradba install gui --port 8080 --host 0.0.0.0
```

### Access

- **URL:** http://localhost:5000
- **Username:** admin
- **Password:** admin123 (you'll be forced to change it on first login)

### Features

- ✅ **Dashboard** - Real-time Oracle status monitoring
- ✅ **Database Management** - Create, start, stop databases
- ✅ **Storage** - Tablespaces, datafiles, redo logs
- ✅ **Security** - Users, roles, privileges, audit
- ✅ **Backups** - RMAN, Flashback, archive logs
- ✅ **Cluster** - RAC, ASM, NFS configuration
- ✅ **Terminal** - Execute oradba commands via browser
- ✅ **Installation Wizard** - One-click Oracle 19c setup

### Security

- PBKDF2-SHA256 password hashing with 100,000 iterations
- Session management with auto-timeout
- Admin and user roles
- Mandatory password change on first login

### Files Added

- **oracledba/web_server.py** (1,274 lines) - Flask server with all routes
- **oracledba/web/** - HTML templates and static assets
  - templates/ - 13 HTML pages (dashboard, databases, storage, etc.)
  - static/ - CSS, JavaScript, images
- **oracledba/cli.py** - Updated with `install gui` command
- **requirements-gui.txt** - Flask, Flask-CORS, SocketIO

### Testing

Web GUI is now running locally on http://localhost:5000 ✅
