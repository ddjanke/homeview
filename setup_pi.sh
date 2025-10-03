#!/bin/bash

# Homeview Raspberry Pi Zero W Setup Script
# This script sets up a fresh Raspbian Lite installation for the Homeview app

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_USER="pi"
APP_NAME="homeview"
APP_DIR="/home/$APP_USER/$APP_NAME"
SERVICE_NAME="homeview.service"
DESKTOP_FILE="homeview-kiosk.desktop"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Homeview Raspberry Pi Zero W Setup   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run this script as root. Run as the 'pi' user.${NC}"
    echo "The script will ask for sudo privileges when needed."
    exit 1
fi

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo -e "${YELLOW}Warning: This script is designed for Raspberry Pi. Continue anyway? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}Starting setup process...${NC}"
echo ""

# Update system packages
echo -e "${BLUE}1. Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y

# Install required system packages
echo -e "${BLUE}2. Installing system dependencies...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    midori \
    unclutter \
    xserver-xorg \
    xinit \
    x11-xserver-utils \
    xinput \
    xinput-calibrator \
    lightdm \
    desktop-file-utils \
    chromium-browser \
    --no-install-recommends

# Install additional packages for better performance
sudo apt install -y \
    htop \
    vim \
    curl \
    wget \
    --no-install-recommends

# Clean up package cache
sudo apt autoremove -y
sudo apt autoclean

echo -e "${GREEN}System packages installed successfully!${NC}"

# Configure auto-login
echo -e "${BLUE}3. Configuring auto-login...${NC}"

# Enable auto-login for pi user
sudo systemctl set-default graphical.target
sudo ln -fs /lib/systemd/system/getty@.service /etc/systemd/system/getty.target.wants/getty@tty1.service
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d

# Create auto-login configuration
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $APP_USER --noclear %I \$TERM
EOF

# Configure lightdm for auto-login
sudo tee /etc/lightdm/lightdm.conf > /dev/null <<EOF
[SeatDefaults]
autologin-user=$APP_USER
autologin-user-timeout=0
user-session=LXDE-pi
EOF

echo -e "${GREEN}Auto-login configured!${NC}"

# Create application directory
echo -e "${BLUE}4. Setting up application directory...${NC}"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# If the app is not already here, clone it
if [ ! -f "run.py" ]; then
    echo -e "${YELLOW}Please copy your homeview application files to $APP_DIR${NC}"
    echo -e "${YELLOW}You can use scp, git clone, or copy from USB drive${NC}"
    echo ""
    echo "Example commands:"
    echo "  # From another machine:"
    echo "  scp -r /path/to/homeview pi@$(hostname -I | awk '{print $1}'):~/"
    echo "  # Or clone from git:"
    echo "  git clone <your-repo-url> homeview"
    echo ""
    echo -e "${YELLOW}Press Enter when you have copied the files...${NC}"
    read -r
fi

