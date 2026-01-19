To be added in details later...

You need:
* Raspberry Pi 5
* Waveshare UPS HAT E
* Telegram bot (easy to register via @botfather

Install smbus python lib if not installed
`sudo apt install python3-smbus`

Check UPS's register (needed to be updated in the script)
`i2cdetect -y 1`

Update the code (add telegram bot info, update UPS's register, other fine tunings)

Create service

`sudo nano /etc/systemd/system/ups-monitor.service`

Add this code, update your paths and usernames

```
[Unit]
Description=UPS Power Monitor
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/UPS_HAT_E/monitor_light.py
WorkingDirectory=/home/pi/UPS_HAT_E/
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Launch service

```
sudo systemctl enable ups-monitor
sudo systemctl start ups-monitor
```
