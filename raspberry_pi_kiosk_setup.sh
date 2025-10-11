#!/bin/bash

# Raspberry Pi Official Kiosk Mode Setup
# Based on official Raspberry Pi documentation and best practices

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_USER="pi"
APP_DIR="/home/$APP_USER/homeview"
APP_URL="http://127.0.0.1:5000"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Raspberry Pi Official Kiosk Setup    ${NC}"
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

echo -e "${BLUE}Setting up Raspberry Pi kiosk mode...${NC}"
echo ""

# 1. Enable Auto-Login using raspi-config
echo -e "${BLUE}1. Enabling auto-login using raspi-config...${NC}"
echo -e "${YELLOW}This will open raspi-config. Please select:${NC}"
echo -e "${YELLOW}  System Options → Boot / Auto Login → Desktop Autologin${NC}"
echo ""
read -p "Press Enter to open raspi-config..."
sudo raspi-config

echo -e "${GREEN}✓ Auto-login configured${NC}"

# 2. Install Required Packages
echo -e "${BLUE}2. Installing required packages...${NC}"
sudo apt update
sudo apt install -y \
    midori \
    matchbox-window-manager \
    unclutter \
    xserver-xorg \
    xinit \
    x11-xserver-utils \
    xscreensaver \
    xdotool \
    --no-install-recommends

echo -e "${GREEN}✓ Required packages installed${NC}"

# 3. Set up Python Environment
echo -e "${BLUE}3. Setting up Python environment...${NC}"

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

# 4. Create Systemd Service for the App
echo -e "${BLUE}4. Creating systemd service for Homeview app...${NC}"

sudo tee /etc/systemd/system/homeview.service > /dev/null <<EOF
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
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 1 --timeout 120 run:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable homeview.service
sudo systemctl start homeview.service

echo -e "${GREEN}✓ Homeview service created and started${NC}"

# 5. Create Kiosk Startup Script
echo -e "${BLUE}5. Creating kiosk startup script...${NC}"

cat > /home/$APP_USER/startKiosk.sh << 'EOF'
#!/bin/bash

# Raspberry Pi Kiosk Mode Startup Script
# This script starts the X server and launches Midori in kiosk mode

# Configuration
APP_URL="http://127.0.0.1:5000"
SERVICE_NAME="homeview.service"
MAX_WAIT_TIME=60

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Raspberry Pi Kiosk Mode...${NC}"

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

# Wait for app to be ready
if ! wait_for_app; then
    echo -e "${RED}App is not responding. Check service status and logs.${NC}"
    echo "Service status: $(systemctl is-active $SERVICE_NAME)"
    echo "Check logs: journalctl -u $SERVICE_NAME -n 20"
    exit 1
fi

# Disable screen blanking and power management
xset -dpms          # Disable DPMS (Energy Star) features
xset s off          # Disable screen saver
xset s noblank      # Don't blank the video device

# Hide mouse cursor
unclutter -idle 1 -root &

# Start window manager
matchbox-window-manager &

# Disable screensaver
xscreensaver -no-splash &

# Wait a moment for everything to initialize
sleep 2

# Launch Midori in fullscreen kiosk mode
echo -e "${GREEN}Launching Midori in kiosk mode...${NC}"
midori -e Fullscreen -a "$APP_URL" &

# Get the Midori process ID
MIDORI_PID=$!

# Monitor Midori process and restart if it crashes
while true; do
    if ! kill -0 $MIDORI_PID 2>/dev/null; then
        echo -e "${YELLOW}Midori crashed, restarting in 5 seconds...${NC}"
        sleep 5
        
        # Check if app is still responding
        if check_app; then
            midori -e Fullscreen -a "$APP_URL" &
            MIDORI_PID=$!
        else
            echo -e "${RED}App is not responding, waiting...${NC}"
            sleep 10
        fi
    fi
    sleep 5
done
EOF

chmod +x /home/$APP_USER/startKiosk.sh

