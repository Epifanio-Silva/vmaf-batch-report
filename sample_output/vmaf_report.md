# VMAF Batch Report

| Run | Profile | File | Codec | Resolution | Bitrate Mbps | Test | Precheck | Quality | Mean VMAF | Min VMAF | PSNR Avg | SSIM All | Quality/Mbps | Savings | VMAF Δ | Worst Timestamp | Chart | Notes |
|---|---|---|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| h264_baseline | 1080p | encoded_1080p.mp4 | h264 | 1920x1080 | 4.791 | native | PASS | PASS | 93.564 | 87.605 | 49.418 | 0.991431 | 19.529 | 0.0% | 0.000 | 00:00.250 | [chart](charts/h264_baseline_encoded_1080p_native_vmaf.svg) | Very good |
| h264_baseline | 1080p | encoded_1080p.mp4 | h264 | 1920x1080 | 4.791 | upscaled_3840x2160 | PASS | WARN | 86.139 | 76.870 | 48.449 | 0.990091 | 17.979 | 0.0% | 0.000 | 00:00.217 | [chart](charts/h264_baseline_encoded_1080p_upscaled_3840x2160_vmaf.svg) | Good; inspect visually; Low frame warning: min VMAF=76.870 |
| h264_baseline | 2160p | encoded_2160p.mp4 | h264 | 3840x2160 | 8.57 | native | PASS | WARN | 89.429 | 85.036 | 49.299 | 0.991281 | 10.435 | 0.0% | 0.000 | 00:00.384 | [chart](charts/h264_baseline_encoded_2160p_native_vmaf.svg) | Good; inspect visually |
| h264_baseline | 2160p | encoded_2160p.mp4 | h264 | 3840x2160 | 8.57 | upscaled_3840x2160 | PASS | WARN | 89.429 | 85.036 | 49.299 | 0.991281 | 10.435 | 0.0% | 0.000 | 00:00.384 | [chart](charts/h264_baseline_encoded_2160p_upscaled_3840x2160_vmaf.svg) | Good; inspect visually |
| h264_baseline | 720p | encoded_720p.mp4 | h264 | 1280x720 | 2.674 | native | PASS | PASS | 94.600 | 86.809 | 49.389 | 0.991719 | 35.378 | 0.0% | 0.000 | 00:00.150 | [chart](charts/h264_baseline_encoded_720p_native_vmaf.svg) | Very good |
| h264_baseline | 720p | encoded_720p.mp4 | h264 | 1280x720 | 2.674 | upscaled_3840x2160 | PASS | FAIL | 80.368 | 65.168 | 47.523 | 0.988866 | 30.056 | 0.0% | 0.000 | 00:00.284 | [chart](charts/h264_baseline_encoded_720p_upscaled_3840x2160_vmaf.svg) | Good; inspect visually; CRITICAL low frame detected: min VMAF=65.168; Large quality swing: mean-min delta=15.200 |
| hevc_low | 1080p | encoded_1080p.mp4 | hevc | 1920x1080 | 1.874 | native | PASS | PASS | 93.162 | 83.348 | 49.477 | 0.991689 | 49.713 | 60.9% | -0.402 | 00:00.150 | [chart](charts/hevc_low_encoded_1080p_native_vmaf.svg) | Very good |
| hevc_low | 1080p | encoded_1080p.mp4 | hevc | 1920x1080 | 1.874 | upscaled_3840x2160 | PASS | WARN | 85.798 | 71.397 | 48.476 | 0.990612 | 45.783 | 60.9% | -0.341 | 00:00.150 | [chart](charts/hevc_low_encoded_1080p_upscaled_3840x2160_vmaf.svg) | Good; inspect visually; Low frame warning: min VMAF=71.397 |
| hevc_low | 2160p | encoded_2160p.mp4 | hevc | 3840x2160 | 3.308 | native | PASS | PASS | 90.160 | 80.694 | 49.212 | 0.991389 | 27.255 | 61.4% | 0.731 | 00:00.100 | [chart](charts/hevc_low_encoded_2160p_native_vmaf.svg) | Very good |
| hevc_low | 2160p | encoded_2160p.mp4 | hevc | 3840x2160 | 3.308 | upscaled_3840x2160 | PASS | PASS | 90.160 | 80.694 | 49.212 | 0.991389 | 27.255 | 61.4% | 0.731 | 00:00.100 | [chart](charts/hevc_low_encoded_2160p_upscaled_3840x2160_vmaf.svg) | Very good |
| hevc_low | 720p | encoded_720p.mp4 | hevc | 1280x720 | 0.935 | native | PASS | PASS | 93.493 | 84.450 | 49.105 | 0.991449 | 99.993 | 65.0% | -1.106 | 00:00.067 | [chart](charts/hevc_low_encoded_720p_native_vmaf.svg) | Very good |
| hevc_low | 720p | encoded_720p.mp4 | hevc | 1280x720 | 0.935 | upscaled_3840x2160 | PASS | FAIL | 78.329 | 61.785 | 47.294 | 0.988987 | 83.774 | 65.0% | -2.039 | 00:00.067 | [chart](charts/hevc_low_encoded_720p_upscaled_3840x2160_vmaf.svg) | Noticeable degradation; CRITICAL low frame detected: min VMAF=61.785; Large quality swing: mean-min delta=16.544 |
| hevc_medium | 1080p | encoded_1080p.mp4 | hevc | 1920x1080 | 3.016 | native | PASS | PASS | 94.116 | 83.346 | 50.151 | 0.992561 | 31.206 | 37.0% | 0.552 | 00:00.150 | [chart](charts/hevc_medium_encoded_1080p_native_vmaf.svg) | Very good |
| hevc_medium | 1080p | encoded_1080p.mp4 | hevc | 1920x1080 | 3.016 | upscaled_3840x2160 | PASS | WARN | 87.502 | 71.396 | 49.019 | 0.991301 | 29.012 | 37.0% | 1.363 | 00:00.150 | [chart](charts/hevc_medium_encoded_1080p_upscaled_3840x2160_vmaf.svg) | Good; inspect visually; Low frame warning: min VMAF=71.396; Large quality swing: mean-min delta=16.106 |
| hevc_medium | 2160p | encoded_2160p.mp4 | hevc | 3840x2160 | 5.689 | native | PASS | PASS | 91.986 | 81.396 | 49.948 | 0.992241 | 16.169 | 33.6% | 2.557 | 00:00.083 | [chart](charts/hevc_medium_encoded_2160p_native_vmaf.svg) | Very good |
| hevc_medium | 2160p | encoded_2160p.mp4 | hevc | 3840x2160 | 5.689 | upscaled_3840x2160 | PASS | PASS | 91.986 | 81.396 | 49.948 | 0.992241 | 16.169 | 33.6% | 2.557 | 00:00.083 | [chart](charts/hevc_medium_encoded_2160p_upscaled_3840x2160_vmaf.svg) | Very good |
| hevc_medium | 720p | encoded_720p.mp4 | hevc | 1280x720 | 1.697 | native | PASS | PASS | 94.618 | 85.588 | 50.061 | 0.992708 | 55.756 | 36.5% | 0.019 | 00:00.100 | [chart](charts/hevc_medium_encoded_720p_native_vmaf.svg) | Very good |
| hevc_medium | 720p | encoded_720p.mp4 | hevc | 1280x720 | 1.697 | upscaled_3840x2160 | PASS | FAIL | 81.026 | 64.478 | 47.933 | 0.989939 | 47.746 | 36.5% | 0.657 | 00:00.100 | [chart](charts/hevc_medium_encoded_720p_upscaled_3840x2160_vmaf.svg) | Good; inspect visually; CRITICAL low frame detected: min VMAF=64.478; Large quality swing: mean-min delta=16.548 |

