# Environment observations

Date: 2026-10-21. This report records observed setup facts, not a completed simulation validation.

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
| Guest OS / ROS | Ubuntu 24.04 / ROS 2 Jazzy, reported existing installation |
| Gazebo | 8.15.0, reported by the developer |
| Guest GL | SVGA3D, OpenGL 4.3, Mesa 25.2.8 |
| Guest acceleration report | `Accelerated: no`, `Video memory: 1MB`; under investigation |
| Host VMware renderer | DX12 renderer on RTX 4060, observed in renderer log |

Do not infer a literal 1 MB physical GPU from the guest diagnostic value. Simulation rendering and PyTorch CUDA access are different paths. Keep absolute machine paths and raw logs in ignored local files.
