import time
import requests
import sys
import smbus
import threading
import queue

# === TELEGRAM SETTINGS ===
TOKEN = "___" # add your tocken here
CHAT_ID = "1234567890" # add chat id
I2C_ADDRESS = 0x2d  # <--- check via i2cdetect

# message queue init
message_queue = queue.Queue()

# background worker
def telegram_worker():
    while True:
        # 1. Get messages from the queue (if queue is empty, then waits here)
        message = message_queue.get()

        sent = False
        while not sent:
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                data = {"chat_id": CHAT_ID, "text": message}
                requests.post(url, data=data, timeout=10)
                sent = True # success
            except Exception as e:
                # 2. if error (no internet), wait 5 seconds & start again
                print(f"No internet connection. Try again... ({e})")
                time.sleep(5)

        # inform queue that the task is done
        message_queue.task_done()
        print(f"Message sent: {message}")

# === DAEMON LAUNCH ===
# daemon=True means this thread exists when we stop the main script
worker_thread = threading.Thread(target=telegram_worker, daemon=True)
worker_thread.start()

# === MAIN CODE ===
def send_telegram(message):
    # puts msg to the queue
    message_queue.put(message)

# === UPS HAT E DRIVER ===
class SimpleUps:
    def __init__(self, addr):
        self.bus = smbus.SMBus(1)
        self.addr = addr

    def get_voltage(self):
        try:
            result = self.bus.read_word_data(self.addr, 0x02)
            
            fixed_result = ((result & 0xFF) << 8) | ((result >> 8) & 0xFF)
            
            voltage = (fixed_result >> 3) * 0.004
            return voltage
        except Exception:
            return 0.0

# init
ups = SimpleUps(I2C_ADDRESS)

print("Launch of monitoring. Waiting for status change...")

# initial check
# if now > 1V it means there's electricity (True). if 0V then no electricity (False).
voltage = ups.get_voltage()
power_is_online = voltage > 1.0 

print(f"Current voltage: {voltage:.2f} V. Status: {'ELECTRICITY TRUE' if power_is_online else 'ON BATTERY'}")

while True:
    current_voltage = ups.get_voltage()
    
    # logics
    if power_is_online:
        # waiting for no electricity (voltage down to almost 0)
        if current_voltage < 0.5:
            print("⚠️ Detection: Voltage low!")
            # second check in 2 secs (in case of glitch)
            time.sleep(2)
            if ups.get_voltage() < 0.5:
                print("⚠️ No electricity. Adding message to the queue.")
                # adding timestamp to understand when it occured
                timestamp = time.strftime("%H:%M:%S")
                send_telegram(f"⚠️ NO ELECTRICITY at {timestamp}!\n🔋 Switch to UPS.")
                power_is_online = False
    else:
        # waiting for the electricity
        if current_voltage > 1.0:
            time.sleep(2)
            if ups.get_voltage() > 1.0:
                print("✅ Electricity is back. Adding message to the queue.")
                timestamp = time.strftime("%H:%M:%S")
                send_telegram(f"✅ ELECTRICITY IS BACK at {timestamp}!\n🔌 Switch to grid.")
                power_is_online = True
    
    time.sleep(3)
