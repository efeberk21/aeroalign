# Scene-variant and negative pilot — 2 November 2026

Captured with `scene_capture.py` (scripted downward camera, no flight) to check every new world, both platform appearances, the distractors and the platform-absent negatives before Day 5 collection. See [Day 4 variants](../docs/day-04-variants.md) for the method.

## Sessions

One session per world, heights rotating 5/8/10 m, platform appearance alternating; 2 positives + 3 negatives each.

| Scene | World | Platform | Height |
|---|---|---|---:|
| `pilot04_01` | `platform_world` (gray, default) | orange | 5 m |
| `pilot04_02` | gray, low | blue | 8 m |
| `pilot04_03` | gray, dim | orange | 10 m |
| `pilot04_04` | sand, default | blue | 5 m |
| `pilot04_05` | sand, low | orange | 8 m |
| `pilot04_06` | sand, dim | blue | 10 m |
| `pilot04_07` | asphalt, default | orange | 5 m |
| `pilot04_08` | asphalt, low | blue | 8 m |
| `pilot04_09` | asphalt, dim | orange | 10 m |
| `pilot04_10` | grass, default | blue | 5 m |
| `pilot04_11` | grass, low | orange | 8 m |
| `pilot04_12` | grass, dim | blue | 10 m |

## Integrity

- 60 images: 24 positive (12 `orange_h_v1`, 12 `blue_ring_v1`) and 36 negative (`platform_variant=none`).
- 15 per ground variant, 20 per light variant, 20 per height.
- Every PNG decodes at 640 × 480; manifest rows, `capture_poses.csv` rows and PNG files match one-to-one in every session; source timestamps strictly increase.
- Manifest `platform_variant=none` matches the pose file's `neg` kind for every row.
- No exact duplicate PNGs. The first run produced two pixel-identical empty-ground negatives in `pilot04_04`; the tool now allows at most one empty negative per session and that scene was recaptured.

## Visual review

Contact sheets of all 60 frames were inspected:

- Both platform appearances, all four distractors, the four grounds and the low-sun shadows render as intended. Positives contain the platform; negatives contain no platform.
- Apparent platform size at 10 m is roughly 40 px, consistent with the planning estimate.
- `sun_default_v1` over-brightens light grounds: sand appears pale yellow. Kept as a bright condition.
- The dark mat is barely visible on dim asphalt, as expected for a hard negative.
- One 10 m partial positive (`pilot04_12`) shows only a corner of the platform at the image edge; partial positives are intended but must be reviewed during labeling.

## Limits

The camera is an ideal nadir camera with exact height, not the flying gimbal camera. Labels have not been produced. The pilot is a tooling/scene check and is not intended as the Day 5 training set.

Evidence (ignored by Git): `reports/raw/day04_variant_pilot/` (audit JSON and contact sheets) and `datasets/platform/pilot04_*`.
