#!/bin/bash

# Quick SSH Setup Script for Raspberry Pi
# This script enables SSH and sets up basic security

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    Raspberry Pi SSH Setup Script      ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run this script as root. Run as the 'pi' user.${NC}"
    exit 1
fi

# Enable SSH service
echo -e "${BLUE}1. Enabling SSH service...${NC}"
sudo systemctl enable ssh
sudo systemctl start ssh

# Check if SSH is running
if systemctl is-active --quiet ssh; then
    echo -e "${GREEN}✓ SSH service is running${NC}"
else
    echo -e "${RED}✗ Failed to start SSH service${NC}"
    exit 1
fi

# Change default password
echo -e "${BLUE}2. Setting up password...${NC}"
echo -e "${YELLOW}Please change the default password for security:${NC}"
passwd

# Get IP address
PI_IP=$(hostname -I | awk '{print $1}')

# Set up basic firewall
echo -e "${BLUE}3. Configuring firewall...${NC}"
if command -v ufw >/dev/null 2>&1; then
    sudo ufw --force enable
    sudo ufw allow ssh
    sudo ufw allow 5000  # For Homeview app
    echo -e "${GREEN}✓ Firewall configured${NC}"
else
    echo -e "${YELLOW}⚠ UFW not installed, skipping firewall setup${NC}"
fi

# Display connection information
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SSH Setup Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Your Pi's IP address: $PI_IP${NC}"
echo ""
echo -e "${YELLOW}You can now connect via SSH:${NC}"
echo "  ssh pi@$PI_IP"
echo ""
echo -e "${YELLOW}To copy files to your Pi:${NC}"
echo "  scp -r /path/to/homeview pi@$PI_IP:/home/pi/"
echo ""
echo -e "${YELLOW}To deploy Homeview app:${NC}"
echo "  ssh pi@$PI_IP"
echo "  cd homeview"
echo "  ./setup_pi.sh"
echo ""

# Optional: Set up SSH key authentication
echo -e "${BLUE}4. Optional: Set up SSH key authentication${NC}"
echo -e "${YELLOW}Would you like to set up SSH key authentication? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Setting up SSH key authentication...${NC}"
    
    # Create .ssh directory if it doesn't exist
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    
    # Generate SSH key if it doesn't exist
    if [ ! -f ~/.ssh/id_rsa ]; then
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
        echo -e "${GREEN}✓ SSH key pair generated${NC}"
    else
        echo -e "${YELLOW}⚠ SSH key already exists${NC}"
    fi
    
    # Add public key to authorized_keys
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    
    echo -e "${GREEN}✓ SSH key authentication configured${NC}"
    echo ""
    echo -e "${BLUE}Your public key:${NC}"
    cat ~/.ssh/id_rsa.pub
    echo ""
    echo -e "${YELLOW}Copy this public key to your computer's ~/.ssh/authorized_keys${NC}"
    echo -e "${YELLOW}Or use ssh-copy-id from your computer:${NC}"
    echo "  ssh-copy-id pi@$PI_IP"
fi

echo -e "${GREEN}SSH setup complete!${NC}"

