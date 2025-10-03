#!/bin/bash

# Quick Setup Script for Homeview on Raspberry Pi
# This is a simplified version for quick deployment

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Homeview Quick Setup for Raspberry Pi${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "run.py" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}Please run this script from the homeview directory${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${BLUE}Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p credentials
mkdir -p instance
mkdir -p logs

# Copy Pi-optimized config if it doesn't exist
if [ ! -f "config.py" ]; then
    echo -e "${BLUE}Setting up Pi-optimized configuration...${NC}"
    cp config_pi.py config.py
fi

# Create a simple startup script
cat > start_homeview.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export FLASK_APP=run.py
export FLASK_ENV=production
gunicorn --bind 127.0.0.1:5000 --workers 1 --timeout 120 run:app
EOF

chmod +x start_homeview.sh

# Create systemd service
echo -e "${BLUE}Creating systemd service...${NC}"
sudo tee /etc/systemd/system/homeview.service > /dev/null <<EOF
[Unit]
Description=Homeview Flask Application
After=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
Environment=PYTHONPATH=$(pwd)
ExecStart=$(pwd)/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 1 --timeout 120 run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable homeview.service
sudo systemctl start homeview.service

echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Copy your Google credentials to: $(pwd)/credentials/"
echo "2. Update $(pwd)/config.py with your API keys"
echo "3. Test the app: curl http://127.0.0.1:5000"
echo "4. For kiosk mode, run: ./kiosk_launcher.sh"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  sudo systemctl status homeview.service"
echo "  sudo systemctl restart homeview.service"
echo "  journalctl -u homeview.service -f"




