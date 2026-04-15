import cv2 as cv
import numpy as np

from display import display
from get_qr import get_qr

def main():
	canny_threshold_hard: int = 0
	canny_threshold_soft: int = 0
	contour_size_threshold: int = 0
	
	def on_canny_threshold_hard_new_value(
		new_value: int,
	):
		nonlocal canny_threshold_hard
		canny_threshold_hard = new_value
	
	def on_canny_threshold_soft_new_value(
		new_value: int,
	):
		nonlocal canny_threshold_soft
		canny_threshold_soft = new_value
	
	def on_contour_size_threshold_new_value(
		new_value: int,
	):
		nonlocal contour_size_threshold
		contour_size_threshold = new_value
	
	video_capture = cv.VideoCapture( 0 )
	cv.namedWindow( 'Display window' )
	cv.namedWindow( 'Settings window' )
	
	cv.createTrackbar( 'CnyThrHrd', 'Settings window', 127, 255, on_canny_threshold_hard_new_value )
	cv.createTrackbar( 'CnyThrSft', 'Settings window', 63, 255, on_canny_threshold_soft_new_value )
	cv.createTrackbar( 'CntrSzThr', 'Settings window', 0, 10000, on_contour_size_threshold_new_value )
	
	while cv.waitKey( 10 ) != ord( 'q' ):
		success, frame = video_capture.read()
		if not success:
			break
		
		frame_gray = cv.cvtColor( frame, cv.COLOR_BGR2GRAY )
		frame_gray_blurred = cv.GaussianBlur( frame_gray, (5, 5), 0 )
		original_edges = cv.Canny( frame_gray_blurred, canny_threshold_soft, canny_threshold_hard )
		edges = cv.dilate( original_edges, np.ones( (3, 3), np.uint8 ), iterations = 1 )
		all_contours, _ = cv.findContours( edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE )
		contours = []
		for contour in all_contours:
			if cv.contourArea( contour ) > contour_size_threshold:
				contours.append( contour )
		shapes = []
		for contour in contours:
			perimeter = cv.arcLength( contour, True )
			shape = cv.approxPolyDP( contour, 0.02 * perimeter, True )
			shapes.append( shape )
		rectangles = []
		for shape in shapes:
			if len( shape ) == 4:
				rectangles.append( shape )
		dimensions_list = []
		for rectangle in rectangles:
			rectangle_info = cv.minAreaRect( rectangle )
			width, height = rectangle_info[1]
			dimensions = [width, height]
			dimensions.sort( reverse = True )
			dimensions_list.append( dimensions )
		
		display( frame, edges, contours, shapes, rectangles )
		print('Dimensions:')
		for dimensions in dimensions_list:
			print(f'{dimensions[0]} x {dimensions[1]}')
		print( get_qr( frame ) )
	
	video_capture.release()
	cv.destroyAllWindows()

if __name__ == "__main__":
	main()