## Notes

- Native tests scale the source down to the encoded rendition resolution.
- Upscaled tests scale the encoded rendition up to the target display resolution.
- Mean VMAF is useful, but minimum VMAF helps identify worst-frame quality drops.
- PSNR Avg is a pixel-error metric reported in dB; higher is better, but it is less perceptual than VMAF.
- SSIM All is a structural similarity metric from 0 to 1; higher is better.
- Quality/Mbps is VMAF Mean divided by bitrate Mbps; it is useful for efficiency comparisons but should not be used alone.
- Savings and delta columns are populated when `--runs-dir` and `--baseline-run` are used.
- Precheck PASS means duration/frame-rate checks did not detect obvious mismatches.
- Precheck WARN means the VMAF result may still be useful, but the file should be reviewed carefully.
- Quality WARN/FAIL is based on mean VMAF, minimum VMAF, and large mean-to-min drops.
- Use VMAF with visual inspection and playback testing.


## Worst Frame Details

### h264_baseline / encoded_1080p.mp4 — native

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 15 | 00:00.250 | 87.605 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_native_frame_15_vmaf_87.605.jpg) |
| 9 | 00:00.150 | 87.610 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_native_frame_9_vmaf_87.610.jpg) |
| 13 | 00:00.217 | 87.651 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_native_frame_13_vmaf_87.651.jpg) |
| 14 | 00:00.234 | 87.865 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_native_frame_14_vmaf_87.865.jpg) |
| 10 | 00:00.167 | 87.873 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_native_frame_10_vmaf_87.873.jpg) |

