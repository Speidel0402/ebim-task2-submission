# Pre-submission verification

Run this checklist against the exact commit and image tag submitted to the
organizers.

## Repository and build

- [ ] Verify the repository payload: `sha256sum -c REPOSITORY_SHA256SUMS.txt`.
- [ ] Build the documented image tag from a fresh checkout:
  `docker build --build-arg TERMINAL_CONTROLLER=rmpflow -t ebim-task2-policy:20260816-rmpflow-stagefix-final .`
- [ ] Confirm that no Docker image archive, benchmark workspace, credential or
  generated cache is committed to Git.
- [ ] Confirm that the public repository visibility and organizer access match
  the submission instructions.

## Runtime contract

- [ ] Start the organizer-provided Task 2 scene at its official initial state.
- [ ] Run exactly one arm-command producer. Disable keyboard, browser, or
  other teleoperation controllers before starting the policy.
- [ ] Inspect `/tmp/ebim-task2-runtime/ros_interface_preflight.json` and
  confirm the expected ROS topic types, QoS and command-topic consumers.
- [ ] Confirm that the policy does not subscribe to eval-camera, object-state,
  reset or evaluator inputs.
- [ ] Confirm the active camera set contains only the declared policy cameras.

## RMPFlow decision

The policy's internal terminal action is Cartesian. The delivered overlay maps
it through per-arm Lula/RMPFlow. Its current revision applies the generated
joint targets within the bridge after receiving the two declared extension
topics below:

| Extension topic | Purpose |
|---|---|
| `/isaac/task2/agent_ee_target` | Cartesian endpoint target |
| `/isaac/spine_target` | Lift-column target |

- [ ] Obtain organizer confirmation for this bridge execution path, **or** use
  an organizer-approved adapter revision that republishes the generated
  `sensor_msgs/msg/JointState` targets through the official left/right arm
  command topics.
- [ ] Record the chosen adapter revision, image ID, benchmark commit and one
  representative seed/run log with the submission materials.

This check protects the interface boundary: no controller should bypass the
organizer-approved execution contract merely because the internal policy action
space is Cartesian.
