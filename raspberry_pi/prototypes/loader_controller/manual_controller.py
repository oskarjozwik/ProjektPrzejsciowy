import sys
import socket


def is_num(value):
	try:
		int(value)
		return True
	except ValueError:
		return False


if len(sys.argv) != 4:
	print(
		'Required arguments: <stepper_driver_port> <command> <parameter>'
	)
	sys.exit()

if not is_num(sys.argv[1]):
	print(f'{sys.argv[1]} is not a valid port number.')
	sys.exit()

comm_port = int(sys.argv[1])
command = sys.argv[2]
parameter = sys.argv[3]

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
		sys.exit()
	if not definition_found:
		print('No parameter definition found.')
		sys.exit()

command = f'{command} {parameter}'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(command.encode(), ('127.0.0.1', comm_port))

print(f'Command "{command}" sent.')
