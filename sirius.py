import os
import cv2
import time
import asyncio
import numpy as np
import subprocess
from picamera import PiCamera
from time import sleep
from PIL import Image, ImageStat
from kasa import SmartPlug
from miio import Yeelight

image = '/current.jpg'
def takeNewPicture ():
    camera = PiCamera()
    camera.start_preview()
    sleep(2)
    camera.capture(image)
    camera.stop_preview()
    camera.close()
   
# Option 1, calculate brightness using ImageStat. While using this value, set brightness threshold to approx 65
def brightness(image):
   # Convert to greyscale
   img = Image.open(image).convert('L')
   stat = ImageStat.Stat(img)
   print(stat.mean)
   return stat.mean[0]

# Option 2, calculate brightness based on LAB color space
def LABColorSpace (image):
    img = cv2.imread(image)
    # Convert to LAB format
    L, A, B = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2LAB))
    # Normalize the result
    L = L/np.max(L)
    return np.mean(L)

######## Regular lamp connected via TP-Link smart plug #######
async def turnOnLamp(outsideBrightness):
    # IP address of the SmartPlus used by the lamp
    regularLamp = SmartPlug('<ipAddr>')
    print('outsideBrightness: ', outsideBrightness)
    if (outsideBrightness < 0.37) :
        await regularLamp.turn_on()
    elif (outsideBrightness > 0.55):
        await regularLamp.turn_off()
    # Get the latest properties of the lamp
    await regularLamp.update()
    print('light.is_on: ', regularLamp.is_on)

###### Mi LED Dimmable Lamp ######
def dimMiLight (outsideBrightness):
    # IP address and token of the Mi LED lamp
    dimmableLamp = Yeelight('<ipAddr>', '<token>')
    
    # Turn the lamp on the lamp and set brightness to an initial value of 20
    if not dimmableLamp.status().is_on and outsideBrightness < 0.53:
        dimmableLamp.set_brightness(20)
        dimmableLamp.toggle()
    print('outsideBrightness: ', outsideBrightness)

    # Adjust brightness if necessary
    if (outsideBrightness > 0.37 and outsideBrightness < 0.5):
        dimmableLamp.set_brightness(50)
    elif (outsideBrightness > 0.5 and outsideBrightness < 0.53):
        dimmableLamp.set_brightness(30)
    elif (outsideBrightness > 0.53):
        dimmableLamp.toggle()
    print('lamp.brightness: ', dimmableLamp.status().brightness)

###### MAIN ######
def controlAmbientLighting():
    # Option 1
    #currentBrightness = brightness(image)
   
    # Option 2
    outsideBrightness = LABColorSpace(image)
    
    # Control un-dimmable lamp
    asyncio.run(turnOnLamp(outsideBrightness))

    # Control dimmable lamp
    dimMiLight(outsideBrightness)
   

if __name__ == '__main__':
    while True:
        takeNewPicture()
        time.sleep(4)
        controlAmbientLighting()
        time.sleep(3)