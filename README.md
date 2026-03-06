# UPS Battery Monitor for Raspberry Pi

Monitor your Uninterruptible Power Supply (UPS) on a Raspberry Pi and receive real-time Telegram notifications when the power supply changes. This project uses the Waveshare UPS HAT E to track battery status and sends alerts via Telegram Bot.

## Table of Contents

- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Install Python Dependencies](#1-install-python-dependencies)
  - [2. Detect UPS I2C Address](#2-detect-ups-i2c-address)
  - [3. Configure Telegram Bot](#3-configure-telegram-bot)
  - [4. Update Script Configuration](#4-update-script-configuration)
  - [5. Setup System Service](#5-setup-system-service)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- 🔋 Continuous monitoring of UPS battery status
- 📱 Telegram notifications for power events
- 🔄 Automatic reconnection and message retry
- 🎛️ Systemd service for background operation
- 🛡️ Resilient to network interruptions

## Hardware Requirements

- Raspberry Pi 5
- Waveshare UPS HAT E
- Stable internet connection (for Telegram notifications)
- Power supply

## Prerequisites

- Raspberry Pi OS (or compatible Linux distribution)
- Python 3.x
- Telegram account with bot created

## Installation

### 1. Install Python Dependencies

Install required Python libraries:

```bash
sudo apt update
sudo apt install python3-smbus
```

Then install Python packages:

```bash
pip install requests
```

### 2. Detect UPS I2C Address

Connect the UPS HAT E to your Raspberry Pi, then find its I2C address (usually `0x2d` but may vary):

```bash
i2cdetect -y 1
```

Note the hexadecimal address displayed in the output.

### 3. Configure Telegram Bot

1. Open Telegram and search for `@botfather`
2. Send `/newbot` and follow the instructions
3. Copy your bot token (format: `123456789:ABCdefGHIjklmnoPQRstuvwxyzABCDEf`)
4. Get your Chat ID by sending `/start` to `@userinfobot` to find your Telegram user ID

### 4. Update Script Configuration

Edit `monitor_light.py` and update these values:

```python
TOKEN = "your_bot_token_here"  # Replace with your Telegram bot token
CHAT_ID = "your_chat_id_here"  # Replace with your Telegram Chat ID
I2C_ADDRESS = 0x2d             # Replace with your UPS I2C address if different
```

### 5. Setup System Service

Create a systemd service file to run the monitor in the background:

```bash
sudo nano /etc/systemd/system/ups-monitor.service
```

Add the following content, updating the paths and username to match your setup:

```ini
[Unit]
Description=UPS Power Monitor
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/monitor_light.py
WorkingDirectory=/path/to/project/
Restart=always
RestartSec=10
User=pi
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ups-monitor
sudo systemctl start ups-monitor
```

Check service status:

```bash
sudo systemctl status ups-monitor
```

View logs:

```bash
sudo journalctl -u ups-monitor -f
```

## Usage

Once the service is running, you'll receive Telegram messages when:

- Power transitions occur
- Battery status changes
- System events are detected

The monitor runs continuously in the background and automatically reconnects if the internet connection is lost.

## Troubleshooting

**No messages received:**
- Verify your Telegram token and Chat ID are correct
- Check internet connectivity: `ping google.com`
- Review logs: `sudo journalctl -u ups-monitor -f`

**I2C address not found:**
- Ensure the UPS HAT is properly connected to the GPIO pins
- Try: `sudo i2cdetect -y 0` (some Pi versions use bus 0)

**Permission denied error:**
- Run: `sudo usermod -a -G i2c,gpio pi`
- Reboot the device

**Service fails to start:**
- Check file paths in the service file are correct
- Ensure Python script has execute permissions: `chmod +x monitor_light.py`

## License

See LICENSE file for details.
