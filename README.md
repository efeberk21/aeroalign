# AeroAlign

Vision-based platform alignment for a simulated drone using ROS 2, Gazebo, ArduPilot, and PyTorch.

AeroAlign will detect a delivery platform in a downward-facing camera image and issue bounded horizontal velocity commands to align a simulated drone above it. The first version ends with hovering over the platform. It does not include autonomous landing or real-aircraft operation.

## Current status

Environment setup has started. The flight and perception application has not been implemented yet.

| Component | Environment | Status |
|---|---|---|
| Training | Windows, Python 3.12, RTX 4060 | CUDA, backward pass and YOLO11n architecture forward verified |
| ROS 2 | Ubuntu 24.04 VM, Jazzy | Existing installation reported by the developer |
| Simulation | Gazebo Harmonic 8.15.0 | Existing installation; visual jitter under investigation |
| Autopilot | ArduPilot SITL | Not installed or verified for this project yet |
| Ground station | Mission Planner on Windows | Installation status not checked yet |

## Working environments

- Windows: training, Git operations, and Mission Planner.
- Ubuntu VM: Gazebo, ROS 2 nodes, and ArduPilot SITL.
- GitHub: source, configuration, documentation, and measured results.

Keep virtual environments, datasets, checkpoints, generated ROS build output, and private machine details out of Git.

## Documentation

- [15-day roadmap (Turkish)](docs/roadmap.md)
- [Day 1 setup and diagnostics (Turkish)](docs/day-01.md)
- [Progress and decisions](docs/progress.md)
- [Environment observations](reports/environment.md)
- [Actual Windows GPU check](reports/windows_gpu_check.json)
- [Installed Windows package versions](reports/requirements_windows.txt)

The roadmap describes intended work. Checked items and evidence in the progress log describe work actually completed.
