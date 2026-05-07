import cv2 as cv
import numpy as np

class ContourDimensions:
	def __init__(
		self,
		x: float,
		y: float,
	):
		self.x = x
		self.y = y

class ContourCheckResult:
	def __init__(
		self,
		contour_detected: bool,
		contour_dimensions: ContourDimensions = ContourDimensions( 0, 0 ),
	):
		self.contour_detected = contour_detected
		self.contour_dimensions = contour_dimensions

def check_for_contours(
	frame: np.ndarray,
	canny_threshold_hard: int,
	canny_threshold_soft: int,
	contour_size_threshold: int,
) -> ContourCheckResult:
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
	
	if len( dimensions_list ) == 0:
		return ContourCheckResult( contour_detected = False )
	
	return ContourCheckResult( contour_detected = True, contour_dimensions = dimensions_list[0] )
