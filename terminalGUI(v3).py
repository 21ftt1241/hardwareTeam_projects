import tkinter as tk
from tkinter import *
from functools import partial
import cv2
from PIL import Image, ImageTk
import time
import mysql.connector

# Replace these values with your database configuration
db_config = {
    "host": "192.168.0.188",
    "user": "mus_pi",
    "password": "21ftt1241",
    "database": "pi_test"
}

# Establish a connection to the database
connection = mysql.connector.connect(**db_config)

if connection.is_connected():
    cursor = connection.cursor()
    
    query = "SELECT * FROM user"
    cursor.execute(query)
    
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        
    cursor.close()

# ~ # Close the connection when you're done
# ~ connection.close()

class QrPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="orange")
        self.controller = controller
        self.controller.geometry("1024x600")
        
        label = tk.Label(self, text="Scan QR code here")
        label.pack(pady=10, padx=10)
        
        self.label_widget = tk.Label(self, bg="orange")  # Define label_widget as an instance variable
        self.label_widget.pack()
        
        button1 = tk.Button(self, text="Back to Home", command=lambda: self.close_camera_and_return(controller))
        button1.place(relx=0.1, rely=0.8, anchor=tk.CENTER)
        
        button_camera = tk.Button(self, text="Toggle Camera", command=self.toggle_camera)
        button_camera.place(relx=0.1, rely=0.6, anchor=tk.CENTER)
        
        # ~ close_camera = tk.Button(self, text="Close Camera", command=self.close_camera)
        # ~ close_camera.place(relx=0.1, rely=0.65, anchor=tk.CENTER)
        
        # Add a flag to control the camera feed
        self.camera_running = False
        
        # Store the start time when the camera is opened
        self.start_time = None
        
    def toggle_camera(self):
        if self.camera_running:
            self.close_camera()
        else:
            self.open_camera()
        
    def open_camera(self):     
        self.start_time = time.time()  # Store the start time
        self.camera_running = True
        self.camera_feed_loop()
        
        
    def camera_feed_loop(self):
        if self.camera_running and time.time() - self.start_time <= 30:  # Check if less than 30 seconds
            _, frame = vid.read()
            data, decoded_info, _ = detector.detectAndDecode(frame)
            # ~ user_id_dat, user_pass_dat = data.split(',')
            
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            captured_image = Image.fromarray(opencv_image)
            photo_image = ImageTk.PhotoImage(image=captured_image)
            
            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)
            
            # ~ connect to database
            connection = mysql.connector.connect(**db_config)
            
            if data:
                # ~ Used to interact with the db object
                cursor = connection.cursor()
                
                user_id_dat, user_pass_dat = data.split(',')
                query = "SELECT * FROM user WHERE user_id = %s AND unique_pass = %s"
                cursor.execute(query, (user_id_dat, user_pass_dat))
                
                # interact to the next row of the database
                row = cursor.fetchone()
                
                if row:
                    print("Valid user")
                else:
                    print("Invalid user")
                    
                print("Data acquired")
                print("user ID: ",user_id_dat)
                print("User pass: ",user_pass_dat)
                user_id_dat, user_pass_dat = (' ', ' ')
                
                self.close_camera()
                connection.close()
            else:
                print("No Data")
            
            self.label_widget.after(10, self.camera_feed_loop)
            
        else:
            self.close_camera()
        
    def close_camera(self):
        # ~ vid.release()
        self.camera_running = False
        
        #Reset the label_widget
        self.label_widget.photo_image = None
        self.label_widget.configure(image=None)
        
    def close_camera_and_return(self, controller):
        self.close_camera()
        controller.show_frame(StartPage)

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

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.controller.geometry("1024x600")

        button_frame = Frame(self, bg="orange")
        button_frame.pack(fill=BOTH, anchor=CENTER, expand=True)

        self.button1 = Button(button_frame, text="Use Password", width=35, height=20,
                              command=lambda: controller.show_frame(PassPage))
        self.button1.place(relx=0.35, rely=0.5, anchor=CENTER)

        self.button2 = Button(button_frame, text="Use QR Code", width=35, height=20,
                              command=lambda: controller.show_frame(QrPage))
        self.button2.place(relx=0.65, rely=0.5, anchor=CENTER)

class PassPage(tk.Frame):
    def openLocker(self, userid, userpass):
        entered_userid = userid.get()
        entered_userpass = userpass.get()
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor()

            query = "SELECT * FROM user WHERE user_id = %s AND unique_pass = %s"
            cursor.execute(query, (entered_userid, entered_userpass))

            row = cursor.fetchone()

            if row:
                print("Opening Locker")
            else:
                print("Invalid UserID or Password")

            cursor.close()
            connection.close()

        else:
            print("Database connection error")
            connection.close()

    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg="orange")
        self.controller = controller
        self.controller.geometry("1024x600")
        label = Label(self, text="Input locker ID and OTP here")
        label.pack(pady=10, padx=10)

        label2 = Label(self, text="User ID", bg="orange")
        label2.place(relx=0.5, rely=0.25, anchor=CENTER)
        self.userid = tk.StringVar()  # Make userid a class attribute
        idEntry = tk.Entry(self, textvariable=self.userid)
        idEntry.place(relx=0.5, rely=0.30, anchor=CENTER)

        label3 = Label(self, text="password", bg="orange")
        label3.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.userpass = tk.StringVar()  # Make userpass a class attribute
        otpEntry = tk.Entry(self, textvariable=self.userpass)
        otpEntry.place(relx=0.5, rely=0.45, anchor=CENTER)

        openbutton = Button(self, text="Open Locker",
                            command=lambda: self.openLocker(self.userid, self.userpass))  # Pass the user input
        openbutton.place(relx=0.5, rely=0.55, anchor=CENTER)

        button1 = Button(self, text="Back to Home",
                         command=lambda: controller.show_frame(StartPage))
        button1.place(relx=0.5, rely=0.8, anchor=CENTER)


# Define a video capture object
vid = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

# Declare the width and height in variables
width, height = 800, 600

# Set the width and height
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

app = MainFrame()
app.mainloop()

# Release the video capture object when the app is closed
vid.release()
