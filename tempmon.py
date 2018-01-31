"""
Thanks to this project for base methods to read the temperature
https://github.com/timfernando/temperature-serve-pi/blob/master/temperature.py
"""

from os import listdir, system
import sys
import json
import config as cfg
import requests
import socket
import time

TEMPMON_VERSION = 0.1

API_SECRET = cfg.api['api_secret']
API_URL_STORE = cfg.api['url_store']
API_URL_NAME = cfg.api['url_name']
LOCATION_ID = cfg.api['location_id']

DEVICE_FOLDER = "/sys/bus/w1/devices/"
DEVICE_SUFFIX = "/w1_slave"
WAIT_INTERVAL = 0.2

system('modprobe w1-gpio')
system('modprobe w1-therm')

print('\n\n\n')
print('#############################')
print("TempMon v" + str(TEMPMON_VERSION) + " is running.")
print('#############################')


def main():
    #print("DEVICE")
    #print(socket.gethostname() + '\n')
    #print("LOCATION ID")
    #print(LOCATION_ID + '\n')
    #print("LOCATION NAME")
    #location_name = get_location_name()
    #print(location_name + '\n')
    #print('#############################')

    device = guess_temperature_sensor();

    while 1 < 2:
        temp_c = read_temperature_c(device)
        #print('#############################')
        #print("TEMP_C")
        #print(temp_c)
        temp_f = round((temp_c * 1.8) + 32.0, 1)
        #print("TEMP_F")
        #print(temp_f)

        store(temp_c, temp_f)
        time.sleep(60)


def get_location_name():

    response = requests.post(API_URL_NAME, data={
        'api_secret': API_SECRET,
        'location_id': LOCATION_ID
    })

    return response.text


def store(c, f):

    response = requests.post(API_URL_STORE, data={
        'api_secret': API_SECRET,
        'location_id': LOCATION_ID,
        'celsius': c,
        'fahrenheit': f
    })

    print(response.text)


def guess_temperature_sensor():
    # Try guessing the location of the installed temperature sensor

    devices = listdir(DEVICE_FOLDER)
    devices = [device for device in devices if device.startswith('28-')]
    if devices:
        #print('#############################')
        #print "Found", len(devices), "devices which appear to be temperature sensors."
        return DEVICE_FOLDER + devices[0] + DEVICE_SUFFIX
    else:
        sys.exit("Sorry, no temperature sensors found")


def raw_temperature(device):
    # Get a raw temperature reading from the temperature sensor

    raw_reading = None
    with open(device, 'r') as sensor:
        raw_reading = sensor.readlines()
    return raw_reading


def read_temperature_c(device):
    # Keep trying to read the temperature from the sensor until it returns a valid result

    lines = raw_temperature(device)

    # Keep retrying till we get a YES from the thermometer
    # 1. Make sure that the response is not blank
    # 2. Make sure the response has at least 2 lines
    # 3. Make sure the first line has a "YES" at the end
    while not lines and len(lines) < 2 and lines[0].strip()[-3:] != 'YES':
        # If we haven't got a valid response, wait for the WAIT_INTERVAL
        # (seconds) and try again.
        time.sleep(WAIT_INTERVAL)
        lines = raw_temperature()

    # Split out the raw temperature number
    temperature = lines[1].split('t=')[1]

    # Check that the temperature is not invalid
    if temperature != -1:
        temperature_c = round(float(temperature) / 1000.0, 1)

    return temperature_c

main()
