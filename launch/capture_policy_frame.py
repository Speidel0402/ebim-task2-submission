#!/usr/bin/env python3
"""Save one raw Task 2 policy-camera frame for operator visual inspection.

This is a QC utility only. It subscribes to exactly one caller-selected ROS
Image topic and does not alter simulation state, recording streams, or data
labels. Use only ``head``, ``left_wrist_camera``, or ``right_wrist_camera``
for policy-camera checks; never pass the QC-only eval camera to training.
"""

from __future__ import annotations

import argparse
import sys
import time

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class FrameSaver(Node):
    def __init__(self, topic: str, output: str) -> None:
        super().__init__("task2_policy_frame_saver")
        self.output = output
        self.saved = False
        self.error = ""
        self.create_subscription(
            Image, topic, self._on_image, qos_profile_sensor_data
        )

    def _on_image(self, msg: Image) -> None:
        if self.saved or self.error:
            return
        encoding = str(msg.encoding).lower()
        channels = {"rgb8": 3, "bgr8": 3, "rgba8": 4, "bgra8": 4}.get(encoding)
        if channels is None or msg.width <= 0 or msg.height <= 0:
            self.error = f"unsupported image encoding={encoding!r}"
            return
        row = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.step)
        image = row[:, : msg.width * channels].reshape(msg.height, msg.width, channels)
        if encoding == "rgb8":
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif encoding == "rgba8":
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        elif encoding == "bgra8":
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        if not cv2.imwrite(self.output, image):
            self.error = f"could not write {self.output}"
            return
        self.saved = True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout-s", type=float, default=15.0)
    args = parser.parse_args(argv)
    rclpy.init()
    node = FrameSaver(args.topic, args.output)
    try:
        deadline = time.monotonic() + args.timeout_s
        while time.monotonic() < deadline and not node.saved and not node.error:
            rclpy.spin_once(node, timeout_sec=0.25)
        if node.saved:
            print(f"saved {args.output}")
            return 0
        print(node.error or f"timed out waiting for {args.topic}", file=sys.stderr)
        return 2
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