# Verify app files exist
if [ ! -f "run.py" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: Required app files not found in $APP_DIR${NC}"
    echo "Please ensure run.py and requirements.txt are present"
    exit 1
fi

# Create Python virtual environment
echo -e "${BLUE}5. Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo -e "${BLUE}6. Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Install additional packages for better performance on Pi Zero
pip install gunicorn

echo -e "${GREEN}Python environment set up successfully!${NC}"

# Create systemd service
echo -e "${BLUE}7. Creating systemd service...${NC}"
sudo tee /etc/systemd/system/$SERVICE_NAME > /dev/null <<EOF
[Unit]
Description=Homeview Flask Application
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 1 --timeout 120 run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo -e "${GREEN}Systemd service created and started!${NC}"

# Create desktop autostart file for kiosk mode
echo -e "${BLUE}8. Setting up kiosk mode...${NC}"

# Create autostart directory
mkdir -p "/home/$APP_USER/.config/autostart"

# Create desktop file for kiosk mode
tee "/home/$APP_USER/.config/autostart/$DESKTOP_FILE" > /dev/null <<EOF
[Desktop Entry]
Type=Application
Name=Homeview Kiosk
Comment=Homeview Application in Kiosk Mode
Exec=sh -c 'sleep 10 && unclutter -idle 1 -root & midori -e Fullscreen -a http://127.0.0.1:5000'
Icon=midori
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
EOF

# Make desktop file executable
chmod +x "/home/$APP_USER/.config/autostart/$DESKTOP_FILE"

echo -e "${GREEN}Kiosk mode configured!${NC}"

# Configure display settings
echo -e "${BLUE}9. Configuring display settings...${NC}"

# Disable screen blanking
sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart > /dev/null <<EOF
@xset s off
@xset -dpms
@xset s noblank
EOF

# Configure Midori for better performance
mkdir -p "/home/$APP_USER/.config/midori"
tee "/home/$APP_USER/.config/midori/config" > /dev/null <<EOF
[settings]
default-encoding=utf-8
enable-plugins=false
enable-scripts=true
enable-javascript=true
load-images=true
enable-site-specific-quirks=true
enable-html5-database=true
enable-html5-local-storage=true
enable-offline-web-application-cache=true
enable-universal-access-from-file-uris=true
enable-universal-access-from-file-uris=true
enable-file-access-from-file-uris=true
enable-xss-auditor=false
enable-spell-checking=false
enable-accelerated-compositing=true
enable-accelerated-2d-canvas=true
enable-accelerated-video-decode=true
enable-accelerated-video-encode=true
enable-hardware-acceleration=true
enable-webgl=true
enable-webgl2=true
enable-accelerated-2d-canvas=true
enable-accelerated-video-decode=true
enable-accelerated-video-encode=true
enable-hardware-acceleration=true
enable-webgl=true
enable-webgl2=true
EOF

echo -e "${GREEN}Display settings configured!${NC}"

# Create configuration template
echo -e "${BLUE}10. Creating configuration template...${NC}"
tee "$APP_DIR/config_template.py" > /dev/null <<EOF
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///homeview.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google API Configuration
    GOOGLE_CREDENTIALS_FILE = "credentials/google_credentials.json"
    GOOGLE_SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID") or "primary"

    # Google Sheets Configuration
    GOOGLE_SHEETS_ID = "YOUR_GOOGLE_SHEETS_ID_HERE"
    CHORES_SHEET_NAME = "Chores"
    TODOS_SHEET_NAME = "Todos"

    # Google Drive Configuration
    GOOGLE_DRIVE_ICONS_FOLDER_ID = "YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE"

    # Weather API Configuration
    WEATHER_API_KEY = "YOUR_WEATHER_API_KEY_HERE"
    WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    WEATHER_LOCATION = {
        "lat": float(os.environ.get("WEATHER_LAT", "39.9342")),
        "lon": float(os.environ.get("WEATHER_LON", "-105.0570")),
        "city": "YOUR_CITY_NAME",
    }

    # Cache Configuration
    CACHE_DEFAULT_TIMEOUT = 900  # 15 minutes
    WEATHER_CACHE_TIMEOUT = 600  # 10 minutes (safe for 60 calls/minute limit)
    CALENDAR_CACHE_TIMEOUT = 900  # 15 minutes

    # UI Configuration
    TOUCH_TARGET_SIZE = 44  # minimum touch target size in pixels
EOF

# Create setup completion script
tee "$APP_DIR/setup_complete.sh" > /dev/null <<EOF
#!/bin/bash
# Homeview Setup Completion Script

echo "Homeview Raspberry Pi Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Copy your Google credentials to: $APP_DIR/credentials/"
echo "2. Update configuration in: $APP_DIR/config.py"
echo "3. Set your weather location and API keys"
echo "4. Reboot the Pi to start kiosk mode"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status $SERVICE_NAME    # Check app status"
echo "  sudo systemctl restart $SERVICE_NAME   # Restart app"
echo "  sudo systemctl stop $SERVICE_NAME      # Stop app"
echo "  journalctl -u $SERVICE_NAME -f         # View app logs"
echo ""
echo "To disable kiosk mode temporarily:"
echo "  sudo systemctl stop $SERVICE_NAME"
echo "  rm ~/.config/autostart/$DESKTOP_FILE"
echo ""
echo "To re-enable kiosk mode:"
echo "  ln -s $APP_DIR/autostart/$DESKTOP_FILE ~/.config/autostart/"
echo "  sudo systemctl start $SERVICE_NAME"
EOF

chmod +x "$APP_DIR/setup_complete.sh"

# Set proper ownership
sudo chown -R $APP_USER:$APP_USER "$APP_DIR"
sudo chown -R $APP_USER:$APP_USER "/home/$APP_USER/.config"

echo -e "${GREEN}Configuration files created!${NC}"

# Final status check
echo -e "${BLUE}11. Performing final checks...${NC}"

# Check if service is running
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✓ Service is running${NC}"
else
    echo -e "${YELLOW}⚠ Service is not running. Check logs with: journalctl -u $SERVICE_NAME${NC}"
fi

# Check if app is responding
if curl -s http://127.0.0.1:5000 > /dev/null; then
    echo -e "${GREEN}✓ Application is responding${NC}"
else
    echo -e "${YELLOW}⚠ Application is not responding. Check service status.${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Your Homeview app is now configured for Raspberry Pi Zero W!${NC}"
echo ""
echo -e "${YELLOW}Important next steps:${NC}"
echo "1. Copy your Google API credentials to: $APP_DIR/credentials/"
echo "2. Update $APP_DIR/config.py with your API keys and settings"
echo "3. Reboot the Pi: sudo reboot"
echo ""
echo -e "${BLUE}The app will automatically start in kiosk mode after reboot.${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  sudo systemctl status $SERVICE_NAME    # Check app status"
echo "  sudo systemctl restart $SERVICE_NAME   # Restart app"
echo "  journalctl -u $SERVICE_NAME -f         # View app logs"
echo ""
echo -e "${GREEN}Run $APP_DIR/setup_complete.sh for more information.${NC}"

