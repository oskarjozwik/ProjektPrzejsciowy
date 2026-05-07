from camera.process_camera_image import process_camera_image
from package_detection.get_distance_reading import get_distance_reading
from package_detection.px_to_meters import px_to_meters

class BoxDimensions:
	def __init__(
		self,
		x: float,
		y: float,
		z: float,
	):
		self.x = x
		self.y = y
		self.z = z

class PackageCheckResult:
	def __init__(
		self,
		box_detected: bool = True,
		qr_detected: bool = True,
		box_dimensions: BoxDimensions = BoxDimensions( 0, 0, 0 ),
		qr_code: int = 0,
	):
		self.box_detected = box_detected
		self.qr_detected = qr_detected
		self.box_dimensions = box_dimensions
		self.qr_code = qr_code

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
		z = distance_reading
	)
	
	return PackageCheckResult(
		box_dimensions = box_dimensions,
		qr_detected = camera_image_processing_result.qr_detected,
		qr_code = camera_image_processing_result.qr_code
	)
