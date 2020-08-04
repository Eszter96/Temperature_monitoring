from time import sleep
from umqtt.simple import MQTTClient 
import ubinascii
from machine import Pin
from dht import DHT22
import network
import machine
import json
import webrepl

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
webrepl.start()

client = MQTTClient(CLIENT_ID, SERVER)
client.connect()   # Connect to MQTT broker

sensor = DHT22(Pin(9, Pin.IN, Pin.PULL_UP))   # DHT-22 on GPIO 15 (input with internal pull-up resistor)

measuring_freq = 100   # The number represents how many times I want to get readings in 24 hours
sleeping_time = int(86400/measuring_freq * 1000) # Calculating sleeping time in millisecs
try:
    sensor.measure()   # Poll sensor
    t = sensor.temperature()
    h = sensor.humidity()
    if isinstance(t, float) and isinstance(h, float):  # Confirm sensor results are numeric
        msg = (b'{:3.1f},{:3.1f}'.format(t, h))
        client.publish(TOPIC, msg)  # Publish sensor data to MQTT topic
        print('Temperature: %3.1f°C' %t)             
        print('Humidity: %3.1f%%' %h)
        sleep(0.1)
    else:
        print('Invalid sensor readings.')
except OSError:
    print('Failed to read sensor.')
#sleep(4)
machine.deepsleep(sleeping_time)