### h264_baseline / encoded_1080p.mp4 — upscaled_3840x2160

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 13 | 00:00.217 | 76.870 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_upscaled_3840x2160_frame_13_vmaf_76.870.jpg) |
| 9 | 00:00.150 | 76.942 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_upscaled_3840x2160_frame_9_vmaf_76.942.jpg) |
| 17 | 00:00.284 | 77.014 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_upscaled_3840x2160_frame_17_vmaf_77.014.jpg) |
| 15 | 00:00.250 | 77.046 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_upscaled_3840x2160_frame_15_vmaf_77.046.jpg) |
| 14 | 00:00.234 | 77.133 | [thumbnail](thumbnails/h264_baseline_encoded_1080p_upscaled_3840x2160_frame_14_vmaf_77.133.jpg) |

### h264_baseline / encoded_2160p.mp4 — native

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 23 | 00:00.384 | 85.036 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_native_frame_23_vmaf_85.036.jpg) |
| 13 | 00:00.217 | 85.222 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_native_frame_13_vmaf_85.222.jpg) |
| 7 | 00:00.117 | 85.237 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_native_frame_7_vmaf_85.237.jpg) |
| 400 | 00:06.673 | 85.504 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_native_frame_400_vmaf_85.504.jpg) |
| 15 | 00:00.250 | 85.610 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_native_frame_15_vmaf_85.610.jpg) |

### h264_baseline / encoded_2160p.mp4 — upscaled_3840x2160

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 23 | 00:00.384 | 85.036 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_upscaled_3840x2160_frame_23_vmaf_85.036.jpg) |
| 13 | 00:00.217 | 85.222 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_upscaled_3840x2160_frame_13_vmaf_85.222.jpg) |
| 7 | 00:00.117 | 85.237 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_upscaled_3840x2160_frame_7_vmaf_85.237.jpg) |
| 400 | 00:06.673 | 85.504 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_upscaled_3840x2160_frame_400_vmaf_85.504.jpg) |
| 15 | 00:00.250 | 85.610 | [thumbnail](thumbnails/h264_baseline_encoded_2160p_upscaled_3840x2160_frame_15_vmaf_85.610.jpg) |

### h264_baseline / encoded_720p.mp4 — native

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 9 | 00:00.150 | 86.809 | [thumbnail](thumbnails/h264_baseline_encoded_720p_native_frame_9_vmaf_86.809.jpg) |
| 2 | 00:00.033 | 86.872 | [thumbnail](thumbnails/h264_baseline_encoded_720p_native_frame_2_vmaf_86.872.jpg) |
| 13 | 00:00.217 | 86.899 | [thumbnail](thumbnails/h264_baseline_encoded_720p_native_frame_13_vmaf_86.899.jpg) |
| 11 | 00:00.184 | 87.018 | [thumbnail](thumbnails/h264_baseline_encoded_720p_native_frame_11_vmaf_87.018.jpg) |
| 17 | 00:00.284 | 87.074 | [thumbnail](thumbnails/h264_baseline_encoded_720p_native_frame_17_vmaf_87.074.jpg) |

