#!/usr/bin/env python3
"""Raspberry Pi camera FPS benchmark with an FPS + exposure overlay (picamera2).

Important: WIDTH/HEIGHT only set the output (scaling) size of the displayed
stream. The framerate ceiling is set by which *sensor mode* runs, which you
pick with --mode (see --list-modes). On the Camera v2 (imx219) the ~100fps
"480p" figure is sensor mode 0 (a cropped 640x480 mode) — selecting a small
output size alone will NOT engage it.

Usage:
    python video_fps.py WIDTH HEIGHT [--fps F] [--mode N] [--no-display]
    python video_fps.py --list-modes

    # e.g. push the imx219 toward 100fps (needs good light):
    python video_fps.py 640 480 --mode 0 --fps 100

Press 'q' to quit (Ctrl-C when using --no-display).

Dependencies: picamera2  opencv-contrib-python
"""

import argparse
import time

import cv2 as cv
from picamera2 import Picamera2


def main():
    parser = argparse.ArgumentParser(description="Pi camera FPS benchmark with overlay.")
    parser.add_argument("width", type=int, nargs="?", help="output width in pixels")
    parser.add_argument("height", type=int, nargs="?", help="output height in pixels")
    parser.add_argument("--camera", type=int, default=0, help="camera index (default: 0)")
    parser.add_argument("--fps", type=float, default=0.0,
                        help="force a max framerate (0 = camera default)")
    parser.add_argument("--mode", type=int, default=-1,
                        help="sensor mode index to force (see --list-modes); -1 = auto")
    parser.add_argument("--list-modes", action="store_true",
                        help="list the sensor modes (size + max fps) and exit")
    parser.add_argument("--no-display", action="store_true",
                        help="benchmark capture without the preview window (isolates the camera "
                             "from imshow/X11); prints FPS to the console")
    args = parser.parse_args()

    picam = Picamera2(camera_num=args.camera)

    if args.list_modes:
        for i, mode in enumerate(picam.sensor_modes):
            w, h = mode["size"]
            print(f"  mode {i}: {w}x{h} @ {mode['fps']:.0f} fps  (bit_depth {mode['bit_depth']})")
        return

    if args.width is None or args.height is None:
        parser.error("WIDTH and HEIGHT are required (unless using --list-modes)")

    config_kwargs = {"main": {"format": "RGB888", "size": (args.width, args.height)}}
    if args.mode >= 0:
        if args.mode >= len(picam.sensor_modes):
            parser.error(f"--mode {args.mode} out of range; "
                         f"this camera has {len(picam.sensor_modes)} modes (see --list-modes)")
        # Forcing the raw size is what actually selects the sensor mode / fps ceiling.
        config_kwargs["raw"] = {"size": picam.sensor_modes[args.mode]["size"]}
    picam.configure(picam.create_video_configuration(**config_kwargs))
    picam.start()

    if args.fps > 0:
        duration_us = int(1_000_000 / args.fps)
        picam.set_controls({"FrameDurationLimits": (duration_us, duration_us)})

    cfg = picam.camera_configuration()
    out_w, out_h = cfg["main"]["size"]
    raw_size = cfg["raw"]["size"] if cfg.get("raw") else "auto"
    hint = "Counting only (Ctrl-C to stop)." if args.no_display else "Press 'q' to quit."
    print(f"Output {out_w}x{out_h}, sensor mode {raw_size}. {hint}")

    fps = 0.0
    previous = time.monotonic()
    last_print = previous
    try:
        while True:
            request = picam.capture_request()
            exposure_us = request.get_metadata().get("ExposureTime", 0)
            # Skip the (costly) array conversion when we're not displaying, so the
            # number reflects camera throughput rather than RGB copy + imshow.
            frame = None if args.no_display else request.make_array("main")
            request.release()

            now = time.monotonic()
            elapsed = now - previous
            previous = now
            if elapsed > 0:
                instantaneous = 1.0 / elapsed
                # Exponential smoothing so the number doesn't jitter.
                fps = instantaneous if fps == 0.0 else 0.9 * fps + 0.1 * instantaneous

            if args.no_display:
                if now - last_print >= 1.0:
                    print(f"{fps:6.1f} FPS   {exposure_us / 1000:5.1f} ms exp")
                    last_print = now
            else:
                cv.putText(frame, f"{fps:5.1f} FPS", (10, 35),
                           cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv.putText(frame, f"{exposure_us / 1000:5.1f} ms exp", (10, 70),
                           cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv.imshow("video_fps", frame)
                if (cv.waitKey(1) & 0xFF) == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        picam.stop()
        cv.destroyAllWindows()


if __name__ == "__main__":
    main()
