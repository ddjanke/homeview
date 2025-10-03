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

