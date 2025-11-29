Go to https://github.com/balena-io/etcher/releases/ and download the latest version of balenaEtcher for your operating system.
For Ubuntu or Debian-based systems, you can download the .deb package.

Install balenaEtcher:
```bash
cd ~/Downloads
sudo apt install ./balena-etcher-*.deb
```

Go to https://joshua-riek.github.io/ubuntu-rockchip-download/boards/orangepi-5-max.html and download the latest Ubuntu 24.04 image for Orange Pi 5 Max.

Step 1: Flash the Image
Flash the image to your SD card using balenaEtcher as usual. Do not remove the card yet.
Step 2: Access the Configuration Partition
Re-insert the SD card into your computer. You should see a partition named system-boot (or sometimes just boot). Open it.

Step 3: Configure WiFi (network-config)
Open the network-config file in a text editor (Notepad++, VS Code, or Sublime Text). Do not use Windows Notepad as it can mess up line endings.

Uncomment and edit the WiFi section to look like this:

```yaml
version: 2
ethernets:
  eth0:
    dhcp4: true
    optional: true
wifis:
  wlan0:
    dhcp4: true
    optional: true
    access-points:
      "YOUR_WIFI_NAME":
        password: "YOUR_WIFI_PASSWORD"
```

Step 5: Boot
Save both files.
Safely eject the SD card.
Insert it into the Orange Pi 5 Max.
Power on.
Wait 2-3 minutes.


## Post-Installation Setup

### Update System (Critical First Step)

```bash
# Update package lists
sudo apt update

# Upgrade all packages
sudo apt upgrade -y

# Distribution upgrade (if available)
sudo apt dist-upgrade -y

# Clean up
sudo apt autoremove -y
sudo apt autoclean
```

**Time required**: 10-30 minutes depending on connection

### Enable SSH (For Headless Access)

```bash
# Install SSH server (if not installed)
sudo apt install -y openssh-server

# Enable and start SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Check status
sudo systemctl status ssh

# Find your IP address
ip addr show
# or
hostname -I
```

**Connect from another computer:**
```bash
ssh username@192.168.1.xxx
```

**Security hardening (recommended):**
```bash
# Disable root login via SSH
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Restart SSH
sudo systemctl restart ssh

# Optional: Set up SSH key authentication
ssh-keygen -t ed25519 -C "your-email@example.com"
ssh-copy-id username@orangepi-ip
```

### Install Essential Tools

```bash
# Development tools
sudo apt install -y build-essential git curl wget vim nano htop

# System monitoring
sudo apt install -y neofetch cpufrequtils lm-sensors

# Networking tools
sudo apt install -y net-tools iperf3 ethtool

# Compression utilities
sudo apt install -y zip unzip p7zip-full

# Optional: zsh and oh-my-zsh
sudo apt install -y zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

## Performance Tuning

### Enable Performance Governor

```bash
# Install cpufrequtils
sudo apt install -y cpufrequtils

# Set performance governor
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils

# Apply immediately
sudo systemctl disable ondemand
sudo systemctl restart cpufrequtils

# Verify
cpufreq-info | grep "current policy"