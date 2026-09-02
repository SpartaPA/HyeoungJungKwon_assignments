#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$SCRIPT_DIR/ros2_ws"

source /opt/ros/humble/setup.bash
cd "$WORKSPACE"
colcon build --symlink-install --event-handlers console_direct+
source install/setup.bash
PYTHONPATH="$WORKSPACE/src/turtle_py${PYTHONPATH:+:$PYTHONPATH}" pytest -q src/turtle_py/test
echo "Build and pure-function tests passed. Run LINUX_COMMANDS.md for GUI and ROS checks."
