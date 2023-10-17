from gpiozero import Buzzer
from time import sleep
buzz = Buzzer(21)
    
# ~ while True:
    # ~ buzz.beep()

for _ in range(2):
    buzz.on()
    sleep(0.1)
    buzz.off()
    sleep(0.1)
