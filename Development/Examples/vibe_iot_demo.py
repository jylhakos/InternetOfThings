# vibe_iot_demo.py
# Vibe: "Make a script for Raspberry Pi that sends temp data to AWS IoT"
#
# Description:
#   This script demonstrates a "Vibe Coding" workflow for IoT development.
#   It connects a Raspberry Pi to AWS IoT Core via MQTT and publishes
#   simulated environmental sensor data at a fixed interval.
#
# Requirements:
#   pip install AWSIoTPythonSDK
#
# AWS Prerequisites:
#   1. Create an AWS IoT Thing in the AWS Console.
#   2. Download the device certificate, private key, and root CA.
#   3. Update the configuration constants below with your endpoint and file paths.

import time
import json
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# ---------------------------------------------------------------------------
# 1. Setup Vibe (Configurations)
# ---------------------------------------------------------------------------
ENDPOINT   = "your-iot-endpoint.iot.us-east-1.amazonaws.com"
CLIENT_ID  = "PiVibeCoder"
PATH_TO_CERT = "/home/pi/certs/certificate.pem.crt"
PATH_TO_KEY  = "/home/pi/certs/private.pem.key"
PATH_TO_ROOT = "/home/pi/certs/rootCA.pem"
TOPIC      = "raspberrypi/vibe"

# ---------------------------------------------------------------------------
# 2. Vibe Action: Connect to AWS IoT Core
# ---------------------------------------------------------------------------
myAWSIoTMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)

myAWSIoTMQTTClient.connect()
print("Vibe Check: Connected to AWS IoT!")

# ---------------------------------------------------------------------------
# 3. Vibe Loop: Simulate & Send sensor data
# ---------------------------------------------------------------------------
while True:
    data = {
        "timestamp":   time.time(),
        "temperature": round(random.uniform(20.0, 30.0), 2),  # Simulated Celsius
        "humidity":    round(random.uniform(40.0, 70.0), 2),  # Simulated %RH
        "status":      "vibing"
    }
    myAWSIoTMQTTClient.publish(TOPIC, json.dumps(data), 1)
    print(f"Sent: {data}")
    time.sleep(5)
