import time
import requests
import smbus
import threading
import queue

# === TELEGRAM SETTINGS ===
TOKEN = "___"  # Telegram bot token (obtain from BotFather)
CHAT_ID = "1234567890"  # Target Telegram chat ID for notifications
I2C_ADDRESS = 0x2d  # I2C address of UPS HAT (verify using i2cdetect)

# Queue for handling Telegram messages asynchronously
message_queue = queue.Queue()

# Background worker thread that sends queued messages to Telegram
def telegram_worker():
    while True:
        # Wait for and retrieve next message from queue
        message = message_queue.get()

        sent = False
        while not sent:
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                data = {"chat_id": CHAT_ID, "text": message}
                requests.post(url, data=data, timeout=10)
                sent = True
            except Exception as e:
                # Retry on connection failure after brief delay
                print(f"No internet connection. Try again... ({e})")
                time.sleep(5)

        # Mark message as processed in queue
        message_queue.task_done()
        print(f"Message sent: {message}")

# Start background thread for sending Telegram messages
# daemon=True ensures thread exits when main script stops
worker_thread = threading.Thread(target=telegram_worker, daemon=True)
worker_thread.start()

# Queue message for sending via Telegram
def send_telegram(message):
    message_queue.put(message)

# Interface for reading UPS HAT power supply voltage
class SimpleUps:
    def __init__(self, addr):
        self.bus = smbus.SMBus(1)
        self.addr = addr

    def get_voltage(self):
        try:
            result = self.bus.read_word_data(self.addr, 0x02)
            # Swap byte order from I2C data
            fixed_result = ((result & 0xFF) << 8) | ((result >> 8) & 0xFF)
            # Convert raw value to voltage (mV -> V)
            voltage = (fixed_result >> 3) * 0.004
            return voltage
        except Exception:
            return 0.0

# Initialize UPS voltage reader
ups = SimpleUps(I2C_ADDRESS)

print("Launch of monitoring. Waiting for status change...")

# Initial power status: voltage > 1V indicates grid power is available
voltage = ups.get_voltage()
power_is_online = voltage > 1.0 

print(f"Current voltage: {voltage:.2f} V. Status: {'ELECTRICITY TRUE' if power_is_online else 'ON BATTERY'}")

while True:
    current_voltage = ups.get_voltage()
    
    # Monitor power status and detect changes
    if power_is_online:
        # Check if grid power has failed (voltage drops below threshold)
        if current_voltage < 0.5:
            print("⚠️ Detection: Voltage low!")
            # Wait 2 seconds to confirm (filter false triggers)
            time.sleep(2)
            if ups.get_voltage() < 0.5:
                print("⚠️ No electricity. Adding message to the queue.")
                timestamp = time.strftime("%H:%M:%S")
                send_telegram(f"⚠️ NO ELECTRICITY at {timestamp}!\n🔋 Switch to UPS.")
                power_is_online = False
    else:
        # Check if grid power has been restored
        if current_voltage > 1.0:
            time.sleep(2)
            if ups.get_voltage() > 1.0:
                print("✅ Electricity is back. Adding message to the queue.")
                timestamp = time.strftime("%H:%M:%S")
                send_telegram(f"✅ ELECTRICITY IS BACK at {timestamp}!\n🔌 Switch to grid.")
                power_is_online = True
    
    time.sleep(3)
