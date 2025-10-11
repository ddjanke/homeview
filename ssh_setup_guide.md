# Raspberry Pi SSH Setup Guide

This guide covers multiple methods to enable SSH access on your Raspberry Pi for remote management.

## Method 1: Enable SSH Before First Boot (Recommended)

### Using Raspberry Pi Imager
1. Download [Raspberry Pi Imager](https://www.raspberrypi.org/software/)
2. Select your OS image (Raspberry Pi OS Lite recommended)
3. Click the gear icon (⚙️) for advanced options
4. Enable SSH and set a password
5. Optionally set WiFi credentials
6. Flash the image to your SD card

### Manual Method
1. Flash your OS image to the SD card
2. Before ejecting, create an empty file named `ssh` in the boot partition
3. Create `wpa_supplicant.conf` for WiFi (optional):

```conf
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOUR_WIFI_NAME"
    psk="YOUR_WIFI_PASSWORD"
}
```

## Method 2: Enable SSH After Boot

### Using raspi-config (if you have keyboard/monitor)
```bash
sudo raspi-config
# Navigate to: Interfacing Options → SSH → Yes
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Using systemctl (if you have terminal access)
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

## Method 3: Enable SSH via SD Card (No Boot Required)

If your Pi won't boot or you don't have keyboard/monitor:

1. **Remove SD card** from Pi
2. **Insert SD card** into your computer
3. **Mount the boot partition** (usually appears as "boot" drive)
4. **Create empty file** named `ssh` (no extension)
5. **Eject and reinsert** into Pi
6. **Boot the Pi** - SSH will be enabled

## Finding Your Pi's IP Address

### From the Pi itself:
```bash
hostname -I
# or
ip addr show | grep inet
```

### From your local network:
```bash
# Scan for Raspberry Pi devices
nmap -sn 192.168.1.0/24 | grep -B 2 "Raspberry Pi"
# or
arp -a | grep -i "b8:27:eb\|dc:a6:32\|e4:5f:01"
```

### Using your router's admin panel:
- Log into your router (usually 192.168.1.1 or 192.168.0.1)
- Look for connected devices
- Find "Raspberry Pi" or MAC address starting with b8:27:eb, dc:a6:32, or e4:5f:01

## Connecting via SSH

### Basic SSH connection:
```bash
ssh pi@<PI_IP_ADDRESS>
# Default password: raspberry
```

### With key-based authentication (recommended):
```bash
# Generate SSH key pair (on your computer)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy public key to Pi
ssh-copy-id pi@<PI_IP_ADDRESS>

# Now you can connect without password
ssh pi@<PI_IP_ADDRESS>
```

## Security Best Practices

### 1. Change Default Password
```bash
passwd
```

### 2. Disable Password Authentication (after setting up keys)
Edit `/etc/ssh/sshd_config`:
```bash
sudo nano /etc/ssh/sshd_config
```

Add/modify these lines:
```
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

Restart SSH:
```bash
sudo systemctl restart ssh
```

### 3. Change Default SSH Port (optional)
Edit `/etc/ssh/sshd_config`:
```
Port 2222
```

Restart SSH and connect with:
```bash
ssh -p 2222 pi@<PI_IP_ADDRESS>
```

### 4. Set up Firewall
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 5000  # For your Homeview app
```

## Troubleshooting SSH Issues

### Can't connect to Pi
1. **Check if SSH is running:**
   ```bash
   sudo systemctl status ssh
   ```

2. **Check if port 22 is open:**
   ```bash
   sudo netstat -tlnp | grep :22
   ```

3. **Check firewall:**
   ```bash
   sudo ufw status
   ```

4. **Test from Pi itself:**
   ```bash
   ssh pi@localhost
   ```

### "Connection refused" error
- SSH service not running: `sudo systemctl start ssh`
- Wrong IP address: Check with `hostname -I`
- Firewall blocking: `sudo ufw allow ssh`

### "Permission denied" error
- Wrong password: Try default "raspberry"
- Wrong username: Try "pi" or "raspberry"
- SSH keys not set up properly

### Can't find Pi on network
- Check WiFi connection
- Try wired Ethernet connection
- Check router's connected devices
- Use `nmap` to scan network

## Quick Setup Script

Create this script to quickly enable SSH and change password:

```bash
#!/bin/bash
# quick_ssh_setup.sh

echo "Enabling SSH..."
sudo systemctl enable ssh
sudo systemctl start ssh

echo "Changing default password..."
passwd

echo "Setting up firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 5000

echo "SSH setup complete!"
echo "Your Pi's IP address: $(hostname -I | awk '{print $1}')"
```

## For Homeview App Deployment

Once SSH is working, you can easily deploy your Homeview app:

```bash
# Copy app files to Pi
scp -r /path/to/homeview pi@<PI_IP>:/home/pi/

# Connect and run setup
ssh pi@<PI_IP>
cd homeview
chmod +x setup_pi.sh
./setup_pi.sh
```

## Useful SSH Commands

```bash
# Connect with specific port
ssh -p 2222 pi@<PI_IP>

# Connect with key file
ssh -i ~/.ssh/id_rsa pi@<PI_IP>

# Copy files to Pi
scp file.txt pi@<PI_IP>:/home/pi/

# Copy files from Pi
scp pi@<PI_IP>:/home/pi/file.txt ./

# Run command on Pi without interactive shell
ssh pi@<PI_IP> "sudo systemctl status homeview"

# Port forwarding (access Pi's web server from your computer)
ssh -L 5000:localhost:5000 pi@<PI_IP>
# Then visit http://localhost:5000 on your computer
```

This setup will give you full remote access to manage your Raspberry Pi and deploy the Homeview application easily!

