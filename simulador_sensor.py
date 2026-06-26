import paho.mqtt.client as mqtt
import time
import random

client = mqtt.Client()
client.connect("mosquitto", 1883)

print("Simulando sensor de nivel de agua. Ctrl+C para detener.")

while True:
    nivel = round(random.uniform(20, 95), 1)
    client.publish("sensores/los_cocos/nivel", nivel)
    print(f"Enviado: nivel = {nivel}%")
    time.sleep(5)