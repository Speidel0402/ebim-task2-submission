# Copyright (c) 2026 The EBiM Benchmark Contributors
# SPDX-License-Identifier: Apache-2.0
"""Scene-agnostic argparse options shared by the Task 2 teleop bridge scripts.

Import-safe before SimulationApp is created (no Isaac Sim imports here).
"""

from __future__ import annotations

import argparse
from pathlib import Path


def add_common_bridge_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--embodiment",
        default="fr3duo_mobile",
        help="Embodiment key under task1_isaacsim/assets/embodiments.",
    )
    parser.add_argument(
        "--franka-root",
        default="/workspace/EBiM_Challenge/task1_isaacsim",
        help="Task 1 root (containing assets/embodiments) inside the "
        "container.",
    )
    parser.add_argument(
        "--disable-browser-command-topics",
        action="store_true",
        help="Do not subscribe to /isaac/browser/* command topics.",
    )
    parser.add_argument("--ros-publish-rate", type=float, default=60.0)
    parser.add_argument(
        "--pedal-linear-speed",
        type=float,
        default=0.5,
        help="Base lateral translation speed in m/s used for pedal A/B "
        "commands.",
    )
    parser.add_argument(
        "--pedal-angular-speed",
        type=float,
        default=1.2,
        help="Base yaw speed in rad/s used for pedal A+C/B+C commands.",
    )
    parser.add_argument(
        "--pedal-timeout",
        type=float,
        default=1.0,
        help="Seconds without a new /pedal/state message before forcing "
        "the base command to NONE.",
    )
    parser.add_argument(
        "--command-timeout",
        type=float,
        default=1.0,
        help="Seconds without a new message on a joint group's command "
        "topics before its cached command stops being applied (the drives "
        "hold the last applied target). Negative disables the watchdog.",
    )
    parser.add_argument(
        "--spine-keyboard-control",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use keyboard Up/Down arrows to command "
        "franka_spine_vertical_joint height.",
    )
    parser.add_argument(
        "--spine-keyboard-step",
        type=float,
        default=0.01,
        help="Height target increment in meters for each Up/Down key "
        "press or repeat.",
    )
    parser.add_argument(
        "--spine-keyboard-min",
        type=float,
        default=-0.05,
        help="Minimum franka_spine_vertical_joint target in meters for "
        "keyboard control.",
    )
    parser.add_argument(
        "--spine-keyboard-max",
        type=float,
        default=0.85,
        help="Maximum franka_spine_vertical_joint target in meters for "
        "keyboard control.",
    )
    parser.add_argument(
        "--spine-target-topic",
        default="/isaac/spine_target",
        help="Optional std_msgs/Float64 absolute target for "
        "franka_spine_vertical_joint. Values are clamped to the configured "
        "spine min/max limits.",
    )
    parser.add_argument(
        "--arm-keyboard-teleop",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Drive both arm end effectors with the Kit-window keyboard "
        "through dual RMPflow. While active, ROS arm and gripper "
        "commands are NOT applied (joint states are still published).",
    )
    parser.add_argument(
        "--agent-ee-target-topic",
        default="",
        help="Optional std_msgs/String JSON topic for headless RMPflow agent "
        "targets. Each payload selects left/right and supplies a robot-root "
        "position [x,y,z], optional orientation_wxyz, and optional "
        "gripper_open or normalized gripper_open_fraction. When set, it "
        "takes exclusive arm control.",
    )
    parser.add_argument(
        "--arm-teleop-linear-speed",
        type=float,
        default=0.18,
        help="End-effector translation speed in m/s while a move key is held.",
    )
    parser.add_argument(
        "--arm-teleop-angular-speed-deg",
        type=float,
        default=60.0,
        help="End-effector rotation speed in deg/s while a rotate key is "
        "held.",
    )
    parser.add_argument(
        "--arm-teleop-gripper-open",
        type=float,
        default=0.0,
        help="Gripper driver joint position in radians for the open state "
        "of the keyboard gripper toggle.",
    )
    parser.add_argument(
        "--arm-teleop-gripper-closed",
        type=float,
        default=0.8,
        help="Gripper driver joint position in radians for the closed "
        "state of the keyboard gripper toggle.",
    )
    parser.add_argument("--physics-hz", type=float, default=60.0)
    parser.add_argument("--render-hz", type=float, default=60.0)
    parser.add_argument(
        "--force-render-loop",
        action=argparse.BooleanOptionalAction,
        default=False,
        help=(
            "Force world.step(render=True) even when no ROS camera graph is "
            "enabled. Intended for renderer performance diagnostics."
        ),
    )
    parser.add_argument(
        "--configure-base-drives",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Author Task 1 actuator gains on the base drives "
        "(steer 500/50, wheel 0/5). "
        "Wheel joints need zero position stiffness for velocity control.",
    )
    parser.add_argument(
        "--apply-gripper-coupled-targets",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Also command the coupled Robotiq linkage joints "
        "(driver target x multiplier). "
        "Not needed for the default robot USD: its linkage joints carry "
        "PhysxMimicJointAPI, so PhysX couples them to the driver natively.",
    )
    parser.add_argument(
        "--disable-embedded-omnigraph",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Deactivate OmniGraph action graphs embedded in the robot USD "
        "(ROS_JointStates / Steer_joint_Controller); they duplicate this "
        "bridge "
        "and their script node crashes plain Isaac Sim.",
    )
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--app-width",
        type=int,
        default=1280,
        help="Kit render-buffer width (default: 1280).",
    )
    parser.add_argument(
        "--app-height",
        type=int,
        default=720,
        help="Kit render-buffer height (default: 720).",
    )
    _add_recording_args(parser)


