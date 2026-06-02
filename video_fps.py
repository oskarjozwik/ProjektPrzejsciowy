#!/usr/bin/env python3
"""Display Raspberry Pi camera video at a given capture size with an FPS counter.

Uses picamera2 (the native libcamera API for the Pi camera module).

Usage:
    python video_fps.py WIDTH HEIGHT [--camera N]

Example:
    python video_fps.py 1280 720

Press 'q' in the window to quit.

Dependencies: picamera2  opencv-contrib-python
"""

import argparse
import time

import cv2 as cv
from picamera2 import Picamera2


def main():
    parser = argparse.ArgumentParser(description="Show Pi camera video with an FPS overlay.")
    parser.add_argument("width", type=int, help="capture width in pixels")
    parser.add_argument("height", type=int, help="capture height in pixels")
    parser.add_argument("--camera", type=int, default=0, help="camera index (default: 0)")
    args = parser.parse_args()

    picam = Picamera2(camera_num=args.camera)
    picam.configure(picam.create_preview_configuration(
        main={"format": "RGB888", "size": (args.width, args.height)},
    ))
    picam.start()

    # The pipeline may adjust the size; report what we actually got.
    actual_w, actual_h = picam.camera_configuration()["main"]["size"]
    print(f"Requested {args.width}x{args.height}, capturing at {actual_w}x{actual_h}. "
          f"Press 'q' to quit.")

    fps = 0.0
    previous = time.monotonic()
    try:
        while True:
            frame = picam.capture_array()

            now = time.monotonic()
            elapsed = now - previous
            previous = now
            if elapsed > 0:
                instantaneous = 1.0 / elapsed
                # Exponential smoothing so the number doesn't jitter.
                fps = instantaneous if fps == 0.0 else 0.9 * fps + 0.1 * instantaneous

            cv.putText(frame, f"{fps:5.1f} FPS", (10, 35),
                       cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv.imshow("video_fps", frame)
            if (cv.waitKey(1) & 0xFF) == ord("q"):
                break
    finally:
        picam.stop()
        cv.destroyAllWindows()


if __name__ == "__main__":
    main()
