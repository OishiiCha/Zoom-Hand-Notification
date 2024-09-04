# Zoom-Hand-Notification
Quick app for KH to notify the speaker that there are hands up on zoom so they can look at the tablet, the rpi pico device would be connected to a 3v led strip, code for pico currently in debug mode to use the debug light, pin will need to be changed for the led strip in code

![image](https://github.com/user-attachments/assets/88a38e2c-8110-42a0-b919-281d3c46e387)


### Installer Command
```
pyinstaller --onefile --windowed --name "Zoom Hand" --icon="images/logo.ico" --add-data "images:images" --hidden-import=serial --hidden-import=serial.tools.list_ports --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --add-data "qt_toggle.py:." zoom_hand_v3.py  
```
