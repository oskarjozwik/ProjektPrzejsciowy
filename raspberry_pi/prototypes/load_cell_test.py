"""
Dependencies: cedargrove-nau7802  adafruit-blinka  numpy
"""

import time

import numpy as np
import board
from cedargrove_nau7802 import NAU7802

NAU7802_ADDRESS: int = 0x2A
SAMPLES_PER_READING: int = 10
TARE_SAMPLES: int = 40
SAMPLE_PERIOD_S: float = 0.5


def read_average(sensor: NAU7802, count: int) -> float:
	samples = []
	while len(samples) < count:
		if sensor.available():
			samples.append(sensor.read())
		else:
			time.sleep(0.005)
	return float(np.mean(samples))


def main():
	i2c = board.I2C()
	sensor = NAU7802(i2c, address = NAU7802_ADDRESS, active_channels = 1)
	sensor.enable(True)
	sensor.channel = 1
	sensor.calibrate("INTERNAL")
	sensor.calibrate("OFFSET")

	print("Taring — keep the beam empty...")
	zero_offset = read_average(sensor, TARE_SAMPLES)
	print(f"Zero offset: {zero_offset:.0f}")
	print("Now add weight. Press Ctrl-C to quit.")

	try:
		while True:
			raw = read_average(sensor, SAMPLES_PER_READING)
			corrected = raw - zero_offset
			print(f"raw: {raw:12.0f}   corrected: {corrected:12.0f}")
			time.sleep(SAMPLE_PERIOD_S)
	except KeyboardInterrupt:
		print("\nStopping")


if __name__ == "__main__":
	main()
