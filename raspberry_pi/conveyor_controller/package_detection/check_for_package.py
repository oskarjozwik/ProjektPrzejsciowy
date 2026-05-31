from camera.process_camera_image import process_camera_image
from package_detection.get_distance_reading import get_distance_reading
from package_detection.get_mass_measurement import get_mass_measurement
from package_detection.px_to_meters import px_to_meters

distance_sensor_distance_from_base: float = 0.25
box_dimensions_acceptable_difference: float = 1e-3
mass_acceptable_difference = 1e-3

class BoxDimensions:
	def __init__(
		self,
		x: float,
		y: float,
		z: float,
	):
		self.x, self.y, self.z = sorted([x, y, z])

class PackageCheckResult:
	def __init__(
		self,
		box_detected: bool = True,
		qr_detected: bool = True,
		box_dimensions: BoxDimensions = BoxDimensions( 0, 0, 0 ),
		qr_code: int = 0,
		mass: float = 0
	):
		self.box_detected = box_detected
		self.qr_detected = qr_detected
		self.box_dimensions = box_dimensions
		self.qr_code = qr_code
		self.mass = mass
	
	def isSimilarTo(self, otherResult: PackageCheckResult) -> bool:
		if self.box_detected != otherResult.box_detected:
			return False
		if self.qr_detected != otherResult.qr_detected:
			return False
		if self.qr_code != otherResult.qr_code:
			return False
		if abs(self.mass - otherResult.mass) > mass_acceptable_difference:
			return False
		if abs(self.box_dimensions.x - otherResult.box_dimensions.x) > box_dimensions_acceptable_difference:
			return False
		if abs(self.box_dimensions.y - otherResult.box_dimensions.y) > box_dimensions_acceptable_difference:
			return False
		if abs(self.box_dimensions.z - otherResult.box_dimensions.z) > box_dimensions_acceptable_difference:
			return False
		return True
	
	def print(self):
		if not self.box_detected:
			print('Box not detected!')
		else:
			print(
				f'Box detected! Dimensions: \t{int(self.box_dimensions.x * 1000)}mm x \t{int(self.box_dimensions.y * 1000)}mm x \t{int(self.box_dimensions.z * 1000)}mm x')

		if not self.qr_detected:
			print('QR not detected!')
		else:
			print(f'QR detected! Code: {self.qr_code}')

def check_for_package() -> PackageCheckResult:
	camera_image_processing_result = process_camera_image()
	
	if not camera_image_processing_result.contour_detected:
		return PackageCheckResult(
			box_detected = False,
			qr_detected = camera_image_processing_result.qr_detected,
			qr_code = camera_image_processing_result.qr_code,
		)
	
	distance_reading = get_distance_reading()
	box_dimensions = BoxDimensions(
		x = px_to_meters(
			dimension_px = camera_image_processing_result.contour_dimensions.x,
			distance = distance_reading
		),
		y = px_to_meters(
			dimension_px = camera_image_processing_result.contour_dimensions.y,
			distance = distance_reading
		),
		z = distance_sensor_distance_from_base - distance_reading
	)
	
	return PackageCheckResult(
		box_dimensions = box_dimensions,
		qr_detected = camera_image_processing_result.qr_detected,
		qr_code = camera_image_processing_result.qr_code,
		mass = get_mass_measurement()
	)
