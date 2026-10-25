#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ALIGN_GZ_ROOT="${ALIGN_GZ_ROOT:-$HOME/projects/drone_alignment_vendor/ardupilot_gazebo}"

source /opt/ros/jazzy/setup.bash
export GZ_SIM_SYSTEM_PLUGIN_PATH="$ALIGN_GZ_ROOT/build${GZ_SIM_SYSTEM_PLUGIN_PATH:+:$GZ_SIM_SYSTEM_PLUGIN_PATH}"
export GZ_SIM_RESOURCE_PATH="$PROJECT_ROOT/sim/models:$ALIGN_GZ_ROOT/models:$ALIGN_GZ_ROOT/worlds${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"

exec gz sim -v 3 -r "$PROJECT_ROOT/sim/worlds/platform_world.sdf" --render-engine ogre "$@"
