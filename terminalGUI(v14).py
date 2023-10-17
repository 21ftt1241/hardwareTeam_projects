import tkinter as tk
from tkinter import *
from functools import partial
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import time
import datetime
import mysql.connector
from pyzbar.pyzbar import decode
import pigpio
import RPi.GPIO as GPIO
import datetime
import random


# Replace these values with your database configuration
#Dont open this when streaming
db_config = {
    "host": "167.172.75.119",
    "user": "hardware-Team",
    "password": "hardware123",
    "database": "drop_n_go"
}

# Establish a connection to the database
connection = mysql.connector.connect(**db_config)

# Initialize servo IO pins
servo1 = 12
servo2 = 16

# Setup pigpio and frequency of servo(s)
pwm = pigpio.pi()
pwm.set_mode(servo1, pigpio.OUTPUT)
pwm.set_mode(servo2, pigpio.OUTPUT)

# ~ locker number : servo pin
lockerNumArr = {
    "OS1":12,
    "OS2":16
}

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 18

#set GPIO pins for sensor 2
GPIO_TRIGGER2 = 25
GPIO_ECHO2 = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
GPIO.setup(GPIO_ECHO2, GPIO.IN)


# ~ trig1:echo1
# ~ insert new sensor pin num here
locker_sens = {
    "OS1": {
    "Trig": 23,
    "Echo": 18
    },
    "OS2":{
    "Trig": 25,
    "Echo": 24
    }
}

# Define a video capture object
vid = cv2.VideoCapture(0)

# Declare the width and height in variables
width, height = 640, 480

# Set the width and height
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

