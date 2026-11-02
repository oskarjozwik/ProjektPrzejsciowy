# Ten sam schemat co wcześniej, ale ładniej rozpisany

import time

import cv2 as cv
import mysql.connector

import config
import database
import gates
import hardware
import measurements
import plc

_qr_detector = cv.QRCodeDetector()


def scan_for_qr() -> str | None:
	data, _, _ = _qr_detector.detectAndDecode(hardware.capture_frame())
	return data or None


def process_package(qr_data: str) -> int:
	if not qr_data.isnumeric():
		print("  QR not numeric -> error gate")
		return config.ERROR_GATE
	qr_id = int(qr_data)

	try:
		criteria = database.fetch_package(qr_id)
	except mysql.connector.Error as e:
		print(f"  SQL error: {e} -> error gate")
		return config.ERROR_GATE
	if criteria is None:
		print(f"  qr_id {qr_id} not in DB -> error gate")
		return config.ERROR_GATE

	print(f"  settling {config.SETTLE_BEFORE_MEASURE_S:.1f}s before measurement...")
	time.sleep(config.SETTLE_BEFORE_MEASURE_S)
	measured = measurements.measure_package()
	if measured is None:
		print("  no object found -> error gate")
		return config.ERROR_GATE

	print(f"  measured: long={measured['long'] * 1000:.0f}mm short={measured['short'] * 1000:.0f}mm "
		f"z={measured['z'] * 1000:.0f}mm weight={measured['weight']:.1f}g")

	reasons = measurements.check_package_spec(measured, criteria)
	if reasons:
		print(f"  out of spec: {'; '.join(reasons)} -> error gate")
		return config.ERROR_GATE

	gate = gates.select_gate_for_destination(criteria["destination"], gates.load_gate_config())
	print(f"  {criteria['origin']} -> {criteria['destination']}: gate {gate}")
	return gate


def main():
	print("Starting up...")
	try:
		hardware.init()
		if not plc.connect():
			print(f"Could not connect to the PLC at {config.PLC_IP}:{config.PLC_PORT}")
			return
		print("PLC connected and reset")
		database.connect()
		print("SQL connected")

		print("\nReady. Scanning for QR codes.")
		while True:
			loop_start = time.monotonic()
			qr_data = scan_for_qr()
			if qr_data:
				print(f"\nQR detected: {qr_data!r}")
				gate = process_package(qr_data)
				plc.transport_package_to_gate(gate)
				continue
			elapsed = time.monotonic() - loop_start
			if elapsed < config.CAPTURE_PERIOD_S:
				time.sleep(config.CAPTURE_PERIOD_S - elapsed)
	except KeyboardInterrupt:
		print("\nStopping")
	finally:
		plc.close()
		database.close()
		hardware.shutdown()


if __name__ == "__main__":
	main()
