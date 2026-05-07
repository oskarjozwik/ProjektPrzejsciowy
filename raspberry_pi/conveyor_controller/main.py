import cv2 as cv

from package_detection.check_for_package import check_for_package

def main():
	while cv.waitKey( 10 ) != ord( 'q' ):
		package_check_result = check_for_package()
		
		if not package_check_result.box_detected:
			print('Box not detected!')
		else:
			print(f'Box detected! Dimensions: \t{int(package_check_result.box_dimensions.x*1000)}mm x \t{int(package_check_result.box_dimensions.y*1000)}mm x \t{int(package_check_result.box_dimensions.z*1000)}mm x')
		
		if not package_check_result.qr_detected:
			print('QR not detected!')
		else:
			print(f'QR detected! Code: {package_check_result.qr_code}')

if __name__ == "__main__":
	main()