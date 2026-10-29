import sys
import socket

if len(sys.argv) != 4:
	print(
		'Required arguments: <stepper_driver_port> <command> <parameter>'
	)
	sys.exit()

try:
	comm_port = int(sys.argv[1])
except:
	print(f'{sys.argv[1]} is not a valid port number.')
	sys.exit()

command = sys.argv[2]
parameter = sys.argv[3]

if not parameter.isnumeric():
	with open("pos_def.txt", "r") as file:
		for line in file:
			line = line.split()
			if len(line) != 2:
				continue
			if parameter == line[0]:
				parameter = line[1]
				break
			

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(f'{command} {parameter}'.encode(), ('127.0.0.1', comm_port))

print('Command sent.')