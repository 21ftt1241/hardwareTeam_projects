import cv2
import customtkinter as ctk
from tkinter import *
from PIL import Image, ImageTk


def open_camera():
	cap = cv2.VideoCapture(0)
	detector = cv2.QRCodeDetector()
	
	# ~ loop so that the program could decode the qr
	while True:
		_, img = cap.read()
		data, decoded_info, _ = detector.detectAndDecode(img)

		if data:
			print("data found:", data)
			print("Decoded info:", decoded_info)
			break	
		cv2.imshow("code detector", img)
		if(cv2.waitKey(1) == ord("q")):
			break
	
			
	# When the code is stopped the code below closes all the applications/windows that the above has created
	cap.release()
	cv2.destroyAllWindows()

app = ctk.CTk()
app.title("Camera")
app.geometry("400x150")

camera_frame = ctk.CTkLabel(app, text=" ")
camera_frame.pack()

button = ctk.CTkButton(app, text="Open Camera", command=open_camera)
button.pack(padx=20, pady=20)

app.mainloop()


		



