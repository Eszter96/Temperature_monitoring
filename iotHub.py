import json
import time
import ssl
from paho.mqtt import client as mqtt

CREDENTIALS = json.load(open('creds.json', 'r'))

# Get certificate form here: https://github.com/Azure/azure-iot-sdk-c/blob/master/certs/certs.c - \r\n and "" has to be deleted
PATH_TO_ROOT_CERT = CREDENTIALS["PATH_TO_ROOT_CERT"]
DEVICE_ID = CREDENTIALS["DEVICE_ID"]
IOT_HUB_NAME = CREDENTIALS["IOT_HUB_NAME"]

# VS code: Azure IoT Tools extension is needed to generate sas-token
SAS_TOKEN = CREDENTIALS["SAS_TOKEN"]

ESP32_TO_FLOOR = CREDENTIALS["ESP32_TO_FLOOR"]

# Connecting to Azure IoT Hub via MQTT 
# https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-mqtt-support
def on_connect_azure(client, userdata, flags, rc):
    """
    Callback function after connection attempt (get result)
    """
    print("[Azure] Device connected with result code: " + str(rc))


def on_disconnect_azure(client, userdata, rc):
    """
    Callback function after disconnection attempt (get result)
    """
    print("[Azure] Device disconnected with result code: " + str(rc))


def on_publish_azure(client, userdata, mid):
    """
    Callback function after publishing to Azure Iot Hub
    """
    print("[Azure] Device sent message")

# Connecting to ESP32-s via MQTT
def on_connect_local(client, userdata, flags, rc):
    """
    Connecting to server and subscribe to topic(s)
    """
    print("[Local] Device connected with result code: " + str(rc))
    client.subscribe('esp32/#')

def on_message_local(client, userdata, msg):
    """
    Get message from ESP32-s
    """
    print("[Local] Message received from ESP32:\n{}".format(msg.payload.decode()))
    temp, hum = [float(x) for x in msg.payload.decode().split(',')]
    esp32_id = msg.topic.split("esp32/")[1]
    floor = ESP32_TO_FLOOR[esp32_id]

    message = { "temp": str(temp), "hum": str(hum), "floor": floor }
    
    # Convert message to JSON string
    data = json.dumps(message)
    print(data)
    
    # Publish data by azure_client
    azure_client = userdata["AzureMQTTClient"]
    azure_client.publish("devices/" + DEVICE_ID + "/messages/events/", data, qos=1)

# Main - this wiil be executed when running code (but not importing)
if __name__ == '__main__':
    # Azure IoTHub mqtt client
    azure_client = mqtt.Client(client_id=DEVICE_ID, protocol=mqtt.MQTTv311)

    azure_client.on_connect = on_connect_azure
    azure_client.on_disconnect = on_disconnect_azure
    azure_client.on_publish = on_publish_azure

    azure_client.username_pw_set(username=IOT_HUB_NAME+".azure-devices.net/" +
                        DEVICE_ID + "/?api-version=2018-06-30", password=SAS_TOKEN)

    azure_client.tls_set(ca_certs=PATH_TO_ROOT_CERT, certfile=None, keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    azure_client.tls_insecure_set(False)

    azure_client.connect(IOT_HUB_NAME+".azure-devices.net", port=8883)
    # Start loop to initiate connection to Azure
    azure_client.loop_start()
   

    # Local mqtt client
    client = mqtt.Client(client_id="Eszter", userdata={"AzureMQTTClient": azure_client})
    client.on_connect = on_connect_local 
    client.on_message = on_message_local
    client.connect('127.0.0.1', 1883, 60)
    client.loop_forever()
