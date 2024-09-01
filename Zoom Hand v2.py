import os
import sys
import tkinter as tk
import serial
import serial.tools.list_ports
import time
import threading

class ZoomHandApp:
    def __init__(self, root):
        self.root = root
        self.ser = None
        self.led_on = False
        self.flashing = False
        self.device_connected = False

        self.initialize_ui()
        self.start_connection_thread()

    def start_connection_thread(self):
        self.connection_thread = threading.Thread(target=self.manage_connection, daemon=True)
        self.connection_thread.start()

    def manage_connection(self):
        while True:
            if not self.ser:
                self.find_pico_port()
            else:
                try:
                    self.ser.write(b'PING\r')
                    response = self.ser.read_until().strip()
                    if not response:
                        raise serial.SerialException("No response from device")
                except (OSError, serial.SerialException):
                    print("Device disconnected. Reconnecting...")
                    self.update_status("Device disconnected. Reconnecting...")
                    self.ser.close()
                    self.ser = None
                    self.device_connected = False
                    self.update_indicator("orange")
                    self.button.config(text="Raise hand for Zoom", bg="#007BFF")
                    self.stop_flashing()

            time.sleep(2)

    def find_pico_port(self):
        self.update_status("Looking for device...")
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                s = serial.Serial(port.device, 9600, timeout=1)
                time.sleep(2)
                s.write(b'PING\r')
                response = s.read_until().strip()
                if response:
                    print(f"Connected to {port.device}")
                    self.ser = s
                    self.device_connected = True
                    self.update_status(f"Device connected on {port.device}")
                    return
                s.close()
            except (OSError, serial.SerialException):
                continue

    def toggle_led(self):
        if not self.ser:
            print("Device not connected.")
            return

        if self.led_on:
            self.ser.write(b'OFF\r')
            self.ser.flush()
            print("Sent: OFF")
            self.button.config(text="Raise hand for Zoom", bg="#007BFF")
            self.led_on = False
            self.update_indicator("orange")
            self.stop_flashing()
        else:
            self.ser.write(b'ON\r')
            self.ser.flush()
            print("Sent: ON")
            self.button.config(text="Lower hand for Zoom", bg="#007BFF")
            self.led_on = True
            self.start_flashing()

    def start_flashing(self):
        self.flashing = True
        self.flash_step()

    def stop_flashing(self):
        self.flashing = False

    def flash_step(self):
        if not self.led_on:
            return

        flash_speed = 500

        def flash():
            if not self.flashing or not self.led_on:
                return

            current_color = self.canvas.itemcget(self.indicator_circle, 'fill')
            new_color = "white" if current_color == "#00FF00" else "#00FF00"
            self.update_indicator(new_color)
            self.root.after(flash_speed, flash)

        flash()

    def update_indicator(self, color):
        self.canvas.itemconfig(self.indicator_circle, fill=color)

    def update_status(self, message):
        self.status_label.config(text=message)

    def initialize_ui(self):
        self.root.title("Notify Speaker of Zoom Hands")
        self.root.configure(bg="white")

        icon_path = self.resource_path('images/logo.ico')

        try:
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except tk.TclError as e:
            print(f"Error setting icon: {e}")

        self.root.resizable(False, False)

        frame = tk.Frame(self.root, bg="white")
        frame.pack(pady=20, padx=20)

        self.button = tk.Button(frame, text="Raise hand for Zoom", command=self.toggle_led,
                                font=('Helvetica', 12), width=20, height=2,
                                bg="#007BFF", fg="white", relief="flat")
        self.button.pack(side=tk.LEFT, padx=(0, 20))

        self.canvas = tk.Canvas(frame, width=50, height=50, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT)

        self.indicator_circle = self.canvas.create_oval(5, 5, 45, 45, fill="orange", outline="black")

        self.status_label = tk.Label(self.root, text="Looking for device...", bg="white", font=('Helvetica', 10))
        self.status_label.pack(side=tk.BOTTOM, pady=(0, 10))

        self.root.geometry("400x150")
        self.root.eval('tk::PlaceWindow . center')

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def on_closing(self):
        if self.led_on and self.ser:
            self.ser.write(b'OFF\r')
            self.ser.flush()
        self.stop_flashing()
        if self.ser:
            self.ser.close()
        self.root.destroy()

root = tk.Tk()
app = ZoomHandApp(root)

root.protocol("WM_DELETE_WINDOW", app.on_closing)

root.mainloop()

