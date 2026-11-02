# Delivery platform dataset

## Class and annotation boundary

- Class ID: `0`; class name: `delivery_platform`.
- Label the whole visible outer physical boundary of the platform, including its dark rim. Do not label only the white H or orange deck. Exclude the shadow.
- Use the tight axis-aligned image rectangle around the visible platform; keep coordinates inside the image. Record partial visibility when the platform crosses an image edge.
- Negative images contain no platform and have no positive box.

## First simulator variant

- Variant: `orange_h_v1`.
- Physical footprint: 2 x 2 m; body thickness: 0.12 m; decorative deck/marking top: 0.128 m.
- Dark outer rim, orange inset and centered white H; the mark is symmetric about the physical center.
- World: `iris_runway`, with a matte gray ground and an initial platform center at `(1, 0, 0)` m.
- Gazebo's editor grid and selection handles are UI overlays. Collect camera images from `/camera/image_raw`.
- A commanded flight height is nominal; it is not measured ground-truth height.

## Status

The Ubuntu pilot contains 141 images across nominal 5, 8 and 10 m sessions. PNG/CSV integrity was verified through SSH; appearance/ground/light variants, negative collection, scene-based splits, labeling and training remain pending.

The CSV recorder was validated on the Ubuntu pilot. Each session has its own `manifest.csv`. Image paths are relative to that manifest's directory. Nominal height is operator-supplied; an unknown value is stored as an empty field, not a measured altitude. See the [recorder guide](../docs/day-04-recording.md) and [audit](recording_audit_2026-10-25.md).

## Collection scope updated on 2026-10-25

- First-version detection/tracking target: approximately 5 to 10 m, sampled at 5, 8 and 10 m.
- Keep the wide horizontal FOV of 2.0 rad and zoom 1. Preserve the physical platform size across heights.
- Store original 640 x 480 PNGs; model input resizing is a separate step. The upper target is not yet validated with a trained detector.
- Assign all height sessions from the same scene to the same dataset split.
- Start with a small pilot, then approximately 540 varied images across 12 scene groups. Recorder checks captured on the ground are excluded from training.
- See the [collection plan](../docs/dataset-collection-plan.md) for assumptions, pixel-size estimates, metadata and evaluation.

## Scene variants added on 2026-11-02

- Second platform appearance `blue_ring_v1`: same 2 x 2 m dark-rim body, blue deck, white ring and center dot. Same class and same outer-boundary label rule as `orange_h_v1`.
- Ground variants: `matte_gray_v1`, `sand_v1`, `asphalt_dark_v1`, `grass_v1`. Light variants: `sun_default_v1`, `sun_low_v1`, `overcast_dim_v1`. Values are in `sim/worlds/scene_variants.json`.
- Non-platform distractors: crate, 2 x 2 m dark mat (hard negative with the platform footprint), hazard stripes and an orange barrel. They are never labeled.
- Negative images use `platform_variant=none`.
- Images from `scene_capture.py` use `camera_profile=rig_nadir_640x480_hfov2`: an ideal downward camera with the flight camera's resolution and FOV, at an exact height, without the drone. Their `capture_poses.csv` records camera, platform and distractor poses. Flight images keep `iris_wide_640x480_hfov2_zoom1`.
- The 60-image `pilot04_*` set is a scene/tooling check; see the [variant pilot report](variant_pilot_2026-11-02.md). Labels and splits are still pending.

## Version platform_v1 (2026-11-02)

- Definition: `configs/dataset_v1.json`. Twelve scripted-camera scene groups `sim01`-`sim12`, one per ground/light world, with alternating platform appearance. Scene-based split: 8 train, 2 val (`sim06`, `sim11`), 2 test (`sim03`, `sim08`).
- 533 simulation images after removing 7 exact duplicates: train 357 (288 positive / 69 negative), val 88 (72/16), test 88 (72/16). All three heights are present in every split.
- The 141 flight images (`scene01`) form a separate `flight_eval` set with the real gimbal camera; positives only; not used for training.
- Split file: `datasets/platform/platform_v1/split_manifest.csv`; the split is fixed before training. Raw backup: `datasets/backups/platform_v1_raw.tar.gz`. See [Day 5 dataset](../docs/day-05-dataset.md).
- Labels are still pending (Day 6).
