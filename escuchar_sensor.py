import paho.mqtt.client as mqtt

def al_recibir_mensaje(client, userdata, msg):
    print(f"Recibido en '{msg.topic}': {msg.payload.decode()}%")

client = mqtt.Client()
client.on_message = al_recibir_mensaje
client.connect("mosquitto", 1883)
client.subscribe("sensores/los_cocos/nivel")

print("Escuchando datos del sensor. Ctrl+C para detener.")
client.loop_forever()