#!/bin/bash

# Remote Deployment Script for Homeview
# Deploys the Homeview app to a remote Raspberry Pi via SSH

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEFAULT_PI_USER="pi"
DEFAULT_PI_HOST=""
APP_DIR="/home/pi/homeview"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    Homeview Remote Deployment Script   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get Pi connection details
if [ -z "$1" ]; then
    echo -e "${YELLOW}Enter your Raspberry Pi's IP address:${NC}"
    read -r PI_HOST
else
    PI_HOST="$1"
fi

if [ -z "$2" ]; then
    echo -e "${YELLOW}Enter Pi username (default: pi):${NC}"
    read -r PI_USER
    PI_USER=${PI_USER:-$DEFAULT_PI_USER}
else
    PI_USER="$2"
fi

echo -e "${BLUE}Deploying to: $PI_USER@$PI_HOST${NC}"
echo ""

# Test SSH connection
echo -e "${BLUE}Testing SSH connection...${NC}"
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$PI_USER@$PI_HOST" exit 2>/dev/null; then
    echo -e "${RED}✗ Cannot connect to $PI_USER@$PI_HOST${NC}"
    echo -e "${YELLOW}Make sure:${NC}"
    echo "  1. SSH is enabled on the Pi"
    echo "  2. The Pi is connected to the network"
    echo "  3. You have the correct IP address"
    echo "  4. SSH keys are set up (or password authentication is enabled)"
    exit 1
fi

echo -e "${GREEN}✓ SSH connection successful${NC}"

# Check if we're in the homeview directory
if [ ! -f "run.py" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}✗ Please run this script from the homeview directory${NC}"
    exit 1
fi

# Create deployment package
echo -e "${BLUE}Creating deployment package...${NC}"
TEMP_DIR=$(mktemp -d)
PACKAGE_NAME="homeview-deploy-$(date +%Y%m%d-%H%M%S)"

# Copy application files
cp -r app "$TEMP_DIR/"
cp -r static "$TEMP_DIR/" 2>/dev/null || true
cp -r templates "$TEMP_DIR/" 2>/dev/null || true
cp run.py "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp config_pi.py "$TEMP_DIR/"
cp setup_pi.sh "$TEMP_DIR/"
cp quick_setup.sh "$TEMP_DIR/"
cp kiosk_launcher.sh "$TEMP_DIR/"
cp homeview.service "$TEMP_DIR/"
cp homeview-kiosk.desktop "$TEMP_DIR/"
cp enable_ssh.sh "$TEMP_DIR/"

# Create credentials directory
mkdir -p "$TEMP_DIR/credentials"

# Create deployment script
cat > "$TEMP_DIR/deploy.sh" << 'EOF'
#!/bin/bash

# Deployment script that runs on the Pi
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Running deployment on Pi...${NC}"

# Stop existing service if running
if systemctl is-active --quiet homeview.service; then
    echo -e "${YELLOW}Stopping existing service...${NC}"
    sudo systemctl stop homeview.service
fi

# Backup existing installation if it exists
if [ -d "/home/pi/homeview" ]; then
    echo -e "${YELLOW}Backing up existing installation...${NC}"
    sudo mv /home/pi/homeview /home/pi/homeview.backup.$(date +%Y%m%d-%H%M%S)
fi

# Move new files
echo -e "${BLUE}Installing new version...${NC}"
sudo mv /tmp/homeview-deploy /home/pi/homeview
sudo chown -R pi:pi /home/pi/homeview

# Make scripts executable
chmod +x /home/pi/homeview/*.sh

# Run setup
echo -e "${BLUE}Running setup...${NC}"
cd /home/pi/homeview
./setup_pi.sh

echo -e "${GREEN}Deployment complete!${NC}"
EOF

chmod +x "$TEMP_DIR/deploy.sh"

# Create tarball
echo -e "${BLUE}Creating deployment package...${NC}"
cd "$TEMP_DIR"
tar -czf "/tmp/$PACKAGE_NAME.tar.gz" .
cd - > /dev/null

# Transfer to Pi
echo -e "${BLUE}Transferring files to Pi...${NC}"
scp "/tmp/$PACKAGE_NAME.tar.gz" "$PI_USER@$PI_HOST:/tmp/"

# Extract and deploy on Pi
echo -e "${BLUE}Deploying on Pi...${NC}"
ssh "$PI_USER@$PI_HOST" "
    cd /tmp
    tar -xzf $PACKAGE_NAME.tar.gz
    mv * homeview-deploy
    chmod +x deploy.sh
    ./deploy.sh
    rm -rf homeview-deploy $PACKAGE_NAME.tar.gz
"

# Clean up local files
rm -rf "$TEMP_DIR"
rm -f "/tmp/$PACKAGE_NAME.tar.gz"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Your Homeview app has been deployed to $PI_USER@$PI_HOST${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. SSH into your Pi: ssh $PI_USER@$PI_HOST"
echo "2. Configure your API keys: nano /home/pi/homeview/config.py"
echo "3. Copy your Google credentials to: /home/pi/homeview/credentials/"
echo "4. Reboot the Pi: sudo reboot"
echo ""
echo -e "${BLUE}The app will start automatically in kiosk mode after reboot.${NC}"

# Optional: Test the deployment
echo -e "${YELLOW}Would you like to test the deployment now? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Testing deployment...${NC}"
    
    # Wait a moment for service to start
    sleep 5
    
    # Test if service is running
    if ssh "$PI_USER@$PI_HOST" "systemctl is-active --quiet homeview.service"; then
        echo -e "${GREEN}✓ Service is running${NC}"
        
        # Test if app is responding
        if ssh "$PI_USER@$PI_HOST" "curl -s http://127.0.0.1:5000 > /dev/null"; then
            echo -e "${GREEN}✓ Application is responding${NC}"
            echo -e "${BLUE}You can access your app at: http://$PI_HOST:5000${NC}"
        else
            echo -e "${YELLOW}⚠ Application is not responding yet. Check logs:${NC}"
            echo "  ssh $PI_USER@$PI_HOST 'journalctl -u homeview.service -f'"
        fi
    else
        echo -e "${YELLOW}⚠ Service is not running. Check logs:${NC}"
        echo "  ssh $PI_USER@$PI_HOST 'journalctl -u homeview.service -f'"
    fi
fi

echo -e "${GREEN}Deployment script complete!${NC}"

