# Recording audit — 25 October 2026

Connected to Ubuntu through the authorized `aeroalign-vm` SSH alias. Inspected existing recordings without changing application code, source images or manifests.

## Pilot recording integrity

| Nominal height | Session suffix | PNGs | CSV rows | Unique PNG hashes | Source interval range |
|---|---|---:|---:|---:|---|
| 5 m | `205005_310871` | 52 | 52 | 52 | 1.0–1.5 s |
| 8 m | `205218_882890` | 52 | 52 | 52 | 1.0–1.4 s |
| 10 m | `205343_541992` | 37 | 37 | 37 | 1.0–1.4 s |
| Total | | 141 | 141 | 141 | |

All images decoded at 640 × 480. Each CSV image reference resolves inside its session and matches the image ID/file stem. Image dimensions match the actual decoded PNG. Source timestamps strictly increase; no sampling gap is below the configured one-second interval. Scene/session IDs, camera profile and nominal-height values are consistent within each session. No missing images, unlisted PNGs inside these sessions, duplicate IDs or malformed rows were found.

Nominal heights are the operator-supplied CSV values. This audit does not verify actual flight height against telemetry.

## Visual review and curation

First/middle/last images from all three sessions were inspected in a contact sheet. The platform changes image position and orientation; the sessions are not simply pixel-identical copies.

A color-based review proxy found the orange deck touching the image boundary in 14 frames at 5 m and 6 frames at 8 m; none at 10 m. These 20 frames are candidates for partial-visibility curation, not automatic negative labels. A 5 m example was also inspected at original size and confirms that the platform crosses the bottom image boundary. Some 8 m samples include drone hardware at the edge. Keep mostly fully visible targets in the first training selection and review the more severely clipped examples separately.

The color proxy found orange platform content in all 141 pilot frames. Platform-absent negatives still need deliberate collection and human confirmation. All three sessions share `scene01`, the same platform variant, gray ground and sun profile; they do not yet provide independent validation/test scenes or background diversity.

## Recorder tests excluded from training

- `recorder_csv_check`: four PNGs, four matching rows, blank nominal height. All four PNGs are pixel-identical. This is a recorder test, not a training session.
- Legacy `recorder_check`: two PNGs without a manifest, from the earlier PNG-only recorder. These are separate from the three pilot sessions and should remain excluded from training.

## Evidence and method

- Parsed all four manifests with `csv.DictReader`; checked names, paths, required columns, dimensions, timestamps and metadata.
- Decoded all manifest-referenced PNGs using OpenCV; computed SHA-256 hashes for exact duplicates.
- Used HSV connected components only to select visual-review candidates, not to create ground-truth labels or claim learned detection accuracy.
- Detailed JSON and the visual contact sheet are in ignored `reports/raw/recording_audit_20261025/` in both the Windows workspace and Ubuntu checkout.

Result: live PNG+CSV recording passes the pilot file-integrity check. Labeling, partial-frame curation, negative collection, additional scenes and model training/evaluation remain pending.
