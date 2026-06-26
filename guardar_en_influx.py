import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

TOKEN = "NIfnx0mQU6xN3Ad1w_neWIubhUfHtP2g2uIid25gH4ZDqg5uTdvcS1EyReqmHCqlFM_ge5OQ5E_GEd73OLsufQ=="
ORG = "humanidad"
BUCKET = "telemetria"
URL = "http://influxdb:8086"

cliente_influx = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = cliente_influx.write_api(write_options=SYNCHRONOUS)

def al_recibir_mensaje(client, userdata, msg):
    nivel = float(msg.payload.decode())
    sitio = msg.topic.split("/")[1]  # ej: los_cocos
    punto = Point("nivel_agua").tag("sitio", sitio).field("nivel", nivel)
    write_api.write(bucket=BUCKET, record=punto)
    print(f"Guardado en InfluxDB: {sitio} -> {nivel}%")

client = mqtt.Client()
client.on_message = al_recibir_mensaje
client.connect("mosquitto", 1883)
client.subscribe("sensores/+/nivel")

print("Escuchando y guardando en InfluxDB. Ctrl+C para detener.")
client.loop_forever()