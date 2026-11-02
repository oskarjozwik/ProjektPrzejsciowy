# konfiguracja sprzętowa

import time

import board
import cv2 as cv
import numpy as np
from cedargrove_nau7802 import NAU7802
from gpiozero import DistanceSensor
from picamera2 import Picamera2

import config
from get_real_dimension import CameraParams

# Shared handles. Other modules must use `hardware.picam` (attribute access),
# not `from hardware import picam`, because these are assigned in init().
picam: Picamera2 | None = None
camera: CameraParams | None = None
mog: cv.BackgroundSubtractorMOG2 | None = None
distance_sensor: DistanceSensor | None = None
load_cell: NAU7802 | None = None
load_cell_zero: float = 0.0
baseline_distance_m: float = 0.0


def median_distance(count: int) -> float:
	return float(np.median([distance_sensor.distance for _ in range(count)]))


def read_load_cell_average(count: int) -> float:
	samples = []
	while len(samples) < count:
		if load_cell.available():
			samples.append(load_cell.read())
		else:
			time.sleep(0.005)
	return float(np.mean(samples))


def capture_frame() -> np.ndarray:
	return picam.capture_array()


def _lock_camera_controls() -> None:
	# Let AE/AWB converge on the empty belt, then freeze them so the MOG2
	# model and the live frames stay exposure- and colour-matched.
	picam.set_controls({"AeEnable": True, "AwbEnable": True})
	time.sleep(config.SETTLE_TIME_S)
	meta = picam.capture_metadata()
	picam.set_controls({
		"AeEnable": False,
		"AwbEnable": False,
		"ExposureTime": int(meta["ExposureTime"]),
		"AnalogueGain": float(meta["AnalogueGain"]),
		"ColourGains": tuple(meta["ColourGains"]),
	})


def _build_subtractor() -> cv.BackgroundSubtractorMOG2:
	subtractor = cv.createBackgroundSubtractorMOG2(
		history = config.BG_REFERENCE_FRAMES,
		varThreshold = config.VAR_THRESHOLD,
		detectShadows = True,
	)
	subtractor.setShadowThreshold(config.SHADOW_THRESHOLD)
	for _ in range(config.BG_REFERENCE_FRAMES):
		subtractor.apply(picam.capture_array(), learningRate = -1)
	return subtractor


def init() -> None:
	"""Brings up camera, ultrasonic and load cell. The belt must be empty."""
	global picam, camera, mog, distance_sensor, load_cell
	global load_cell_zero, baseline_distance_m

	picam = Picamera2()
	picam.configure(picam.create_preview_configuration(
		main = {"format": "RGB888", "size": config.CAMERA_SIZE}
	))
	picam.start()
	camera = CameraParams(config.CAMERA_FOV_MAP, horizontal_resolution_px = config.CAMERA_SIZE[0])

	distance_sensor = DistanceSensor(
		echo = config.ECHO_PIN,
		trigger = config.TRIGGER_PIN,
		max_distance = config.MAX_DISTANCE_M,
	)

	load_cell = NAU7802(board.I2C(), address = config.NAU7802_ADDRESS, active_channels = 1)
	load_cell.enable(True)
	load_cell.channel = 1
	load_cell.calibrate("INTERNAL")
	load_cell.calibrate("OFFSET")
	print("Taring load cell — keep the belt empty...")
	load_cell_zero = read_load_cell_average(config.TARE_SAMPLES)
	print(f"  zero offset: {load_cell_zero:.0f}")

	print("Letting camera settle, then locking exposure/AWB...")
	_lock_camera_controls()
	print(f"Training MOG2 on {config.BG_REFERENCE_FRAMES} empty-belt frames...")
	mog = _build_subtractor()
	baseline_distance_m = median_distance(config.DISTANCE_SAMPLES * 4)
	print(f"  baseline distance: {baseline_distance_m * 100:.1f} cm")


def shutdown() -> None:
	try:
		picam.stop()
	except Exception:
		pass