def distance(echo_value, trig_value):
    # set Trigger to HIGH
    GPIO.output(trig_value, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(trig_value, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(echo_value) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(echo_value) == 1:
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
            
        insert_query = "INSERT INTO log (log_id, rent_id, log_message) VALUES (NULL, %s, %s)"
        cursor.execute(insert_query, (rentid, log_message))
        connection.commit()
            
        print("Log updated:", log_message)
        
        cursor.close()
        
def genPass(lockerNum):
    newPass = random.randint(1000, 9999)
    print("genPass", lockerNum)
    print(newPass)
    if connection.is_connected():
        cursor = connection.cursor()
        update_query = "UPDATE locker SET locker_otp = %s WHERE locker_number = %s"
        cursor.execute(update_query, (newPass, lockerNum))
        connection.commit()
        
        cursor.close()
        
def timer(door_sens):
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if door_sens >= 10:
            if elapsed_time >= 10:
                messagebox.showerror("BEWARE", "CLOSE THE LOCKER DOOR WHEN NOT IN USE")
                break
            else:
                print(elapsed_time)
                break
            print(door_sens)
    
        
def locker_open(servoVal):
    pwm.set_servo_pulsewidth(servoVal, 500)
    pwm.set_PWM_frequency(servoVal, 50)
    print("Servo lock open")
    
def locker_close(servoVal):
    pwm.set_servo_pulsewidth(servoVal, 1500)
    pwm.set_PWM_frequency(servoVal, 50)
    print("Servo lock close")
    

def locker_checker(lockernum, otp):
    try:
        # Establish a new connection for this function
        new_connection = mysql.connector.connect(**db_config)
        
        if new_connection.is_connected():
            cursor = new_connection.cursor()
            query = """
                SELECT r.rent_id, l.locker_number
                FROM rentdetail r
                INNER JOIN locker l ON r.locker_id = l.locker_id
                WHERE l.locker_number = %s AND l.locker_otp =%s
                AND (r.start_rent <= %s AND r.end_rent >=%s);
            """
            current_date = datetime.date.today()
            
            formatted_date = current_date.strftime('%Y-%m-%d')
            
            cursor.execute(query, (lockernum, otp, current_date, current_date))
            row = cursor.fetchone()
            print(row)
            
            if row is None:
                messagebox.showerror("Invalid Data", "The Locker Number / OTP is Invalid")
                return
            elif row is not None:
                messagebox.showinfo("Valid Data", "Locker " + row[1] + " is now unlocked")
                
            # Assign rentid to a var
            rentid = row[0]
            
            # Assign locker number to a var
            lockerNum = row[1]
            
            # Code to open and close the door
            if lockerNum in lockerNumArr:
                servoVal = lockerNumArr[lockerNum]
                lockerSensor = locker_sens[lockerNum]
                echo_value = lockerSensor["Echo"]
                trig_value = lockerSensor["Trig"]
                while True:
                    door_sens = distance(echo_value, trig_value)
                    time.sleep(0.5)
                    while door_sens <= 10:
                        door_sens = distance(echo_value, trig_value)
                        time.sleep(1)
                        locker_open(servoVal)
                        print("Locker door closed")
                        if door_sens > 10:
                            break
                        
                    while door_sens >= 10:
                        time.sleep(0.5)
                        door_sens = distance(echo_value, trig_value)
                        print("locker door open")
                        # ~ timer(door_sens)
                        if door_sens < 10:
                            time.sleep(2)
                            locker_close(servoVal)
                            updateLog(rentid)  # Updates log
                            genPass(lockerNum)
                            break
                    break
            else:
                print("Invalid Data")
                messagebox.showerror("Locker unavailable", "Locker is not available")
                return
                
            rentid = 0
            lockernNum = 0
            cursor.close()
            
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        # Close the cursor and connection, even if an exception occurs
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'new_connection' in locals() and new_connection.is_connected():
            new_connection.close()

# ~ main design
main_bg="#ffab1b"

# ~ main btn design
btn_font = ('Helvetica', 18, "bold")
btn_fg = "#ffffff"
btn_activ_fg = "#ffffff"
btn_activ_bg = "#499de6"
btn_bg = "#1e96ff"

#title Design
title_font = ('Helvetica' , 28, "bold")
title_fg = "#0325a1"

# ~ subtitle design
sub_fg = "#0325a1"

#side button
sd_btn_font = ('Helvetica', 14, "bold")
        
# ~ basically holds all the other page and manage the page swap
class MainFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # ~ self.attributes('-fullscreen', True)
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
        Frame.__init__(self, parent, bg=main_bg)
        self.controller = controller
        self.controller.geometry("1024x600")
        
        title_lbl = Label(self, text="Drop N' Go", bg=main_bg ,fg=title_fg, font=title_font)
        title_lbl.pack(pady=15, padx=10)

        button_frame = Frame(self, bg=main_bg)
        button_frame.pack(fill=BOTH, anchor=CENTER, expand=True)

        self.button1 = Button(button_frame, text="OTP", width=27, height=13,
                              command=lambda: controller.show_frame(PassPage)
                              , bg=btn_bg, activebackground=btn_activ_bg, font=btn_font, fg=btn_fg, activeforeground=btn_activ_fg)
        self.button1.place(relx=0.30, rely=0.5, anchor=CENTER)

        self.button2 = Button(button_frame, text="QR Code", width=27, height=13,
                              command=lambda: controller.show_frame(QrPage)
                              , bg=btn_bg, activebackground=btn_activ_bg, font=btn_font, fg=btn_fg, activeforeground=btn_activ_fg)
        self.button2.place(relx=0.70, rely=0.5, anchor=CENTER)

class PassPage(tk.Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg="#ffa91e")
        self.controller = controller
        self.controller.geometry("1024x600")
        label = Label(self, text="Input Locker Number and OTP here", font=title_font, bg=main_bg, fg=title_fg)
        label.pack(pady=10, padx=10)

        label2 = Label(self, text="Locker Num", bg="orange", font=sd_btn_font, fg=sub_fg)
        label2.place(relx=0.5, rely=0.25, anchor=CENTER)
        self.lockernum = tk.StringVar()  # Make lockernum a class attribute
        idEntry = tk.Entry(self, textvariable=self.lockernum)
        idEntry.place(relx=0.5, rely=0.30, anchor=CENTER)
        idEntry.focus()

        label3 = Label(self, text="OTP", bg="orange", font=sd_btn_font, fg=sub_fg)
        label3.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.otp = tk.StringVar()  # Make otp a class attribute
        otpEntry = tk.Entry(self, textvariable=self.otp, show="*")
        otpEntry.place(relx=0.5, rely=0.45, anchor=CENTER)
    
        openbutton = Button(self, text="Open Locker", command=lambda: self.openLocker(self.lockernum, self.otp)
                                                    , bg=btn_bg, activebackground=btn_activ_bg, fg=btn_fg, activeforeground=btn_activ_fg, font=sd_btn_font)  # Pass the user input
        openbutton.place(relx=0.5, rely=0.55, anchor=CENTER)
        
        self.qr_page_instance = QrPage(parent, controller)  # Create an instance of QrPage
        
        # ~ used to refresh the user input when going back to home
        def goHome():
            idEntry.delete(0, END)
            otpEntry.delete(0, END)
            idEntry.focus()
            controller.show_frame(StartPage)
            
        homebutton = Button(self, text="Back to Home", command=goHome
                            , bg=btn_bg, activebackground=btn_activ_bg, fg=btn_fg, activeforeground=btn_activ_fg, font=sd_btn_font)
        homebutton.place(relx=0.5, rely=0.8, anchor=CENTER)
        
    def openLocker(self, lockernum, otp):
        lockernum = lockernum.get()
        otp = otp.get()
        
        locker_checker(lockernum, otp)
        
        # ~ check the validity of Locker Num and OTP)
        
class QrPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#ffa91e")
        self.controller = controller
        self.controller.geometry("1024x600")
        
        self.frame = None

        label = tk.Label(self, text="Scan QR code here", bg=main_bg ,fg=title_fg, font=title_font)
        label.pack(pady=10, padx=10)

        # ~ this label widget is used to display the video feed
        self.label_widget = tk.Label(self, bg="#ffa91e")  # Define label_widget as an instance variable
        self.label_widget.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

        self.button_bck = tk.Button(self, text="Back to Home", command=lambda: self.close_camera_and_return(controller)
                                    , bg=btn_bg, activebackground=btn_activ_bg, fg=btn_fg, activeforeground=btn_activ_fg, font=sd_btn_font)
        self.button_bck.place(relx=0.75, rely=0.12, anchor=tk.CENTER)

        self.button_camera = tk.Button(self, text="Toggle QR Scanner", command=self.toggle_camera
                                    , bg=btn_bg, activebackground=btn_activ_bg, fg=btn_fg, activeforeground=btn_activ_fg, font=sd_btn_font)
        self.button_camera.place(relx=0.25, rely=0.12, anchor=tk.CENTER)

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
            photo_image = ImageTk.PhotoImage(image=Image.fromarray(opencv_image))
            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)
            
            if decoded_objects:
                data = decoded_objects[0].data.decode('utf-8')
                lockernum, otp = data.split(',')

                cursor = connection.cursor()
                query = """
                    SELECT r.rent_id, l.locker_number
                    FROM rentdetail r
                    INNER JOIN locker l ON r.locker_id = l.locker_id
                    WHERE l.locker_number = %s AND l.locker_otp = %s
                """
                cursor.execute(query, (lockernum, otp))
                row = cursor.fetchone()
                
                if row is None:
                    messagebox.showerror("Invalid Data", "The Locker Number / OTP is Invalid")
                    return
                elif row is not None:
                    messagebox.showinfo("Valid Data", "Locker " + row[1] + " is now unlocked")
                
                print(row)
                # ~ code to open and close the door
                locker_checker(lockernum, otp)
                        
                self.close_camera()
            
            else:
                print("No Data")
 
            self.label_widget.after(30, self.camera_feed_loop)
            
        else:
            print("Camera shutting down")
            self.close_camera()
            
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
