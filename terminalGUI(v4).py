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

# Define a video capture object
vid = cv2.VideoCapture(0)
# ~ detector = cv2.QRCodeDetector()

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

        self.button1 = Button(button_frame, text="Use Password", width=35, height=20,
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

        openbutton = Button(self, text="Open Locker", command=lambda: self.openLocker(self.userid, self.userpass))  # Pass the user input
        openbutton.place(relx=0.5, rely=0.55, anchor=CENTER)

        button1 = Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))
        button1.place(relx=0.5, rely=0.8, anchor=CENTER)
        
    def openLocker(self, userid, userpass):
        entered_userid = userid.get()
        entered_userpass = userpass.get()
        # ~ connection = mysql.connector.connect(**db_config)

        # ~ used to check if the user id and pass is valid(available in db)
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT * FROM user WHERE user_id = %s AND unique_pass = %s"
            cursor.execute(query, (entered_userid, entered_userpass))
            row = cursor.fetchone()
            lockerNum = row[2]
            lockerStatus = row[3]
            if row:
                print("Opening locker: ", lockerNum)

                if lockerStatus == "Empty":
                    newLockerStatus = "Occupied"
                    query = "UPDATE user SET locker_status = %s WHERE user_id = %s"
                    cursor.execute(query, (newLockerStatus, entered_userid))
                    connection.commit()
                    print("Change locker ", lockerNum, " status to ", newLockerStatus)
                elif lockerStatus == "Occupied":
                    newLockerStatus = "Empty"
                    query = "UPDATE user SET locker_status = %s WHERE user_id = %s" 
                    cursor.execute(query, (newLockerStatus, entered_userid))
                    connection.commit()
                    print("Change locker ", lockerNum, " status to ", newLockerStatus)
            else:
                print("Invalid UserID or Password")
            cursor.close()
            # ~ connection.close()
        else:
            print("Database connection error")
            # ~ connection.close()

class QrPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="orange")
        self.controller = controller
        self.controller.geometry("1024x600")
        
        self.data = ''
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
        
        # ~ self.button_bck.config(state=tk.DISABLED)
    def camera_feed_loop(self):
        # ~ if the camera is on for more than 30 seconds, it will automatically shut itself down
        if self.camera_running and time.time() - self.start_time <= 30:
        # ~ if self.camera_running:
            
            data, decoded_info, _ = '', '', ''
            _, frame = '', ''
            _, frame = vid.read()
            qr_detector = cv2.QRCodeDetector()
            data, decoded_info, _ = qr_detector.detectAndDecode(frame)

            # ~ configure the raspi cam settings
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

            # ~ capture the feed as image and parse it as a var to be displayed on the label_widget
            captured_image = Image.fromarray(opencv_image)
            photo_image = ImageTk.PhotoImage(image=captured_image)
            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)

            if data:
                # ~ Used to interact with the db object
                cursor = connection.cursor()
                user_id_dat, user_pass_dat, user_locker_num = data.split(',')
                query = "SELECT * FROM user WHERE user_id = %s AND unique_pass = %s"
                cursor.execute(query, (user_id_dat, user_pass_dat))

                # interact to the next row of the database
                row = cursor.fetchone()
                lockerNum = row[2]
                lockerStatus = row[3]
                if row:
                    print("")
                    print("Valid user")
                    print("Opening Locker ", lockerNum)
                    # ~ temp code to check the data captured from the qr
                    print("user ID: ", user_id_dat)
                    print("User pass: ", user_pass_dat)
                    print("Opening locker: ", lockerNum)
                    if lockerStatus == "Empty":
                        newLockerStatus = "Occupied"
                        query = "UPDATE user SET locker_status = %s WHERE user_id = %s"
                        cursor.execute(query, (newLockerStatus, user_id_dat))
                        connection.commit()
                        print("Change locker ", lockerNum, " status to ", newLockerStatus)
                        print("")
                        row = ''
                    else:
                        newLockerStatus = "Empty"
                        query = "UPDATE user SET locker_status = %s WHERE user_id = %s"
                        cursor.execute(query, (newLockerStatus, user_id_dat))
                        connection.commit()
                        print("Change locker ", lockerNum, " status to ", newLockerStatus)
                        print("")
                        row = ''
                
                # ~ time.sleep(20)
                cursor.close()
                self.close_camera()
            
            else:
                print("No Data")
 
            self.label_widget.after(30, self.camera_feed_loop)
            data = ''

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
        data, decoded_info, _ = '', '', ''
        _, frame = '', ''
        self.camera_feed_loop()
        
    def close_camera(self):

        print("close cam")
        self.camera_running = False
        self.button_bck.config(state=tk.NORMAL)

        # Reset the label_widget
        self.label_widget.photo_image = None
        self.label_widget.configure(image=None)
        data, decoded_info, _ = '', '', ''
        _, frame = '', ''

    def close_camera_and_return(self, controller):
        # ~ self.close_camera()
        controller.show_frame(StartPage)


app = MainFrame()
app.mainloop()

# Release the video capture object when the app is closed
connection.close()
vid.release()
