"""
Dependencies: gpiozero  RPi.GPIO
"""

import time

from gpiozero import DistanceSensor

# BCM pin numbering — match these to your wiring.
TRIGGER_PIN: int = 23
ECHO_PIN: int = 24
MAX_DISTANCE_M: float = 1.0     # readings saturate at this range
SAMPLE_PERIOD_S: float = 0.5


def main():
	sensor = DistanceSensor(
		echo = ECHO_PIN,
		trigger = TRIGGER_PIN,
		max_distance = MAX_DISTANCE_M,
	)

	print(f"Reading HC-SR04 (trigger=GPIO{TRIGGER_PIN}, echo=GPIO{ECHO_PIN}). "
		f"Press Ctrl-C to quit.")
	try:
		while True:
			distance_m = sensor.distance
			print(f"distance: {distance_m * 100:6.1f} cm  ({distance_m:.3f} m)")
			time.sleep(SAMPLE_PERIOD_S)
	except KeyboardInterrupt:
		print("\nStopping")


if __name__ == "__main__":
	main()