def _add_recording_args(parser: argparse.ArgumentParser) -> None:
    """Demonstration-recording options (see task2_isaacsim/README.md and
    services/recording/record_task2.py)."""
    parser.add_argument(
        "--record",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Convenience switch: enables --publish-recording-topics, "
        "--enable-robot-cameras, --enable-scene-cameras, "
        "--publish-ground-truth, and --scene-reset-hotkey for a "
        "demonstration-recording session.",
    )
    parser.add_argument(
        "--publish-recording-topics",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Publish the recording streams (applied joint commands, "
        "odometry, applied base twist, EE poses — names from "
        "config/topics.yaml), all stamped with simulation time.",
    )
    parser.add_argument(
        "--enable-robot-cameras",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Publish the head + wrist robot cameras and /clock over ROS 2 "
        "(OmniGraph render products on the Camera prims authored in the "
        "robot USD).",
    )
    parser.add_argument(
        "--robot-camera-keys",
        type=str,
        default="",
        help=(
            "Optional comma-separated camera_sensors.yaml keys to publish. "
            "The empty default publishes every contracted robot camera. "
            "This is useful for per-camera performance diagnostics without "
            "changing camera poses, optics, or resolutions."
        ),
    )
    parser.add_argument(
        "--robot-camera-depth",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Also publish a depth topic per robot camera.",
    )
    parser.add_argument(
        "--robot-camera-frame-skip",
        type=int,
        default=0,
        help="Render frames skipped between camera messages (0 publishes "
        "every render frame; 1 halves the publish rate).",
    )
    parser.add_argument(
        "--robot-camera-sensor-data-qos",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Publish robot RGB/depth with ROS sensor-data QoS: best effort, "
            "volatile, keep-last depth 1. This matches the recorder's image "
            "subscriptions and prevents stale raw-image backlogs."
        ),
    )
    parser.add_argument(
        "--robot-camera-direct-tick",
        action=argparse.BooleanOptionalAction,
        default=False,
        help=(
            "Drive each camera RenderProduct directly from OnPlaybackTick. "
            "This avoids requesting an extra simulation frame inside a "
            "world.step(render=True) loop and is intended for that loop."
        ),
    )
    parser.add_argument(
        "--camera-sensors-yaml",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "assets"
        / "embodiments"
        / "fr3duo_mobile_task2"
        / "camera_sensors.yaml",
        help="Robot camera_sensors.yaml consumed by the camera publishers.",
    )
    parser.add_argument(
        "--enable-scene-cameras",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Build the scene cameras (e.g. the eval camera) described in "
        "the scene camera config: create the Camera prim when missing, "
        "apply the configured pose, and publish over ROS 2.",
    )
    parser.add_argument(
        "--scene-cameras-config",
        type=Path,
        default=None,
        help="Scene camera yaml; defaults to the scene script's "
        "config/cameras_<scene>.yaml.",
    )
    parser.add_argument(
        "--publish-ground-truth",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Publish task-object world poses (/isaac/task2/object_poses) "
        "and deformed thermal-pad vertices (/isaac/task2/pad_points).",
    )
    parser.add_argument(
        "--ground-truth-pad-every",
        type=int,
        default=6,
        help="Publish the thermal-pad vertices every N loop iterations "
        "(6 = 10 Hz at the default 60 Hz render rate; 0 disables).",
    )
    parser.add_argument(
        "--scene-reset-hotkey",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable the '5' key in the Isaac Sim window to reset (and "
        "optionally randomize) the task objects between episodes.",
    )
    parser.add_argument(
        "--randomize-objects",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Randomize the task-object spawn poses on each scene reset "
        "(the thermal pad and its sticker base move as one group).",
    )
    parser.add_argument(
        "--randomize-xy-cm",
        type=float,
        default=2.0,
        help="Max +/- XY spawn jitter in centimeters for --randomize-objects.",
    )
    parser.add_argument(
        "--randomize-yaw-deg",
        type=float,
        default=10.0,
        help="Max +/- yaw spawn jitter in degrees for --randomize-objects.",
    )
    parser.add_argument(
        "--randomize-target-board-slot",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Stress-test mode: on each scene reset, uniformly place the "
        "red board_target asset in one of the four authored board slots and "
        "swap the displaced green board into the original target slot. "
        "Disabled by default because the public official scene keeps the "
        "target identity fixed.",
    )
    parser.add_argument(
        "--randomization-seed",
        type=int,
        default=None,
        help="Optional deterministic seed for the sequence of default scene "
        "resets. Per-request JSON seeds remain independent of this sequence.",
    )


def resolve_recording_flags(args) -> None:
    """Fold the --record convenience switch into the individual flags."""
    if getattr(args, "record", False):
        args.publish_recording_topics = True
        args.enable_robot_cameras = True
        args.enable_scene_cameras = True
        args.publish_ground_truth = True
        args.scene_reset_hotkey = True
