import uasyncio as asyncio
from umqtt.robust import MQTTClient
from machine import Pin, UART
import network
from verification import Password
import gc
import _thread
import time

# Initialize GPIO pins
pin_config = {
    "201": 4, "202": 26, "203": 27, "204": 16, "205": 17,
    "301": 19, "302": 23, "303": 25, "304": 14, "305": 15
}
keylist = {key: Pin(pin_config[key], Pin.OUT) for key in pin_config}

# Define interrupt handler
def handle_interrupt(pin):
    for key in keylist.values():
        key.value(0)
    print("All pins reset due to interrupt.")
    asyncio.create_task(post_interrupt_processing())

# Setup interrupt on a specific pin
reset_pin = Pin(18, Pin.IN, Pin.PULL_UP)
reset_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)

async def post_interrupt_processing():
    print("Post-interrupt processing started")
    await asyncio.sleep(0)  # Yield control back to the event loop
    print("Post-interrupt processing completed")

password = Password()
mqtt_connected = False  # Flag to track MQTT connection status
wifi_connected = False  # Flag to track WiFi connection status

# WiFi connection setup
WIFI_SSID = '3bb-wlan'
WIFI_PASSWORD = 'power999'

async def connect_wifi():
    global wifi_connected
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(30):  # Try for 30 seconds
        if wifi.isconnected():
            print('WiFi connected')
            wifi_connected = True
            return True
        print('Connecting to WiFi...')
        await asyncio.sleep(1)
    print('Could not connect to WiFi')
    wifi_connected = False
    return False

# MQTT communication setup
mqtt_client_id = 'wirat'
broker_url = 'broker.hivemq.com'
topic_list = ['FL1/#', 'FL2/#', 'FL3/#', 'FL4/#', 'FL5/#']
heartbeat_topic = 'heartbeat'

# Define callback function for MQTT client
def cb(topic, msg):
    print(f'Received Data: Topic = {topic}, Msg = {msg}')
    R_msg = str(msg, 'utf-8')
    R_topic = str(topic, 'utf-8')
    password_changed = False

    # Check if the topic starts with any of the FL1, FL2, FL3, FL4, FL5
    if any(R_topic.startswith(f'FL{i}/key/') for i in range(1, 6)):
        key_num = R_topic.split('/')[-1]
        if key_num in keylist:
            keylist[key_num].value(1 if R_msg == 'OPEN' else 0)

    # Check if the topic starts with any of the FL*/pwd/*/new
    for i in range(1, 6):
        for j in range(1, 10):
            room_num = i * 100 + j
            if R_topic.startswith(f'FL{i}/pwd/{room_num}/new'):
                if (str(room_num) in password.code_map) and (len(R_msg) == 6):
                    password.code_map[str(room_num)] = R_msg
                    password_changed = True
                    print(f'Updated password for room {room_num} to {R_msg}')

    # Save passwords if any were changed
    if password_changed:
        password.save_passwords()

client = MQTTClient(client_id=mqtt_client_id, server=broker_url)
client.set_callback(cb)

def mqtt_connect():
    global mqtt_connected
    while not mqtt_connected:
        try:
            client.connect()
            print("MQTT connected.")
            # Resubscribe to all topics after connecting
            for topic in topic_list:
                try:
                    client.subscribe(topic)
                    print(f"Subscribed to topic: {topic}")
                except Exception as e:
                    print(f"Failed to subscribe to topic {topic}: {e}")
            mqtt_connected = True
        except OSError as e:
            print(f"Could not connect to MQTT server: {type(e).__name__} {e}, retrying in 5 seconds...")
            mqtt_connected = False
            time.sleep(5)  # Retry connection after 5 seconds

def mqtt_check():
    global mqtt_connected
    while True:
        if mqtt_connected:
            try:
                client.check_msg()
            except OSError as e:
                print(f"Error while checking MQTT message: {e}")
                mqtt_connected = False
        else:
            print("MQTT client disconnected, attempting to reconnect.")
            mqtt_connect()
        time.sleep(0.1)  # Adding a small delay to yield control

_thread.start_new_thread(mqtt_check, ())

async def mqtt_pub():
    global mqtt_connected
    while True:
        if mqtt_connected:
            try:
                # Publish all room's current password    
                password.load_passwords()
                for i in range(1, 6):
                    for j in range(1, 10):
                        room_num = i * 100 + j
                        client.publish(f'FL{i}/pwd/{room_num}/now', password.code_map[str(room_num)])
                # Publish heartbeat
                client.publish(heartbeat_topic, b'heartbeat')
                print("Heartbeat sent")
            except OSError as e:
                print(f"Error while publishing MQTT message: {e}")
                mqtt_connected = False
        else:
            print("MQTT client disconnected, attempting to reconnect.")
            await mqtt_connect()
        await asyncio.sleep(60)  # Publish every 60 seconds

async def execution():
    while True:
        relay2act = await password.check()
        if relay2act in keylist:
            keylist[relay2act].value(1)
        await asyncio.sleep(0.1)  # Non-blocking sleep to allow other tasks to run

async def periodic_reconnect():
    while True:
        print("Periodic check of WiFi connection")
        if not wifi_connected:
            await connect_wifi()
        else:
            print("WiFi is already connected")
        await asyncio.sleep(30)  # Check every 30 seconds

async def main():
    global wifi_connected
    wifi_connected = await connect_wifi()  # Attempt to connect to WiFi
    if wifi_connected:
        asyncio.create_task(mqtt_pub())
    asyncio.create_task(execution())
    asyncio.create_task(periodic_reconnect())
    print("Starting event loop...")
    while True:
        gc.collect()  # Perform garbage collection to free up memory
        await asyncio.sleep(3600)

try:
    asyncio.run(main())
except Exception as e:
    print(f"Exception in main: {e}")
