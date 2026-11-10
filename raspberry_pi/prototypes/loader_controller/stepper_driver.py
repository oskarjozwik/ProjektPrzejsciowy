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


if len(sys.argv) != 7:
	print(
		'Required arguments: <stepper_coil_1_pin> <stepper_coil_2_pin> <stepper_coil_3_pin> <stepper_coil_4_pin> <input_port> <output_port>'
	)
	sys.exit()

for arg in sys.argv[1:5]:
	if not is_num(arg):
		print(f'{arg} is not a valid pin number.')
		sys.exit()

if not is_num(sys.argv[5]):
	print(f'{sys.argv[5]} is not a valid port number.')
	sys.exit()
if not is_num(sys.argv[6]):
	print(f'{sys.argv[6]} is not a valid port number.')
	sys.exit()

input_port = int(sys.argv[5])
output_port = int(sys.argv[6])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
	sock.bind(('0.0.0.0', input_port))
except socket.error:
	print(f'Port {input_port} is busy.')
	sys.exit()
sock.setblocking(False)

stepper_coil_pins = []
for arg in sys.argv[1:5]:
	try:
		stepper_coil_pins.append(DigitalOutputDevice(int(arg)))
	except:
		print(f'Pin {arg} is busy.')
		sys.exit()

try:
	print(f'Driver active. Listening on port {input_port}')
	
	speed = 250
	target_pos = 0
	current_pos = 0
	active_coil_idx = 0
	client_address = None
	
	while True:
		try:
			while True:
				data, addr = sock.recvfrom(1024)
				client_address = (addr[0], output_port)
				
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
				if client_address:
					sock.sendto(b'done', client_address)
		elif target_pos < current_pos:
			stepper_coil_pins[active_coil_idx].off()
			active_coil_idx -= 1
			active_coil_idx %= 4
			stepper_coil_pins[active_coil_idx].on()
			current_pos -= 1
			if target_pos == current_pos:
				print('Target pos reached.')
				if client_address:
					sock.sendto(b'done', client_address)
		
		time.sleep(1 / speed)

except:
	for pin in stepper_coil_pins:
		pin.close()
	print('Pins closed.')
	sys.exit()