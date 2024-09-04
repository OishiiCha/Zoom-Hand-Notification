import os
import sys
import serial
import serial.tools.list_ports
import time
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QIcon, QColor, QPainter, QBrush, QPen

class QToggle(QWidget):
    clicked = pyqtSignal(bool)  # Custom signal for when the toggle is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 25)
        self.checked = False
        self.setStyleSheet("background-color: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set colors
        bg_color = QColor("#4CAF50" if self.checked else "#494A4A")
        circle_color = QColor("#FFFFFF")

        # Draw rounded rectangle background
        rect = self.rect()
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

        # Draw circle
        circle_rect = QRectF(
            rect.x() + (rect.width() - rect.height()) * self.checked,
            rect.y(),
            rect.height(),
            rect.height()
        )
        painter.setBrush(QBrush(circle_color))
        painter.drawEllipse(circle_rect)

    def mousePressEvent(self, event):
        self.checked = not self.checked
        self.update()
        self.clicked.emit(self.checked)

class ZoomHandApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ser = None
        self.led_on = False
        self.flashing = False
        self.device_connected = False

        self.initUI()
        self.start_connection_thread()

    def initUI(self):
        self.setWindowTitle("")

        self.setGeometry(100, 100, 300, 150)  # Narrower window

        icon_path = self.resource_path('images/logo.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.notify_label = QLabel("Notify Speaker", self)
        self.notify_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notify_label.setStyleSheet("font-size: 14px; color: white; font-weight: bold;")
        self.layout.addWidget(self.notify_label)

        self.frame = QFrame()
        self.frame_layout = QHBoxLayout(self.frame)
        self.layout.addWidget(self.frame)

        self.toggle = QToggle(self)
        self.toggle.setFixedSize(50, 25)
        self.toggle.clicked.connect(self.toggle_led)
        self.frame_layout.addWidget(self.toggle)

        self.indicator = Indicator(self)
        self.indicator.setFixedSize(50, 50)
        self.frame_layout.addWidget(self.indicator)

        self.led_status_label = QLabel("", self)
        self.led_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.led_status_label.setStyleSheet("font-size: 12px; color: white;")
        self.layout.addWidget(self.led_status_label)

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
                    self.indicator.update_color("orange")
                    self.toggle.checked = False
                    self.toggle.update()
                    self.stop_flashing()
                    self.led_status_label.setText("")  # Clear the LED status

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
                    self.update_status(f"Connected on {port.device}")
                    return
                s.close()
            except (OSError, serial.SerialException):
                continue

    def toggle_led(self, checked):
        if not self.ser:
            print("Device not connected.")
            return

        if checked:
            self.ser.write(b'ON\r')
            self.ser.flush()
            print("Sent: ON")
            self.led_on = True
            self.start_flashing()
            self.led_status_label.setText("LED strip is active")
        else:
            self.ser.write(b'OFF\r')
            self.ser.flush()
            print("Sent: OFF")
            self.led_on = False
            self.stop_flashing()
            self.indicator.update_color("orange")
            self.led_status_label.setText("")

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

            current_color = self.indicator.color_name
            new_color = "white" if current_color == "#00FF00" else "#00FF00"
            self.indicator.update_color(new_color)
            QTimer.singleShot(flash_speed, flash)

        flash()

    def update_status(self, message):
        self.setWindowTitle(message)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def closeEvent(self, event):
        if self.led_on and self.ser:
            self.ser.write(b'OFF\r')
            self.ser.flush()
        self.stop_flashing()
        if self.ser:
            self.ser.close()

class Indicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = QColor("orange")
        self.color_name = "orange"

    def update_color(self, color_name):
        self.color_name = color_name
        self.color = QColor(color_name)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawEllipse(5, 5, 40, 40)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ZoomHandApp()
    main_window.show()
    sys.exit(app.exec())

