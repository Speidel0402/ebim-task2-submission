# EBiM Task 2 submission

This repository contains a Dockerized policy for **Task 2 — Deformable Material Handling (Thermal Pad Placement)**. The runtime consumes only the official policy-facing ROS streams, drives the robot from the official spawn to the work pose using odometry, raises the spine, estimates the pad and visually designated target board from the head camera, and executes a right-arm placement trajectory.

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

## Recommended: complete cloud delivery

This GitHub repository is the compact, reviewable submission component. For a
matched policy image, Isaac Sim runtime, benchmark workspace and RMPFlow bridge
overlay, use the complete cloud delivery first:

- [Download the complete delivery](https://drive.google.com/file/d/12HafElMaPuBduBuj8GEUksmjtrNVlqCS/view?usp=drive_link)
- Archive: `ebim-task2-rmpflow-stagefix-20260816-reprofix.tar` (7.68 GB)
- SHA-256: `b455b3cc4ba298eda68c11c1f5c48d065b2912ccc78874006a41b2bf27a7fc16`

Restore the complete package on Linux x86_64 with Docker Engine, Docker Compose
v2, NVIDIA drivers, NVIDIA Container Toolkit and a licensed Isaac Sim display
host:

```bash
sha256sum ebim-task2-rmpflow-stagefix-20260816-reprofix.tar
tar -xf ebim-task2-rmpflow-stagefix-20260816-reprofix.tar
cd final_20260816_rmpflow_stagefix/complete_offline
sha256sum -c SHA256SUMS

./load_images.sh
./extract_workspace.sh /absolute/empty/path/benchmark

export HOST_UID=$(id -u)
export HOST_GID=$(id -g)
export DISPLAY=:0
export XAUTHORITY=/run/user/$(id -u)/gdm/Xauthority
export ISAAC_DOCKER_ROOT=/absolute/empty/docker-root
sudo runtime_workspace/prepare_isaac_docker_root.sh \
  "$ISAAC_DOCKER_ROOT" "$HOST_UID" "$HOST_GID"

cd /absolute/empty/path/benchmark/docker
docker compose --env-file .env.base --profile isaac-sim-5.1.0 up -d \
  --no-build isaac-sim-5-1-0
```

Use the episode command in the complete-delivery section below, followed by
the packaged policy image. This is the recommended path because its images,
workspace and bridge overlay were prepared together.

## GitHub-only policy build

This route builds only the policy container. It does not provide Isaac Sim,
the benchmark workspace, Docker images, or the matching RMPFlow overlay; those
components must already be started separately.

```bash
docker build \
  --build-arg TERMINAL_CONTROLLER=rmpflow \
  -t ebim-task2-policy:20260816-rmpflow-stagefix-final .
```

Verify the published repository bytes before building:

```bash
sha256sum -c REPOSITORY_SHA256SUMS.txt
```

## Run one official attempt

Isaac Sim must already publish its normal Task 2 ROS graph. Run:

```bash
docker run --rm --network host \
  --ipc host \
  -e ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}" \
  -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  ebim-task2-policy:20260816-rmpflow-stagefix-final
```

The default entry point executes exactly one attempt. It does not request a scene reset, control a recorder, subscribe to the eval camera, or invoke an evaluator.

Start state requirement: use the organizer's official field spawn. The policy
first performs an odometry-feedback staging maneuver to the work area; this
navigation is part of the deployed policy and is not a simulator-side pose
teleport. If an organizer wrapper already starts the robot at the work pose,
set that wrapper back to the official spawn before invoking this image.

Before publishing any command, the entry point waits for the exact ROS topic
types and for consumers of every command topic. It writes the discovered
publisher/subscriber QoS profiles to
`/tmp/ebim-task2-runtime/ros_interface_preflight.json`. Camera and other
observation readers request BEST_EFFORT, which is compatible with both the
BEST_EFFORT and RELIABLE publishers used by supported Isaac ROS graph variants.
Images outside the active `/isaac/clock` epoch and duplicate timestamps are
discarded.

Required policy inputs:

- `/isaac/head_camera/image_raw` and camera info
- `/isaac/right_wrist_camera/image_raw`
- `/isaac/odom`, `/isaac/cmd_vel_applied`, `/isaac/joint_states_full`
- `/isaac/clock`

Expected command outputs include the public arm, gripper and pedal-state
topics. In RMPFlow mode, Cartesian targets are handled by the delivered bridge
adapter: `/isaac/task2/agent_ee_target` selects an arm endpoint and
`/isaac/spine_target` selects the lift-column target. These explicit extension
topics are not entries in the organizer's `topics.yaml`; they must be enabled
only with the delivered, organizer-compatible bridge overlay.

The container is CPU-only; it does not require `--gpus`. Keep the organizer's
Isaac Sim container and ROS bridge running throughout the attempt.

## Complete-delivery episode command

The complete, checksummed delivery is provided separately because it includes
large Docker image archives, the benchmark workspace and the RMPFlow bridge
overlay used to align Cartesian policy targets with the Task 2 motion-generation
path. These large artifacts must not be committed to Git history:

- [Download the complete offline bundle](https://drive.google.com/file/d/12HafElMaPuBduBuj8GEUksmjtrNVlqCS/view?usp=drive_link)
- Archive: `ebim-task2-rmpflow-stagefix-20260816-reprofix.tar` (7.68 GB)
- SHA-256: `b455b3cc4ba298eda68c11c1f5c48d065b2912ccc78874006a41b2bf27a7fc16`

The Drive artifact is access-controlled. Organizers must be granted access
before relying on it as supplementary reproduction material.

On a Linux host with Docker, NVIDIA drivers, NVIDIA Container Toolkit and a
licensed Isaac Sim display host, restore and run the full delivery as follows:

```bash
sha256sum ebim-task2-rmpflow-stagefix-20260816-reprofix.tar
tar -xf ebim-task2-rmpflow-stagefix-20260816-reprofix.tar
cd final_20260816_rmpflow_stagefix/complete_offline
sha256sum -c SHA256SUMS

./load_images.sh
./extract_workspace.sh /absolute/empty/path/benchmark

export HOST_UID=$(id -u)
export HOST_GID=$(id -g)
export DISPLAY=:0
export XAUTHORITY=/run/user/$(id -u)/gdm/Xauthority
export ISAAC_DOCKER_ROOT=/absolute/empty/docker-root
sudo runtime_workspace/prepare_isaac_docker_root.sh \
  "$ISAAC_DOCKER_ROOT" "$HOST_UID" "$HOST_GID"

cd /absolute/empty/path/benchmark/docker
docker compose --env-file .env.base --profile isaac-sim-5.1.0 up -d \
  --no-build isaac-sim-5-1-0

cd ../..
runtime_workspace/restart_task2_isaac_randomized.sh \
  --terminal-controller rmpflow --headless --render-hz 60 \
  --ros-publish-rate 30 --policy-cameras-only --strict-official-runtime \
  --robot-camera-keys head,wrist_left,wrist_right \
  --robot-camera-frame-skip 2 --robot-camera-sensor-data-qos \
  --force-render-loop

docker run --rm --network host --ipc host \
  -e ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}" \
  -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  ebim-task2-policy:20260816-rmpflow-stagefix-final
```

## Controller alignment

The policy represents its terminal action as Cartesian endpoint targets. The
RMPFlow bridge layer converts those targets through per-arm Lula/RMPFlow motion
generation, while preserving the Task 2 scene, physics, policy-observation and
evaluator boundaries. This makes the policy's internal Cartesian action space
compatible with the benchmark's joint-level robot execution path without
granting access to simulator object state or evaluator inputs.

`/isaac/task2/agent_ee_target` and `/isaac/spine_target` are explicit bridge
extension inputs, not entries in the organizer's public `topics.yaml` and not
claims of real-robot interfaces. The current overlay applies the resulting
joint actions inside the supplied bridge. Run it with the delivered matching
overlay. See `PRE_SUBMISSION_VERIFICATION.md`.

The policy image itself does not start Isaac Sim or modify the organizer's
scene.

## Runtime behavior and safety

1. Raise the spine while holding the expert ready pose.
2. Move from the official spawn to the calibrated work pose with odometry-bounded commands.
3. Estimate pad pose and the red target-board slot from head RGB.
4. Select one of two fixed expert motion assets based only on the visual target slot.
5. Continuously compensate normal base drift through the contact-critical pickup phase.
6. Use right-wrist RGB for bounded visual alignment and release adaptation.
7. Retarget transport and release from policy camera observations and normal robot state; wrist perception is not used as a fatal pickup gate.

The eval camera and simulator object/mesh ground truth are excluded from policy observations. Evaluation is expected to be performed by the organizers after this container exits.

## Runtime package

The repository includes the runtime modules, launch scripts, kinematics and
Docker recipe required by the documented image. Build and file integrity can be
checked with the commands above; the image requires no private service or
credential.

## Evaluation

The official Task 2 evaluator is available separately in the benchmark and is
not run by the policy container. It calculates pad/target IoU and orientation
from eval-camera streams after policy motion stops. See `EVALUATION.md` for
verified one-episode and multi-seed procedures, result retention, and the
exact packaged randomization settings.

## Troubleshooting

- If the ROS preflight times out, inspect `ros_interface_preflight.json` when
  present and verify host networking, `ROS_DOMAIN_ID`, topic types, and that
  the official Isaac scene and position-controller sidecar are fully ready.
- Use the same Fast DDS transport setting in the Isaac and policy containers.
- Do not run a second teleoperation controller concurrently with this policy.
- Logs and the non-privileged policy audit are written under `/tmp/ebim-task2-runtime` inside the container.
