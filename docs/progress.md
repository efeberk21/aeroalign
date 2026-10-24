# AeroAlign progress

Plan: [15-day roadmap](roadmap.md)

## 2026-10-21 — Day 1

### Scope

Initialize the repository, verify the Windows GPU training environment, and investigate the existing Gazebo jitter. Application development is not part of this setup checkpoint.

### Decisions

- Ruling: use a new, separate repository; there is no existing checkout or user work requiring a worktree. Bootstrap documentation is created on `main`.
- Ruling: use a project-specific Python 3.12 runtime and virtual environment; preserve the existing Windows Python 3.14 installation.
- Ruling: ROS 2 Jazzy and Gazebo already exist in Ubuntu; do not reinstall them.
- Ruling: the developer runs Ubuntu terminal commands; no SSH server or remote access is added.
- Ruling: repository starts private; visibility can be changed deliberately later.
- Ruling: the daily roadmap is a human learning plan, not a machine-parsed task template; record setup evidence here directly.

### Evidence so far

- NVIDIA RTX 4060 Laptop GPU detected on Windows, 8188 MiB reported VRAM.
- Git and an existing GitHub account credential are available; account authentication verified without displaying credential values.
- Python 3.12.13 installed into the task's runtime directory using existing `uv`.
- Separate training virtual environment created; CUDA PyTorch and Ultralytics packages installed.
- Actual GPU matmul/backward check passed; YOLO11n architecture forward on a 416 x 416 CUDA tensor passed. No platform model was trained.
- Exact package versions captured in `reports/requirements_windows.txt`; actual check output saved in `reports/windows_gpu_check.json`.
- Private GitHub repository created at `https://github.com/efeberk21/aeroalign` using the existing authenticated account. Credentials were not displayed or saved in the repository.
- Bootstrap commit `cf9ac83` pushed to `origin/main`; local and remote commit IDs verified equal.
- Markdown links and fenced blocks checked; saved CUDA evidence validated. No application unit tests exist at this environment-only checkpoint.
- Existing Ubuntu VM started; 3B acceleration is enabled in configuration.
- Developer supplied Gazebo 8.15.0, memory and renderer diagnostics.
- Developer performed the same-scene renderer comparison: default renderer jitters; `gz sim -v 4 shapes.sdf --render-engine ogre` does not jitter. This narrows the issue to the rendering path; the exact underlying driver/renderer defect has not been proven.
- Ruling: use explicit Ogre for the next simulation setup tests. Do not change VM resources, drivers or global shell settings without a new reason. Camera rendering must be checked separately.

### Additional Day 1 evidence

- Developer confirmed `ros_gz_bridge` resolves to `/opt/ros/jazzy` and the `rclpy` / `cv_bridge` import succeeds.
- Developer reported `/usr/bin/colcon` and `/opt/ros/jazzy` for `rqt_image_view` after installing the Ubuntu tooling.
- Developer repeated the Windows CUDA check: `cuda:0`, loss `13.0`, gradient `[4.0, 6.0]`.
- Developer confirmed the running Ogre shapes scene works and the repository was cloned into `~/projects/aeroalign`.
- Existing VS Code is sufficient; further editor setup was explicitly skipped at the developer's request.

Day 1 basic environment gate passed. Camera output and ROS camera bridging remain separate Day 3 checks.

## 2026-10-21 — Day 2

### Scope and evidence

