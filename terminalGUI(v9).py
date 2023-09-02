import tkinter as tk
from tkinter import *
from functools import partial
import cv2
from PIL import Image, ImageTk
import time
import mysql.connector
from pyzbar.pyzbar import decode
import pigpio
import RPi.GPIO as GPIO
import datetime


# Replace these values with your database configuration
db_config = {
    "host": "192.168.0.194",
    "user": "mus_pi",
    "password": "21ftt1241",
    "database": "db_test"
}

# Establish a connection to the database
connection = mysql.connector.connect(**db_config)

# Initialize servo IO pins
servo = 12
servo2 = 16

# Setup pigpio and frequency of servo(s)
pwm = pigpio.pi()
pwm.set_mode(servo, pigpio.OUTPUT)
pwm.set_mode(servo2, pigpio.OUTPUT)

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    distance = round(distance, 2)
 
    return distance

def updateLog(rentid):
    if connection.is_connected():
        cursor = connection.cursor()

        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"Locker Accessed: {formatted_time}"
            
        insert_query = "INSERT INTO log (rent_id, log_message) VALUES (%s, %s)"
        cursor.execute(insert_query, (rentid, log_message))
        connection.commit()
            
        print("Log updated:", log_message)
        
        cursor.close()

# Define a video capture object
vid = cv2.VideoCapture(0)

# Declare the width and height in variables
width, height = 640, 480

# Set the width and height
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# ~ basically holds all the other page and manage the page swap
class MainFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PassPage, QrPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# ~ the global frame conf
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry("1024x600")

        button_frame = Frame(self, bg="orange")
        button_frame.pack(fill=BOTH, anchor=CENTER, expand=True)

        self.button1 = Button(button_frame, text="Use OTP", width=35, height=20,
                              command=lambda: controller.show_frame(PassPage))
        self.button1.place(relx=0.35, rely=0.5, anchor=CENTER)

        self.button2 = Button(button_frame, text="Use QR Code", width=35, height=20,
                              command=lambda: controller.show_frame(QrPage))
        self.button2.place(relx=0.65, rely=0.5, anchor=CENTER)


class PassPage(tk.Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg="orange")
        self.controller = controller
        self.controller.geometry("1024x600")
        label = Label(self, text="Input Rent ID and OTp here")
        label.pack(pady=10, padx=10)

        label2 = Label(self, text="Rent ID", bg="orange")
        label2.place(relx=0.5, rely=0.25, anchor=CENTER)
        self.rentid = tk.StringVar()  # Make rentid a class attribute
        idEntry = tk.Entry(self, textvariable=self.rentid)
        idEntry.place(relx=0.5, rely=0.30, anchor=CENTER)
        idEntry.focus()

        label3 = Label(self, text="OTP", bg="orange")
        label3.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.otp = tk.StringVar()  # Make otp a class attribute
        otpEntry = tk.Entry(self, textvariable=self.otp, show="*")
        otpEntry.place(relx=0.5, rely=0.45, anchor=CENTER)
    
        openbutton = Button(self, text="Open Locker", command=lambda: self.openLocker(self.rentid, self.otp))  # Pass the user input
        openbutton.place(relx=0.5, rely=0.55, anchor=CENTER)
        
        self.qr_page_instance = QrPage(parent, controller)  # Create an instance of QrPage
        
        # ~ used to refresh the user input when going back to home
        def goHome():
            idEntry.delete(0, END)
            otpEntry.delete(0, END)
            idEntry.focus()
            controller.show_frame(StartPage)
            
        homebutton = Button(self, text="Back to Home", command=goHome)
        homebutton.place(relx=0.5, rely=0.8, anchor=CENTER)
        
    def openLocker(self, rentid, otp):
        rentid = rentid.get()
        otp = otp.get()
        
        # ~ check the validity of rent id and OTP)
        if connection.is_connected():
            cursor = connection.cursor()
            query = """
                SELECT r.*, l.locker_number 
                FROM rentdetail r
                INNER JOIN locker l ON r.locker_id = l.locker_id
                WHERE r.rent_id = %s AND r.locker_otp = %s
            """
            cursor.execute(query, (rentid, otp))
            row = cursor.fetchone()
            
            locker_sens = distance()
            print(locker_sens)
            if row:
                lockerNum = row[8]
                print("Opening locker: ", lockerNum)
                
                # Servo door opening code
                if lockerNum == 105:
                    print("Valid user")
                    print("Opening Locker", lockerNum)
                    
                    while True:
                        while locker_sens <=15:
                            locker_sens = distance()
                            time.sleep(1)
                            self.qr_page_instance.locker1_open()
                    
                            if locker_sens > 15:
                                break
                            
                        while locker_sens >= 15:
                            print("Door Open")
                            locker_sens = distance()
                            if locker_sens < 15:
                                time.sleep(2)
                                self.qr_page_instance.locker1_close()
                                print("closing door")
                                updateLog(rentid) #updates log
                                break
                        break
                    
                elif lockerNum == 202:
                    print("Valid user")
                    print("Opening Locker", lockerNum)
                    
                    while True:
                        while locker_sens <=15:
                            locker_sens = distance()
                            time.sleep(1)
                            self.locker2_open()
                            if locker_sens > 15:
                                break
                            
                        while locker_sens >= 15:
                            print("Door Open")
                            locker_sens = distance()
                            if locker_sens < 15:
                                time.sleep(2)
                                self.locker2_close()
                                print("closing door")
                                updateLog(rentid) #updates log
                                break
                        break
            else:
                print("Invalid rentid or Password")
                cursor.close()
                # ~ connection.close()
        else:
            print("Database connection error")
            # ~ connection.close()
    
    # ~ def locker1_open(self):
        # ~ pwm.set_servo_pulsewidth(servo, 1500)
        # ~ pwm.set_PWM_frequency(servo, 50)
    
    # ~ def locker1_close(self):
        # ~ pwm.set_servo_pulsewidth(servo, 500)
        # ~ pwm.set_PWM_frequency(servo, 50)
        
    # ~ def locker2_open(self):
        # ~ pwm.set_servo_pulsewidth(servo2, 1500)
        # ~ pwm.set_PWM_frequency(servo2, 50)
    
    # ~ def locker2_close(self):
        # ~ pwm.set_servo_pulsewidth(servo2, 500)
        # ~ pwm.set_PWM_frequency(servo2, 50)
        
class QrPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="orange")
        self.controller = controller
        self.controller.geometry("1024x600")
        
        self.frame = None

        label = tk.Label(self, text="Scan QR code here")
        label.pack(pady=10, padx=10)

        # ~ this label widget is used to display the video feed
        self.label_widget = tk.Label(self, bg="orange")  # Define label_widget as an instance variable
        self.label_widget.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

        self.button_bck = tk.Button(self, text="Back to Home", command=lambda: self.close_camera_and_return(controller))
        self.button_bck.place(relx=0.75, rely=0.1, anchor=tk.CENTER)

        self.button_camera = tk.Button(self, text="Toggle QR Scanner", command=self.toggle_camera)
        self.button_camera.place(relx=0.25, rely=0.1, anchor=tk.CENTER)

        # Add a flag to control the camera feed
        self.camera_running = False

        # Store the start time when the camera is opened
        self.start_time = None

    def camera_feed_loop(self):
        # ~ if the camera is on for more than 30 seconds, it will automatically shut itself down
        if self.camera_running and time.time() - self.start_time <= 30:
            
            # ~ this code is used to skip the first few frames of the video feed
            # ~ i did this because everytime it loops, it keeps taking previous image_get
            # ~ sad
            frames_to_skip = 10
            for _ in range(frames_to_skip):
                _, _ = vid.read()
            
            _, frame = vid.read()
            decoded_objects = decode(frame)
            
            # ~ configure the raspi cam settings
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

            # ~ capture the feed as image and parse it as a var to be displayed on the label_widget
            captured_image = Image.fromarray(opencv_image)
            photo_image = ImageTk.PhotoImage(image=captured_image)
            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)
            
            locker_sens = distance()
            print(locker_sens)
            if decoded_objects:
                data = decoded_objects[0].data.decode('utf-8')
                rentid, otp = data.split(',')

                cursor = connection.cursor()
                query = """
                    SELECT r.*, l.locker_number 
                    FROM rentdetail r
                    INNER JOIN locker l ON r.locker_id = l.locker_id
                    WHERE r.rent_id = %s AND r.locker_otp = %s
                """
                cursor.execute(query, (rentid, otp))
                row = cursor.fetchone()
                if row:
                    lockerNum = row[8]
                    if lockerNum == 105:
                        print("Valid user")
                        print("Opening Locker", lockerNum)
                        while True:
                            while locker_sens <=15:
                                locker_sens = distance()
                                time.sleep(1)
                                self.locker1_open()
                                if locker_sens > 15:
                                    break
                            
                            while locker_sens >= 15:
                                print("Door Open")
                                locker_sens = distance()
                                if locker_sens < 15:
                                    time.sleep(2)
                                    self.locker1_close()
                                    print("closing door")
                                    updateLog(rentid) #updates log
                                    break
                            break
                    
                    # ~ Currently the sensor is being shared for blocker1_close
                    # ~ fix it fast
                    if lockerNum == 202:
                        print("Valid user")
                        print("Opening Locker", lockerNum)
                        while True:
                            while locker_sens <=15:
                                locker_sens = distance()
                                time.sleep(1)
                                self.locker2_open()
                                if locker_sens > 15:
                                    break
                            
                            while locker_sens >= 15:
                                print("Door Open")
                                locker_sens = distance()
                                if locker_sens < 15:
                                    time.sleep(2)
                                    self.locker2_close()
                                    print("closing door")
                                    updateLog(rentid) #updates log
                                    break
                            break
                        
                else:
                    print("Invalid QR code data")

                cursor.close()
                self.close_camera()
                # ~ vid.grab()
            
            else:
                print("No Data")
 
            self.label_widget.after(30, self.camera_feed_loop)
            
        else:
            print("Camera shutting down")
            self.close_camera()
    
    def locker1_open(self):
        pwm.set_servo_pulsewidth(servo, 1500)
        pwm.set_PWM_frequency(servo, 50)
    
    def locker1_close(self):
        pwm.set_servo_pulsewidth(servo, 500)
        pwm.set_PWM_frequency(servo, 50)
        
    def locker2_open(self):
        pwm.set_servo_pulsewidth(servo2, 1500)
        pwm.set_PWM_frequency(servo2, 50)
    
    def locker2_close(self):
        pwm.set_servo_pulsewidth(servo2, 500)
        pwm.set_PWM_frequency(servo2, 50)
            
    def toggle_camera(self):
        if self.camera_running:
            self.close_camera()
        else:
            self.open_camera()
 
    def open_camera(self):
        print("Open cam")
        self.start_time = time.time()  # Store the start time
        self.camera_running = True
        self.button_bck.config(state=tk.DISABLED)
        self.camera_feed_loop()
        
    def close_camera(self):
        print("close cam")
        self.camera_running = False
        self.button_bck.config(state=tk.NORMAL)

        # Reset the label_widget
        self.label_widget.photo_image = None
        self.label_widget.configure(image=None)

    def close_camera_and_return(self, controller):
        controller.show_frame(StartPage)


app = MainFrame()
app.mainloop()

# Release the video capture object when the app is closed
connection.close()
vid.release()
GPIO.cleanup()
