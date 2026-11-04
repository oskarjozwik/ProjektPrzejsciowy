import sys
import socket
from enum import Enum, auto


class Axis(Enum):
	Long = auto()
	Vert = auto()
	Extd = auto()
	Grip = auto()


ports = {
	Axis.Long: {
		'in': 5005, 'out': 5055
	},
	Axis.Vert: {
		'in': 5006, 'out': 5066
	},
	Axis.Extd: {
		'in': 5007, 'out': 5077
	},
	Axis.Grip: {
		'in': 5008, 'out': 5088
	}
}

socks: dict[Axis, socket.socket] = {}


def init():
	for axis in Axis:
		socks[axis] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			socks[axis].bind(('127.0.0.1', ports[axis]['in']))
		except socket.error:
			print(f'Port {ports[axis]['in']} is busy.')
			sys.exit()
		socks[axis].connect(('127.0.0.1', ports[axis]['out']))


def _send_command(axis: Axis, command: str, parameter) -> bool:
	def is_num(value):
		try:
			int(value)
			return True
		except ValueError:
			return False
	
	if not is_num(parameter):
		definition_found = False
		try:
			with open("pos_def.txt", "r") as file:
				for line in file:
					line = line.split()
					if len(line) != 2:
						continue
					if parameter == line[0]:
						parameter = line[1]
						definition_found = True
						break
		except FileNotFoundError:
			print('Definition file "pos_def.txt" cannot be opened.')
			return False
		if not definition_found:
			print('No parameter definition found.')
			return False
	
	socks[axis].send(f'{command} {parameter}'.encode())
	return True


def _wait_for_completion(axis: Axis):
	data = None
	while data != b'done':
		data, addr = socks[axis].recvfrom(1024)


###################################################
# ! END ALL SEQUENCES BY RETRACTING THE GRIPPER ! #
###################################################

def insert_from(x: int, y: int):
	_send_command(Axis.Long, 'target', f'rack_h{x}')
	_send_command(Axis.Vert, 'target', f'rack_v{y}')
	_wait_for_completion(Axis.Long)
	_wait_for_completion(Axis.Vert)
	
	_send_command(Axis.Extd, 'right', f'extd_max')
	_wait_for_completion(Axis.Extd)
	
	_send_command(Axis.Grip, 'right', f'grip_max')
	_wait_for_completion(Axis.Grip)
	
	_send_command(Axis.Vert, 'target', f'rack_v{y}_lifted')
	_wait_for_completion(Axis.Vert)
	
	_send_command(Axis.Extd, 'left', f'extd_max')
	_wait_for_completion(Axis.Extd)
	
	_send_command(Axis.Long, 'target', f'plate_h')
	_send_command(Axis.Vert, 'target', f'plate_v_lifted')
	_wait_for_completion(Axis.Long)
	_wait_for_completion(Axis.Vert)
	
	_send_command(Axis.Extd, 'right', f'extd_max')
	_wait_for_completion(Axis.Extd)
	
	_send_command(Axis.Vert, 'target', f'plate_v')
	_wait_for_completion(Axis.Vert)
	
	_send_command(Axis.Grip, 'left', f'grip_max')
	_wait_for_completion(Axis.Grip)
	
	# retracting
	_send_command(Axis.Extd, 'left', f'extd_max')
	_wait_for_completion(Axis.Extd)


def push_from_plate():
	_send_command(Axis.Long, 'target', f'plate_h_before_push')
	_send_command(Axis.Vert, 'target', f'plate_v')
	_wait_for_completion(Axis.Long)
	_wait_for_completion(Axis.Vert)
	
	_send_command(Axis.Extd, 'right', f'extd_max')
	_wait_for_completion(Axis.Extd)
	
	_send_command(Axis.Long, 'target', f'plate_h_after_push')
	_wait_for_completion(Axis.Long)
	
	# retracting
	_send_command(Axis.Extd, 'left', f'extd_max')
	_wait_for_completion(Axis.Extd)


def go_to_zero():
	_send_command(Axis.Long, 'target', 0)
	_send_command(Axis.Vert, 'target', 0)
	_wait_for_completion(Axis.Long)
	_wait_for_completion(Axis.Vert)


# CONNECT THIS TO HARDWARE INTERRUPT TO RESET STEP COUNT WHEN LIMIT SWITCH ACTIVATED
def reset_step_count(axis: Axis):
	_send_command(axis, 'current', 0)