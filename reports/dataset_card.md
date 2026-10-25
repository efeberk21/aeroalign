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
