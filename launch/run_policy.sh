#!/usr/bin/env bash
set -euo pipefail

# ROS setup scripts legitimately probe optional variables.  Source them with
# nounset disabled, then restore strict mode for our own launcher.
set +u
source /opt/ros/jazzy/setup.bash
set -u
export FASTDDS_BUILTIN_TRANSPORTS="${FASTDDS_BUILTIN_TRANSPORTS:-UDPv4}"
export PYTHONUNBUFFERED=1
exec python3 /opt/ebim-task2/launch/run_module.py submission_entry "$@"
