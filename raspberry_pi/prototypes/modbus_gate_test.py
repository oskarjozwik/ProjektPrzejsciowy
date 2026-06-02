"""
Dependencies: pymodbus
"""

import time

from pymodbus.client import ModbusTcpClient

PLC_IP: str = "10.0.0.10"
PLC_PORT: int = 502
DEVICE_ID: int = 255

REG_GATE: int = 12               # MI12
COIL_PACKAGE_ARRIVED: int = 0    # MB0

PACKAGE_CLEAR_TIMEOUT_S: float = 30.0
INVALID_GATE: int = 3

# (gate number, human label) sequence to send
TEST_SEQUENCE = [
	(1, "gate 1"),
	(2, "gate 2"),
	(INVALID_GATE, "invalid gate"),
]


def read_coil(client: ModbusTcpClient, coil: int) -> bool:
	result = client.read_coils(coil, count = 1, device_id = DEVICE_ID)
	if result.isError():
		return False
	return bool(result.bits[0])


def send_package(client: ModbusTcpClient, gate: int) -> None:
	client.write_register(REG_GATE, gate, device_id = DEVICE_ID)
	client.write_coil(COIL_PACKAGE_ARRIVED, True, device_id = DEVICE_ID)
	print(f"  wrote MI12 = {gate}, set MB0 = 1; waiting for the PLC to clear MB0...")

	deadline = time.monotonic() + PACKAGE_CLEAR_TIMEOUT_S
	while time.monotonic() < deadline:
		if not read_coil(client, COIL_PACKAGE_ARRIVED):
			print("  PLC cleared MB0 — package went through")
			return
		time.sleep(0.1)
	print("  TIMEOUT — MB0 still set; check the PLC ladder / exit sensor")


def main():
	client = ModbusTcpClient(PLC_IP, port = PLC_PORT)
	if not client.connect():
		print(f"Could not connect to the PLC at {PLC_IP}:{PLC_PORT}")
		return
	print("PLC connected")

	try:
		for gate, label in TEST_SEQUENCE:
			input(f"\nPress Enter to send a package to {label} (MI12={gate})... ")
			send_package(client, gate)
	except KeyboardInterrupt:
		print("\nStopping")
	finally:
		client.close()


if __name__ == "__main__":
	main()
