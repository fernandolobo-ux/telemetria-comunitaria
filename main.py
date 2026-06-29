import os
import ssl
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

load_dotenv()

HIVEMQ_HOST = os.getenv("HIVEMQ_HOST")
HIVEMQ_PUERTO = int(os.getenv("HIVEMQ_PUERTO", 8883))
HIVEMQ_USUARIO = os.getenv("HIVEMQ_USUARIO")
HIVEMQ_PASSWORD = os.getenv("HIVEMQ_PASSWORD")

INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")

influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx.write_api(write_options=SYNCHRONOUS)
query_api = influx.query_api()

def al_recibir_mensaje(client, userdata, msg):
    nivel = float(msg.payload.decode())
    sitio = msg.topic.split("/")[1]
    punto = Point("nivel_agua").tag("sitio", sitio).field("nivel", nivel)
    write_api.write(bucket=INFLUX_BUCKET, record=punto)
    print(f"Guardado: {sitio} -> {nivel}%")

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(HIVEMQ_USUARIO, HIVEMQ_PASSWORD)
mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLS)
mqtt_client.on_message = al_recibir_mensaje

@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client.connect(HIVEMQ_HOST, HIVEMQ_PUERTO)
    mqtt_client.subscribe("sensores/+/nivel")
    mqtt_client.loop_start()
    print("Backend conectado a HiveMQ Cloud, escuchando sensores.")
    yield
    mqtt_client.loop_stop()

app = FastAPI(title="Telemetría Comunitaria", lifespan=lifespan)

@app.get("/lecturas/{sitio}")
def historial(sitio: str):
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -24h)
      |> filter(fn: (r) => r._measurement == "nivel_agua" and r.sitio == "{sitio}")
      |> filter(fn: (r) => r._field == "nivel")
    '''
    tablas = query_api.query(query)
    resultado = [
        {"momento": str(registro.get_time()), "nivel": registro.get_value()}
        for tabla in tablas for registro in tabla.records
    ]
    return {"sitio": sitio, "lecturas": resultado}

@app.get("/lecturas/{sitio}/ultimo")
def ultimo(sitio: str):
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "nivel_agua" and r.sitio == "{sitio}")
      |> filter(fn: (r) => r._field == "nivel")
      |> last()
    '''
    tablas = query_api.query(query)
    for tabla in tablas:
        for registro in tabla.records:
            return {"sitio": sitio, "nivel": registro.get_value(), "momento": str(registro.get_time())}
    raise HTTPException(status_code=404, detail="No hay datos para este sitio todavía")