import tkinter as tk
from tkinter import *
from functools import partial
import cv2
from PIL import Image, ImageTk

# Define a video capture object
vid = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

# Declare the width and height in variables
width, height = 800, 600

# Set the width and height
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Create a GUI app
app = Tk()

# Create a label and display it on app
# ~ label_widget = Label(app)
# ~ label_widget.pack()

# Create a function to open camera and
# display it in the label_widget on app


def open_camera():
	# Capture the video frame by frame/
    _, frame = vid.read()
    # ~ detect the qr and decode it
    data, decoded_info, _ = detector.detectAndDecode(frame)

    # Convert image from one color space to other
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

	# Capture the latest frame and transform to image
    captured_image = Image.fromarray(opencv_image)

	# Convert captured image to photoimage
    photo_image = ImageTk.PhotoImage(image=captured_image)

	# Displaying photoimage in the label
    label_widget.photo_image = photo_image

	# Configure image in the label
    label_widget.configure(image=photo_image)

	# Repeat the same process after every 10 seconds
    label_widget.after(10, open_camera)

    # ~ print the data
    if data:
        print ("Data found:", data)


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


class StartPage(Frame):
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


class PassPage(Frame):
    def openLocker(self, userid, userpass):
        print("UserID: ", userid.get())
        print("User OTP: ", userpass.get())
        return

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

        label3 = Label(self, text="One Time Password", bg="orange")
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



class QrPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg="orange")
        self.controller = controller
        self.controller.geometry("1024x600")
        label = Label(self, text="Scan QR code here")
        label.pack(pady=10, padx=10)

        button1 = Button(self, text="Back to Home",
                         command=lambda: controller.show_frame(StartPage))
        button1.place(relx=0.5, rely=0.8, anchor=CENTER)
        
        label_widget = Label(self)
        label_widget.pack()
        
        # Create a button to open the camera in GUI app
        button1 = Button(app, text="Open Camera", command=open_camera)
        button1.place(relx=0.5, rely=0.5, anchor=CENTER)


app = MainFrame()
app.mainloop()
