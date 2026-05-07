import cv2 as cv

from package_detection.camera.check_for_contours import ContourDimensions, check_for_contours
from package_detection.camera.check_for_qr import check_for_qr

class CameraImageProcessingResult:
	def __init__(
		self,
		no_video: bool = False,
		contour_detected: bool = True,
		qr_detected: bool = True,
		contour_dimensions: ContourDimensions = ContourDimensions( 0, 0 ),
		qr_code: int = 0,
	):
		self.no_video = no_video
		self.contour_detected = contour_detected
		self.qr_detected = qr_detected
		self.contour_dimensions = contour_dimensions
		self.qr_code = qr_code

canny_threshold_hard: int = 127
canny_threshold_soft: int = 63
contour_size_threshold: int = 10000

video_capture = cv.VideoCapture( 0 )

def process_camera_image() -> CameraImageProcessingResult:
	success, frame = video_capture.read()
	
	if not success:
		return CameraImageProcessingResult( no_video = True )
	
	contour_check_result = check_for_contours( frame, canny_threshold_hard, canny_threshold_soft, contour_size_threshold )
	qr_check_result = check_for_qr( image = frame )
	
	return CameraImageProcessingResult(
		contour_detected = contour_check_result.contour_detected,
		qr_detected = qr_check_result.qr_detected,
		contour_dimensions = contour_check_result.contour_dimensions,
		qr_code = qr_check_result.qr_code,
	)
