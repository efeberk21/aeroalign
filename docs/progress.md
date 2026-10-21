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
- Developer supplied Gazebo 8.15.0, memory and renderer diagnostics. Jitter root cause is not yet proven.

### Next actions

- Compare paused/default-renderer and paused/Ogre Gazebo runs using developer-supplied observations.

Day 1 remains in progress: Windows setup and repository bootstrap are verified; Gazebo stability is pending the comparison. No permanent guest graphics change or new ROS/Gazebo installation has been applied.
