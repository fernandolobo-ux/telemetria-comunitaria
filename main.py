from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

TOKEN = "NIfnx0mQU6xN3Ad1w_neWIubhUfHtP2g2uIid25gH4ZDqg5uTdvcS1EyReqmHCqlFM_ge5OQ5E_GEd73OLsufQ=="
ORG = "humanidad"
BUCKET = "telemetria"
URL = "http://influxdb:8086"

influx = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = influx.write_api(write_options=SYNCHRONOUS)
query_api = influx.query_api()

def al_recibir_mensaje(client, userdata, msg):
    nivel = float(msg.payload.decode())
    sitio = msg.topic.split("/")[1]
    punto = Point("nivel_agua").tag("sitio", sitio).field("nivel", nivel)
    write_api.write(bucket=BUCKET, record=punto)
    print(f"Guardado: {sitio} -> {nivel}%")

mqtt_client = mqtt.Client()
mqtt_client.on_message = al_recibir_mensaje

@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client.connect("mosquitto", 1883)
    mqtt_client.subscribe("sensores/+/nivel")
    mqtt_client.loop_start()
    print("Backend escuchando sensores por MQTT.")
    yield
    mqtt_client.loop_stop()

app = FastAPI(title="Telemetría Comunitaria", lifespan=lifespan)

@app.get("/lecturas/{sitio}")
def historial(sitio: str):
    query = f'''
    from(bucket: "{BUCKET}")
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
    from(bucket: "{BUCKET}")
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