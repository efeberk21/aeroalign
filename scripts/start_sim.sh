#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ALIGN_GZ_ROOT="${ALIGN_GZ_ROOT:-$HOME/projects/drone_alignment_vendor/ardupilot_gazebo}"
ALIGN_WORLD="${ALIGN_WORLD:-platform_world}"
WORLD_FILE="$PROJECT_ROOT/sim/worlds/${ALIGN_WORLD}.sdf"

if [ ! -f "$WORLD_FILE" ]; then
  echo "Dunya dosyasi bulunamadi: $WORLD_FILE" >&2
  exit 1
fi

source /opt/ros/jazzy/setup.bash
export GZ_SIM_SYSTEM_PLUGIN_PATH="$ALIGN_GZ_ROOT/build${GZ_SIM_SYSTEM_PLUGIN_PATH:+:$GZ_SIM_SYSTEM_PLUGIN_PATH}"
export GZ_SIM_RESOURCE_PATH="$PROJECT_ROOT/sim/models:$ALIGN_GZ_ROOT/models:$ALIGN_GZ_ROOT/worlds${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"

exec gz sim -v 3 -r "$WORLD_FILE" --render-engine ogre "$@"