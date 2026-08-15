FROM ros:jazzy-ros-base@sha256:31daab66eef9139933379fb67159449944f4e2dcf2e22c2d12cc715f29873e0f

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-pip \
        ros-jazzy-geometry-msgs \
        ros-jazzy-nav-msgs \
        ros-jazzy-rosgraph-msgs \
        ros-jazzy-sensor-msgs \
        ros-jazzy-std-msgs \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages --ignore-installed --no-cache-dir \
        --timeout 300 --retries 10 \
        numpy==2.2.6 \
        opencv-python-headless==4.13.0.92 \
        pandas==2.3.3 \
        pillow==12.3.0 \
        pyarrow==25.0.0

WORKDIR /opt/ebim-task2
COPY runtime/ /opt/ebim-task2/runtime/
COPY launch/ /opt/ebim-task2/launch/

ENV PYTHONPATH=/opt/ebim-task2/runtime \
    PYTHONUNBUFFERED=1 \
    FASTDDS_BUILTIN_TRANSPORTS=UDPv4

RUN chmod 0555 /opt/ebim-task2/launch/*.py /opt/ebim-task2/launch/*.sh \
    && source /opt/ros/jazzy/setup.bash \
    && python3 -c 'import importlib; names=("task2_head_color_pose","replay_task2_sample","replay_task2_cartesian_retarget","replay_task2_hybrid_retarget","run_head_rule_retarget_campaign","stage_task2_base_from_official_start","estimate_task2_initial_head_odom","estimate_task2_postdrift_head_target","move_task2_base_by_odom","submission_embedded_config","submission_embedded_assets","submission_entry"); assert all(importlib.import_module(name).__file__.endswith(".so") for name in names)'

ENTRYPOINT ["/opt/ebim-task2/launch/run_policy.sh"]
