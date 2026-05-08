#!/usr/bin/env python3

import argparse
import csv
import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path


def run_cmd(cmd):
    print("Running:", " ".join(cmd))
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed:\n{' '.join(cmd)}\n\nSTDERR:\n{result.stderr}"
        )

    return result.stdout, result.stderr


def ffprobe_video(path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries",
        "stream=codec_name,width,height,r_frame_rate,bit_rate,duration",
        "-of", "json",
        str(path)
    ]

    stdout, _ = run_cmd(cmd)
    data = json.loads(stdout)

    if not data.get("streams"):
        return None

    stream = data["streams"][0]

    return {
        "codec": stream.get("codec_name", "unknown"),
        "width": int(stream.get("width", 0)),
        "height": int(stream.get("height", 0)),
        "frame_rate": stream.get("r_frame_rate", "unknown"),
        "bit_rate": int(stream.get("bit_rate", 0)) if stream.get("bit_rate") else 0,
        "duration": float(stream.get("duration", 0)) if stream.get("duration") else 0.0,
    }


def parse_frame_rate(rate_str):
    """
    Converts ffprobe frame rate strings like '30000/1001' or '60/1'
    into a float.
    """
    if not rate_str or rate_str == "unknown":
        return 0.0

    try:
        return float(Fraction(rate_str))
    except Exception:
        return 0.0


def build_precheck(source_info, encoded_info, duration_tolerance=0.25, fps_tolerance=0.01):
    """
    Compares source and encoded video properties before running VMAF.

    This does not necessarily block the run. It generates PASS/WARN status
    and warning text that gets added to the report.
    """
    warnings = []

    source_duration = source_info.get("duration", 0.0)
    encoded_duration = encoded_info.get("duration", 0.0)

    if source_duration and encoded_duration:
        duration_delta = abs(source_duration - encoded_duration)

        if duration_delta > duration_tolerance:
            warnings.append(
                f"Duration mismatch: source={source_duration:.3f}s, "
                f"encoded={encoded_duration:.3f}s, delta={duration_delta:.3f}s"
            )

    source_fps = parse_frame_rate(source_info.get("frame_rate", "unknown"))
    encoded_fps = parse_frame_rate(encoded_info.get("frame_rate", "unknown"))

    if source_fps and encoded_fps:
        fps_delta = abs(source_fps - encoded_fps)

        if fps_delta > fps_tolerance:
            warnings.append(
                f"Frame-rate mismatch: source={source_fps:.3f} fps, "
                f"encoded={encoded_fps:.3f} fps"
            )

    if encoded_info.get("width", 0) <= 0 or encoded_info.get("height", 0) <= 0:
        warnings.append("Invalid encoded resolution detected")

    if source_info.get("width", 0) <= 0 or source_info.get("height", 0) <= 0:
        warnings.append("Invalid source resolution detected")

    status = "PASS" if not warnings else "WARN"

    return status, "; ".join(warnings) if warnings else "None"


def parse_vmaf_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pooled = data.get("pooled_metrics", {})

    if "vmaf" in pooled:
        vmaf = pooled["vmaf"]
    elif "integer_vmaf" in pooled:
        vmaf = pooled["integer_vmaf"]
    else:
        raise ValueError(f"No VMAF pooled metrics found in {path}")

    return {
        "vmaf_min": vmaf.get("min"),
        "vmaf_max": vmaf.get("max"),
        "vmaf_mean": vmaf.get("mean"),
        "vmaf_harmonic_mean": vmaf.get("harmonic_mean"),
        "frames": data.get("frames", []),
    }


def classify_quality(vmaf_mean, vmaf_min):
    """
    Produces a PASS/WARN/FAIL style quality status.
    """
    if vmaf_mean is None or vmaf_min is None:
        return "FAIL"

    quality_drop = vmaf_mean - vmaf_min

    if vmaf_min < 70:
        return "FAIL"
    if vmaf_min < 80:
        return "WARN"
    if vmaf_mean < 90:
        return "WARN"
    if quality_drop > 15:
        return "WARN"

    return "PASS"


def build_quality_notes(vmaf_mean, vmaf_min):
    """
    Generates human-readable warnings based on score behavior.
    """
    if vmaf_mean is None or vmaf_min is None:
        return "No VMAF score"

    notes = []
    quality_drop = vmaf_mean - vmaf_min

    if vmaf_mean >= 95 and vmaf_min >= 90:
        notes.append("Excellent")
    elif vmaf_mean >= 90:
        notes.append("Very good")
    elif vmaf_mean >= 80:
        notes.append("Good; inspect visually")
    elif vmaf_mean >= 70:
        notes.append("Noticeable degradation")
    else:
        notes.append("Poor; needs investigation")

    if vmaf_min < 70:
        notes.append(f"CRITICAL low frame detected: min VMAF={vmaf_min:.3f}")
    elif vmaf_min < 80:
        notes.append(f"Low frame warning: min VMAF={vmaf_min:.3f}")

    if quality_drop > 15:
        notes.append(f"Large quality swing: mean-min delta={quality_drop:.3f}")

    return "; ".join(notes)


def classify_notes(vmaf_mean, vmaf_min, test_type):
    return build_quality_notes(vmaf_mean, vmaf_min)


def get_frame_vmaf(frame):
    metrics = frame.get("metrics", {})

    if "vmaf" in metrics:
        return metrics.get("vmaf")

    if "integer_vmaf" in metrics:
        return metrics.get("integer_vmaf")

    return None


