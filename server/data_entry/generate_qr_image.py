import numpy as np
import cv2 as cv

scale_factor: float = 10


def generate_qr_image(qr_code: int) -> np.ndarray:
	data_string = str(qr_code)
	
	encoder_params = cv.QRCodeEncoder.Params()
	encoder_params.correction_level = cv.QRCodeEncoder_CORRECT_LEVEL_M
	encoder_params.mode = cv.QRCodeEncoder_MODE_NUMERIC
	
	encoder = cv.QRCodeEncoder.create(
		parameters = encoder_params
	)
	
	qr_matrix = encoder.encode(data_string)
	height, width = qr_matrix.shape
	
	qr_image = cv.resize(
		qr_matrix,
		(width * scale_factor, height * scale_factor),
		interpolation = cv.INTER_NEAREST
	)
	
	return qr_image