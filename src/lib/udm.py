# https://core-electronics.com.au/tutorials/hc-sr04-ultrasonic-sensor-with-pycom-tutorial.html
# with some modification
import utime, time
import machine
from machine import Pin

# Ultrasonic distance measurment
class UDM:

    def __init__(self, echo_pin, trigger_pin):
        self.trigger = Pin(trigger_pin, mode=Pin.OUT)
        self.echo    = Pin(echo_pin, mode=Pin.IN)

        self.trigger(0)
        time.sleep(1.0)

    # returns the sounds time travelled
    # return -1 if time out
    def send_pulse(self):
        # trigger pulse LOW for 2us (just in case)
        self.trigger(0)
        utime.sleep_us(2)
        # trigger HIGH for a 10us pulse
        self.trigger(1)
        utime.sleep_us(10)
        self.trigger(0)

        # wait for the rising edge of the echo then start timer
        timeOut = utime.ticks_us()
        while self.echo() == 0:
            if utime.ticks_us() - timeOut > 1000:
                return -1
            pass
        start = utime.ticks_us()

        # wait for end of echo pulse then stop timer
        timeOut = utime.ticks_us()
        while self.echo() == 1:
            if utime.ticks_us() - timeOut > 1000:
                return -1
            pass
        finish = utime.ticks_us()


        # pause for 20ms to prevent overlapping echos
        utime.sleep_ms(20)


        return utime.ticks_diff(start, finish)



    def measure_cm(self):
        pulse_time = self.send_pulse()
        # calculate distance by using time difference between start and stop
        # speed of sound 340m/s or .034cm/us. Time * .034cm/us = Distance sound travelled there and back
        # divide by two for distance to object detected.
        distance = (pulse_time * .034)/2

        return distance

    def measure_mm(self):
        pulse_time = self.send_pulse()

        # To calculate the distance we get the pulse_time and divide it by 2
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.34320 mm/us that is 1mm each 2.91us
        # pulse_time // 2 // 2.91 -> pulse_time // 5.82 -> pulse_time * 100 // 582
        mm = pulse_time * 100 // 582
        return mm

    def median(self):
        samples = []
        for count in range(10):
            samples.append(self.measure_cm())

        samples = sorted(samples)
        median = samples[int(len(samples)/2)]

        # print(samples)

        return int(median)

    def median_mm(self, tray_height):

        samples = []
        for count in range(100):
            utime.sleep_us(100)
            m = self.measure_mm()
            if m < 0 or m >= tray_height: # filter outside of bounds
                continue
            else :
                samples.append(m)

        samples = sorted(samples)
        median = samples[int(len(samples)/2)]

        print(samples)

        return int(median)
