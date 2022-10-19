# -*- encoding: UTF-8 -*-
# Before running this command please check your PYTHONPATH is set correctly to the folder of your pynaoqi sdk.
from naoqi import ALProxy 
from nao_conf import *
import time

# Set the IP address of your NAO.
ip = IP

# Connect to ALSonar module.
sonarProxy = ALProxy("ALSonar", ip, 9559)

# Subscribe to sonars, this will launch sonars (at hardware level) and start data acquisition.
sonarProxy.subscribe("myApplication")

#Now you can retrieve sonar data from ALMemory.
memoryProxy = ALProxy("ALMemory", ip, 9559)

while True:
    # Get sonar left first echo (distance in meters to the first obstacle).
    print("Left:",memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value1"))

    # Same thing for right.
    print("Right:", memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value1"), "\n")
    time.sleep(1)


# Please read Sonar ALMemory keys section if you want to know the other values you can get.