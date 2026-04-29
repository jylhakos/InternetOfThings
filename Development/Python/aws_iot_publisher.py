# aws_iot_publisher.py
# Vibe Prompt: "Make a script for Raspberry Pi that sends temp data to AWS IoT"
#
# Description:
#   Production-ready implementation that extends Examples/vibe_iot_demo.py.
#   Connects a Raspberry Pi to AWS IoT Core via MQTT and publishes
#   environmental sensor data at a configurable interval.
#   Configuration is loaded from environment variables to keep credentials
#   out of source code. A simulated sensor is provided by default; see the
#   read_sensor() function for instructions to substitute a real DHT22.
#
# Requirements:
#   pip install -r Python/requirements.txt
#
# Configuration — export these environment variables before running:
#
#   AWS_IOT_ENDPOINT        Your AWS IoT custom endpoint
#                           Example: abc123.iot.us-east-1.amazonaws.com
#   AWS_IOT_CLIENT_ID       MQTT client identifier (default: PiVibeCoder)
#   AWS_IOT_CERT            Path to device certificate (.pem.crt)
#   AWS_IOT_KEY             Path to private key (.pem.key)
#   AWS_IOT_ROOT_CA         Path to Amazon Root CA certificate (.pem)
#   AWS_IOT_TOPIC           MQTT publish topic (default: raspberrypi/vibe)
#   PUBLISH_INTERVAL_SEC    Seconds between publishes (default: 5)
#
# Usage:
#   export AWS_IOT_ENDPOINT="your-endpoint.iot.us-east-1.amazonaws.com"
#   export AWS_IOT_CERT="/home/pi/certs/certificate.pem.crt"
#   export AWS_IOT_KEY="/home/pi/certs/private.pem.key"
#   export AWS_IOT_ROOT_CA="/home/pi/certs/rootCA.pem"
#   source .venv/bin/activate
#   python3 Python/aws_iot_publisher.py

import os
import time
import json
import random
import signal
import logging

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — loaded from environment variables
# ---------------------------------------------------------------------------
ENDPOINT     = os.environ.get("AWS_IOT_ENDPOINT",  "your-endpoint.iot.us-east-1.amazonaws.com")
CLIENT_ID    = os.environ.get("AWS_IOT_CLIENT_ID", "PiVibeCoder")
PATH_TO_CERT = os.environ.get("AWS_IOT_CERT",      "/home/pi/certs/certificate.pem.crt")
PATH_TO_KEY  = os.environ.get("AWS_IOT_KEY",       "/home/pi/certs/private.pem.key")
PATH_TO_ROOT = os.environ.get("AWS_IOT_ROOT_CA",   "/home/pi/certs/rootCA.pem")
TOPIC        = os.environ.get("AWS_IOT_TOPIC",     "raspberrypi/vibe")
INTERVAL     = int(os.environ.get("PUBLISH_INTERVAL_SEC", "5"))

# ---------------------------------------------------------------------------
# Graceful shutdown on SIGINT (Ctrl+C) and SIGTERM
# ---------------------------------------------------------------------------
_running = True


def _handle_signal(signum, frame):
    global _running
    logger.info("Shutdown signal received. Stopping publish loop.")
    _running = False


signal.signal(signal.SIGINT,  _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


# ---------------------------------------------------------------------------
# MQTT client factory
# ---------------------------------------------------------------------------
def build_client() -> AWSIoTMQTTClient:
    client = AWSIoTMQTTClient(CLIENT_ID)
    client.configureEndpoint(ENDPOINT, 8883)
    client.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
    # Reconnection: initial 1 s, maximum 32 s, stable after 20 s connected
    client.configureAutoReconnectBackoffTime(1, 32, 20)
    # Unlimited offline queue; drain at 2 messages/second after reconnect
    client.configureOfflinePublishQueueing(-1)
    client.configureDrainingFrequency(2)
    client.configureConnectDisconnectTimeout(10)
    client.configureMQTTOperationTimeout(5)
    return client


# ---------------------------------------------------------------------------
# Sensor reading
#
# This function simulates a DHT22 sensor using random values.
# To use real hardware on Raspberry Pi, replace the body with:
#
#   import Adafruit_DHT
#   DHT_SENSOR = Adafruit_DHT.DHT22
#   DHT_PIN    = 4  # GPIO pin number
#
#   def read_sensor() -> dict:
#       humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
#       if humidity is None or temperature is None:
#           raise RuntimeError("DHT22 sensor read failed.")
#       return {
#           "temperature": round(temperature, 2),
#           "humidity":    round(humidity, 2),
#       }
#
# Also add Adafruit-DHT to Python/requirements.txt.
# ---------------------------------------------------------------------------
def read_sensor() -> dict:
    return {
        "temperature": round(random.uniform(20.0, 30.0), 2),  # Celsius
        "humidity":    round(random.uniform(40.0, 70.0), 2),  # %RH
    }


# ---------------------------------------------------------------------------
# Main publish loop
# ---------------------------------------------------------------------------
def main():
    logger.info("Connecting to AWS IoT Core at %s ...", ENDPOINT)
    client = build_client()
    client.connect()
    logger.info("Connected. Publishing to topic '%s' every %d s.", TOPIC, INTERVAL)

    while _running:
        reading = read_sensor()
        payload = {
            "timestamp": time.time(),
            "device_id": CLIENT_ID,
            **reading,
            "status": "vibing",
        }
        client.publish(TOPIC, json.dumps(payload), 1)
        logger.info("Published: %s", payload)
        time.sleep(INTERVAL)

    client.disconnect()
    logger.info("Disconnected. Session ended.")


if __name__ == "__main__":
    main()