echo -e "${GREEN}✓ Kiosk startup script created${NC}"

# 6. Configure rc.local for Auto-Start
echo -e "${BLUE}6. Configuring rc.local for auto-start...${NC}"

# Backup original rc.local
sudo cp /etc/rc.local /etc/rc.local.backup

# Create new rc.local
sudo tee /etc/rc.local > /dev/null <<EOF
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Start Homeview kiosk mode
# Wait for network to be ready
sleep 10

# Start X server and kiosk mode as pi user
sudo -u pi startx /home/pi/startKiosk.sh -- -nocursor &

exit 0
EOF

# Make rc.local executable
sudo chmod +x /etc/rc.local

echo -e "${GREEN}✓ rc.local configured for auto-start${NC}"

# 7. Configure X Server
echo -e "${BLUE}7. Configuring X server...${NC}"

# Create .xinitrc for pi user
cat > /home/$APP_USER/.xinitrc << 'EOF'
#!/bin/bash
# Start kiosk mode
exec /home/pi/startKiosk.sh
EOF

chmod +x /home/$APP_USER/.xinitrc

# Configure X server to disable cursor
sudo tee -a /boot/config.txt > /dev/null <<EOF

# Disable cursor for kiosk mode
dtoverlay=vc4-kms-v3d
disable_overscan=1
EOF

echo -e "${GREEN}✓ X server configured${NC}"

# 8. Disable Screensaver
echo -e "${BLUE}8. Disabling screensaver...${NC}"

# Create xscreensaver config
mkdir -p /home/$APP_USER/.xscreensaver
cat > /home/$APP_USER/.xscreensaver/xscreensaver << 'EOF'
mode: off
EOF

echo -e "${GREEN}✓ Screensaver disabled${NC}"

# 9. Set Proper Ownership
echo -e "${BLUE}9. Setting file ownership...${NC}"
sudo chown -R $APP_USER:$APP_USER "$APP_DIR"
sudo chown -R $APP_USER:$APP_USER /home/$APP_USER/.xinitrc
sudo chown -R $APP_USER:$APP_USER /home/$APP_USER/.xscreensaver

echo -e "${GREEN}✓ File ownership set${NC}"

# Final status check
echo -e "${BLUE}10. Performing final checks...${NC}"

# Check if service is running
if systemctl is-active --quiet homeview.service; then
    echo -e "${GREEN}✓ Homeview service is running${NC}"
else
    echo -e "${YELLOW}⚠ Homeview service is not running. Check logs with: journalctl -u homeview.service${NC}"
fi

# Check if app is responding
if curl -s http://127.0.0.1:5000 > /dev/null; then
    echo -e "${GREEN}✓ Application is responding${NC}"
else
    echo -e "${YELLOW}⚠ Application is not responding. Check service status.${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Raspberry Pi Kiosk Setup Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Your Raspberry Pi is now configured for official kiosk mode:${NC}"
echo "  ✓ Auto-login enabled via raspi-config"
echo "  ✓ Homeview service starts automatically"
echo "  ✓ X server starts with kiosk mode"
echo "  ✓ Midori launches in fullscreen"
echo "  ✓ Mouse cursor hidden"
echo "  ✓ Screen blanking disabled"
echo "  ✓ Auto-restart on crashes"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure your API keys in config.py"
echo "2. Copy your Google credentials to credentials/"
echo "3. Reboot: sudo reboot"
echo ""
echo -e "${BLUE}After reboot, the app will start automatically in kiosk mode!${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  sudo systemctl status homeview.service    # Check app status"
echo "  sudo systemctl restart homeview.service   # Restart app"
echo "  journalctl -u homeview.service -f         # View app logs"
echo "  /home/pi/startKiosk.sh                    # Test kiosk mode manually"
echo ""
echo -e "${BLUE}To disable kiosk mode temporarily:${NC}"
echo "  sudo systemctl disable homeview.service"
echo "  sudo mv /etc/rc.local /etc/rc.local.disabled"
echo "  sudo reboot"