def get_worst_frames(frames, limit=5):
    scored_frames = []

    for frame in frames:
        frame_num = frame.get("frameNum")
        vmaf_score = get_frame_vmaf(frame)

        if frame_num is None or vmaf_score is None:
            continue

        scored_frames.append({
            "frame_num": int(frame_num),
            "vmaf": float(vmaf_score),
        })

    scored_frames.sort(key=lambda item: item["vmaf"])
    return scored_frames[:limit]


def frame_to_timestamp(frame_num, frame_rate):
    fps = parse_frame_rate(frame_rate)

    if not fps:
        return 0.0

    return frame_num / fps


def format_timestamp(seconds):
    seconds = max(0.0, float(seconds))
    minutes = int(seconds // 60)
    remaining = seconds - (minutes * 60)
    return f"{minutes:02d}:{remaining:06.3f}"


def safe_stem(value):
    safe = []

    for char in value:
        if char.isalnum() or char in ("-", "_"):
            safe.append(char)
        else:
            safe.append("_")

    return "".join(safe)


def extract_thumbnail(video_path, timestamp, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", f"{timestamp:.3f}",
        "-i", str(video_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(output_path),
    ]

    try:
        run_cmd(cmd)
        return True
    except RuntimeError as exc:
        print(f"  Thumbnail extraction failed for {video_path}: {exc}")
        return False


def create_vmaf_svg_chart(frames, frame_rate, output_path, title):
    scored = []

    for frame in frames:
        frame_num = frame.get("frameNum")
        vmaf_score = get_frame_vmaf(frame)

        if frame_num is None or vmaf_score is None:
            continue

        timestamp = frame_to_timestamp(int(frame_num), frame_rate)
        scored.append((timestamp, float(vmaf_score)))

    if not scored:
        return ""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    width = 1000
    height = 320
    margin_left = 60
    margin_right = 24
    margin_top = 40
    margin_bottom = 44
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    min_time = min(t for t, _ in scored)
    max_time = max(t for t, _ in scored)
    time_span = max(max_time - min_time, 0.001)

    points = []
    for timestamp, score in scored:
        x = margin_left + ((timestamp - min_time) / time_span) * plot_width
        y = margin_top + ((100.0 - score) / 100.0) * plot_height
        points.append(f"{x:.2f},{y:.2f}")

    mean_score = sum(score for _, score in scored) / len(scored)
    min_vmaf = min(score for _, score in scored)
    max_vmaf = max(score for _, score in scored)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{margin_left}" y="24" font-family="Arial" font-size="18" font-weight="bold">{title}</text>
  <text x="{margin_left}" y="{height - 12}" font-family="Arial" font-size="12" fill="#555">Mean={mean_score:.3f} Min={min_vmaf:.3f} Max={max_vmaf:.3f}</text>
  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#333" stroke-width="1"/>
  <line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" stroke="#333" stroke-width="1"/>
  <line x1="{margin_left}" y1="{margin_top + plot_height * 0.1}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height * 0.1}" stroke="#ddd" stroke-width="1"/>
  <line x1="{margin_left}" y1="{margin_top + plot_height * 0.2}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height * 0.2}" stroke="#eee" stroke-width="1"/>
  <line x1="{margin_left}" y1="{margin_top + plot_height * 0.5}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height * 0.5}" stroke="#eee" stroke-width="1"/>
  <text x="12" y="{margin_top + 4}" font-family="Arial" font-size="12">100</text>
  <text x="20" y="{margin_top + plot_height * 0.1 + 4}" font-family="Arial" font-size="12">90</text>
  <text x="20" y="{margin_top + plot_height * 0.2 + 4}" font-family="Arial" font-size="12">80</text>
  <text x="20" y="{margin_top + plot_height * 0.5 + 4}" font-family="Arial" font-size="12">50</text>
  <text x="{margin_left}" y="{margin_top + plot_height + 24}" font-family="Arial" font-size="12">{format_timestamp(min_time)}</text>
  <text x="{margin_left + plot_width - 52}" y="{margin_top + plot_height + 24}" font-family="Arial" font-size="12">{format_timestamp(max_time)}</text>
  <polyline points="{' '.join(points)}" fill="none" stroke="#0d6efd" stroke-width="2"/>
</svg>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    return output_path


def create_worst_frame_artifacts(encoded, frames, frame_rate, test_label, output_dir, artifact_stem=None, limit=5):
    worst_frames = get_worst_frames(frames, limit=limit)
    thumbnails_dir = output_dir / "thumbnails"
    artifacts = []

    for item in worst_frames:
        frame_num = item["frame_num"]
        timestamp = frame_to_timestamp(frame_num, frame_rate)
        timestamp_label = format_timestamp(timestamp)
        safe_artifact_stem = safe_stem(artifact_stem or encoded.stem)
        thumb_name = (
            f"{safe_artifact_stem}_{safe_stem(test_label)}_"
            f"frame_{frame_num}_vmaf_{item['vmaf']:.3f}.jpg"
        )
        thumb_path = thumbnails_dir / thumb_name
        extracted = extract_thumbnail(encoded, timestamp, thumb_path)

        artifacts.append({
            "frame_num": frame_num,
            "timestamp": timestamp,
            "timestamp_label": timestamp_label,
            "vmaf": item["vmaf"],
            "thumbnail": thumb_path.relative_to(output_dir).as_posix() if extracted else "",
        })

    return artifacts


def build_visual_artifacts(encoded, metrics, encoded_info, test_label, output_dir, artifact_stem=None):
    frames = metrics.pop("frames", [])
    chart_path = ""
    worst_frames = []

    if frames:
        charts_dir = output_dir / "charts"
        safe_artifact_stem = safe_stem(artifact_stem or encoded.stem)
        chart_file = charts_dir / f"{safe_artifact_stem}_{safe_stem(test_label)}_vmaf.svg"
        created_chart = create_vmaf_svg_chart(
            frames,
            encoded_info["frame_rate"],
            chart_file,
            f"{encoded.name} - {test_label} VMAF Over Time",
        )

        if created_chart:
            chart_path = created_chart.relative_to(output_dir).as_posix()

        worst_frames = create_worst_frame_artifacts(
            encoded,
            frames,
            encoded_info["frame_rate"],
            test_label,
            output_dir,
            artifact_stem=artifact_stem,
            limit=5,
        )

    return chart_path, worst_frames


def run_vmaf_native(encoded, source, encoded_info, output_json):
    width = encoded_info["width"]
    height = encoded_info["height"]

    filter_complex = (
        f"[0:v]setpts=PTS-STARTPTS,format=yuv420p[dist];"
        f"[1:v]setpts=PTS-STARTPTS,scale={width}:{height}:flags=bicubic,"
        f"format=yuv420p[ref];"
        f"[dist][ref]libvmaf=log_fmt=json:log_path={output_json}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(encoded),
        "-i", str(source),
        "-filter_complex", filter_complex,
        "-f", "null",
        "-"
    ]

    run_cmd(cmd)



def run_vmaf_upscaled(encoded, source, target_width, target_height, output_json):
    filter_complex = (
        f"[0:v]setpts=PTS-STARTPTS,scale={target_width}:{target_height}:flags=bicubic,"
        f"format=yuv420p[dist];"
        f"[1:v]setpts=PTS-STARTPTS,scale={target_width}:{target_height}:flags=bicubic,"
        f"format=yuv420p[ref];"
        f"[dist][ref]libvmaf=log_fmt=json:log_path={output_json}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(encoded),
        "-i", str(source),
        "-filter_complex", filter_complex,
        "-f", "null",
        "-"
    ]

    run_cmd(cmd)


# --------- PSNR/SSIM NATIVE/UPSCALED SUPPORT ---------

def parse_psnr_from_stderr(stderr):
    match = re.search(r"average:([0-9.]+)", stderr)

    if not match:
        return None

    return float(match.group(1))


def parse_ssim_from_stderr(stderr):
    match = re.search(r"All:([0-9.]+)", stderr)

    if not match:
        return None

    return float(match.group(1))


def run_psnr_native(encoded, source, encoded_info, stats_file):
    width = encoded_info["width"]
    height = encoded_info["height"]

    filter_complex = (
        f"[0:v]setpts=PTS-STARTPTS,format=yuv420p[dist];"
        f"[1:v]setpts=PTS-STARTPTS,scale={width}:{height}:flags=bicubic,"
        f"format=yuv420p[ref];"
        f"[dist][ref]psnr=stats_file={stats_file}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(encoded),
        "-i", str(source),
        "-filter_complex", filter_complex,
        "-f", "null",
        "-"
    ]

    _, stderr = run_cmd(cmd)
    return parse_psnr_from_stderr(stderr)


def run_ssim_native(encoded, source, encoded_info, stats_file):
    width = encoded_info["width"]
    height = encoded_info["height"]

    filter_complex = (
        f"[0:v]setpts=PTS-STARTPTS,format=yuv420p[dist];"
        f"[1:v]setpts=PTS-STARTPTS,scale={width}:{height}:flags=bicubic,"
        f"format=yuv420p[ref];"
        f"[dist][ref]ssim=stats_file={stats_file}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(encoded),
        "-i", str(source),
        "-filter_complex", filter_complex,
        "-f", "null",
        "-"
    ]

    _, stderr = run_cmd(cmd)
    return parse_ssim_from_stderr(stderr)


def run_psnr_upscaled(encoded, source, target_width, target_height, stats_file):
    filter_complex = (
        f"[0:v]setpts=PTS-STARTPTS,scale={target_width}:{target_height}:flags=bicubic,"
        f"format=yuv420p[dist];"
        f"[1:v]setpts=PTS-STARTPTS,scale={target_width}:{target_height}:flags=bicubic,"
        f"format=yuv420p[ref];"
        f"[dist][ref]psnr=stats_file={stats_file}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(encoded),
        "-i", str(source),
        "-filter_complex", filter_complex,
        "-f", "null",
        "-"
    ]

    _, stderr = run_cmd(cmd)
    return parse_psnr_from_stderr(stderr)


def run_ssim_upscaled(encoded, source, target_width, target_height, stats_file):
    filter_complex = (
        f"[0:v]setpts=PTS-STARTPTS,scale={target_width}:{target_height}:flags=bicubic,"
        f"format=yuv420p[dist];"
        f"[1:v]setpts=PTS-STARTPTS,scale={target_width}:{target_height}:flags=bicubic,"
        f"format=yuv420p[ref];"
        f"[dist][ref]ssim=stats_file={stats_file}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(encoded),
        "-i", str(source),
        "-filter_complex", filter_complex,
        "-f", "null",
        "-"
    ]

    _, stderr = run_cmd(cmd)
    return parse_ssim_from_stderr(stderr)


def format_optional_metric(value, decimals=3):
    if value in (None, ""):
        return ""

    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)



def bitrate_mbps(bit_rate):
    if not bit_rate:
        return ""
    return round(bit_rate / 1_000_000, 3)


# --------- RUN/PROFILE/BASELINE COMPARISON HELPERS ---------

def extract_profile_name(path):
    stem = path.stem.lower()

    for token in ("2160p", "1440p", "1080p", "720p", "540p", "480p", "360p", "240p"):
        if token in stem:
            return token

    return stem


def quality_per_mbps(vmaf_mean, bitrate):
    if vmaf_mean is None or not bitrate:
        return None

    try:
        return vmaf_mean / float(bitrate)
    except ZeroDivisionError:
        return None


def compare_to_baseline(row, baseline_lookup):
    profile = row.get("profile", "")
    test_type = row.get("test_type", "")
    baseline = baseline_lookup.get((profile, test_type))

    row["baseline_bitrate_mbps"] = ""
    row["bitrate_savings_percent"] = ""
    row["vmaf_delta"] = ""
    row["psnr_delta"] = ""
    row["ssim_delta"] = ""

    if not baseline:
        return row

    row_bitrate = row.get("bitrate_mbps")
    base_bitrate = baseline.get("bitrate_mbps")

    if row_bitrate not in (None, "") and base_bitrate not in (None, "") and base_bitrate:
        row["baseline_bitrate_mbps"] = base_bitrate
        row["bitrate_savings_percent"] = ((base_bitrate - row_bitrate) / base_bitrate) * 100.0

    if row.get("vmaf_mean") is not None and baseline.get("vmaf_mean") is not None:
        row["vmaf_delta"] = row["vmaf_mean"] - baseline["vmaf_mean"]

    if row.get("psnr_avg") is not None and baseline.get("psnr_avg") is not None:
        row["psnr_delta"] = row["psnr_avg"] - baseline["psnr_avg"]

    if row.get("ssim_all") is not None and baseline.get("ssim_all") is not None:
        row["ssim_delta"] = row["ssim_all"] - baseline["ssim_all"]

    return row


def apply_run_comparisons(rows, baseline_run):
    if not baseline_run:
        return rows

    baseline_lookup = {}

    for row in rows:
        if row.get("run_name") == baseline_run:
            key = (row.get("profile", ""), row.get("test_type", ""))
            baseline_lookup[key] = row

    for row in rows:
        compare_to_baseline(row, baseline_lookup)

    return rows


def format_optional_percent(value):
    if value in (None, ""):
        return ""

    return f"{value:.1f}%"


def get_encoded_files(encoded_dir):
    return sorted(
        p for p in encoded_dir.glob("*.mp4")
        if p.is_file()
    )


def write_csv(rows, output_path):
    fieldnames = [
        "run_name",
        "profile",
        "file",
        "codec",
        "resolution",
        "frame_rate",
        "bitrate_mbps",
        "duration",
        "test_type",
        "scale_method",
        "precheck_status",
        "precheck_warnings",
        "quality_status",
        "worst_frame",
        "worst_timestamp",
        "chart",
        "vmaf_min",
        "vmaf_max",
        "vmaf_mean",
        "vmaf_harmonic_mean",
        "psnr_avg",
        "ssim_all",
        "quality_per_mbps",
        "baseline_bitrate_mbps",
        "bitrate_savings_percent",
        "vmaf_delta",
        "psnr_delta",
        "ssim_delta",
        "notes",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows, output_path):
    lines = []
    lines.append("# VMAF Batch Report\n")
    lines.append("| Run | Profile | File | Codec | Resolution | Bitrate Mbps | Test | Precheck | Quality | Mean VMAF | Min VMAF | PSNR Avg | SSIM All | Quality/Mbps | Savings | VMAF Δ | Worst Timestamp | Chart | Notes |")
    lines.append("|---|---|---|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|")

    for row in rows:
        chart_link = f"[chart]({row['chart']})" if row.get("chart") else ""

        lines.append(
            f"| {row.get('run_name', '')} "
            f"| {row.get('profile', '')} "
            f"| {row['file']} "
            f"| {row['codec']} "
            f"| {row['resolution']} "
            f"| {row['bitrate_mbps']} "
            f"| {row['test_type']} "
            f"| {row['precheck_status']} "
            f"| {row['quality_status']} "
            f"| {format_optional_metric(row.get('vmaf_mean'), 3)} "
            f"| {format_optional_metric(row.get('vmaf_min'), 3)} "
            f"| {format_optional_metric(row.get('psnr_avg'), 3)} "
            f"| {format_optional_metric(row.get('ssim_all'), 6)} "
            f"| {format_optional_metric(row.get('quality_per_mbps'), 3)} "
            f"| {format_optional_percent(row.get('bitrate_savings_percent'))} "
            f"| {format_optional_metric(row.get('vmaf_delta'), 3)} "
            f"| {row.get('worst_timestamp', '')} "
            f"| {chart_link} "
            f"| {row['notes']} |"
        )

    lines.append("\n## Notes\n")
    lines.append("- Native tests scale the source down to the encoded rendition resolution.")
    lines.append("- Upscaled tests scale the encoded rendition up to the target display resolution.")
    lines.append("- Mean VMAF is useful, but minimum VMAF helps identify worst-frame quality drops.")
    lines.append("- PSNR Avg is a pixel-error metric reported in dB; higher is better, but it is less perceptual than VMAF.")
    lines.append("- SSIM All is a structural similarity metric from 0 to 1; higher is better.")
    lines.append("- Quality/Mbps is VMAF Mean divided by bitrate Mbps; it is useful for efficiency comparisons but should not be used alone.")
    lines.append("- Savings and delta columns are populated when `--runs-dir` and `--baseline-run` are used.")
    lines.append("- Precheck PASS means duration/frame-rate checks did not detect obvious mismatches.")
    lines.append("- Precheck WARN means the VMAF result may still be useful, but the file should be reviewed carefully.")
    lines.append("- Quality WARN/FAIL is based on mean VMAF, minimum VMAF, and large mean-to-min drops.")
    lines.append("- Use VMAF with visual inspection and playback testing.\n")

    lines.append("\n## Worst Frame Details\n")

    for row in rows:
        worst_frames = row.get("worst_frames", [])
        if not worst_frames:
            continue

        run_label = row.get("run_name", "")
        heading = f"{run_label} / {row['file']}" if run_label else row["file"]
        lines.append(f"### {heading} — {row['test_type']}\n")
        lines.append("| Frame | Timestamp | VMAF | Thumbnail |")
        lines.append("|---:|---:|---:|---|")

        for item in worst_frames:
            thumb_link = f"[thumbnail]({item['thumbnail']})" if item.get("thumbnail") else ""
            lines.append(
                f"| {item['frame_num']} "
                f"| {item['timestamp_label']} "
                f"| {item['vmaf']:.3f} "
                f"| {thumb_link} |"
            )

        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_html(rows, output_path, source, source_info):
    import html as _html
    _esc = _html.escape

    total = len(rows)
    pass_count = sum(1 for r in rows if r["quality_status"] == "PASS")
    warn_count = sum(1 for r in rows if r["quality_status"] == "WARN")
    fail_count = sum(1 for r in rows if r["quality_status"] == "FAIL")
    precheck_warn_count = sum(1 for r in rows if r["precheck_status"] == "WARN")
    run_names = sorted(set(r.get("run_name", "") for r in rows if r.get("run_name")))
    profile_names = sorted(set(r.get("profile", "") for r in rows if r.get("profile")))

    def status_class(status):
        if status == "PASS":
            return "pass"
        if status == "WARN":
            return "warn"
        if status == "FAIL":
            return "fail"
        return ""

    def fmt_score(value):
        if value is None:
            return "N/A"
        return f"{value:.3f}"

    html = []

    html.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>VMAF Batch Report</title>
<style>
    body {
        font-family: Arial, Helvetica, sans-serif;
        margin: 24px;
        background: #f7f7f7;
        color: #222;
    }

    h1, h2 {
        margin-bottom: 8px;
    }

    .card {
        background: #fff;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(120px, 1fr));
        gap: 12px;
        margin-top: 12px;
    }

    .summary-box {
        border-radius: 8px;
        padding: 12px;
        background: #f0f0f0;
        text-align: center;
        font-weight: bold;
    }

    .summary-box.pass {
        background: #d7f5df;
        color: #145c2e;
    }

    .summary-box.warn {
        background: #fff3cd;
        color: #7a5a00;
    }

    .summary-box.fail {
        background: #f8d7da;
        color: #842029;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        background: #fff;
        font-size: 14px;
    }

    th {
        background: #333;
        color: #fff;
        padding: 8px;
        text-align: left;
        position: sticky;
        top: 0;
    }

    td {
        border: 1px solid #ddd;
        padding: 8px;
        vertical-align: top;
    }

    tr.pass {
        background: #eaf8ee;
    }

    tr.warn {
        background: #fff8e1;
    }

    tr.fail {
        background: #fdebed;
    }

    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: bold;
    }

    .badge.pass {
        background: #198754;
        color: white;
    }

    .badge.warn {
        background: #ffc107;
        color: #222;
    }

    .badge.fail {
        background: #dc3545;
        color: white;
    }

    .mono {
        font-family: Consolas, Monaco, monospace;
    }

    .warning-list li {
        margin-bottom: 6px;
    }

    .chart-preview {
        width: 100%;
        max-width: 1000px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background: #fff;
        margin-top: 8px;
    }

    .thumb-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 12px;
        margin-top: 10px;
    }

    .thumb-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 8px;
        background: #fff;
    }

    .thumb-card img {
        width: 100%;
        border-radius: 6px;
        border: 1px solid #eee;
    }

    .thumb-meta {
        font-size: 12px;
        margin-top: 6px;
        color: #333;
    }
