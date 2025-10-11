# Homeview Raspberry Pi Zero W Setup Guide

This guide will help you set up your Homeview application on a Raspberry Pi Zero W to run automatically in kiosk mode.

## Prerequisites

- Raspberry Pi Zero W (or any Raspberry Pi model)
- MicroSD card (8GB minimum, 16GB recommended)
- Power supply (5V, 2.5A recommended)
- HDMI cable and monitor/TV
- USB keyboard (for initial setup)
- Internet connection

## Step 1: Install Raspbian Lite OS

1. Download the latest [Raspberry Pi OS Lite](https://www.raspberrypi.org/downloads/raspberry-pi-os/) image
2. Flash the image to your microSD card using [Raspberry Pi Imager](https://www.raspberrypi.org/software/) or similar tool
3. Before ejecting the card, enable SSH and set up WiFi (optional but recommended):
   - Create an empty file named `ssh` in the boot partition
   - Create a `wpa_supplicant.conf` file in the boot partition with your WiFi credentials:

```conf
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOUR_WIFI_NAME"
    psk="YOUR_WIFI_PASSWORD"
}
```

## Step 2: Initial Pi Setup

1. Insert the microSD card into your Pi and power it on
2. Connect via SSH or directly with keyboard/monitor
3. Login with default credentials: `pi` / `raspberry`
4. Change the default password: `passwd`
5. Update the system: `sudo apt update && sudo apt upgrade -y`

## Step 3: Transfer Homeview Application

### Option A: Using SCP (from another computer)
```bash
scp -r /path/to/homeview pi@<PI_IP_ADDRESS>:~/
```

### Option B: Using Git (if your app is in a repository)
```bash
git clone <your-repo-url> homeview
```

### Option C: Using USB drive
1. Copy the homeview folder to a USB drive
2. Insert USB drive into Pi
3. Mount and copy: `sudo mount /dev/sda1 /mnt && cp -r /mnt/homeview ~/`

## Step 4: Run the Setup Script

1. Make the setup script executable:
```bash
chmod +x setup_pi.sh
```

2. Run the setup script:
```bash
./setup_pi.sh
```

The script will:
- Install all required system packages
- Set up Python virtual environment
- Install Python dependencies
- Configure auto-login
- Create systemd service
- Set up kiosk mode
- Configure display settings

## Step 5: Configure Your Application

After the setup script completes, you need to configure your app:

1. **Copy Google API credentials:**
```bash
mkdir -p ~/homeview/credentials
# Copy your google_credentials.json to this directory
```

2. **Update configuration:**
Edit `~/homeview/config.py` with your settings:
- Google Sheets ID
- Google Drive folder ID
- Weather API key
- Weather location coordinates
- Any other API keys or settings

3. **Test the application:**
```bash
cd ~/homeview
source venv/bin/activate
python run.py
```

Visit `http://<PI_IP>:5000` in a browser to test.

## Step 6: Enable Kiosk Mode

The setup script has already configured kiosk mode, but you can control it:

**To start kiosk mode:**
```bash
sudo systemctl start homeview.service
~/homeview/kiosk_launcher.sh
```

**To enable auto-start on boot:**
```bash
# The desktop file should already be in place
# If not, copy it:
cp homeview-kiosk.desktop ~/.config/autostart/
```

**To disable kiosk mode temporarily:**
```bash
sudo systemctl stop homeview.service
rm ~/.config/autostart/homeview-kiosk.desktop
```

## Step 7: Reboot and Test

1. Reboot the Pi: `sudo reboot`
2. The Pi should automatically:
   - Login as the pi user
   - Start the Homeview service
   - Launch Midori in fullscreen kiosk mode
   - Display your Homeview application

## Troubleshooting

### Service Issues
```bash
# Check service status
sudo systemctl status homeview.service

# View service logs
journalctl -u homeview.service -f

# Restart service
sudo systemctl restart homeview.service
```

### Application Issues
```bash
# Check if app is responding
curl http://127.0.0.1:5000

# Test manually
cd ~/homeview
source venv/bin/activate
python run.py
```

### Display Issues
```bash
# Check display configuration
xrandr

# Test kiosk launcher manually
~/homeview/kiosk_launcher.sh
```

### Network Issues
```bash
# Check network connectivity
ping google.com

# Check if service is bound to correct interface
netstat -tlnp | grep 5000
```

## Performance Optimization for Pi Zero W

The setup includes several optimizations for the Pi Zero W:

1. **Gunicorn with single worker** - Reduces memory usage
2. **Request limits** - Prevents memory leaks
3. **Caching** - Reduces API calls
4. **Lightweight browser** - Midori instead of Chromium
5. **Disabled unnecessary services** - Reduces background processes

## Customization

### Change Browser
Edit `~/homeview/kiosk_launcher.sh` and change the `BROWSER` variable:
```bash
BROWSER="chromium"  # or "midori"
```

### Change Display Resolution
Add to `/boot/config.txt`:
```
hdmi_group=2
hdmi_mode=82  # 1920x1080 60Hz
```

### Add Touch Screen Support
If using a touch screen, install calibration tools:
```bash
sudo apt install xinput-calibrator
```

## Security Considerations

1. **Change default password** - Always change the pi user password
2. **Disable SSH** - If not needed: `sudo systemctl disable ssh`
3. **Firewall** - Consider setting up a firewall
4. **HTTPS** - For production, set up SSL certificates
5. **API Keys** - Keep your API keys secure and rotate them regularly

## Maintenance

### Regular Updates
```bash
sudo apt update && sudo apt upgrade -y
cd ~/homeview
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Log Rotation
The systemd service automatically handles log rotation, but you can check:
```bash
journalctl --disk-usage
```

### Backup
Regularly backup your configuration and database:
```bash
tar -czf homeview-backup-$(date +%Y%m%d).tar.gz ~/homeview/
```

## Support

If you encounter issues:

1. Check the service logs: `journalctl -u homeview.service -f`
2. Verify all dependencies are installed
3. Ensure all configuration files are properly set
4. Test the application manually before running in kiosk mode

## Files Created by Setup

- `/etc/systemd/system/homeview.service` - Systemd service file
- `~/homeview/venv/` - Python virtual environment
- `~/.config/autostart/homeview-kiosk.desktop` - Desktop autostart file
- `~/homeview/kiosk_launcher.sh` - Kiosk launcher script
- `~/homeview/setup_complete.sh` - Setup completion information

The setup script creates a complete, production-ready installation optimized for the Raspberry Pi Zero W.





