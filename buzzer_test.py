import RPi.GPIO as GPIO
import time
BuzzerPin = 6
GPIO.setmode(GPIO.BCM)
GPIO.setup(BuzzerPin, GPIO.OUT)
GPIO.setwarnings(False)

Buzz = GPIO.PWM(BuzzerPin, GPIO.HIGH)
if __name__ == '__main__':
    try:
        while True:
            # ~ GPIO.output(BuzzerPin, GPIO.HIGH)
            # ~ GPIO.output(BuzzerPin, 880)
            # ~ time.sleep(0.5)
            # ~ GPIO.output(BuzzerPin, 450)
            # ~ time.sleep(0.5)
            
            
            Buzz.start(50)
    except KeyboardInterrupt:
        print("Stop buzzer")
        GPIO.output(BuzzerPin, GPIO.LOW)
        # ~ Buzz.stop()


#To setup the buzzer, just assign the corret pin, and set the current to it either high or low for on and off respectively


