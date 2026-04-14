import cv2 as cv
import numpy as np

from get_lines import get_lines
from get_qr import get_qr


def main():
	canny_threshold_hard: int = 0
	canny_threshold_soft: int = 0
	line_detection_threshold: int = 0
	min_line_length: int = 0
	max_line_gap: int = 0
	
	def on_canny_threshold_hard_new_value( new_value: int ):
		nonlocal canny_threshold_hard
		canny_threshold_hard = new_value
	
	def on_canny_threshold_soft_new_value( new_value: int ):
		nonlocal canny_threshold_soft
		canny_threshold_soft = new_value
	
	def on_line_detection_threshold_new_value( new_value: int ):
		nonlocal line_detection_threshold
		line_detection_threshold = new_value
	
	def on_min_line_length_new_value( new_value: int ):
		nonlocal min_line_length
		min_line_length = new_value
	
	def on_max_line_gap_new_value( new_value: int ):
		nonlocal max_line_gap
		max_line_gap = new_value
	
	video_capture = cv.VideoCapture( 0 )
	cv.namedWindow( 'Main window' )
	cv.namedWindow( 'Settings window' )
	
	cv.createTrackbar( 'CnyThrHrd', 'Settings window', 127, 255, on_canny_threshold_hard_new_value )
	cv.createTrackbar( 'CnyThrSft', 'Settings window', 63, 255, on_canny_threshold_soft_new_value )
	cv.createTrackbar( 'LnDtctThr', 'Settings window', 30, 255, on_line_detection_threshold_new_value )
	cv.createTrackbar( 'MnLnLngth', 'Settings window', 100, 500, on_min_line_length_new_value )
	cv.createTrackbar( 'MxLineGap', 'Settings window', 30, 100, on_max_line_gap_new_value )
	
	while cv.waitKey( 10 ) != ord( 'q' ):
		success, frame = video_capture.read()
		if not success:
			break
		
		canny, detected_lines = get_lines(frame, canny_threshold_hard, canny_threshold_soft, line_detection_threshold, min_line_length, max_line_gap)
		
		detected_lines_image = np.zeros_like( frame )
		if detected_lines is not None:
			for line in detected_lines:
				x1, y1, x2, y2 = line[0]
				cv.line( detected_lines_image, (x1, y1), (x2, y2), (0, 0, 255), 2 )
		
		display_image = np.hstack( (
			frame,
			cv.cvtColor(canny,cv.COLOR_GRAY2BGR),
			detected_lines_image
		) )
		cv.imshow( 'Main window', display_image )
		
		print(get_qr(frame))
	
	video_capture.release()
	cv.destroyAllWindows()


if __name__ == "__main__":
	main()