import numpy as np


class CameraParams:
	def __init__( self, distance_to_fov_width_map, horizontal_resolution_px: int ):
		distances = np.array( list( distance_to_fov_width_map.keys( ) ) )
		widths = np.array( list( distance_to_fov_width_map.values( ) ) )
		
		self.horizontal_resolution_px = horizontal_resolution_px
		self.fov_slope, self.fov_intercept = np.polyfit( distances, widths, 1 )
	
	def get_total_fov_width( self, distance_from_camera: float ) -> float:
		return distance_from_camera * self.fov_slope + self.fov_intercept
	
	def get_real_dimension( self, dimension_in_pixels: float, distance_from_camera: float ):
		total_width = self.get_total_fov_width( distance_from_camera )
		meters_per_pixel = total_width / self.horizontal_resolution_px
		return dimension_in_pixels * meters_per_pixel