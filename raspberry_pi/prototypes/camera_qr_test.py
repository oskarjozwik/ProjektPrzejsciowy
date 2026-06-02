"""
Dependencies: picamera2  opencv-contrib-python  numpy
"""

import cv2 as cv
import numpy as np
from picamera2 import Picamera2

CAMERA_SIZE: tuple = (1920, 1080)
WINDOW_NAME: str = "camera_qr_test"


def main():
	picam = Picamera2()
	picam.configure(picam.create_preview_configuration(
		main = {"format": "RGB888", "size": CAMERA_SIZE}
	))
	picam.start()

	detector = cv.QRCodeDetector()
	last_printed = None

	print("Camera running. Hold a QR code up to the lens. Press 'q' to quit.")
	try:
		while True:
			frame = picam.capture_array()
			data, points, _ = detector.detectAndDecode(frame)

			if points is not None and len(points) > 0:
				polygon = np.intp(points).reshape(-1, 2)
				cv.polylines(frame, [polygon], True, (0, 255, 0), 2)

			if data != "":
				numeric = "numeric" if data.isnumeric() else "NOT numeric"
				if data != last_printed:
					print(f"QR: {data!r} ({numeric})")
					last_printed = data
				corner = np.intp(points).reshape(-1, 2)[0] if points is not None else (10, 30)
				cv.putText(frame, data, (int(corner[0]), int(corner[1]) - 10),
					cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
			else:
				last_printed = None

			cv.imshow(WINDOW_NAME, frame)
			if (cv.waitKey(1) & 0xFF) == ord("q"):
				break
	except KeyboardInterrupt:
		pass
	finally:
		picam.stop()
		cv.destroyAllWindows()


if __name__ == "__main__":
	main()
