# AeroAlign

Vision-based platform alignment for a simulated drone using ROS 2, Gazebo, ArduPilot, and PyTorch.

AeroAlign will detect a delivery platform in a downward-facing camera image and issue bounded horizontal velocity commands to align a simulated drone above it. The first version ends with hovering over the platform. It does not include autonomous landing or real-aircraft operation.

## Current status

Day 1 environment checks, Day 2 simulation flights and the revised Day 3 functional camera checkpoint have passed. Day 4's first platform and PNG/CSV recorder work: 141 pilot images at nominal 5, 8 and 10 m passed the recording-integrity audit. Additional platform/ground/light variants and platform-absent recordings remain before Day 4 is complete. Detection training and alignment control are still pending; application development continues together, step by step.

| Component | Environment | Status |
|---|---|---|
| Training | Windows, Python 3.12, RTX 4060 | CUDA, backward pass and YOLO11n architecture forward verified |
| ROS 2 | Ubuntu 24.04 VM, Jazzy | `rclpy`, `cv_bridge`, `ros_gz_bridge`, colcon and image viewer availability confirmed |
| Simulation | Gazebo Harmonic 8.15.0, ROS vendor packages | Iris flight, ROS camera stream and PNG/CSV recording verified with Ogre for GUI and sensors |
| Autopilot | ArduPilot SITL, ArduCopter 4.8.0-dev | Gazebo flight and takeoff/landing confirmed; full ArduPilot and plugin source revisions recorded |
| Ground station | Mission Planner 1.3.83 on Windows | UDP connection and takeoff/landing confirmed; normal arm verified directly after switching from LAND to GUIDED |

## Working environments

- Windows: training, Git operations, and Mission Planner.
- Ubuntu VM: Gazebo, ROS 2 nodes, and ArduPilot SITL.
- GitHub: source, configuration, documentation, and measured results.

Keep virtual environments, datasets, checkpoints, generated ROS build output, and private machine details out of Git.

## Documentation

- [15-day roadmap (Turkish)](docs/roadmap.md)
- [Day 1 setup and diagnostics (Turkish)](docs/day-01.md)
- [Day 2 setup, restart commands and troubleshooting (Turkish)](docs/day-02.md)
- [Day 4 platform scene and startup (Turkish)](docs/day-04-scene.md)
- [Day 4 image and CSV recorder (Turkish)](docs/day-04-recording.md)
- [Progress and decisions](docs/progress.md)
- [Environment observations](reports/environment.md)
- [Actual Windows GPU check](reports/windows_gpu_check.json)
- [Installed Windows package versions](reports/requirements_windows.txt)

The roadmap describes intended work. Checked items and evidence in the progress log describe work actually completed.
