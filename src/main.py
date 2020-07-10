import pycom
from network import WLAN
import urequests as requests
import machine
import time
import config
from machine import Pin
from dht import DHT
from udm import UDM
from lgt import LGT

# -------------------------------------- Boring connection and setup
TOKEN       = config.TOKEN # ubidots token
SLEEPY_TIME = config.DELAY  # time between samples
TRAY        = config.TRAY_SPACE # space between distance sensor and tray

wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.INT_ANT)

# Assign your Wi-Fi credentials
wlan.connect(config.WIFI_SSID
            , auth=(WLAN.WPA2
            , config.WIFI_PASS)
            , timeout=5000)

while not wlan.isconnected ():
    print("Beeb boop!\n")
    machine.idle()

print("Connected to Wifi! :D\n")

print("Connecting sensors...\n")

distance_sensor  = UDM(echo_pin='P21', trigger_pin='P20')
temp_sensor      = DHT(pin='P10')
light_sensor     = LGT(pin='P15')

time.sleep(2)
print("Let's a go!")

# -------------------------------------- Funky functions

# make a json package of the data
def build_json(variable1, value1, variable2, value2, variable3, value3, variable4, value4):
    try:
        data = {variable1: {"value": value1},
                variable2: {"value": value2},
                variable3: {"value": value3},
                variable4: {"value": value4}}
        return data
    except:
        return None

# and send the package to ubidots
# using their REST API https://ubidots.com/docs/api/
def post_var(device, temp, humidity, plant_height, light):
    try:
        url = "https://industrial.api.ubidots.com/"
        url = url + "api/v1.6/devices/" + device
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        data = build_json(
        "temperature", temp,
        "height", plant_height,
        "humidity", humidity,
        "light", light)

        if data is not None:
            print(data)
            req = requests.post(url=url, headers=headers, json=data)
            return req.json()
        else:
            pass
    except:
        pass

# Gather data from sensors
def get_env():
    result = temp_sensor.read()
    while not result.is_valid():
        time.sleep(.5)
        result = temp_sensor.read()
    temp = result.temperature
    humidity = result.humidity
    return temp, humidity

def get_height():
    # Height of greens = difference between tray and sensor value
    height = TRAY - distance_sensor.median_mm(TRAY)
    return height


def get_light():
    return light_sensor.median()

# -------------------------------------- Actually doing stuff

while True:
    temp, humidity = get_env()
    plant_height = get_height()
    light = get_light()

    print('Temp:', temp)
    print('RH:', humidity)
    print("Plant height : ", plant_height)
    print("light = %5.1f" % light)
    print("")

    post_var("Bellsprout", temp, humidity, plant_height, light)
    time.sleep(SLEEPY_TIME)
