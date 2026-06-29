import os
import ssl
import time
import random
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HIVEMQ_HOST")
PUERTO = int(os.getenv("HIVEMQ_PUERTO", 8883))
USUARIO = os.getenv("HIVEMQ_USUARIO")
PASSWORD = os.getenv("HIVEMQ_PASSWORD")

client = mqtt.Client()
client.username_pw_set(USUARIO, PASSWORD)
client.tls_set(tls_version=ssl.PROTOCOL_TLS)
client.connect(HOST, PUERTO)

print("Simulando sensor hacia HiveMQ Cloud. Ctrl+C para detener.")

while True:
    nivel = round(random.uniform(20, 95), 1)
    client.publish("sensores/los_cocos/nivel", nivel)
    print(f"Enviado: nivel = {nivel}%")
    time.sleep(5)