### h264_baseline / encoded_720p.mp4 — upscaled_3840x2160

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 17 | 00:00.284 | 65.168 | [thumbnail](thumbnails/h264_baseline_encoded_720p_upscaled_3840x2160_frame_17_vmaf_65.168.jpg) |
| 19 | 00:00.317 | 65.254 | [thumbnail](thumbnails/h264_baseline_encoded_720p_upscaled_3840x2160_frame_19_vmaf_65.254.jpg) |
| 15 | 00:00.250 | 65.338 | [thumbnail](thumbnails/h264_baseline_encoded_720p_upscaled_3840x2160_frame_15_vmaf_65.338.jpg) |
| 13 | 00:00.217 | 65.348 | [thumbnail](thumbnails/h264_baseline_encoded_720p_upscaled_3840x2160_frame_13_vmaf_65.348.jpg) |
| 9 | 00:00.150 | 65.511 | [thumbnail](thumbnails/h264_baseline_encoded_720p_upscaled_3840x2160_frame_9_vmaf_65.511.jpg) |

### hevc_low / encoded_1080p.mp4 — native

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 9 | 00:00.150 | 83.348 | [thumbnail](thumbnails/hevc_low_encoded_1080p_native_frame_9_vmaf_83.348.jpg) |
| 4 | 00:00.067 | 83.629 | [thumbnail](thumbnails/hevc_low_encoded_1080p_native_frame_4_vmaf_83.629.jpg) |
| 5 | 00:00.083 | 83.655 | [thumbnail](thumbnails/hevc_low_encoded_1080p_native_frame_5_vmaf_83.655.jpg) |
| 3 | 00:00.050 | 83.848 | [thumbnail](thumbnails/hevc_low_encoded_1080p_native_frame_3_vmaf_83.848.jpg) |
| 6 | 00:00.100 | 84.027 | [thumbnail](thumbnails/hevc_low_encoded_1080p_native_frame_6_vmaf_84.027.jpg) |

### hevc_low / encoded_1080p.mp4 — upscaled_3840x2160

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 9 | 00:00.150 | 71.397 | [thumbnail](thumbnails/hevc_low_encoded_1080p_upscaled_3840x2160_frame_9_vmaf_71.397.jpg) |
| 5 | 00:00.083 | 72.020 | [thumbnail](thumbnails/hevc_low_encoded_1080p_upscaled_3840x2160_frame_5_vmaf_72.020.jpg) |
| 4 | 00:00.067 | 72.140 | [thumbnail](thumbnails/hevc_low_encoded_1080p_upscaled_3840x2160_frame_4_vmaf_72.140.jpg) |
| 7 | 00:00.117 | 72.522 | [thumbnail](thumbnails/hevc_low_encoded_1080p_upscaled_3840x2160_frame_7_vmaf_72.522.jpg) |
| 3 | 00:00.050 | 72.608 | [thumbnail](thumbnails/hevc_low_encoded_1080p_upscaled_3840x2160_frame_3_vmaf_72.608.jpg) |

### hevc_low / encoded_2160p.mp4 — native

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 6 | 00:00.100 | 80.694 | [thumbnail](thumbnails/hevc_low_encoded_2160p_native_frame_6_vmaf_80.694.jpg) |
| 7 | 00:00.117 | 80.913 | [thumbnail](thumbnails/hevc_low_encoded_2160p_native_frame_7_vmaf_80.913.jpg) |
| 5 | 00:00.083 | 80.948 | [thumbnail](thumbnails/hevc_low_encoded_2160p_native_frame_5_vmaf_80.948.jpg) |
| 9 | 00:00.150 | 81.013 | [thumbnail](thumbnails/hevc_low_encoded_2160p_native_frame_9_vmaf_81.013.jpg) |
| 4 | 00:00.067 | 81.893 | [thumbnail](thumbnails/hevc_low_encoded_2160p_native_frame_4_vmaf_81.893.jpg) |

