import cv2 as cv
import numpy as np


def get_lines(
	image: np.ndarray,
	canny_threshold_hard: int,
	canny_threshold_soft: int,
	line_detection_threshold: int,
	min_line_length: int,
	max_line_gap: int
):
	image_grayscale = cv.cvtColor( image, cv.COLOR_BGR2GRAY )
	image_edges = cv.Canny( image_grayscale, canny_threshold_hard, canny_threshold_soft )
	return image_edges, cv.HoughLinesP(
		image_edges,
		1,
		np.pi / 180,
		line_detection_threshold,
		minLineLength=min_line_length,
		maxLineGap=max_line_gap
	)
