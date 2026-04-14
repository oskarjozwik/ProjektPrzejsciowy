import numpy as np
import cv2 as cv

detector = cv.QRCodeDetector()

def get_qr(
	image: np.ndarray,
) -> str:
	string, _, _ = detector.detectAndDecode(image)
	return string