import time
import socket
from gpiozero import DigitalOutputDevice

stepper_coil_pins = [
	DigitalOutputDevice(25),
	DigitalOutputDevice(8),
	DigitalOutputDevice(7),
	DigitalOutputDevice(1)
]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen_address = ('127.0.0.1', 5005)
sock.bind(listen_address)
sock.setblocking(False)

speed = 250
requested_steps = 0

try:
	print("Starting motor rotation. Press Ctrl+C to exit.")
	
	active_coil_idx = 0
	while True:
		try:
			data, addr = sock.recvfrom(1024)
			if requested_steps != 0:
				print('Request cancelled.')
			requested_steps = int(data.decode())
			print(f'New request: {requested_steps} steps.')
		except BlockingIOError:
			pass
		
		if requested_steps > 0:
			stepper_coil_pins[active_coil_idx].off()
			active_coil_idx += 1
			active_coil_idx %= 4
			stepper_coil_pins[active_coil_idx].on()
			requested_steps -= 1
			if requested_steps == 0:
				print('Request completed.')
		elif requested_steps < 0:
			stepper_coil_pins[active_coil_idx].off()
			active_coil_idx -= 1
			active_coil_idx %= 4
			stepper_coil_pins[active_coil_idx].on()
			requested_steps += 1
			if requested_steps == 0:
				print('Request completed.')
		
		time.sleep(1 / speed)

except KeyboardInterrupt:
	print('Exiting.')
