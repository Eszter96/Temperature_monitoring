from time import sleep
from umqtt.simple import MQTTClient 
import ubinascii
from machine import Pin
from dht import DHT22
import network
import machine
import json

CREDENTIALS = json.load(open('creds.json', 'r'))

SERVER = CREDENTIALS["IP"]  # MQTT Server Address (Change to the IP address of your Pi)
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b'esp32/' + CLIENT_ID
SSID = CREDENTIALS["SSID"]
SSID_PASSWD = CREDENTIALS["SSID_PASSWORD"]

def do_connect():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    if not station.isconnected():
        print('connecting to network...')
        station.connect(SSID, SSID_PASSWD)
        while not station.isconnected():
            pass
    print('network config:', station.ifconfig())
do_connect()

client = MQTTClient(CLIENT_ID, SERVER)
client.connect()   # Connect to MQTT broker

sensor = DHT22(Pin(9, Pin.IN, Pin.PULL_UP))   # DHT-22 on GPIO 15 (input with internal pull-up resistor)

while True:
    measuring_freq = 3000   # The number represents how many times I want to get in 24 hours
    sleeping_time = 86400/measuring_freq
    for i in range(measuring_freq):
        try:
            sensor.measure()   # Poll sensor
            t = sensor.temperature()
            h = sensor.humidity()
            if isinstance(t, float) and isinstance(h, float):  # Confirm sensor results are numeric
                msg = (b'{:3.1f},{:3.1f}'.format(t, h))
                client.publish(TOPIC, msg)  # Publish sensor data to MQTT topic
                print(b'{:3.1f},{:3.1f}'.format(t, h))
            else:
                print('Invalid sensor readings.')
        except OSError:
            print('Failed to read sensor.')
        sleep(sleeping_time)

