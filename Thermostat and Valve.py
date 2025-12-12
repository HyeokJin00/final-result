#-------------------------Valve---------------------------
from IO7FuPython import ConfiguredDevice
import json
import time
import uComMgr32
from machine import Pin

relay_ac = Pin(16, Pin.OUT)
relay_heat = Pin(15, Pin.OUT)

relay_ac.value(0)
relay_heat.value(0)

lastPub = 0

def handleCommand(topic, msg):
    global lastPub
    
    try:
        payload_str = msg.decode('utf-8')
        
        if "{" in payload_str:
            jo = json.loads(payload_str)
            if 'd' in jo:
                payload = jo['d']
            else:
                payload = payload_str
        else:
            payload = payload_str
            
    except:
        payload = str(msg)
    
    if "AC_ON" in str(payload):
        relay_ac.value(1)
        print(">>> AC ON")
    elif "AC_OFF" in str(payload):
        relay_ac.value(0)
        print(">>> AC OFF")
        
    if "HEAT_ON" in str(payload):
        relay_heat.value(1)
        print(">>> HEAT ON")
    elif "HEAT_OFF" in str(payload):
        relay_heat.value(0)
        print(">>> HEAT OFF")

    lastPub = - device.meta['pubInterval']

nic = uComMgr32.startWiFi('valve2') 
device = ConfiguredDevice()
device.setUserCommand(handleCommand)
device.connect()

TARGET_TOPIC = b"iot3/valve2/cmd/+/fmt/json"
device.client.subscribe(TARGET_TOPIC)
print(f">>> Ready. Subscribed: {TARGET_TOPIC}")

lastPub = time.ticks_ms() - device.meta['pubInterval']

while True:
    if not device.loop():
        break
        
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        
        status_payload = {
            'd': {
                'ac': 'on' if relay_ac.value() else 'off',
                'heater': 'on' if relay_heat.value() else 'off'
            }
        }


        device.publishEvent('status', json.dumps(status_payload))


#--------------------------------------------Thermostat ---------------------------------------------
from IO7FuPython import ConfiguredDevice
import json
import time
import uComMgr32
from machine import Pin, ADC, Timer
import st7789
import tft_config
import vga2_8x16 as font1
import vga1_bold_16x32 as font2
import dht

sensor = dht.DHT22(Pin(16))

temperature = 0
humidity = 0
value = 71 

tft = tft_config.config(3, buffer_size=64*64*2)
tft.init()
tft.fill(st7789.BLACK)

tft.text(font2, 'Thermostat', 85, 5, st7789.WHITE)
tft.text(font1, 'Target      : ', 65, 50, st7789.WHITE)
tft.text(font1, 'Temperature : ', 65, 80, st7789.WHITE)
tft.text(font1, 'Humidity    : ', 65, 110, st7789.WHITE)

def r2t(r):
    return r * 0.1960784 + 10

def t2r(t):
    return (t - 10) / 0.1960784

lastMeasured = -2001

def measureData():
    global temperature, humidity, lastMeasured
    if (time.ticks_ms() - 2000) > lastMeasured:
        lastMeasured = time.ticks_ms()
        try:
            sensor.measure()
            temperature = sensor.temperature()
            humidity = sensor.humidity()
        except OSError as e:
            print("Sensor read failed:", e)
        
        display()

def display():
    tft.text(font1, f'{round(r2t(value),2)}', 200, 50, st7789.WHITE)
    tft.text(font1, f'{round(temperature, 2)}', 200, 80, st7789.WHITE)
    tft.text(font1, f'{round(humidity, 2)}', 200, 110, st7789.WHITE)

def handleCommand(topic, msg):
    global lastPub, value
    try:
        jo = json.loads(str(msg,'utf8'))
        
        if ("target" in jo['d']):
            value = t2r(int(jo['d']['target']))
            lastPub = - device.meta['pubInterval']
            display()
            print(f">>> Target updated: {jo['d']['target']}")
            
    except Exception as e:
        print(f"Command error: {e}")

nic = uComMgr32.startWiFi('io7ther