### hevc_low / encoded_2160p.mp4 — upscaled_3840x2160

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 6 | 00:00.100 | 80.694 | [thumbnail](thumbnails/hevc_low_encoded_2160p_upscaled_3840x2160_frame_6_vmaf_80.694.jpg) |
| 7 | 00:00.117 | 80.913 | [thumbnail](thumbnails/hevc_low_encoded_2160p_upscaled_3840x2160_frame_7_vmaf_80.913.jpg) |
| 5 | 00:00.083 | 80.948 | [thumbnail](thumbnails/hevc_low_encoded_2160p_upscaled_3840x2160_frame_5_vmaf_80.948.jpg) |
| 9 | 00:00.150 | 81.013 | [thumbnail](thumbnails/hevc_low_encoded_2160p_upscaled_3840x2160_frame_9_vmaf_81.013.jpg) |
| 4 | 00:00.067 | 81.893 | [thumbnail](thumbnails/hevc_low_encoded_2160p_upscaled_3840x2160_frame_4_vmaf_81.893.jpg) |

### hevc_low / encoded_720p.mp4 — native

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 4 | 00:00.067 | 84.450 | [thumbnail](thumbnails/hevc_low_encoded_720p_native_frame_4_vmaf_84.450.jpg) |
| 5 | 00:00.083 | 84.633 | [thumbnail](thumbnails/hevc_low_encoded_720p_native_frame_5_vmaf_84.633.jpg) |
| 6 | 00:00.100 | 84.904 | [thumbnail](thumbnails/hevc_low_encoded_720p_native_frame_6_vmaf_84.904.jpg) |
| 3 | 00:00.050 | 85.130 | [thumbnail](thumbnails/hevc_low_encoded_720p_native_frame_3_vmaf_85.130.jpg) |
| 9 | 00:00.150 | 85.400 | [thumbnail](thumbnails/hevc_low_encoded_720p_native_frame_9_vmaf_85.400.jpg) |

### hevc_low / encoded_720p.mp4 — upscaled_3840x2160

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 4 | 00:00.067 | 61.785 | [thumbnail](thumbnails/hevc_low_encoded_720p_upscaled_3840x2160_frame_4_vmaf_61.785.jpg) |
| 5 | 00:00.083 | 61.843 | [thumbnail](thumbnails/hevc_low_encoded_720p_upscaled_3840x2160_frame_5_vmaf_61.843.jpg) |
| 6 | 00:00.100 | 63.065 | [thumbnail](thumbnails/hevc_low_encoded_720p_upscaled_3840x2160_frame_6_vmaf_63.065.jpg) |
| 3 | 00:00.050 | 63.708 | [thumbnail](thumbnails/hevc_low_encoded_720p_upscaled_3840x2160_frame_3_vmaf_63.708.jpg) |
| 7 | 00:00.117 | 64.055 | [thumbnail](thumbnails/hevc_low_encoded_720p_upscaled_3840x2160_frame_7_vmaf_64.055.jpg) |

### hevc_medium / encoded_1080p.mp4 — native

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 9 | 00:00.150 | 83.346 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_native_frame_9_vmaf_83.346.jpg) |
| 4 | 00:00.067 | 83.629 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_native_frame_4_vmaf_83.629.jpg) |
| 5 | 00:00.083 | 83.655 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_native_frame_5_vmaf_83.655.jpg) |
| 3 | 00:00.050 | 83.848 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_native_frame_3_vmaf_83.848.jpg) |
| 6 | 00:00.100 | 84.027 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_native_frame_6_vmaf_84.027.jpg) |