- Developer cloned ArduPilot and its submodules outside the application repo, into `~/projects/drone_alignment_vendor/ardupilot`.
- Official prerequisite script completed; `sim_vehicle.py` and `~/venv-ardupilot/bin/mavproxy.py` became available in the setup terminal.
- Initial standalone quad SITL built and supplied heartbeat, IMU and simulation telemetry.
- Gazebo was identified as the ROS Jazzy vendor installation: `gz` comes from `/opt/ros/jazzy/opt/gz_tools_vendor/bin/gz`; `ros-jazzy-gz-sim-vendor` version `0.0.13-1noble.20260905.073557` is installed.
- The initial standalone-package instruction failed with `Unable to locate package libgz-sim8-dev`. Corrected the dependency list for the existing vendor installation; no OSRF package repository or second Gazebo installation was added.
- Developer built `ArduPilotPlugin`, `ParachutePlugin`, `CameraZoomPlugin` and `GstCameraPlugin` successfully against the sourced ROS environment.
- Prepared a local Ogre copy of the Iris world, changing its sensor render engine as well as selecting the GUI engine. Developer confirmed the drone appears and the scene works.
- SITL ran with `-f gazebo-iris --model JSON`; developer supplied local position, simulation state and `EKF3 IMU1 is using GPS` telemetry.
- `sim_vehicle.py: command not found` in a new terminal was avoided by invoking the file through `python3 ../Tools/autotest/sim_vehicle.py`.
- Arming initially failed with `PreArm: Motors: Check frame class and type`. Developer reported `FRAME_CLASS=0`, `FRAME_TYPE=1`; class was set to `1`, SITL restarted without `-w`, and developer confirmed class remained `1`.
- Developer confirmed takeoff and landing in Gazebo through MAVProxy.
- Windows VMnet8 address was read locally and added as a MAVProxy output on UDP 14550. Developer supplied the resulting output list.
- Mission Planner was inspected directly: connected to `UDP14550-1-QUADROTOR`, version `1.3.83`, running ArduCopter `V4.8.0-dev (5aa07216)`.
- Messages showed `Arm: Land mode not armable`. Guided was selected in the dropdown but had not been applied. Clicking Set Mode changed the actual mode to Guided; normal Arm succeeded and displayed ARMED. No Force Arm was used in this verification.
- The stationary arm test later automatically disarmed; the final directly observed state was Guided and DISARMED.
- Developer then confirmed takeoff and landing from Mission Planner, including completion of the requested landing/disarm step.

### Acceptance and limits

- [x] Gazebo and Mission Planner use the same SITL vehicle.
- [x] Takeoff, hover observation and landing sequence completed by the developer.
- [x] Mission Planner commands and normal arming verified.
- [x] Restart commands and corrections recorded in [Day 2](day-02.md).
- [x] Full source IDs supplied by the developer from Ubuntu: ArduPilot `5aa0721611bdd66ded2285873c091b5ef7ac69e7`, `ardupilot_gazebo` `082a0fe231f6e63bc8d1598f1cba461d9e2ea7f5`. The ArduPilot ID matches the runtime short SHA observed in Mission Planner.

Flight results are manual observations, not recorded accuracy, timing or stability measurements. No camera-to-ROS stream, trained detector, alignment controller or application node has been validated. Application code remains for the developer and assistant to write together.

### Next

Day 2 is complete. Start Day 3 with the downward-facing camera and ROS image bridge when the developer is ready. Keep the ArduPilot Python environment separate from the future ROS/perception environment.

## 2026-10-22 to 2026-10-24 - Day 3 functional checkpoint

### Implemented and verified

- Reused Iris with Gimbal by the developer's choice; camera metadata is 640 x 480, rgb8, with a nominal 10 Hz simulation rate.
- Added the developer-written camera_viewer node: subscribes to /camera/image_raw, converts with CvBridge, displays with OpenCV, and saves a frame when s is pressed.
- Added PlatformObservation and BodyVelocity in the separate drone_alignment_interfaces package; generated definitions and Python message construction were verified.
- Configured one-way Gazebo-to-ROS bridges for image, CameraInfo and Clock. A bounded integration check received matching image/CameraInfo dimensions, an advancing clock, and exactly one publisher per topic.
- Verified camera_viewer can run with use_sim_time=true. This remains a launch-time argument.
- Created the project .venv with system-site-packages. Verified ROS imports and a real CvBridge image round trip alongside PyTorch CPU and Ultralytics.
- Rebuilt through python /usr/bin/colcon build --symlink-install; the camera_viewer entry-point shebang points to /home/efeberk/projects/aeroalign/.venv/bin/python.
- Saved an actual simulation camera frame to reports/raw/camera_check.png.
- Developer ran pretrained YOLO11n on that frame at imgsz=416, device=cpu: 1.1 ms preprocessing, 46.4 ms inference, 0.4 ms postprocessing, and no detections. This is one-image smoke-test evidence, not a live FPS benchmark.
- Actual annotated output directory: runs/detect/reports/raw/day03_inference.
- Captured project-installed Python packages in reports/requirements_ubuntu.txt. Windows GPU remains the planned training environment.

### Acceptance and limits

- Day 3's revised functional scope is complete. Detailed FPS, latency, RTF and jitter analysis were explicitly deferred by the developer; the original sustained-performance gate has not been passed.
- The ready-made model was tested on a saved frame. Platform training, live model integration and visual alignment control remain future work.
- The developer writes application code and runs experiments. SSH access is used only when explicitly requested.
- Python syntax, generated-message imports and the CvBridge round trip pass. The existing package pytest run reports one flake8 failure, one pass and one skipped test; the flake8 failure concerns formatting/import order in the learning code. Application behavior was preserved during this Git checkpoint.

### Next

Day 4: add the target platform scene and begin collecting the project's own training data.
