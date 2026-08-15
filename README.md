# EBiM Task 2 submission

This repository contains a Dockerized policy for **Task 2 — Deformable Material Handling (Thermal Pad Placement)**. The runtime consumes the official policy-facing ROS streams, drives the robot from the official spawn to the work pose using odometry, raises the spine, estimates the pad and visually designated target board from the head camera, and executes a guarded right-arm placement trajectory.

## Compatibility

- EBiM official scene/API baseline: `e36119cc43e949dc6269bfe5c1e7f613f9f24d0c`
- Local post-rollout QC baseline: Task 2 evaluator PR #67 commit
  `9ab59264de75f9cf0564eada259b13c706153c87` plus the merged PR #59
  loose-target stream; neither evaluator nor its diagnostic inputs are shipped
  in or consumed by the policy image.
- Isaac Sim: 5.1.0
- ROS: Jazzy, Fast DDS, host networking
- Architecture: Linux x86_64, Python 3.12 ABI
- Robot: mobile FR3 Duo with Robotiq grippers

The policy does **not** start or reset Isaac Sim. Start the organizer-provided Task 2 scene first and leave it at its official initial state.

## Build

```bash
docker build -t ebim-task2-policy:latest .
```

## Run one official attempt

Isaac Sim must already publish its normal Task 2 ROS graph. Run:

```bash
docker run --rm --network host \
  --ipc host \
  -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  ebim-task2-policy:latest
```

The default entry point executes exactly one attempt. It does not request a scene reset, control a recorder, subscribe to the eval camera, or invoke an evaluator.

Start state requirement: use the organizer's official field spawn. The policy
first performs an odometry-feedback staging maneuver to the work area; this
navigation is part of the deployed policy and is not a simulator-side pose
teleport. If an organizer wrapper already starts the robot at the work pose,
set that wrapper back to the official spawn before invoking this image.

Expected policy inputs:

- `/isaac/head_camera/image_raw` and camera info
- `/isaac/right_wrist_camera/image_raw`
- `/isaac/odom`, `/isaac/joint_states_full`, `/isaac/right_ee_pose`
- `/isaac/clock`

Expected command outputs include the public arm, gripper, spine, RMPflow target, and pedal-state topics used by the official Task 2 bridge.

The container is CPU-only; it does not require `--gpus`. Keep the organizer's
Isaac Sim container and ROS bridge running throughout the attempt.

## Runtime behavior and safety

1. Raise the spine while holding the expert ready pose.
2. Move from the official spawn to the calibrated work pose with odometry-bounded commands.
3. Estimate pad pose and the red target-board slot from head RGB.
4. Select one of two fixed expert motion assets based only on the visual target slot.
5. Continuously compensate normal base drift through the contact-critical pickup phase.
6. Require right-wrist RGB evidence that the blue pad is held; abort if it is absent.
7. Retarget transport and release from policy camera observations and normal robot state.

The eval camera and simulator object/mesh ground truth are excluded from policy observations. Evaluation is expected to be performed by the organizers after this container exits.

## Packaged implementation

Core policy modules, calibration payloads and the two fixed expert trajectories are distributed inside stripped CPython 3.12 compiled extensions. The expert payload is expanded once into the container's private runtime directory at startup; there is no per-control-step decryption or decompression. Small Python launch shims remain for subprocess compatibility. This packaging reduces direct source and trajectory disclosure; it is not presented as tamper-proof cryptography.

The readable core policy source is intentionally not published. This follows
the EBiM submission rule that source code is not required while preserving
execution reproducibility: the repository versions the exact compiled module
bytes, Docker build recipe, dependency ABI, embedded payloads, entrypoint,
checksums and verification procedure. Building this public repository does not
read files outside the repository, contact a private policy service, or require
a decryption key. See `REPRODUCIBILITY.md` for the precise guarantee and its
platform boundary.

See `ARTIFACT_PROVENANCE.md` for the exact separation between entrant-owned policy code, public demonstration-derived trajectory seeds, and official environment/evaluator components deliberately excluded from the image.

## Troubleshooting

- If the container reports that `/isaac/clock` or command subscribers are unavailable, verify host networking and that the official Isaac scene is fully ready.
- Use the same Fast DDS transport setting in the Isaac and policy containers.
- Do not run a second teleoperation controller concurrently with this policy.
- Logs and the non-privileged policy audit are written under `/tmp/ebim-task2-runtime` inside the container.
