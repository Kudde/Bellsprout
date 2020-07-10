import time
import machine
from machine import Pin

# Light Sensor
class LGT:

    def __init__(self, pin):
        adc = machine.ADC()
        self.light_pin = adc.channel(pin=pin)

        time.sleep(1.0)

    def measure(self):
        value = self.light_pin()
        # LoPy  has 1.1 V input range for ADC
        light = value
        return light

    def median(self, itr = 1000):
        samples = []
        for count in range(itr):
            samples.append(self.measure())

        samples = sorted(samples)
        median = samples[int(len(samples)/2)]

        return int(median)
