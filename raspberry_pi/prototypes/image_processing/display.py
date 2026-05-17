import cv2 as cv
import numpy as np

def display(base_frame, edges, contours, shapes, rectangles) -> None:
	empty_frame = np.zeros_like(base_frame)
	
	edges_display = cv.cvtColor( edges, cv.COLOR_GRAY2BGR )
	
	contours_display = base_frame.copy()
	for contour in contours:
		cv.drawContours( contours_display, [contour], -1, (0, 0, 255), 2 )
	
	shapes_display = base_frame.copy()
	for shape in shapes:
		cv.drawContours( shapes_display, [shape], -1, (0, 0, 255), 2 )
	
	rectangles_display = base_frame.copy()
	for rectangle in rectangles:
		cv.drawContours( rectangles_display, [rectangle], -1, (0, 0, 255), 2 )
	
	display_image = np.vstack(
		(
			np.hstack((base_frame, edges_display, contours_display)),
			np.hstack((shapes_display, rectangles_display, empty_frame))
		)
	)
	cv.imshow( 'Display window', display_image )