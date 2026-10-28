import time
import socket
from gpiozero import DigitalInputDevice

control_left_pin = DigitalInputDevice(pin = 21, pull_up = True)
control_right_pin = DigitalInputDevice(pin = 20, pull_up = True)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
target_address = ('127.0.0.1', 5005)

def request_rotation(steps: int):
	sock.sendto(str(steps).encode(), target_address)

def on_left_edge(rising: bool):
	if not rising:
		return
	print('Requesting left rotation')
	request_rotation(512)


def on_right_edge(rising: bool):
	if not rising:
		return
	print('Requesting right rotation')
	request_rotation(-512)


try:
	print("Listening for input. Press Ctrl+C to exit.")
	
	prev_left_state: bool = False
	prev_right_state: bool = False
	while True:
		left_state = control_left_pin.value
		right_state = control_right_pin.value
		
		if left_state != prev_left_state:
			on_left_edge(left_state)
		if right_state != prev_right_state:
			on_right_edge(right_state)
		
		prev_left_state = left_state
		prev_right_state = right_state
		
		time.sleep(0.05)

except KeyboardInterrupt:
	print('Exiting.')
	sock.close()
