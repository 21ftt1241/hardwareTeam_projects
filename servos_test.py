import pigpio
import tkinter as tk
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# Pin numbers
servo = 18

# Initialize pigpio
pwm = pigpio.pi()

# Configure the GPIO pin for servo pulses
pwm.set_mode(servo, pigpio.OUTPUT)
pwm.set_servo_pulsewidth(servo, 1500)  # Initial position

# Function to toggle servo position
def toggle_servo_position():
    current_pulsewidth = pwm.get_servo_pulsewidth(servo)
    new_pulsewidth = 1500 if current_pulsewidth == 500 else 500  # Adjust these values according to your servo's datasheet
    pwm.set_servo_pulsewidth(servo, new_pulsewidth)

# Create Tkinter window
root = tk.Tk()
root.title("Servo Control")

# Create button
toggle_button = tk.Button(root, text="Toggle Servo", command=toggle_servo_position)
toggle_button.pack(pady=20)


def close_window():
    root.destroy()

# Set up window close behavior
root.protocol("WM_DELETE_WINDOW", close_window)

# Start Tkinter main loop
root.mainloop()

# Clean up
pwm.set_servo_pulsewidth(servo, 0)  # Set servo pulsewidth to 0 before stopping
pwm.stop()
