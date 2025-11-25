# Docker Installation Guide for Windows

## Step 1: Download Docker Desktop

1. **Visit Docker's website**:
   - Go to: https://www.docker.com/products/docker-desktop
   - Click "Download for Windows"

2. **System Requirements**:
   - Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
   - OR Windows 11 64-bit
   - WSL 2 feature enabled
   - 4GB RAM minimum (8GB recommended)

## Step 2: Install Docker Desktop

1. **Run the installer**:
   - Double-click `Docker Desktop Installer.exe`
   - Follow the installation wizard
   - **Important**: Check "Use WSL 2 instead of Hyper-V" (recommended)

2. **Restart your computer** when prompted

3. **Start Docker Desktop**:
   - Launch Docker Desktop from Start Menu
   - Wait for Docker to start (you'll see a whale icon in system tray)
   - First start may take 2-3 minutes

## Step 3: Verify Installation

Open PowerShell and run:

```powershell
docker --version
docker-compose --version
```

You should see version numbers like:
```
Docker version 24.0.x
Docker Compose version v2.x.x
```

## Step 4: Run the Farmer Credit Score Engine

Once Docker is installed and running:

```powershell
# Navigate to project
cd "c:\Users\Trade\OneDrive\Desktop\Vnp\New folder\farmer-credit-score-engine"

# Copy environment file
Copy-Item .env.example .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

## Step 5: Access the Application

After services start (takes ~1-2 minutes):

- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Dashboard**: http://localhost:3001
- **Mock Agri Stack**: http://localhost:5001

## Troubleshooting

### Docker Desktop won't start
- Enable WSL 2: `wsl --install` in PowerShell (as Administrator)
- Enable Virtualization in BIOS
- Restart computer

### Services fail to start
```powershell
# View logs
docker-compose logs api

# Restart services
docker-compose restart

# Stop and remove everything
docker-compose down
docker-compose up -d
```

### Port conflicts
If ports 8000, 3000, 3001, or 5432 are in use:
- Stop conflicting applications
- Or edit `docker-compose.yml` to use different ports

## Quick Commands

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Restart a service
docker-compose restart api

# Rebuild after code changes
docker-compose up -d --build
```

## What Happens When You Run docker-compose up

1. **PostgreSQL** starts (database)
2. **Redis** starts (job queue)
3. **Mock Agri Stack** starts (simulated government API)
4. **API Service** starts (FastAPI backend)
5. **Worker Service** starts (background jobs)
6. **Frontend** builds and starts (React app)
7. **Dashboard** builds and starts (Admin UI)

All services are networked together automatically!

## Next Steps After Installation

1. **Download Docker Desktop**: https://www.docker.com/products/docker-desktop
2. **Install and restart** your computer
3. **Come back here** and I'll help you start the project
4. **Run the demo** from DEMO.md

---

**Need Help?**
- Docker Desktop not installing? Let me know your Windows version
- Services not starting? Share the error logs
- Want to test without full installation? I can set up just the API service
