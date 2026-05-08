# VMAF Batch Report

A command-line tool that runs VMAF, PSNR, and SSIM quality measurements against a batch of encoded video files and generates CSV, Markdown, and HTML reports.

---

## Requirements

- Python 3.8+
- [FFmpeg](https://ffmpeg.org/) with `libvmaf` support (verify with `ffmpeg -filters | grep vmaf`)
- `ffprobe` (included with FFmpeg)

---

## What it does

For each `.mp4` file found in the encoded directory, the script:

1. Probes the source and encoded files with `ffprobe` to collect codec, resolution, frame rate, bitrate, and duration.
2. Runs a **pre-check** that flags duration or frame-rate mismatches before spending time on VMAF.
3. Runs **VMAF** (and optionally **PSNR** and **SSIM**) in two modes:
   - **Native** — scales the source *down* to match the encoded rendition's resolution.
   - **Upscaled** — scales both the encoded file and the source *up* to a target display resolution (e.g. 4K).
4. Generates per-file **VMAF-over-time SVG charts** and **worst-frame thumbnails**.
5. Writes three output files to the report directory:
   - `vmaf_summary.csv` — flat data suitable for spreadsheets or further processing.
   - `vmaf_report.md` — Markdown table with all metrics and chart links.
   - `vmaf_report.html` — self-contained HTML report with color-coded quality badges, charts, and thumbnails.

---

## Usage

### Basic — single encoded directory

```bash
./vmaf_batch_report.py \
  --source reference.mp4 \
  --encoded-dir ./encoded \
  --output ./reports \
  --target-display 1920x1080
```

By default, both **native** and **upscaled** tests are run. Use `--native` or `--upscaled` to run only one mode.

### Run only native tests

```bash
./vmaf_batch_report.py \
  --source reference.mp4 \
  --encoded-dir ./encoded \
  --output ./reports \
  --native
```

### Run only upscaled tests at 4K

```bash
./vmaf_batch_report.py \
  --source reference.mp4 \
  --encoded-dir ./encoded \
  --output ./reports \
  --upscaled \
  --target-display 3840x2160
```

### Multi-run comparison

Use `--runs-dir` to point to a folder of subdirectories, where each subdirectory is a separate encode run. Use `--baseline-run` to name which run to compare all others against.

```
test_runs/
  h264_medium/
    clip_720p.mp4
    clip_1080p.mp4
  hevc_medium/
    clip_720p.mp4
    clip_1080p.mp4
```

```bash
./vmaf_batch_report.py \
  --source reference.mp4 \
  --runs-dir test_runs \
  --baseline-run h264_medium \
  --output ./reports \
  --target-display 1920x1080
```

The report will include `bitrate_savings_percent`, `vmaf_delta`, `psnr_delta`, and `ssim_delta` columns showing how each run compares to the baseline.

---

## Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--source` | Yes | — | Path to the reference/source video file |
| `--encoded-dir` | No | `.` | Directory containing encoded `.mp4` files to test |
| `--runs-dir` | No | — | Parent directory of multiple encode-run subdirectories |
| `--baseline-run` | No | — | Run name (subdirectory name) to use as comparison baseline |
| `--output` | No | `reports` | Directory to write report files and artifacts into |
| `--target-display` | No | `1920x1080` | Target display resolution for upscaled tests (e.g. `3840x2160`) |
| `--native` | No | — | Run only native (source-downscale) tests |
| `--upscaled` | No | — | Run only upscaled (encode-upscale) tests |

If neither `--native` nor `--upscaled` is specified, both modes run.

---

## Output files

| File | Description |
|---|---|
| `vmaf_summary.csv` | All results in CSV format |
| `vmaf_report.md` | Markdown table with all metrics |
| `vmaf_report.html` | Full HTML report with badges, charts, thumbnails |
| `charts/*.svg` | Per-file VMAF score over time |
| `thumbnails/*.jpg` | Worst-frame thumbnails for each file and test type |
| `*_vmaf_native.json` | Raw VMAF JSON output (native tests) |
| `*_vmaf_upscaled_*.json` | Raw VMAF JSON output (upscaled tests) |
| `*_psnr_*.log` / `*_ssim_*.log` | Raw PSNR/SSIM stats files |

---

## Quality scoring

| Status | Criteria |
|---|---|
| **PASS** | Mean VMAF ≥ 90, Min VMAF ≥ 80, mean-to-min drop ≤ 15 |
| **WARN** | Mean VMAF ≥ 90 but Min VMAF between 70–80, or mean-to-min drop > 15 |
| **FAIL** | Min VMAF < 70, or no VMAF score |

Mean VMAF reflects overall quality across the clip. **Min VMAF is equally important** — a high mean can hide a severe quality drop on a single scene cut or motion burst. Always review worst-frame thumbnails for WARN results.

### PSNR and SSIM

PSNR and SSIM are included alongside VMAF as secondary metrics:

- **PSNR** — pixel-error metric in dB. Higher is better, but it is less correlated with perceived quality than VMAF.
- **SSIM** — structural similarity from 0 to 1. Higher is better.

These are useful for cross-validating VMAF results, but quality decisions should be based primarily on VMAF and visual inspection.

---

## Pre-check warnings

Before running VMAF, the script validates:

- **Duration mismatch** — if source and encoded durations differ by more than 0.25 seconds.
- **Frame-rate mismatch** — if source and encoded frame rates differ by more than 0.01 fps.
- **Invalid resolution** — if width or height is 0 or missing.

A `precheck_status` of `WARN` does not stop the run but means the VMAF result should be reviewed carefully, as a mismatch may indicate a bad encode or wrong source file.

---

## Notes

- Files with no video stream (e.g. audio-only `.mp4` files) are automatically detected and skipped.
- VMAF JSON, PSNR logs, and SSIM logs are kept in the output directory alongside the reports. Delete them manually if disk space is a concern.
- The `quality_per_mbps` metric (VMAF Mean ÷ bitrate in Mbps) is useful for comparing encoding efficiency across profiles but should not be used as a standalone quality gate.
- Reports are generated relative to the output directory, so charts and thumbnails will load correctly when opening `vmaf_report.html` from the same output folder.

# VMAF Batch Report

A Python command-line tool for running **VMAF**, **PSNR**, and **SSIM** quality measurements against encoded video files and generating CSV, Markdown, and HTML reports.

This project was built as a hands-on video quality testing workflow for evaluating encode quality, troubleshooting bad renditions, and comparing encoding ladders such as **H.264 vs HEVC**.

---

## What This Tool Does

For each encoded `.mp4` file, the script:

1. Uses `ffprobe` to collect codec, resolution, frame rate, bitrate, and duration.
2. Runs pre-checks for duration, frame-rate, and resolution issues.
3. Runs **VMAF** against a reference/source file.
4. Runs supporting **PSNR** and **SSIM** measurements.
5. Supports two comparison modes:
   - **Native**: compares each rendition at its own resolution.
   - **Upscaled**: scales renditions to a target display resolution before comparison.
6. Generates:
   - CSV summary report
   - Markdown report
   - HTML report with color-coded PASS/WARN/FAIL rows
   - VMAF-over-time SVG charts
   - Worst-frame thumbnails
7. Optionally compares multiple encode runs against a baseline to calculate bitrate savings and quality deltas.

---

## Why VMAF?

**VMAF** stands for **Video Multi-Method Assessment Fusion**.

It is a full-reference perceptual quality metric used to compare an encoded or distorted video against a source/reference video.

In simple terms:

```text
source/reference video  ↔  encoded/distorted video
```

VMAF produces per-frame scores and pooled metrics such as minimum, maximum, mean, and harmonic mean.

Typical interpretation:

| VMAF Score | Practical Meaning |
|---:|---|
| 95–100 | Excellent / very close to source |
| 90–95 | Very good |
| 80–90 | Good, but possible visible quality loss |
| 70–80 | Noticeable degradation |
| Below 70 | Poor or visibly degraded |

> VMAF should be used with visual inspection, playback testing, and operational context. It is a decision-support metric, not a replacement for human review.

---

## Requirements

- Python 3.8+
- FFmpeg with `libvmaf` support
- `ffprobe`, included with FFmpeg

Verify FFmpeg has VMAF support:

```bash
ffmpeg -filters | grep vmaf
```

Expected output should include:

```text
libvmaf           VV->V      Calculate the VMAF between two video streams.
vmafmotion        V->V       Calculate the VMAF Motion score.
```

---

## Quick Start: Single Encoded Ladder

Use this mode when testing one encoded ladder folder.

```bash
./vmaf_batch_report.py \
--source reference.mp4 \
--encoded-dir ./encoded_ladder \
--output ./reports_single_review \
--target-display 1920x1080
```

Open the HTML report:

```bash
open ./reports_single_review/vmaf_report.html
```

By default, the script runs both native and upscaled tests. To run only one mode:

```bash
./vmaf_batch_report.py \
--source reference.mp4 \
--encoded-dir ./encoded_ladder \
--output ./reports_native_only \
--native
```

```bash
./vmaf_batch_report.py \
--source reference.mp4 \
--encoded-dir ./encoded_ladder \
--output ./reports_upscaled_only \
--upscaled \
--target-display 3840x2160
```

---

## Quick Start: Multi-Run Comparison

Use this mode when comparing multiple encode runs, such as H.264 vs HEVC or different bitrate ladders.

Example folder layout:

```text
test_runs/
├── h264_baseline/
│   ├── encoded_2160p.mp4
│   ├── encoded_1080p.mp4
│   └── encoded_720p.mp4
├── hevc_medium/
│   ├── encoded_2160p.mp4
│   ├── encoded_1080p.mp4
│   └── encoded_720p.mp4
└── hevc_low/
    ├── encoded_2160p.mp4
    ├── encoded_1080p.mp4
    └── encoded_720p.mp4
```

Run comparison mode:

```bash
./vmaf_batch_report.py \
--source meridian_15s_cleanref.mp4 \
--runs-dir test_runs \
--baseline-run h264_baseline \
--output reports_meridian_compare \
--target-display 3840x2160
```

Open the HTML report:

```bash
open reports_meridian_compare/vmaf_report.html
```

Comparison mode adds fields such as:

| Field | Meaning |
|---|---|
| `quality_per_mbps` | VMAF Mean divided by bitrate Mbps |
| `bitrate_savings_percent` | Bitrate saved versus the baseline run |
| `vmaf_delta` | VMAF difference compared to baseline |
| `psnr_delta` | PSNR difference compared to baseline |
| `ssim_delta` | SSIM difference compared to baseline |

---

## Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--source` | Yes | — | Path to the reference/source video file |
| `--encoded-dir` | No | `.` | Directory containing encoded `.mp4` files to test |
| `--runs-dir` | No | — | Parent directory of multiple encode-run subdirectories |
| `--baseline-run` | No | — | Run name/subdirectory name to use as comparison baseline |
| `--output` | No | `reports` | Directory to write report files and artifacts into |
| `--target-display` | No | `1920x1080` | Target display resolution for upscaled tests, such as `3840x2160` |
| `--native` | No | — | Run only native/source-downscale tests |
| `--upscaled` | No | — | Run only upscaled/encode-upscale tests |

If neither `--native` nor `--upscaled` is specified, both modes run.

---

## Native vs Upscaled Testing

The tool supports two VMAF comparison methods.

| Method | What It Does | Best For |
|---|---|---|
| Native | Scales the source down to the encoded rendition resolution | Measuring encode quality at that rendition |
| Upscaled | Scales the encoded rendition to the target display resolution | Estimating viewer experience on a larger display |

Example:

```text
720p native test:
720p encode ↔ source scaled to 720p

720p upscaled-to-4K test:
720p encode scaled to 3840x2160 ↔ source at 3840x2160
```

A lower-resolution rendition may score well in native mode but much lower when upscaled to a larger display. That is expected.

---

## Output Files

The report output directory contains:

| File / Folder | Description |
|---|---|
| `vmaf_summary.csv` | Flat CSV data for spreadsheets or further processing |
| `vmaf_report.md` | Markdown report with metrics and artifact links |
| `vmaf_report.html` | HTML report with summary sections, charts, thumbnails, and badges |
| `charts/*.svg` | VMAF-over-time charts |
| `thumbnails/*.jpg` | Worst-frame thumbnails |
| `*_vmaf_native.json` | Raw VMAF JSON for native tests |
| `*_vmaf_upscaled_*.json` | Raw VMAF JSON for upscaled tests |
| `*_psnr_*.log` | Raw PSNR stats |
| `*_ssim_*.log` | Raw SSIM stats |

---

## Quality Scoring

The script assigns quality status using VMAF mean, VMAF minimum, and mean-to-min drop.

| Status | Criteria |
|---|---|
| PASS | Mean VMAF ≥ 90, Min VMAF ≥ 80, and no large mean-to-min drop |
| WARN | Mean VMAF is acceptable but Min VMAF is low, or quality swing is large |
| FAIL | Min VMAF < 70 or no valid score |

Mean VMAF is useful, but **minimum VMAF matters** because a high average can hide a severe quality drop around motion, scene cuts, or difficult frames.

Always review worst-frame thumbnails for WARN or FAIL results.

---

## Supporting Metrics: PSNR and SSIM

The tool also reports PSNR and SSIM alongside VMAF.

| Metric | Meaning |
|---|---|
| PSNR | Pixel-error metric in dB. Higher is better, but it is less perceptual. |
| SSIM | Structural similarity score from 0 to 1. Higher is better. |
| VMAF | Perceptual metric designed to better correlate with human visual quality. |

VMAF should usually be treated as the primary metric for streaming encode optimization. PSNR and SSIM are useful supporting signals.

---

## Pre-Check Warnings

Before running quality measurements, the script checks for common problems:

| Check | Why It Matters |
|---|---|
| Duration mismatch | Different durations can indicate bad source/encode alignment |
| Frame-rate mismatch | VMAF compares corresponding frames, so frame cadence matters |
| Invalid resolution | VMAF requires valid matching dimensions after scaling |
| Missing video stream | Audio-only files are skipped automatically |

A `precheck_status` of `WARN` does not stop the report, but it means the result should be reviewed carefully.

---

## Creating a Clean Reference Clip

For repeatable VMAF testing, it helps to create a short reference clip that starts on an I-frame and has a clean GOP structure.

Example using Netflix Meridian content:

```bash
ffmpeg -y -ss 00:02:00 -i Meridian_UHD4k5994_HDR_P3PQ.mp4 -t 15 \
-vf "fps=60000/1001,format=yuv420p" \
-c:v libx264 -crf 10 -preset slow \
-g 60 -keyint_min 60 -sc_threshold 0 \
-an meridian_15s_cleanref.mp4
```

Verify the first frame:

```bash
ffprobe -v error -select_streams v:0 \
-show_entries frame=best_effort_timestamp_time,pict_type \
-of csv=p=0 meridian_15s_cleanref.mp4 | head -20
```

Expected first frame:

```text
0.000000,I
```

> For production-quality testing, the best reference is usually a mezzanine source such as ProRes, DNxHR, JPEG 2000, or uncompressed/lossless video. Highly compressed delivery files can still be useful for tool testing, but they are less ideal as quality references.

---

## Example: Create H.264 and HEVC Test Ladders

Create test folders:

```bash
mkdir -p test_runs/h264_baseline test_runs/hevc_medium test_runs/hevc_low
```

### H.264 Baseline Ladder

```bash
ffmpeg -y -i meridian_15s_cleanref.mp4 \
-vf "fps=60000/1001,scale=3840:2160:flags=bicubic,format=yuv420p" \
-c:v libx264 -b:v 9000k -preset medium -an \
test_runs/h264_baseline/encoded_2160p.mp4

ffmpeg -y -i meridian_15s_cleanref.mp4 \
-vf "fps=60000/1001,scale=1920:1080:flags=bicubic,format=yuv420p" \
-c:v libx264 -b:v 5000k -preset medium -an \
test_runs/h264_baseline/encoded_1080p.mp4

ffmpeg -y -i meridian_15s_cleanref.mp4 \
-vf "fps=60000/1001,scale=1280:720:flags=bicubic,format=yuv420p" \
-c:v libx264 -b:v 2800k -preset medium -an \
test_runs/h264_baseline/encoded_720p.mp4
```

### HEVC Medium Ladder

```bash
ffmpeg -y -i meridian_15s_cleanref.mp4 \
-vf "fps=60000/1001,scale=3840:2160:flags=bicubic,format=yuv420p" \
-c:v libx265 -b:v 6000k -preset medium -an \
test_runs/hevc_medium/encoded_2160p.mp4

ffmpeg -y -i meridian_15s_cleanref.mp4 \
-vf "fps=60000/1001,scale=1920:1080:flags=bicubic,format=yuv420p" \
-c:v libx265 -b:v 3200k -preset medium -an \
test_runs/hevc_medium/encoded_1080p.mp4

ffmpeg -y -i meridian_15s_cleanref.mp4 \
-vf "fps=60000/1001,scale=1280:720:flags=bicubic,format=yuv420p" \
-c:v libx265 -b:v 1800k -preset medium -an \
test_runs/hevc_medium/encoded_720p.mp4
```

### HEVC Low-Bitrate Ladder

```bash
ffmpeg -y -i meridian_15s_cleanref.mp4 \
-vf "fps=60000/1001,scale=3840:2160:flags=bicubic,format=yuv420p" \
-c:v libx265 -b:v 3500k -preset medium -an \
test_runs/hevc_low/encoded_2160p.mp4

ffmpeg -y -i meridian_15s_cleanref.mp4 \
-vf "fps=60000/1001,scale=1920:1080:flags=bicubic,format=yuv420p" \
-c:v libx265 -b:v 2000k -preset medium -an \
test_runs/hevc_low/encoded_1080p.mp4

ffmpeg -y -i meridian_15s_cleanref.mp4 \
-vf "fps=60000/1001,scale=1280:720:flags=bicubic,format=yuv420p" \
-c:v libx265 -b:v 1000k -preset medium -an \
test_runs/hevc_low/encoded_720p.mp4
```

---

## Common VMAF Issues

### Width / Height Must Match

Error:

```text
input width must match
input height must match
```

Cause:

```text
encoded = 1280x720
source  = 1920x1080
```

Fix:

Scale one input so both streams match before passing them into `libvmaf`.

---

### Shell Line Continuation Issues

Incorrect:

```bash
ffmpeg -i encoded.mp4 -i source.mov\
-filter_complex ...
```

The shell may interpret this as:

```text
source.mov-filter_complex
```

Correct:

```bash
ffmpeg -i encoded.mp4 -i source.mov \
-filter_complex "..." \
-f null -
```

On macOS/zsh:

- Do not put blank lines between continued lines.
- The backslash `\` must be the final character on the line.

---

## How This Helps Encoding Decisions

The report can help answer:

```text
Is a profile over-encoded?
Is a profile under-encoded?
Are two ladder rungs too close in quality?
How much bitrate does HEVC save over H.264?
Which encode settings give the best quality-per-bit?
Where are the worst quality drops in the video?
Are quality drops isolated or spread across the whole clip?
```

Example interpretation:

> HEVC medium saved roughly 33–37% bitrate compared to the H.264 baseline while maintaining similar or better native VMAF across 2160p, 1080p, and 720p. HEVC low saved more bitrate but should be visually inspected more carefully.

---

