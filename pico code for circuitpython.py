import board
import pwmio
import time
import digitalio
import supervisor

led = pwmio.PWMOut(board.GP2, frequency=1000)

pulsing = False
pulse_frequency = 1
pulse_step = 10
pulse_delay = 1 / (pulse_frequency * 1000 / pulse_step)

def update_pulse():
    for duty_cycle in range(0, 65536, pulse_step * 64):
        if not pulsing:
            break
        led.duty_cycle = duty_cycle
        time.sleep(pulse_delay)
    for duty_cycle in range(65535, -1, -pulse_step * 64):
        if not pulsing:
            break
        led.duty_cycle = duty_cycle
        time.sleep(pulse_delay)

while True:
    if pulsing:
        update_pulse()
        
    if supervisor.runtime.serial_bytes_available:
        command = input().strip()
        if command == "ON":
            pulsing = True
        elif command == "OFF":
            pulsing = False
            led.duty_cycle = 0

