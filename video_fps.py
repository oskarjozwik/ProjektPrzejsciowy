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
    parser.add_argument("--fps", type=float, default=0.0,
                        help="force a max framerate (0 = camera default; e.g. 60 lifts the "
                             "low-light ~15fps auto-exposure cap, at the cost of a darker image)")
    args = parser.parse_args()

    picam = Picamera2(camera_num=args.camera)
    picam.configure(picam.create_preview_configuration(
        main={"format": "RGB888", "size": (args.width, args.height)},
    ))
    picam.start()

    if args.fps > 0:
        # Cap the frame duration so auto-exposure can't slow the framerate down.
        duration_us = int(1_000_000 / args.fps)
        picam.set_controls({"FrameDurationLimits": (duration_us, duration_us)})

    # The pipeline may adjust the size; report what we actually got.
    actual_w, actual_h = picam.camera_configuration()["main"]["size"]
    print(f"Requested {args.width}x{args.height}, capturing at {actual_w}x{actual_h}. "
          f"Press 'q' to quit.")

    fps = 0.0
    previous = time.monotonic()
    try:
        while True:
            # capture_request() gives the frame and its metadata together, so
            # the exposure time matches the frame we display.
            request = picam.capture_request()
            frame = request.make_array("main")
            exposure_us = request.get_metadata().get("ExposureTime", 0)
            request.release()

            now = time.monotonic()
            elapsed = now - previous
            previous = now
            if elapsed > 0:
                instantaneous = 1.0 / elapsed
                # Exponential smoothing so the number doesn't jitter.
                fps = instantaneous if fps == 0.0 else 0.9 * fps + 0.1 * instantaneous

            cv.putText(frame, f"{fps:5.1f} FPS", (10, 35),
                       cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv.putText(frame, f"{exposure_us / 1000:5.1f} ms exp", (10, 70),
                       cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv.imshow("video_fps", frame)
            if (cv.waitKey(1) & 0xFF) == ord("q"):
                break
    finally:
        picam.stop()
        cv.destroyAllWindows()


if __name__ == "__main__":
    main()
