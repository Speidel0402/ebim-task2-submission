# ROS interface and compliance boundary

The policy is an external ROS 2 client. It does not load Isaac Sim, open the
USD stage, request a reset, or call the evaluator.

## Observation allowlist

| Topic | Type | Use |
|---|---|---|
| `/isaac/clock` | `rosgraph_msgs/msg/Clock` | simulation pacing and stale-frame rejection |
| `/isaac/head_camera/image_raw` | `sensor_msgs/msg/Image` | pad and visually designated target estimation |
| `/isaac/head_camera/camera_info` | `sensor_msgs/msg/CameraInfo` | official camera intrinsics |
| `/isaac/right_wrist_camera/image_raw` | `sensor_msgs/msg/Image` | bounded placement/release alignment |
| `/isaac/odom` | `nav_msgs/msg/Odometry` | base navigation and drift compensation |
| `/isaac/cmd_vel_applied` | `geometry_msgs/msg/Twist` | base stop/settle confirmation |
| `/isaac/joint_states_full` | `sensor_msgs/msg/JointState` | measured spine bootstrap state |

The left wrist camera is neither required nor consumed by this right-arm
policy. The policy never subscribes to `/isaac/eval_camera/*`, object poses,
pad mesh points, geometry state, reset events/offsets, semantic labels, or the
evaluation service.

## Command boundary

The policy publishes the official pedal-state, arm and gripper command
interfaces required by the running Task 2 bridge. Startup preflight requires
an organizer-owned subscriber for every command topic before any motion is
attempted.

The RMPFlow controller layer installs two explicit bridge-extension inputs for
Cartesian endpoint and lift-column targets:

| Topic | Role | Status |
|---|---|---|
| `/isaac/task2/agent_ee_target` | Cartesian endpoint consumed by the supplied RMPFlow overlay | Custom adapter; not in official `topics.yaml` |
| `/isaac/spine_target` | Lift-column target consumed by the supplied overlay | Custom adapter; not in official `topics.yaml` |

Those adapter topics are neither claimed as official interfaces nor as
real-robot commands. The current overlay converts their targets through
per-arm Lula/RMPFlow and applies the result within the bridge; it does not
publish the resulting arm targets back onto the public command topics. This
execution detail requires organizer confirmation or a topic-republishing
adapter revision before an official run. The policy does not load Isaac Sim,
open the USD stage, call an articulation API, request a reset, or invoke the
evaluator.

## Transport compatibility

Observation subscriptions request sensor-data/BEST_EFFORT QoS. Such readers
match both RELIABLE and BEST_EFFORT writers. Camera frames must also agree with
the active `/isaac/clock` epoch; duplicate or non-increasing timestamps are
ignored. This handles ROS writer/QoS differences without selecting a hidden
publisher or inspecting simulator state.
