import paho.mqtt.client as mqtt
import ssl
import time

HOST = "cf5ac14812294708b343eb2f387e95f6.s1.eu.hivemq.cloud"
PUERTO = 8883
USUARIO = "uma_net_backend"
PASSWORD = "uma_net_backendPass1"

def al_conectar(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado a HiveMQ Cloud correctamente")
        client.subscribe("test/conexion")
    else:
        print(f"❌ Falló la conexión, código: {rc}")

def al_recibir_mensaje(client, userdata, msg):
    print(f"📩 Mensaje recibido: {msg.payload.decode()}")

client = mqtt.Client()
client.username_pw_set(USUARIO, PASSWORD)
client.tls_set(tls_version=ssl.PROTOCOL_TLS)
client.on_connect = al_conectar
client.on_message = al_recibir_mensaje

client.connect(HOST, PUERTO)
client.loop_start()

time.sleep(2)
client.publish("test/conexion", "Hola desde el Codespace")
time.sleep(3)

client.loop_stop()
print("Prueba terminada.")