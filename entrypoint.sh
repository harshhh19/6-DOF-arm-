#!/bin/bash
set -e

# Setup ROS 2 environment
source /opt/ros/lyrical/setup.bash
if [ -f "/workspace/install/setup.bash" ]; then
    source /workspace/install/setup.bash
fi

exec "$@"
