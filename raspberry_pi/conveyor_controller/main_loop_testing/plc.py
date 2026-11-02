# Połączenie z modbusem

import time

from pymodbus.client import ModbusTcpClient

import config

_client = ModbusTcpClient(config.PLC_IP, port = config.PLC_PORT)   # connects on connect()


def connect() -> bool:
	if not _client.connect():
		return False
	reset()
	return True


def close() -> None:
	try:
		reset()
	except Exception:
		pass
	_client.close()


def reset() -> None:
	_client.write_register(config.REG_GATE, 0, device_id = config.DEVICE_ID)
	_client.write_coil(config.COIL_PACKAGE_ARRIVED, False, device_id = config.DEVICE_ID)


def transport_package_to_gate(gate: int) -> bool:
	"""
	Writes the gate to MI12, raises MB0 and waits for the PLC to clear MB0.
	Always leaves the PLC outputs reset afterwards.
	Returns True if the PLC confirmed the package was handled.
	"""
	try:
		if not _client.connected and not _client.connect():
			print("  PLC unreachable")
			return False

		reg = _client.write_register(config.REG_GATE, gate, device_id = config.DEVICE_ID)
		if reg.isError():
			print(f"  failed to write MI{config.REG_GATE}: {reg}")
			return False
		coil = _client.write_coil(config.COIL_PACKAGE_ARRIVED, True, device_id = config.DEVICE_ID)
		if coil.isError():
			print(f"  failed to set MB{config.COIL_PACKAGE_ARRIVED}: {coil}")
			return False
		print(f"  -> MI{config.REG_GATE} = {gate}, MB{config.COIL_PACKAGE_ARRIVED} = 1; waiting for PLC...")

		deadline = time.monotonic() + config.PACKAGE_CLEAR_TIMEOUT_S
		while time.monotonic() < deadline:
			result = _client.read_coils(config.COIL_PACKAGE_ARRIVED, count = 1, device_id = config.DEVICE_ID)
			if not result.isError() and not bool(result.bits[0]):
				print("  PLC cleared MB0 — package handled")
				return True
			time.sleep(0.1)
		print("  TIMEOUT — MB0 still set")
		return False
	except Exception as e:
		print(f"  Modbus error: {e}")
		return False
	finally:
		try:
			reset()
		except Exception:
			pass
