# Environment observations

Date: 2026-10-21. Environment and basic simulated flight checks have passed. Flight observations are manual; camera and perception validation remains pending.

| Component | Observed value |
|---|---|
| Host | Windows 11, x64 |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB reported VRAM |
| NVIDIA driver | 617.42 |
| Host memory | Approximately 16 GiB |
| Git | 2.52.0.windows.1 |
| Environment tool | uv 0.11.1 |
| Project Python | 3.12.13, managed separately from system Python 3.14 |
| PyTorch / torchvision | 2.14.1+cu126 / 0.29.1+cu126 |
| Ultralytics / OpenCV | 8.4.183 / 5.0.0 |
| Actual CUDA check | CUDA 12.6, matmul/backward passed, YOLO11n architecture forward passed |
| VMware | Player 17.6.1, virtual hardware version 21 |
| Guest allocation | 4 vCPU, 4096 MiB RAM, NAT |
| Guest OS / ROS | Ubuntu 24.04 / ROS 2 Jazzy; bridge and Python imports confirmed by the developer |
| Gazebo | 8.15.0, reported by the developer |
| Gazebo packaging | ROS vendor; `ros-jazzy-gz-sim-vendor` `0.0.13-1noble.20260905.073557` |
| Gazebo executable | `/opt/ros/jazzy/opt/gz_tools_vendor/bin/gz` |
| Guest GL | SVGA3D, OpenGL 4.3, Mesa 25.2.8 |
| Guest acceleration report | `Accelerated: no`, `Video memory: 1MB`; exact driver limitation not established |
| Host VMware renderer | DX12 renderer on RTX 4060, observed in renderer log |
| Gazebo renderer comparison | Developer reports jitter with default renderer; no jitter with `--render-engine ogre` on the same shapes scene |
| Working launch choice | Ogre for GUI and Sensors in a local Iris world copy; simulated takeoff and landing confirmed |
| ArduPilot runtime | ArduCopter `V4.8.0-dev (5aa07216)` shown in Mission Planner |
| ArduPilot source commit | `5aa0721611bdd66ded2285873c091b5ef7ac69e7` |
| Gazebo integration | `ardupilot_gazebo`, all four plugin targets built |
| Gazebo plugin source commit | `082a0fe231f6e63bc8d1598f1cba461d9e2ea7f5` |
| Vehicle settings | `FRAME_CLASS=1`, `FRAME_TYPE=1`; restart required after changing class |
| Mission Planner | `1.3.83`, build `1.3.9384.38258`, UDP 14550 connection observed directly |
| Flight evidence | Developer confirmed MAVProxy and Mission Planner takeoff/landing; normal Mission Planner arm observed directly in Guided |
| ROS tooling | colcon and `rqt_image_view` availability confirmed by developer |
| Pending validation | Downward camera, ROS image stream, measured RTF/FPS, perception, alignment |

Do not infer a literal 1 MB physical GPU from the guest diagnostic value. Simulation rendering and PyTorch CUDA access are different paths. Keep absolute machine paths and raw logs in ignored local files.

## Restart and network

See [Day 2 commands](../docs/day-02.md). Windows UDP 14550 is the verified Mission Planner destination. The application flight node's Ubuntu UDP 14560 endpoint is planned and has not yet been configured or tested. Gazebo/SITL JSON transport is distinct from both GCS endpoints.

Store the current Windows VMnet8 IPv4 in ignored `reports/paths.local.md`; it is a machine-specific value. Both the network destination and the source revisions should be checked when moving this setup to another computer.

Both full source revisions were supplied by the developer using `git -C ... rev-parse HEAD` in Ubuntu after the successful Day 2 flight checks. These are source identities; no upstream branch or release was inferred from them.

## Day 3 - Ubuntu inference environment (2026-10-24)

- Project Python: 3.12.3, /home/efeberk/projects/aeroalign/.venv/bin/python.
- PyTorch 2.14.1+cpu; torchvision 0.29.1+cpu; CUDA unavailable as expected for this CPU build.
- OpenCV 4.11.0 (wheel 4.11.0.86), NumPy 1.26.4, Ultralytics 8.4.185.
- ROS Jazzy imports, both project messages, and CvBridge image conversion verified together.
- Use python /usr/bin/colcon from the activated project environment; .venv/bin/colcon was not created because system packages were reused.
- requirements_ubuntu.txt is a snapshot of locally installed venv packages; inherited ROS/system packages are documented separately. PyTorch CPU packages use https://download.pytorch.org/whl/cpu.
- One saved simulation frame completed YOLO11n inference in 46.4 ms. Sustained live performance and Gazebo GUI stutter remain unverified/deferred.
