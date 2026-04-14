import numpy as np


def get_box_dimensions_in_pixels( bounds: np.ndarray ) -> np.ndarray:
	assert bounds.shape[0], f'4 bounds expected, got {bounds.shape[0]}'
	
	def get_line_angle( line: np.ndarray ) -> float:
		dx = line[0, 2] - line[0, 0]
		dy = line[0, 3] - line[0, 1]
		return np.arctan2( dy, dx )
	
	def get_line_center( line: np.ndarray ) -> np.ndarray:
		return np.array( [line[0, 0] + line[0, 2], line[0, 1] + line[0, 3]] ) / 2
	
	bound_centers = [get_line_center( line ) for line in bounds]
	
	min_angle_difference = 91
	for i in range( 1, 4 ):
		angle_difference: float = np.abs( np.rad2deg( get_line_angle( bounds[0] ) - get_line_angle( bounds[i] ) ) )
		if angle_difference > 90:
			angle_difference = 180 - angle_difference
		
		if angle_difference < min_angle_difference:
			min_angle_difference = angle_difference
			parallel_pair1 = (0, i)
	
	parallel_pair2 = tuple( idx for idx in range( 4 ) if idx not in parallel_pair1 )
	
	d1 = bound_centers[parallel_pair1[0]] - bound_centers[parallel_pair1[1]]
	d2 = bound_centers[parallel_pair2[0]] - bound_centers[parallel_pair2[1]]
	
	dimension1 = (d1[0] ** 2 + d1[1] ** 2) ** 0.5
	dimension2 = (d2[0] ** 2 + d2[1] ** 2) ** 0.5
	
	return np.array( [dimension1, dimension2] )