### hevc_medium / encoded_1080p.mp4 — upscaled_3840x2160

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 9 | 00:00.150 | 71.396 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_upscaled_3840x2160_frame_9_vmaf_71.396.jpg) |
| 5 | 00:00.083 | 72.020 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_upscaled_3840x2160_frame_5_vmaf_72.020.jpg) |
| 4 | 00:00.067 | 72.140 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_upscaled_3840x2160_frame_4_vmaf_72.140.jpg) |
| 7 | 00:00.117 | 72.522 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_upscaled_3840x2160_frame_7_vmaf_72.522.jpg) |
| 3 | 00:00.050 | 72.608 | [thumbnail](thumbnails/hevc_medium_encoded_1080p_upscaled_3840x2160_frame_3_vmaf_72.608.jpg) |

### hevc_medium / encoded_2160p.mp4 — native

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 5 | 00:00.083 | 81.396 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_native_frame_5_vmaf_81.396.jpg) |
| 7 | 00:00.117 | 81.824 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_native_frame_7_vmaf_81.824.jpg) |
| 4 | 00:00.067 | 81.893 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_native_frame_4_vmaf_81.893.jpg) |
| 6 | 00:00.100 | 82.069 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_native_frame_6_vmaf_82.069.jpg) |
| 3 | 00:00.050 | 82.632 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_native_frame_3_vmaf_82.632.jpg) |

### hevc_medium / encoded_2160p.mp4 — upscaled_3840x2160

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 5 | 00:00.083 | 81.396 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_upscaled_3840x2160_frame_5_vmaf_81.396.jpg) |
| 7 | 00:00.117 | 81.824 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_upscaled_3840x2160_frame_7_vmaf_81.824.jpg) |
| 4 | 00:00.067 | 81.893 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_upscaled_3840x2160_frame_4_vmaf_81.893.jpg) |
| 6 | 00:00.100 | 82.069 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_upscaled_3840x2160_frame_6_vmaf_82.069.jpg) |
| 3 | 00:00.050 | 82.632 | [thumbnail](thumbnails/hevc_medium_encoded_2160p_upscaled_3840x2160_frame_3_vmaf_82.632.jpg) |

### hevc_medium / encoded_720p.mp4 — native

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 6 | 00:00.100 | 85.588 | [thumbnail](thumbnails/hevc_medium_encoded_720p_native_frame_6_vmaf_85.588.jpg) |
| 3 | 00:00.050 | 85.862 | [thumbnail](thumbnails/hevc_medium_encoded_720p_native_frame_3_vmaf_85.862.jpg) |
| 5 | 00:00.083 | 85.879 | [thumbnail](thumbnails/hevc_medium_encoded_720p_native_frame_5_vmaf_85.879.jpg) |
| 2 | 00:00.033 | 86.141 | [thumbnail](thumbnails/hevc_medium_encoded_720p_native_frame_2_vmaf_86.141.jpg) |
| 7 | 00:00.117 | 86.205 | [thumbnail](thumbnails/hevc_medium_encoded_720p_native_frame_7_vmaf_86.205.jpg) |

### hevc_medium / encoded_720p.mp4 — upscaled_3840x2160

| Frame | Timestamp | VMAF | Thumbnail |
|---:|---:|---:|---|
| 6 | 00:00.100 | 64.478 | [thumbnail](thumbnails/hevc_medium_encoded_720p_upscaled_3840x2160_frame_6_vmaf_64.478.jpg) |
| 3 | 00:00.050 | 64.907 | [thumbnail](thumbnails/hevc_medium_encoded_720p_upscaled_3840x2160_frame_3_vmaf_64.907.jpg) |
| 7 | 00:00.117 | 65.001 | [thumbnail](thumbnails/hevc_medium_encoded_720p_upscaled_3840x2160_frame_7_vmaf_65.001.jpg) |
| 5 | 00:00.083 | 65.018 | [thumbnail](thumbnails/hevc_medium_encoded_720p_upscaled_3840x2160_frame_5_vmaf_65.018.jpg) |
| 9 | 00:00.150 | 65.258 | [thumbnail](thumbnails/hevc_medium_encoded_720p_upscaled_3840x2160_frame_9_vmaf_65.258.jpg) |
