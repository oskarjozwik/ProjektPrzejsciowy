# Czujniki na przydatne wartości

import cv2 as cv
import numpy as np

import config
import hardware


def _find_largest_object(frame: np.ndarray) -> tuple | None:
	# learningRate=0 freezes the model so a stationary package isn't absorbed
	# and the model never learns from frames that contain a package.
	raw = hardware.mog.apply(frame, learningRate = 0)
	# MOG2 with detectShadows: 0 = bg, 127 = shadow, 255 = foreground.
	_, fg = cv.threshold(raw, 200, 255, cv.THRESH_BINARY)
	kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (config.MORPH_KERNEL, config.MORPH_KERNEL))
	fg = cv.morphologyEx(fg, cv.MORPH_OPEN, kernel)
	fg = cv.morphologyEx(fg, cv.MORPH_CLOSE, kernel)

	contours, _ = cv.findContours(fg, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
	if not contours:
		return None
	largest = max(contours, key = cv.contourArea)
	if cv.contourArea(largest) < config.MIN_OBJECT_AREA_PX:
		return None
	return cv.minAreaRect(largest)   # sides follow the package's orientation


def get_mass_measurement() -> float:
	# Masa zwracana w gramach. Wymaga początkowej kalibracji w configu
	raw = hardware.read_load_cell_average(config.LOAD_CELL_SAMPLES)
	return (raw - hardware.load_cell_zero) / config.LOAD_CELL_COUNTS_PER_GRAM


def get_dimension_measurement() -> dict | None:
	rect = _find_largest_object(hardware.capture_frame())
	if rect is None:
		return None
	(_, _), (w_px, h_px), _ = rect
	long_px, short_px = sorted((w_px, h_px), reverse = True)

	current_distance_m = hardware.median_distance(config.DISTANCE_SAMPLES)
	z_m = max(0.0, hardware.baseline_distance_m - current_distance_m)
	distance_to_top_m = max(0.01, hardware.baseline_distance_m - z_m)

	return {
		"long": hardware.camera.get_real_dimension(long_px, distance_to_top_m),
		"short": hardware.camera.get_real_dimension(short_px, distance_to_top_m),
		"z": z_m,
	}


def measure_package() -> dict | None:
	# Spakowanie danych w jedną strukturę
	dims = get_dimension_measurement()
	if dims is None:
		return None
	dims["weight"] = get_mass_measurement()
	return dims


def check_package_spec(measured: dict, criteria: dict) -> list[str]:
	# The package can sit at any angle, so compare long-to-long, short-to-short.
	allowed_long = max(criteria["max_x"], criteria["max_y"])
	allowed_short = min(criteria["max_x"], criteria["max_y"])

	reasons: list[str] = []
	if measured["weight"] > criteria["max_weight"]:
		reasons.append(f"too heavy ({measured['weight']:.1f}g > {criteria['max_weight']:.1f}g)")
	if measured["long"] > allowed_long:
		reasons.append(f"long side too big ({measured['long'] * 1000:.0f}mm > {allowed_long * 1000:.0f}mm)")
	if measured["short"] > allowed_short:
		reasons.append(f"short side too big ({measured['short'] * 1000:.0f}mm > {allowed_short * 1000:.0f}mm)")
	if measured["z"] > criteria["max_z"]:
		reasons.append(f"too tall ({measured['z'] * 1000:.0f}mm > {criteria['max_z'] * 1000:.0f}mm)")
	return reasons
