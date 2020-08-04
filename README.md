# Temperature_monitoring
### Temperature and humidity measuring, recording data in Azure Cloud 

 The goal was to create a system which consists several DHT22 sensors, ESP32 microcontrollers and a Raspberry Pi which collects the data from the ESP32 microcontrollers and forwards that to the cloud. 
</br></br>
### Communication between ESP32 and Raspberry Pi
Since the ESP32 uses micropython, the MQTT has to be imported from a specific file which is available on the following repository: https://github.com/micropython/micropython-lib/tree/master/umqtt.simple/umqtt. Copy the code from the simple python file and save it on the ESP32 as a separate file (it's recommended to save that file in a folder - named umqtt). 

For MQTT configuration on the ESP32 WIFI credentials (SSID + password) are needed to be defined to be able to connect to the network. The IP address of the MQTT broker is also needed (in this case the IP the Raspberry Pi). The topic and client id are required as well. 
</br></br>
### Communication between Raspberry Pi and IoT Hub
The data is forwarded via MQTT client to the IoT Hub. The Paho MQTT needs to be imported (and also installed on the machine). 
</br></br>
On the Raspberry Pi two clients are configured. There are a subscriber and a publisher client. The subscriber receives the messages from the microcontrollers and the publisher sends the data to the IoT Hub.
</br></br>
### ESP32 with battery
If the ESP32 is used with battery, the usage of the deep sleep mode is recommended, in order to extend the battery life. The ESP32 reboots after deep sleep mode. Therefore the code has to be on the board as a main file, because the main file is automatically executed after each reboot. If something happens during the process the ESP32 is accessible with webREPL from the browser (after webrepl is configured on the board).
</br></br>
### Timing on ESP32
You can determine how many readings you want to get on daily basis on the ESP32 and according to that the sleeping time will be calculated. If the main file is used there's no need to use any infinite loop, the board will iterate it automatically.
</br></br>
### Credentials
It is good practice to use credential files which contains sensitive data for example for security reasons. Moreover it makes the code much cleaner.
The credential file contains everything for both the ESP32 and the Raspberry Pi, which means it is needed on each device. However, it is recommended to keep only those credentials in the file which the actual device needs. 







