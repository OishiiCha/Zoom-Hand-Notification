import os
import sys
import tkinter as tk
import serial
import serial.tools.list_ports
import time

class ZoomHandApp:
    def __init__(self, root):
        self.root = root
        self.ser = self.find_pico_port()
        if not self.ser:
            print("Pico not found. Please check the connection.")
            sys.exit()
        
        self.led_on = False
        self.flashing = False

        self.initialize_ui()

    def find_pico_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                s = serial.Serial(port.device, 9600, timeout=1)
                time.sleep(2)  # Allow time for connection
                s.write(b'PING\r')  # Send a simple command
                response = s.read_until().strip()
                if response:
                    print(f"Connected to {port.device}")
                    return s
                s.close()
            except (OSError, serial.SerialException):
                continue
        return None

    def toggle_led(self):
        if self.led_on:
            self.ser.write(b'OFF\r')
            self.ser.flush()
            print("Sent: OFF")
            self.button.config(text="Raise hand for Zoom", bg="#007BFF")  # Maintain blue color
            self.led_on = False
            self.update_indicator("orange")  # Amber for inactive
            self.stop_flashing()  # Stop flashing effect
        else:
            self.ser.write(b'ON\r')
            self.ser.flush()
            print("Sent: ON")
            self.button.config(text="Lower hand for Zoom", bg="#007BFF")  # Maintain blue color
            self.led_on = True
            self.start_flashing()  # Start flashing effect

    def start_flashing(self):
        """Start flashing the indicator between white and green."""
        self.flashing = True
        self.flash_step()

    def stop_flashing(self):
        """Stop flashing the indicator."""
        self.flashing = False

    def flash_step(self):
        """Flash between white and green."""
        if not self.led_on:
            return

        # Define the flash parameters
        flash_speed = 500  # Interval in milliseconds

        def flash():
            if not self.flashing or not self.led_on:
                return
            
            current_color = self.canvas.itemcget(self.indicator_circle, 'fill')
            new_color = "white" if current_color == "#00FF00" else "#00FF00"
            self.update_indicator(new_color)
            self.root.after(flash_speed, flash)

        flash()

    def update_indicator(self, color):
        """Update the color of the status indicator circle."""
        self.canvas.itemconfig(self.indicator_circle, fill=color)

    def initialize_ui(self):
        self.root.title("Notify Speaker of Zoom Hands")
        self.root.configure(bg="white")
        
        # Set the icon
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, 'images', 'logo.ico')
        else:
            icon_path = os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')

        try:
            self.root.iconbitmap(icon_path)
        except tk.TclError as e:
            print(f"Error setting icon: {e}")

        self.root.resizable(False, False)

        # Create a frame to hold the button and the indicator
        frame = tk.Frame(self.root, bg="white")
        frame.pack(pady=20, padx=20)

        # Create a button to toggle LED
        self.button = tk.Button(frame, text="Raise hand for Zoom", command=self.toggle_led,
                               font=('Helvetica', 12), width=20, height=2, 
                               bg="#007BFF", fg="white", relief="flat")
        self.button.pack(side=tk.LEFT, padx=(0, 20))

        # Create a canvas to draw the circle indicator
        self.canvas = tk.Canvas(frame, width=50, height=50, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT)

        # Draw the initial circle indicator (amber for not active)
        self.indicator_circle = self.canvas.create_oval(5, 5, 45, 45, fill="orange", outline="black")

        # Set window size and center on screen
        self.root.geometry("400x100")
        self.root.eval('tk::PlaceWindow . center')

    def on_closing(self):
        """Handle the window closing event."""
        if self.led_on:
            self.ser.write(b'OFF\r')  # Ensure LED is turned off
            self.ser.flush()
        self.stop_flashing()  # Stop flashing effect
        if self.ser:
            self.ser.close()  # Close the serial port
        self.root.destroy()

# Initialize the Tkinter root and start the application
root = tk.Tk()
app = ZoomHandApp(root)

# Bind the closing event to ensure the serial port is properly closed
root.protocol("WM_DELETE_WINDOW", app.on_closing)

# Start the Tkinter event loop
root.mainloop()
