import time
import sys
import socket
from gpiozero import DigitalOutputDevice


class Mode:
	class Extend:
		pass
	class Retract:
		pass

def is_num(value):
	try:
		int(value)
		return True
	except ValueError:
		return False


if len(sys.argv) != 5:
	print(
		'Required arguments: <dc_motor_extend_pin> <dc_motor_retract_pin> <input_port> <output_port>'
	)
	sys.exit()

for arg in sys.argv[1:3]:
	if not is_num(arg):
		print(f'{arg} is not a valid pin number.')
		sys.exit()

if not is_num(sys.argv[3]):
	print(f'{sys.argv[3]} is not a valid port number.')
	sys.exit()
if not is_num(sys.argv[4]):
	print(f'{sys.argv[4]} is not a valid port number.')
	sys.exit()

input_port = int(sys.argv[3])
output_port = int(sys.argv[4])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
	sock.bind(('127.0.0.1', input_port))
except socket.error as e:
	print(f'Port {input_port} is busy.')
	sys.exit()
sock.setblocking(False)

try:
	dc_motor_pins = {
		Mode.Extend: DigitalOutputDevice(int(sys.argv[1])),
		Mode.Retract: DigitalOutputDevice(int(sys.argv[2]))
	}
except:
	print('Pin is busy.')
	sys.exit()

try:
	print(f'Driver active. Listening on port {input_port}')
	
	remaining_time = 0
	mode = None
	
	prev_time = int(time.time() * 1000)
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
				
				if data[0] == 'extend':
					if mode is not None:
						dc_motor_pins[Mode.Retract].off()
						print('Request cancelled.')
					mode = Mode.Extend
					dc_motor_pins[Mode.Extend].on()
					remaining_time = int(data[1])
					print(f'New extend command: {remaining_time}ms')
				elif data[0] == 'retract':
					if mode is not None:
						dc_motor_pins[Mode.Extend].off()
						print('Request cancelled.')
					mode = Mode.Retract
					dc_motor_pins[Mode.Retract].on()
					remaining_time = int(data[1])
					print(f'New retract command: {remaining_time}ms')
				else:
					print('Unknown command received.')
		except BlockingIOError:
			pass
		
		curr_time = int(time.time() * 1000)
		delta = curr_time - prev_time
		prev_time = curr_time
		if remaining_time > 0:
			remaining_time -= delta
		
		if mode is not None and remaining_time <= 0:
			dc_motor_pins[mode].off()
			mode = None
			print('Request completed.')
			sock.sendto(b'done', ('127.0.0.1', output_port))
		
except:
	for pin in dc_motor_pins.values():
		pin.close()
	print('Pins closed.')
	sys.exit()