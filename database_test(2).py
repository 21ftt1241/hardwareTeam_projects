import tkinter as tk
import mysql.connector

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Connection App")

        self.connection = None  # Initialize the connection as None

        self.connect_button = tk.Button(root, text="Connect to DB", command=self.open_connection)
        self.connect_button.pack()

        self.disconnect_button = tk.Button(root, text="Disconnect", command=self.close_connection)
        self.disconnect_button.pack()
        
    def open_connection(self):
        if self.connection is None:
            try:
                db_config = {
                    "host": "192.168.0.188",
                    "user": "mus_pi",
                    "password": "21ftt1241",
                    "database": "pi_test"
                }
                self.connection = mysql.connector.connect(**db_config)
                print("Connected to the database")
            except mysql.connector.Error as err:
                print("Error:", err)
        else:
            print("Connection already open")

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Connection closed")
        else:
            print("No connection to close")

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()
