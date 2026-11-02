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

## 2026-10-24 - Day 4 platform model checkpoint

### Scope and changes

- The developer explicitly authorized direct SSH work to finish the simulator model and scene, then hand back a ready startup command. This checkpoint does not implement the remaining application nodes.
- Backed up the developer's initial `sim/` files under `reports/raw/day04-original/` before editing. Copies exist in Ubuntu and the Windows workspace.
- Prepared `delivery_platform`: 2 x 2 m dark body, orange inset and centered white H; body height is 0.12 m and decorative top is 0.128 m. The physical boundary includes the dark rim.
- Kept all model includes inside `world`, preserved the world/drone names used by the ROS bridge, retained the existing NavSat sensor and removed visible world-axis geometry.
- Replaced the runway include with a local matte gray ground plane. Placed the platform center at `(1, 0, 0)` m, clear of the drone's initial position.
- Added `scripts/start_sim.sh` so each invocation sources ROS and sets project/vendor resource and plugin paths. The command works from a fresh terminal without copying exports manually.
- Removed the unsupported Ogre sky element. ArduPilot/vendor source files and flight parameters were not changed by this model preparation.
- Recorded the annotation boundary and first variant in `reports/dataset_card.md`; startup instructions are in [Day 4 scene](day-04-scene.md).

### Verification and limits

- `gz sdf -k` accepted the platform model and world. World validation used `SDF_PATH` for include resolution; the Gazebo launcher uses `GZ_SIM_RESOURCE_PATH`.
- An isolated Gazebo server rendered the model through a fixed downward camera at 5 m. The 640 x 480 image contained the complete platform and 592 white marker pixels inside the orange-deck bounding rectangle. A separate 2 m detail view was also inspected.
- Ran the actual drone world with `bash scripts/start_sim.sh -s`. Scene pose messages contained both `delivery_platform` and `iris_with_gimbal`; the existing bridge delivered three actual Iris camera frames at 640 x 480 with advancing source timestamps.
- Evidence is saved in ignored `reports/raw/platform_preview_check.json`, `platform_detail_check.json`, `platform_world_smoke.json` and the corresponding images/logs. Test processes were stopped after checking.
- A disarmed heartbeat and zero relative altitude were observed before stopping the original session. No arm or takeoff commands were sent during preparation. The fixed-camera views are rendering checks, not flight trials or measured live performance.
- Additional platform/ground/light variants, distractors, the dataset recorder and the pilot dataset remain pending; Day 4 as a whole is not complete.

## 2026-10-25 - Recorder check and collection range decision

- The developer reports that the PNG recorder produced images. CSV/manifest recording has not yet been added or verified in this checkpoint.
- The developer requested multi-height detection/tracking and explicitly chose to keep the wide field of view fixed. They then delegated the first-version maximum-height recommendation to the assistant.
- Recommendation selected: a 5–10 m target range, with data at 5, 7.5 and 10 m, preserving the current camera and physical platform size. This is a validation target, not a measured detection range.
- Updated the roadmap and dataset card; saved a staged pilot/collection/split/evaluation plan in [dataset collection plan](dataset-collection-plan.md).
- Geometric estimates use 640-pixel image width, 2.0 rad horizontal FOV and a 2 m platform: approximately 82.2/54.8/41.1 pixels at 5/7.5/10 m. They assume an ideal downward, axis-aligned camera and are not detector results.
- No camera, flight or recorder application code was changed for this planning decision.

### CSV recorder implementation prepared for the next joint step

- Prepared the complete `dataset_recorder.py` in the Windows workspace for the developer to copy into Ubuntu. No SSH edits or live flights were performed for this step.
- Added per-session CSV records with source stamps, image dimensions, scene/session IDs, variants, camera profile, notes and nominal height. Image paths are relative to each manifest's directory.
- Unknown nominal height is blank in CSV. Parameters are read at startup; a new height requires a new recording session.
- New PNG files use exclusive creation. Failed CSV appends restore the original CSV length and remove the newly created PNG on handled errors. Existing images are preserved.
- Five file-I/O tests were observed failing before implementation and passing afterward; Python syntax and whitespace checks passed. These tests isolate the unchanged production I/O helper without loading ROS on Windows.
- The developer's live Ubuntu PNG+CSV check and the organized multi-height pilot remain pending.

### Intermediate collection height adjusted

- The developer reported `Bad alt` for 7.5 in the flight workflow and requested a different intermediate height. Updated the active collection plan to 5, 8 and 10 m; the exact command/parser cause has not been investigated.
- Use 8 for the intermediate flight target and `nominal_height_m:=8.0` for the recorder's floating-point parameter. Stop recording during height changes and start a new session after settling.
- Updated the geometric estimate at 8 m to approximately 51.4 raw pixels, or 33.4 pixels after scaling to 416 input width. Existing captured data and recorder code were not modified.

### Live Ubuntu recording audit

- At the developer's explicit request, connected through SSH and inspected the existing 5/8/10 m pilot sessions: 52, 52 and 37 images respectively, with exactly matching CSV row counts (141 total).
- All referenced PNGs decode at 640 x 480; IDs, paths, dimensions, headers and metadata are consistent. Source timestamps advance with gaps of at least one simulation second. No exact duplicate PNGs were found within the pilot data.
- Visual review confirms position/orientation variety. A color proxy flagged 20 edge-clipped candidates (14 at nominal 5 m, 6 at nominal 8 m); one original-size 5 m example confirms clipping. Review partial targets during curation. Negative/background/scene diversity and labels remain pending.
- Four identical CSV-recorder test images and two earlier PNG-only test images are separate from the pilot and excluded from training. Height values are nominal operator entries, not audited telemetry.
- Evidence and limitations are recorded in [recording audit](../reports/recording_audit_2026-10-25.md). No application code, images or manifests were changed by this audit.

