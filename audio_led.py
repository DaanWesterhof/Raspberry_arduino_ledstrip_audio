import pyaudio
import numpy as np

import time
import RPi.GPIO as GPIO

import smbus

import math

import matplotlib.pyplot as plt
import matplotlib.animation


import Adafruit_GPIO.SPI as SPI

pixel_multiplier = [
    [100, 0, 0, 0],
    [75, 55, 0, 0],
    [0, 100, 0, 0],
    [0, 75, 35, 0],
    [0, 0, 100, 0]
]


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 25000
RECORD_SECONDS = 100

I2C_CHANNEL = 1
address = 8
register = 0
bus = smbus.SMBus(I2C_CHANNEL)


p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

sub_bas = []
bass = []
low_mid = []
mid = []
high_mid = []
precsence = []
brilliance = []
max_val = 0
while True:
    for j in range(3):
        data = np.fromstring(stream.read(CHUNK, exception_on_overflow=False),dtype=np.int16)
        fft = abs(np.fft.fft(data).real)
        freq = np.fft.fftfreq(CHUNK,1.0/RATE)

        
        i = 0
        for value in fft:
            if freq[i] < 60:
                sub_bas.append(fft[i])
            elif freq[i] > 60 and freq[i] < 250:
                bass.append(fft[i])
            elif freq[i] > 250 and freq[i] < 500:
                low_mid.append(fft[i])
            elif freq[i] > 500 and freq[i] < 2000:
                mid.append(fft[i])
            elif freq[i] > 2000 and freq[i] < 4000:
                high_mid.append(fft[i])
            elif freq[i] > 4000:
                precsence.append(fft[i])
            i +=1

    data = [np.average(bass).round()*1.2, np.average(low_mid).round(), np.average(mid).round()*1.4, np.average(high_mid).round()*5, np.average(precsence).round()*8]
        
    index = data.index(max(data))
    max_val = np.maximum(max(data), max_val)
    pixel_multiplier[index][3] = (int((max(data)*1.0)/(max_val*1.0) * 100))
    print(pixel_multiplier[index])
    try:
        bus.write_i2c_block_data(address, register, pixel_multiplier[index] );
    except:
        print("couldnt find him")
        pass        
    print("current index {} curent value {} max_val: {}".format(index, max(data), max_val))
    sub_bas = []
    bass = []
    low_mid = []
    mid = []
    high_mid = []
    precsence = []
    brilliance = []
    
    
    

stream.stop_stream()
stream.close()
p.terminate()
print("done")
