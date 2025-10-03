# Homeview Raspberry Pi Deployment

This directory contains everything needed to deploy the Homeview application on a Raspberry Pi Zero W in kiosk mode.

## Quick Start

1. **Flash Raspbian Lite** to your microSD card
2. **Copy this entire homeview folder** to your Pi
3. **Run the setup script:**
   ```bash
   chmod +x setup_pi.sh
   ./setup_pi.sh
   ```
4. **Configure your app** (API keys, credentials)
5. **Reboot** and enjoy your kiosk!

## Files Overview

### Setup Scripts
- `setup_pi.sh` - Complete automated setup for fresh Raspbian install
- `quick_setup.sh` - Minimal setup for existing Pi installations
- `kiosk_launcher.sh` - Launches the app in fullscreen kiosk mode

### Configuration
- `config_pi.py` - Pi-optimized configuration template
- `homeview.service` - Systemd service file
- `homeview-kiosk.desktop` - Desktop autostart file

### Documentation
- `RASPBERRY_PI_SETUP.md` - Complete setup guide
- `README_PI.md` - This file

## What the Setup Does

The `setup_pi.sh` script automatically:

1. **Installs dependencies:**
   - Python 3 and pip
   - Midori browser (lightweight)
   - X11 and display tools
   - System utilities

2. **Configures auto-login:**
   - Sets up automatic login for pi user
   - Configures lightdm for kiosk mode

3. **Sets up the application:**
   - Creates Python virtual environment
   - Installs all Python dependencies
   - Creates systemd service for auto-start

4. **Configures kiosk mode:**
   - Sets up Midori to launch in fullscreen
   - Disables screen blanking
   - Hides mouse cursor
   - Auto-restarts browser if it crashes

## Performance Optimizations

The setup includes several optimizations specifically for Raspberry Pi Zero W:

- **Single Gunicorn worker** - Reduces memory usage
- **Extended timeouts** - Accounts for slower Pi performance
- **Caching** - Reduces API calls and database operations
- **Lightweight browser** - Midori instead of Chromium
- **Optimized database settings** - SQLite with connection pooling

## Troubleshooting

### App won't start
```bash
sudo systemctl status homeview.service
journalctl -u homeview.service -f
```

### Kiosk mode issues
```bash
# Test manually
./kiosk_launcher.sh

# Check display
xrandr
```

### Performance issues
```bash
# Monitor resources
htop

# Check memory usage
free -h
```

## Customization

### Change Browser
Edit `kiosk_launcher.sh` and change the `BROWSER` variable:
```bash
BROWSER="chromium"  # or "midori"
```

### Adjust Display
Edit `/boot/config.txt` for resolution changes:
```
hdmi_group=2
hdmi_mode=82  # 1920x1080
```

### Modify Service
Edit `/etc/systemd/system/homeview.service` for service changes.

## Security Notes

- Change the default pi password
- Keep your API keys secure
- Consider setting up a firewall
- For production, use HTTPS

## Support

For issues:
1. Check the service logs
2. Verify all files are in place
3. Test the app manually first
4. Check the complete setup guide

The setup creates a production-ready kiosk installation optimized for Raspberry Pi Zero W performance.