</style>
</head>
<body>
""")

    html.append("<h1>VMAF Batch Report</h1>")

    html.append('<div class="card">')
    html.append("<h2>Summary</h2>")
    html.append('<div class="summary-grid">')
    html.append(f'<div class="summary-box">Total Tests<br>{total}</div>')
    html.append(f'<div class="summary-box pass">PASS<br>{pass_count}</div>')
    html.append(f'<div class="summary-box warn">WARN<br>{warn_count}</div>')
    html.append(f'<div class="summary-box fail">FAIL<br>{fail_count}</div>')
    html.append(f'<div class="summary-box warn">Precheck WARN<br>{precheck_warn_count}</div>')
    if run_names:
        html.append(f'<div class="summary-box">Runs<br>{len(run_names)}</div>')
    if profile_names:
        html.append(f'<div class="summary-box">Profiles<br>{len(profile_names)}</div>')
    html.append("</div>")
    html.append("</div>")

    html.append('<div class="card">')
    html.append("<h2>Source Info</h2>")
    html.append("<table>")
    html.append("<tr><th>Source</th><th>Codec</th><th>Resolution</th><th>Frame Rate</th><th>Duration</th></tr>")
    html.append(
        f"<tr>"
        f"<td class='mono'>{_esc(str(source))}</td>"
        f"<td>{_esc(source_info['codec'])}</td>"
        f"<td>{source_info['width']}x{source_info['height']}</td>"
        f"<td>{_esc(source_info['frame_rate'])}</td>"
        f"<td>{source_info['duration']:.3f}s</td>"
        f"</tr>"
    )
    html.append("</table>")
    html.append("</div>")

    precheck_warnings = [
        r for r in rows
        if r["precheck_status"] == "WARN"
    ]

    if precheck_warnings:
        html.append('<div class="card">')
        html.append("<h2>Precheck Warnings</h2>")
        html.append("<ul class='warning-list'>")
        for row in precheck_warnings:
            html.append(
                f"<li><strong>{row['file']}</strong> "
                f"({row['test_type']}): {row['precheck_warnings']}</li>"
            )
        html.append("</ul>")
        html.append("</div>")

    quality_items = [
        r for r in rows
        if r["quality_status"] in ("WARN", "FAIL")
    ]

    if quality_items:
        html.append('<div class="card">')
        html.append("<h2>Quality Items to Review</h2>")
        html.append("<ul class='warning-list'>")
        for row in quality_items:
            run_label = row.get("run_name", "")
            heading = f"{run_label} / {row['file']}" if run_label else row["file"]
            html.append(
                f"<li><strong>{heading}</strong> "
                f"({row['test_type']}): "
                f"{row['quality_status']} — "
                f"Mean VMAF={fmt_score(row['vmaf_mean'])}, "
                f"Min VMAF={fmt_score(row['vmaf_min'])}. "
                f"{row['notes']}</li>"
            )
        html.append("</ul>")
        html.append("</div>")

    html.append('<div class="card">')
    html.append("<h2>Results</h2>")
    html.append("<table>")
    html.append(
        "<tr>"
        "<th>Run</th>"
        "<th>Profile</th>"
        "<th>File</th>"
        "<th>Codec</th>"
        "<th>Resolution</th>"
        "<th>Bitrate Mbps</th>"
        "<th>Duration</th>"
        "<th>Test</th>"
        "<th>Precheck</th>"
        "<th>Quality</th>"
        "<th>Mean VMAF</th>"
        "<th>Min VMAF</th>"
        "<th>Max VMAF</th>"
        "<th>PSNR Avg</th>"
        "<th>SSIM All</th>"
        "<th>Quality/Mbps</th>"
        "<th>Savings</th>"
        "<th>VMAF Δ</th>"
        "<th>Worst Time</th>"
        "<th>Chart</th>"
        "<th>Notes</th>"
        "</tr>"
    )

    for row in rows:
        q_class = status_class(row["quality_status"])
        p_class = status_class(row["precheck_status"])

        chart_link = f"<a href='{row['chart']}'>chart</a>" if row.get("chart") else ""
        html.append(f"<tr class='{q_class}'>")
        html.append(f"<td>{_esc(row.get('run_name', ''))}</td>")
        html.append(f"<td>{_esc(row.get('profile', ''))}</td>")
        html.append(f"<td class='mono'>{_esc(row['file'])}</td>")
        html.append(f"<td>{_esc(row['codec'])}</td>")
        html.append(f"<td>{row['resolution']}</td>")
        html.append(f"<td>{row['bitrate_mbps']}</td>")
        html.append(f"<td>{row['duration']}</td>")
        html.append(f"<td>{_esc(row['test_type'])}</td>")
        html.append(f"<td><span class='badge {p_class}'>{row['precheck_status']}</span></td>")
        html.append(f"<td><span class='badge {q_class}'>{row['quality_status']}</span></td>")
        html.append(f"<td>{fmt_score(row['vmaf_mean'])}</td>")
        html.append(f"<td>{fmt_score(row['vmaf_min'])}</td>")
        html.append(f"<td>{fmt_score(row['vmaf_max'])}</td>")
        html.append(f"<td>{format_optional_metric(row.get('psnr_avg'), 3)}</td>")
        html.append(f"<td>{format_optional_metric(row.get('ssim_all'), 6)}</td>")
        html.append(f"<td>{format_optional_metric(row.get('quality_per_mbps'), 3)}</td>")
        html.append(f"<td>{format_optional_percent(row.get('bitrate_savings_percent'))}</td>")
        html.append(f"<td>{format_optional_metric(row.get('vmaf_delta'), 3)}</td>")
        html.append(f"<td>{row.get('worst_timestamp', '')}</td>")
        html.append(f"<td>{chart_link}</td>")
        html.append(f"<td>{_esc(row['notes'])}</td>")
        html.append("</tr>")

    html.append("</table>")
    html.append("</div>")

    visual_rows = [r for r in rows if r.get("chart") or r.get("worst_frames")]

    if visual_rows:
        html.append('<div class="card">')
        html.append("<h2>Visual Debug: VMAF Over Time and Worst Frames</h2>")

        for row in visual_rows:
            run_label = row.get("run_name", "")
            heading = f"{run_label} / {row['file']}" if run_label else row["file"]
            html.append(f"<h3>{heading} — {row['test_type']}</h3>")

            if row.get("chart"):
                html.append(f"<img class='chart-preview' src='{row['chart']}' alt='VMAF chart for {row['file']} {row['test_type']}'>")

            worst_frames = row.get("worst_frames", [])
            if worst_frames:
                html.append("<div class='thumb-grid'>")
                for item in worst_frames:
                    html.append("<div class='thumb-card'>")
                    if item.get("thumbnail"):
                        html.append(f"<img src='{item['thumbnail']}' alt='Worst frame thumbnail'>")
                    html.append(
                        f"<div class='thumb-meta'>"
                        f"Frame: {item['frame_num']}<br>"
                        f"Time: {item['timestamp_label']}<br>"
                        f"VMAF: {item['vmaf']:.3f}"
                        f"</div>"
                    )
                    html.append("</div>")
                html.append("</div>")

        html.append("</div>")

    # Profile Comparison Summary card
    comparison_rows = [r for r in rows if r.get("run_name") and r.get("profile")]
    if comparison_rows:
        html.append('<div class="card">')
        html.append("<h2>Profile Comparison Summary</h2>")
        for profile in sorted(set(r.get("profile", "") for r in comparison_rows)):
            html.append(f"<h3>{profile}</h3>")
            html.append("<table>")
            html.append(
                "<tr>"
                "<th>Run</th>"
                "<th>Test</th>"
                "<th>Codec</th>"
                "<th>Bitrate Mbps</th>"
                "<th>VMAF Mean</th>"
                "<th>Quality/Mbps</th>"
                "<th>Savings</th>"
                "<th>VMAF Δ</th>"
                "<th>Quality</th>"
                "</tr>"
            )
            profile_rows = [r for r in comparison_rows if r.get("profile") == profile]
            profile_rows.sort(key=lambda r: (r.get("test_type", ""), r.get("run_name", "")))
            for row in profile_rows:
                q_class = status_class(row["quality_status"])
                html.append(f"<tr class='{q_class}'>")
                html.append(f"<td>{row.get('run_name', '')}</td>")
                html.append(f"<td>{row.get('test_type', '')}</td>")
                html.append(f"<td>{row.get('codec', '')}</td>")
                html.append(f"<td>{row.get('bitrate_mbps', '')}</td>")
                html.append(f"<td>{fmt_score(row.get('vmaf_mean'))}</td>")
                html.append(f"<td>{format_optional_metric(row.get('quality_per_mbps'), 3)}</td>")
                html.append(f"<td>{format_optional_percent(row.get('bitrate_savings_percent'))}</td>")
                html.append(f"<td>{format_optional_metric(row.get('vmaf_delta'), 3)}</td>")
                html.append(f"<td><span class='badge {q_class}'>{row['quality_status']}</span></td>")
                html.append("</tr>")
            html.append("</table>")
        html.append("</div>")

    html.append('<div class="card">')
    html.append("<h2>Interpretation Notes</h2>")
    html.append("<ul>")
    html.append("<li>Native tests scale the source down to the encoded rendition resolution.</li>")
    html.append("<li>Upscaled tests scale the encoded rendition up to the target display resolution.</li>")
    html.append("<li>Mean VMAF gives the average quality score, but Min VMAF helps identify worst-frame quality drops.</li>")
    html.append("<li>PSNR Avg is a pixel-error metric reported in dB; higher is better, but it is less perceptual than VMAF.</li>")
    html.append("<li>SSIM All is a structural similarity metric from 0 to 1; higher is better.</li>")
    html.append("<li>Precheck WARN means duration or frame-rate mismatches were detected and should be reviewed.</li>")
    html.append("<li>Quality WARN/FAIL is based on mean VMAF, minimum VMAF, and large quality drops.</li>")
    html.append("<li>Use this report with visual inspection and playback testing.</li>")
    html.append("</ul>")
    html.append("</div>")

    html.append("</body></html>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))


def main():
    parser = argparse.ArgumentParser(
        description="Run VMAF against encoded files and generate CSV/Markdown reports."
    )

    parser.add_argument("--source", required=True, help="Reference source file")
    parser.add_argument("--encoded-dir", default=".", help="Directory containing encoded files")
    parser.add_argument("--runs-dir", help="Parent directory containing multiple encoded test-run folders")
    parser.add_argument("--baseline-run", help="Run name to use as comparison baseline when --runs-dir is used")
    parser.add_argument("--output", default="reports", help="Output report directory")
    parser.add_argument("--target-display", default="1920x1080", help="Target display resolution for upscaled tests")
    parser.add_argument("--native", action="store_true", help="Run native rendition tests")
    parser.add_argument("--upscaled", action="store_true", help="Run upscaled display tests")

    args = parser.parse_args()

    source = Path(args.source)
    encoded_dir = Path(args.encoded_dir)
    runs_dir = Path(args.runs_dir) if args.runs_dir else None
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        raise RuntimeError(f"Source file does not exist: {source}")

    try:
        target_width, target_height = map(int, args.target_display.lower().split("x"))
    except (ValueError, AttributeError):
        raise RuntimeError(
            f"Invalid --target-display value '{args.target_display}'. "
            "Expected format: WIDTHxHEIGHT, e.g. 1920x1080"
        )

    # If neither mode is specified, run both.
    run_native = args.native or not args.upscaled
    run_upscaled = args.upscaled or not args.native

    source_info = ffprobe_video(source)

    if source_info is None:
        raise RuntimeError(f"Source file has no video stream: {source}")

    if runs_dir:
        if not runs_dir.exists():
            raise RuntimeError(f"Runs directory does not exist: {runs_dir}")

        run_dirs = sorted(p for p in runs_dir.iterdir() if p.is_dir())
        if not run_dirs:
            raise RuntimeError(f"No run subdirectories found in runs directory: {runs_dir}")
    else:
        run_dirs = [encoded_dir]

    rows = []

    for run_dir in run_dirs:
        run_name = run_dir.name if runs_dir else "single_run"
        encoded_files = [p for p in get_encoded_files(run_dir) if p.resolve() != source.resolve()]

        if not encoded_files:
            print(f"Skipping run {run_name}: no .mp4 files found")
            continue

        for encoded in encoded_files:
            profile = extract_profile_name(encoded)
            print(f"\nProcessing {run_name}/{encoded.name}")
            artifact_stem = safe_stem(f"{run_name}_{encoded.stem}")

            encoded_info = ffprobe_video(encoded)

            if encoded_info is None:
                print(f"  Skipping {encoded.name}: no video stream found")
                continue

            resolution = f"{encoded_info['width']}x{encoded_info['height']}"

            precheck_status, precheck_warnings = build_precheck(source_info, encoded_info)

            if precheck_status == "WARN":
                print(f"  Precheck warning for {encoded.name}: {precheck_warnings}")

            if run_native:
                native_json = output_dir / f"{artifact_stem}_vmaf_native.json"
                run_vmaf_native(encoded, source, encoded_info, native_json)
                metrics = parse_vmaf_json(native_json)
                chart_path, worst_frames = build_visual_artifacts(
                    encoded,
                    metrics,
                    encoded_info,
                    "native",
                    output_dir,
                    artifact_stem=artifact_stem,
                )
                worst_frame = worst_frames[0] if worst_frames else None

                psnr_log = output_dir / f"{artifact_stem}_psnr_native.log"
                ssim_log = output_dir / f"{artifact_stem}_ssim_native.log"
                psnr_avg = run_psnr_native(encoded, source, encoded_info, psnr_log)
                ssim_all = run_ssim_native(encoded, source, encoded_info, ssim_log)

                row = {
                    "run_name": run_name,
                    "profile": profile,
                    "file": encoded.name,
                    "codec": encoded_info["codec"],
                    "resolution": resolution,
                    "frame_rate": encoded_info["frame_rate"],
                    "bitrate_mbps": bitrate_mbps(encoded_info["bit_rate"]),
                    "duration": round(encoded_info["duration"], 3),
                    "test_type": "native",
                    "scale_method": "source_downscale",
                    "precheck_status": precheck_status,
                    "precheck_warnings": precheck_warnings,
                    "worst_frame": worst_frame["frame_num"] if worst_frame else "",
                    "worst_timestamp": worst_frame["timestamp_label"] if worst_frame else "",
                    "chart": chart_path,
                    "worst_frames": worst_frames,
                    "psnr_avg": psnr_avg,
                    "ssim_all": ssim_all,
                    "quality_per_mbps": quality_per_mbps(metrics.get("vmaf_mean"), bitrate_mbps(encoded_info["bit_rate"])),
                    "baseline_bitrate_mbps": "",
                    "bitrate_savings_percent": "",
                    "vmaf_delta": "",
                    "psnr_delta": "",
                    "ssim_delta": "",
                    **metrics,
                }

                row["quality_status"] = classify_quality(row["vmaf_mean"], row["vmaf_min"])
                row["notes"] = classify_notes(row["vmaf_mean"], row["vmaf_min"], "native")
                rows.append(row)

            if run_upscaled:
                upscaled_json = output_dir / f"{artifact_stem}_vmaf_upscaled_{target_width}x{target_height}.json"
                run_vmaf_upscaled(encoded, source, target_width, target_height, upscaled_json)
                metrics = parse_vmaf_json(upscaled_json)
                upscaled_test_label = f"upscaled_{target_width}x{target_height}"
                chart_path, worst_frames = build_visual_artifacts(
                    encoded,
                    metrics,
                    encoded_info,
                    upscaled_test_label,
                    output_dir,
                    artifact_stem=artifact_stem,
                )
                worst_frame = worst_frames[0] if worst_frames else None

                psnr_log = output_dir / f"{artifact_stem}_psnr_{upscaled_test_label}.log"
                ssim_log = output_dir / f"{artifact_stem}_ssim_{upscaled_test_label}.log"
                psnr_avg = run_psnr_upscaled(encoded, source, target_width, target_height, psnr_log)
                ssim_all = run_ssim_upscaled(encoded, source, target_width, target_height, ssim_log)

                row = {
                    "run_name": run_name,
                    "profile": profile,
                    "file": encoded.name,
                    "codec": encoded_info["codec"],
                    "resolution": resolution,
                    "frame_rate": encoded_info["frame_rate"],
                    "bitrate_mbps": bitrate_mbps(encoded_info["bit_rate"]),
                    "duration": round(encoded_info["duration"], 3),
                    "test_type": upscaled_test_label,
                    "scale_method": "encode_upscale",
                    "precheck_status": precheck_status,
                    "precheck_warnings": precheck_warnings,
                    "worst_frame": worst_frame["frame_num"] if worst_frame else "",
                    "worst_timestamp": worst_frame["timestamp_label"] if worst_frame else "",
                    "chart": chart_path,
                    "worst_frames": worst_frames,
                    "psnr_avg": psnr_avg,
                    "ssim_all": ssim_all,
                    "quality_per_mbps": quality_per_mbps(metrics.get("vmaf_mean"), bitrate_mbps(encoded_info["bit_rate"])),
                    "baseline_bitrate_mbps": "",
                    "bitrate_savings_percent": "",
                    "vmaf_delta": "",
                    "psnr_delta": "",
                    "ssim_delta": "",
                    **metrics,
                }

                row["quality_status"] = classify_quality(row["vmaf_mean"], row["vmaf_min"])
                row["notes"] = classify_notes(row["vmaf_mean"], row["vmaf_min"], "upscaled")
                rows.append(row)

    rows = apply_run_comparisons(rows, args.baseline_run)

    csv_path = output_dir / "vmaf_summary.csv"
    md_path = output_dir / "vmaf_report.md"
    html_path = output_dir / "vmaf_report.html"

    write_csv(rows, csv_path)
    write_markdown(rows, md_path)
    write_html(rows, html_path, source, source_info)

    print(f"\nDone.")
    print(f"CSV report: {csv_path}")
    print(f"Markdown report: {md_path}")
    print(f"HTML report: {html_path}")


if __name__ == "__main__":
    main()