### Session checkpoint at the developer's request

- The developer requested stopping here and pushing the current work to Git. Day 4 remains incomplete.
- Remaining: 2–3 platform appearances in total, 3–4 ground materials, several lighting options, non-platform distractors and real simulation negatives.
- The next scene-variation step was discussed and the existing setup was inspected, but no additional scene assets or negative recordings were created before stopping.
- Resume with the remaining scene variants and negative pilot, then close Day 4. Do not repeat the existing positive pilot simply to increase the image count.
- Raw datasets, images and machine-specific diagnostics remain ignored by Git and stored in Ubuntu/local `reports/raw`; Git checkpoint contains source, tests and documentation only.

## 2026-11-02 - Day 4 completed: scene variants and negatives

### Scope and decisions

- The developer asked the assistant to do the remaining Day 4 data work directly and to move on to Day 5. The work was done in the Ubuntu checkout with Claude Code.
- `scripts/start_sim.sh` selects a world with `ALIGN_WORLD` (commit `aaaf148`).
- Ruling: collect simulation data with a scripted downward camera instead of manual flights. It replicates the gimbal camera's 640 x 480 image and 2.0 rad FOV, places the camera and objects with `set_pose_vector`, and runs in a separate Gazebo partition. Flight images remain the reference for the real gimbal view.
- Ruling: a second platform appearance (`blue_ring_v1`) with the same 2 x 2 m size; no size variation.
- Ruling: ground/light combinations are generated from `scene_variants.json` (4 x 3 = 12 worlds) instead of hand-copied world files. The untracked `platform_world_ground2.sdf`, still identical to the base world, was removed and replaced by `platform_world_sand_*`.

### Implemented and verified

- Models: `delivery_platform_blue`, `distractor_crate`, `distractor_dark_mat`, `distractor_hazard_stripes`, `distractor_orange_barrel`. All are included in every world at parking positions 40 m away from the origin, so the flight view of the base world is unchanged.
- `scripts/make_scene_worlds.py` generated 11 worlds; all 12 worlds and 6 models pass `gz sdf -k`.
- `scene_capture.py` writes the existing manifest columns through `write_record` and a per-session `capture_poses.csv`. It passes `ament_flake8` and `ament_pep257`. Package tests: 6 passed, 1 skipped; the only failure is the earlier `camera_viewer.py` flake8 failure.
- Pilot: 12 sessions, one per world, 60 images (24 positive, 36 negative), audited for file/manifest/pose consistency and visually reviewed. See [variant pilot report](../reports/variant_pilot_2026-11-02.md).
- Fixed during the pilot: an over-strict uniform-image guard rejected a valid empty-ground negative; empty negatives were capped at one per session after a pixel-identical pair appeared.

### Limits

- Scripted images are ideal nadir views without gimbal tilt, drone parts or motion blur. Grounds are flat colors without textures.
- `sun_default_v1` over-brightens light grounds.
- No labels, splits or trained model yet.

### Next

Day 5: define 12 scene groups (world + platform appearance + seed), capture 5/8/10 m sessions with `scene_capture.py`, then fix the scene-based train/val/test split.

## 2026-11-02 - Day 5 completed: platform_v1 dataset

### Scope and decisions

- The developer asked the assistant to complete Day 5 data collection as well; Day 6 labeling will be done together.
- Ruling: twelve scene groups `sim01`-`sim12`, one per ground/light world, platform appearance alternating, fixed seeds 501-512. New IDs avoid the flight pilot's `scene01`.
- Ruling: split by scene: val `sim06` (sand/dim/blue) and `sim11` (grass/low/orange), test `sim03` (gray/dim/orange) and `sim08` (asphalt/low/blue). Each val/test scene's ground+light pair never appears in train; both platform appearances are in every split.
- Ruling: the 141 flight images are a separate `flight_eval` set for the real gimbal view, not training data.
- The definition is versioned as `platform_v1` in `configs/dataset_v1.json`.

### Implemented and verified

- Captured 36 sessions (12 scenes x 5/8/10 m, 12 positive + 3 negative each) with `scene_capture.py`.
- `scripts/build_split.py` checks every session (manifest/PNG match, decode, size, timestamps, required fields, one session per height). It drops exact duplicate PNGs, writes `split_manifest.csv` and `summary.json`, refuses to overwrite an existing split, and optionally writes a raw backup.
- Result: 533 simulation images (train 357, val 88, test 88; 101 negatives, 19%) plus 141 `flight_eval`. Seven dropped duplicates were empty-ground negatives repeated across heights. No scene appears in more than one split. The backup contains all 681 PNGs.
- Contact sheets of train, val and test sessions were reviewed; evidence is in ignored `reports/raw/day05_platform_v1/`.

### Limits

- Simulation images use the ideal nadir camera; the domain gap to flight images is measured only through `flight_eval`.
- On dark asphalt the platform's dark rim is low-contrast. Partial edge positives exist and need clipped labels.
- No labels or trained model yet.

### Next

Day 6, together with the developer: produce YOLO labels (possibly computed from `capture_poses.csv` and then checked visually), label the flight images, and validate the labels.
