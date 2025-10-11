#!/bin/bash

# Auto-start Setup Script for Homeview on Raspberry Pi
# This script configures automatic login, app startup, and kiosk mode

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_USER="pi"
APP_NAME="homeview"
APP_DIR="/home/$APP_USER/$APP_NAME"
SERVICE_NAME="homeview.service"
DESKTOP_FILE="homeview-kiosk.desktop"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Homeview Auto-Start Setup Script     ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run this script as root. Run as the 'pi' user.${NC}"
    exit 1
fi

# Check if we're in the homeview directory
if [ ! -f "run.py" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Please run this script from the homeview directory${NC}"
    exit 1
fi

echo -e "${BLUE}Setting up auto-start for Homeview...${NC}"
echo ""

# 1. Configure Auto-Login
echo -e "${BLUE}1. Configuring auto-login...${NC}"

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

echo -e "${GREEN}✓ Auto-login configured${NC}"

# 2. Set up Python Environment
echo -e "${BLUE}2. Setting up Python environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo -e "${GREEN}✓ Python environment ready${NC}"

# 3. Create Systemd Service
echo -e "${BLUE}3. Creating systemd service...${NC}"

sudo tee /etc/systemd/system/$SERVICE_NAME > /dev/null <<EOF
[Unit]
Description=Homeview Flask Application
After=network.target
Wants=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=PYTHONPATH=$APP_DIR
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 1 --timeout 120 --max-requests 1000 --max-requests-jitter 100 run:app
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=homeview

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$APP_DIR
ReadWritePaths=$APP_DIR/instance

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo -e "${GREEN}✓ Systemd service created and started${NC}"

# 4. Create Kiosk Launcher Script
echo -e "${BLUE}4. Creating kiosk launcher...${NC}"

cat > kiosk_launcher.sh << 'EOF'
#!/bin/bash

# Homeview Kiosk Launcher Script
# This script launches the homeview app in fullscreen kiosk mode

# Configuration
APP_URL="http://127.0.0.1:5000"
BROWSER="midori"
SERVICE_NAME="homeview.service"
MAX_WAIT_TIME=60  # Maximum time to wait for app to start (seconds)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Homeview Kiosk Mode...${NC}"

# Function to check if service is running
check_service() {
    systemctl is-active --quiet "$SERVICE_NAME"
    return $?
}

# Function to check if app is responding
check_app() {
    curl -s --connect-timeout 5 "$APP_URL" > /dev/null 2>&1
    return $?
}

# Function to wait for app to be ready
wait_for_app() {
    local count=0
    echo -e "${YELLOW}Waiting for Homeview app to start...${NC}"
    
    while [ $count -lt $MAX_WAIT_TIME ]; do
        if check_service && check_app; then
            echo -e "${GREEN}✓ Homeview app is ready!${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 1
        count=$((count + 1))
    done
    
    echo ""
    echo -e "${RED}✗ Timeout waiting for app to start${NC}"
    return 1
}

# Start the homeview service if not running
if ! check_service; then
    echo -e "${BLUE}Starting Homeview service...${NC}"
    sudo systemctl start "$SERVICE_NAME"
    
    if ! check_service; then
        echo -e "${RED}Failed to start Homeview service${NC}"
        echo "Check logs with: journalctl -u $SERVICE_NAME"
        exit 1
    fi
fi

# Wait for app to be ready
if ! wait_for_app; then
    echo -e "${RED}App is not responding. Check service status and logs.${NC}"
    echo "Service status: $(systemctl is-active $SERVICE_NAME)"
    echo "Check logs: journalctl -u $SERVICE_NAME -n 20"
    exit 1
fi

# Hide cursor
unclutter -idle 1 -root &

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Configure browser for kiosk mode
export DISPLAY=:0

# Launch browser in kiosk mode
echo -e "${GREEN}Launching browser in kiosk mode...${NC}"

case "$BROWSER" in
    "midori")
        midori -e Fullscreen -a "$APP_URL" &
        ;;
    "chromium")
        chromium-browser \
            --kiosk \
            --no-first-run \
            --disable-infobars \
            --disable-session-crashed-bubble \
            --disable-dev-shm-usage \
            --disable-gpu \
            --no-sandbox \
            --disable-web-security \
            --disable-features=TranslateUI \
            --disable-ipc-flooding-protection \
            "$APP_URL" &
        ;;
    *)
        echo -e "${RED}Unsupported browser: $BROWSER${NC}"
        exit 1
        ;;
esac

BROWSER_PID=$!

# Monitor browser process
echo -e "${BLUE}Kiosk mode active. Press Ctrl+C to exit.${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down kiosk mode...${NC}"
    kill $BROWSER_PID 2>/dev/null
    pkill unclutter 2>/dev/null
    echo -e "${GREEN}Kiosk mode stopped.${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for browser process
wait $BROWSER_PID

# If we get here, browser exited
echo -e "${YELLOW}Browser exited. Restarting in 5 seconds...${NC}"
sleep 5
exec "$0" "$@"
EOF

chmod +x kiosk_launcher.sh

echo -e "${GREEN}✓ Kiosk launcher created${NC}"

# 5. Create Desktop Autostart File
echo -e "${BLUE}5. Setting up desktop autostart...${NC}"

# Create autostart directory
mkdir -p "/home/$APP_USER/.config/autostart"

# Create desktop file for kiosk mode
cat > "/home/$APP_USER/.config/autostart/$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Homeview Kiosk
Comment=Homeview Application in Kiosk Mode
Exec=$APP_DIR/kiosk_launcher.sh
Icon=midori
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=15
EOF

# Make desktop file executable
chmod +x "/home/$APP_USER/.config/autostart/$DESKTOP_FILE"

echo -e "${GREEN}✓ Desktop autostart configured${NC}"

# 6. Configure Display Settings
echo -e "${BLUE}6. Configuring display settings...${NC}"

# Disable screen blanking
sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart > /dev/null <<EOF
@xset s off
@xset -dpms
@xset s noblank
EOF

# Configure Midori for better performance
mkdir -p "/home/$APP_USER/.config/midori"
cat > "/home/$APP_USER/.config/midori/config" << EOF
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
EOF

echo -e "${GREEN}✓ Display settings configured${NC}"

# 7. Set Proper Ownership
echo -e "${BLUE}7. Setting file ownership...${NC}"
sudo chown -R $APP_USER:$APP_USER "$APP_DIR"
sudo chown -R $APP_USER:$APP_USER "/home/$APP_USER/.config"

echo -e "${GREEN}✓ File ownership set${NC}"

# Final status check
echo -e "${BLUE}8. Performing final checks...${NC}"

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
echo -e "${GREEN}  Auto-Start Setup Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Your Raspberry Pi is now configured to:${NC}"
echo "  ✓ Auto-login as pi user"
echo "  ✓ Start Homeview service automatically"
echo "  ✓ Launch Midori in kiosk mode on startup"
echo "  ✓ Auto-restart if anything crashes"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure your API keys in config.py"
echo "2. Copy your Google credentials to credentials/"
echo "3. Reboot: sudo reboot"
echo ""
echo -e "${BLUE}After reboot, the app will start automatically in kiosk mode!${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  sudo systemctl status $SERVICE_NAME    # Check app status"
echo "  sudo systemctl restart $SERVICE_NAME   # Restart app"
echo "  journalctl -u $SERVICE_NAME -f         # View app logs"
echo "  ./kiosk_launcher.sh                    # Test kiosk mode manually"

