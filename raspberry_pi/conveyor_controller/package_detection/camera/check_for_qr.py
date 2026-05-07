import numpy as np
import cv2 as cv

class QrCheckResult:
	def __init__(
		self,
		qr_detected: bool = True,
		wrong_format: bool = False,
		qr_code: int = 0,
	):
		self.qr_detected = qr_detected
		self.wrong_format = wrong_format
		self.qr_code = qr_code

detector = cv.QRCodeDetector()

def check_for_qr(
	image: np.ndarray,
) -> QrCheckResult:
	detection_result, _, _ = detector.detectAndDecode( image )
	
	if detection_result == '':
		return QrCheckResult( qr_detected = False )
	if not detection_result.isnumeric():
		return QrCheckResult( wrong_format = True )
	
	return QrCheckResult( qr_code = int( detection_result ) )
