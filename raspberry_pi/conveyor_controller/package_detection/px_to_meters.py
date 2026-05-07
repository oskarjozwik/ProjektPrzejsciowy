import numpy as np

horizontal_resolution_px: float = 1080
# to calibrate, measure the largest width the camera could see at a given distance
distances: np.ndarray = np.array( [0.1, 0.15, 0.2] )
widths: np.ndarray = np.array( [0.1, 0.15, 0.2] )

fov_slope, fov_intercept = np.polyfit( distances, widths, 1 )

def get_total_fov_width(
	distance: float,
) -> float:
	return distance * fov_slope + fov_intercept

def px_to_meters(
	dimension_px: float,
	distance: float,
) -> float:
	total_width_m = get_total_fov_width( distance )
	meters_per_pixel = total_width_m / horizontal_resolution_px
	dimension_m = dimension_px * meters_per_pixel
	return dimension_m