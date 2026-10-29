import sys
import time
import socket
from gpiozero import DigitalOutputDevice

def is_num(value):
	try:
		int(value)
		return True
	except ValueError:
		return False

if len(sys.argv) != 6:
	print(
		'Required arguments: <stepper_coil_1_gpio_pin> <stepper_coil_2_gpio_pin> <stepper_coil_3_gpio_pin> <stepper_coil_4_gpio_pin> <comm_port>'
	)
	sys.exit()

stepper_coil_pins = []
try:
	for arg in sys.argv[1:5]:
		if not is_num(arg):
			print(f'{arg} is not a valid pin number.')
			sys.exit()
		
		pin_num = int(arg)
		stepper_coil_pins.append(DigitalOutputDevice(pin_num))
	
	if not is_num(sys.argv[5]):
		print(f'{sys.argv[5]} is not a valid port number.')
		sys.exit()
	
	comm_port = int(sys.argv[5])
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		sock.bind(('127.0.0.1', comm_port))
	except socket.error as e:
		print(f'Port {comm_port} is busy.')
		raise
	sock.setblocking(False)
	
	print(f'Driver active. Listening on port {comm_port}')
	
	speed = 250
	target_pos = 0
	current_pos = 0
	active_coil_idx = 0
	
	while True:
		try:
			while True:
				data, addr = sock.recvfrom(1024)
				data = data.decode()
				data = data.split()
				if len(data) != 2:
					print('Invalid command format received.')
					continue
				if not is_num(data[1]):
					print('Invalid parameter value received.')
					continue
					
				if data[0] == 'target':
					target_pos = int(data[1])
					print(f'New target pos: {target_pos}')
				elif data[0] == 'current':
					current_pos = int(data[1])
					print(f'New current pos: {current_pos}')
				elif data[0] == 'speed':
					speed = int(data[1])
					print(f'New speed: {speed}')
				else:
					print('Unknown command received.')
		except BlockingIOError:
			pass
		
		if target_pos > current_pos:
			stepper_coil_pins[active_coil_idx].off()
			active_coil_idx += 1
			active_coil_idx %= 4
			stepper_coil_pins[active_coil_idx].on()
			current_pos += 1
			if target_pos == current_pos:
				print('Target pos reached.')
		elif target_pos < current_pos:
			stepper_coil_pins[active_coil_idx].off()
			active_coil_idx -= 1
			active_coil_idx %= 4
			stepper_coil_pins[active_coil_idx].on()
			current_pos -= 1
			if target_pos == current_pos:
				print('Target pos reached.')
		
		time.sleep(1 / speed)
	
except:
	for pin in stepper_coil_pins:
		pin.close()
	print('Pins closed.')
	sys.exit()