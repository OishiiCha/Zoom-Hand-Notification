import select
import sys
import machine
import time

# Set up the onboard LED with PWM
led = machine.Pin(25, machine.Pin.OUT)
pwm = machine.PWM(led)
pwm.freq(1000)  # Set PWM frequency to 1 kHz

# Initialize state
pulsing = False
pulse_frequency = 1  # Frequency of pulsing in Hz
pulse_step = 10
pulse_delay = 1 / (pulse_frequency * 1000 / pulse_step)  # Delay for each step

# Function to update the LED pulsing
def update_pulse():
    global pwm_duty_cycle
    for duty_cycle in range(0, 1024, pulse_step):
        if not pulsing:
            break
        pwm.duty_u16(duty_cycle * 64)  # Map range [0, 1023] to [0, 65535]
        time.sleep(pulse_delay)
    for duty_cycle in range(1023, -1, -pulse_step):
        if not pulsing:
            break
        pwm.duty_u16(duty_cycle * 64)  # Map range [0, 1023] to [0, 65535]
        time.sleep(pulse_delay)

# Set up the poll object
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

# Main loop
while True:
    if pulsing:
        update_pulse()  # Update the pulse effect while pulsing is active

    poll_results = poll_obj.poll(10)  # Poll with a small timeout
    if poll_results:
        command = sys.stdin.readline().strip()
        if command == "ON":
            pulsing = True
        elif command == "OFF":
            pulsing = False
            pwm.duty_u16(0)  # Turn off the LED by setting duty cycle to 0
        sys.stdout.write(f"LED is now {'ON' if pulsing else 'OFF'}\r")

