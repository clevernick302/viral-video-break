#!/usr/bin/env python3
"""
Extract a short-form video's analysis packet: metadata, frames, audio, and optional transcript.

Dependencies are optional and discovered at runtime:
- yt-dlp for public URL download and metadata
- ffmpeg / ffprobe for frames, audio, duration
- whisper CLI for transcription
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
DEFAULT_REFERER = "https://www.tiktok.com/"
DEFAULT_RETRIES = 3


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def tool_path(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found

    scripts_dir = Path(sys.executable).with_name("Scripts")
    suffix = ".exe" if os.name == "nt" else ""
    candidate = scripts_dir / f"{name}{suffix}"
    if candidate.exists():
        return str(candidate)

    if name == "ffmpeg":
        try:
            import imageio_ffmpeg  # type: ignore

            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            return None

    return None


def safe_name(value: str, fallback: str = "video") -> str:
    keep = []
    for ch in value:
        if ch.isalnum() or ch in ("-", "_", "."):
            keep.append(ch)
        elif ch.isspace():
            keep.append("-")
    name = "".join(keep).strip("-._")
    return name[:80] or fallback


def is_local_video(source: str) -> bool:
    path = Path(source)
    return path.exists() and path.suffix.lower() in VIDEO_EXTENSIONS


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def ytdlp_base_args(user_agent: str, referer: str, geo_bypass: bool) -> list[str]:
    args = [
        "--no-check-certificates",
        "--user-agent",
        user_agent,
        "--referer",
        referer,
    ]
    if geo_bypass:
        args.append("--geo-bypass")
    return args


def get_metadata(source: str, out_dir: Path, yt_dlp: str | None, user_agent: str, referer: str, geo_bypass: bool) -> dict[str, Any]:
    metadata: dict[str, Any] = {"source": source}
    if not yt_dlp or is_local_video(source):
        return metadata

    proc = run([yt_dlp, *ytdlp_base_args(user_agent, referer, geo_bypass), "--dump-json", "--no-warnings", source])
    if proc.returncode != 0:
        metadata["metadata_error"] = proc.stderr.strip() or proc.stdout.strip()
        return metadata

    try:
        raw = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        metadata["metadata_error"] = f"Could not parse yt-dlp JSON: {exc}"
        return metadata

    wanted = [
        "id",
        "title",
        "description",
        "uploader",
        "uploader_id",
        "channel",
        "channel_id",
        "webpage_url",
        "duration",
        "view_count",
        "like_count",
        "comment_count",
        "repost_count",
        "timestamp",
        "upload_date",
        "tags",
        "categories",
    ]
    for key in wanted:
        if key in raw and raw[key] is not None:
            metadata[key] = raw[key]

    info_path = out_dir / "yt_dlp_metadata.json"
    write_json(info_path, raw)
    metadata["raw_metadata_path"] = str(info_path)
    return metadata


def download_video(
    source: str,
    out_dir: Path,
    yt_dlp: str | None,
    user_agent: str,
    referer: str,
    geo_bypass: bool,
    retries: int,
) -> tuple[Path | None, str | None]:
    if is_local_video(source):
        source_path = Path(source).resolve()
        target = out_dir / f"source{source_path.suffix.lower()}"
        if source_path != target:
            shutil.copy2(source_path, target)
        return target, None

    if not yt_dlp:
        return None, "yt-dlp is not installed, so URL media cannot be downloaded."

    output_tpl = str(out_dir / "source.%(ext)s")
    cmd = [yt_dlp, *ytdlp_base_args(user_agent, referer, geo_bypass), "--no-playlist", "--merge-output-format", "mp4", "-f", "bv*+ba/best", "-o", output_tpl, source]
    last_error: str | None = None
    for attempt in range(1, retries + 1):
        proc = run(cmd)
        if proc.returncode == 0:
            break
        last_error = proc.stderr.strip() or proc.stdout.strip()
    else:
        return None, last_error or "yt-dlp failed."

    candidates = sorted(out_dir.glob("source.*"))
    for candidate in candidates:
        if candidate.suffix.lower() in VIDEO_EXTENSIONS:
            return candidate, None
    return None, "yt-dlp finished but no video file was found."


def probe_duration(video: Path, ffprobe: str | None) -> float | None:
    if not ffprobe:
        return None
    proc = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ]
    )
    if proc.returncode != 0:
        return None
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return None


def extract_frames(video: Path, frames_dir: Path, interval: float, ffmpeg: str | None) -> tuple[list[Path], str | None]:
    if not ffmpeg:
        return [], "ffmpeg is not installed."
    frames_dir.mkdir(parents=True, exist_ok=True)
    fps = 1.0 / interval
    output_pattern = str(frames_dir / "frame_%04d.jpg")
    proc = run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(video),
            "-vf",
            f"fps={fps}",
            "-q:v",
            "2",
            output_pattern,
        ]
    )
    if proc.returncode != 0:
        return [], proc.stderr.strip()
    return sorted(frames_dir.glob("frame_*.jpg")), None


def extract_audio(video: Path, audio_path: Path, ffmpeg: str | None) -> str | None:
    if not ffmpeg:
        return "ffmpeg is not installed."
    proc = run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(audio_path),
        ]
    )
    if proc.returncode != 0:
        return proc.stderr.strip()
    return None


def transcribe_audio(audio_path: Path, out_dir: Path, model: str, whisper: str | None) -> tuple[Path | None, str | None]:
    if not audio_path.exists():
        return None, "audio.wav was not created."

    cli_error: str | None = None
    if whisper:
        transcript_dir = out_dir / "transcript"
        transcript_dir.mkdir(parents=True, exist_ok=True)
        proc = run(
            [
                whisper,
                str(audio_path),
                "--model",
                model,
                "--output_dir",
                str(transcript_dir),
                "--output_format",
                "txt",
            ]
        )
        if proc.returncode == 0:
            txt_files = sorted(transcript_dir.glob("*.txt"))
            if txt_files:
                final_path = out_dir / "transcript.txt"
                final_path.write_text(txt_files[0].read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
                return final_path, None
            cli_error = "whisper finished but no transcript txt was found."
        else:
            cli_error = proc.stderr.strip() or proc.stdout.strip()
    else:
        cli_error = "whisper CLI is not installed."

    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as exc:
        return None, f"{cli_error}; faster-whisper fallback is unavailable: {exc}"

    try:
        fw_model = WhisperModel(model, device="cpu", compute_type="int8")
        segments, info = fw_model.transcribe(str(audio_path), vad_filter=True)
        lines = [f"# faster-whisper transcript ({info.language}, p={info.language_probability:.2f})", ""]
        for segment in segments:
            text = segment.text.strip()
            if text:
                lines.append(f"[{segment.start:07.2f} - {segment.end:07.2f}] {text}")
        final_path = out_dir / "transcript.txt"
        final_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return final_path, f"OpenAI whisper CLI failed; used faster-whisper fallback. Original error: {cli_error}"
    except Exception as exc:
        return None, f"{cli_error}; faster-whisper fallback failed: {exc}"


def build_beats_md(
    path: Path,
    source: str,
    video: Path | None,
    metadata: dict[str, Any],
    duration: float | None,
    frames: list[Path],
    frame_interval: float,
    transcript_path: Path | None,
    errors: list[str],
) -> None:
    lines: list[str] = []
    lines.append("# Video Beats Packet")
    lines.append("")
    lines.append(f"- Source: {source}")
    if video:
        lines.append(f"- Local video: {video}")
    if duration is not None:
        lines.append(f"- Duration: {duration:.2f}s")
    if metadata.get("title"):
        lines.append(f"- Title: {metadata['title']}")
    if metadata.get("uploader") or metadata.get("channel"):
        lines.append(f"- Creator: {metadata.get('uploader') or metadata.get('channel')}")
    for key in ("view_count", "like_count", "comment_count", "repost_count"):
        if key in metadata:
            lines.append(f"- {key}: {metadata[key]}")
    lines.append(f"- Frames extracted: {len(frames)} every {frame_interval:g}s")
    if transcript_path:
        lines.append(f"- Transcript: {transcript_path}")
    if errors:
        lines.append("")
        lines.append("## Extraction Notes")
        for error in errors:
            lines.append(f"- {error}")

    if metadata.get("description"):
        lines.append("")
        lines.append("## Caption / Description")
        lines.append(str(metadata["description"]).strip())

    lines.append("")
    lines.append("## Frame Index")
    if frames:
        for idx, frame in enumerate(frames):
            start = idx * frame_interval
            lines.append(f"- {start:06.2f}s: {frame}")
    else:
        lines.append("- No frames extracted.")

    lines.append("")
    lines.append("## Transcript")
    if transcript_path and transcript_path.exists():
        text = transcript_path.read_text(encoding="utf-8", errors="replace").strip()
        lines.append(text or "(empty transcript)")
    else:
        lines.append("(no transcript)")

    lines.append("")
    lines.append("## Analysis Prompts")
    lines.append("- What does the first frame make the viewer notice?")
    lines.append("- What unresolved question is created in the first 3 seconds?")
    lines.append("- Where are the visual resets, proof moments, turns, and payoff?")
    lines.append("- Why would someone comment, save, share, or rewatch?")
    lines.append("- What is the transferable formula for another niche?")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract metadata, frames, audio, and optional transcript for viral video analysis.")
    parser.add_argument("source", help="Public URL or local video file path.")
    parser.add_argument("--out", default="video-beats", help="Output directory.")
    parser.add_argument("--frame-interval", type=float, default=2.0, help="Seconds between extracted frames.")
    parser.add_argument("--whisper-model", default="base", help="Whisper CLI model name.")
    parser.add_argument("--no-transcribe", action="store_true", help="Skip local Whisper transcription.")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="User-Agent passed to yt-dlp for public URLs.")
    parser.add_argument("--referer", default=DEFAULT_REFERER, help="Referer passed to yt-dlp for public URLs.")
    parser.add_argument("--no-geo-bypass", action="store_true", help="Disable yt-dlp --geo-bypass.")
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES, help="yt-dlp download retry count.")
    args = parser.parse_args()

    if args.frame_interval <= 0:
        print("--frame-interval must be greater than 0", file=sys.stderr)
        return 2

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    yt_dlp = tool_path("yt-dlp")
    ffmpeg = tool_path("ffmpeg")
    ffprobe = tool_path("ffprobe")
    whisper = tool_path("whisper")

    errors: list[str] = []
    metadata = get_metadata(args.source, out_dir, yt_dlp, args.user_agent, args.referer, not args.no_geo_bypass)
    video, download_error = download_video(args.source, out_dir, yt_dlp, args.user_agent, args.referer, not args.no_geo_bypass, max(1, args.retries))
    if download_error:
        errors.append(download_error)

    duration = probe_duration(video, ffprobe) if video else None

    frames: list[Path] = []
    if video:
        frames, frame_error = extract_frames(video, out_dir / "frames", args.frame_interval, ffmpeg)
        if frame_error:
            errors.append(frame_error)

    audio_path = out_dir / "audio.wav"
    if video:
        audio_error = extract_audio(video, audio_path, ffmpeg)
        if audio_error:
            errors.append(audio_error)

    transcript_path: Path | None = None
    if not args.no_transcribe:
        transcript_path, transcript_error = transcribe_audio(audio_path, out_dir, args.whisper_model, whisper)
        if transcript_error:
            errors.append(transcript_error)

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": args.source,
        "output_dir": str(out_dir),
        "tools": {
            "yt_dlp": yt_dlp,
            "ffmpeg": ffmpeg,
            "ffprobe": ffprobe,
            "whisper": whisper,
        },
        "video_path": str(video) if video else None,
        "duration_seconds": duration,
        "frame_interval_seconds": args.frame_interval,
        "frames": [str(frame) for frame in frames],
        "audio_path": str(audio_path) if audio_path.exists() else None,
        "transcript_path": str(transcript_path) if transcript_path else None,
        "metadata": metadata,
        "errors": errors,
    }
    write_json(out_dir / "manifest.json", manifest)
    build_beats_md(
        out_dir / "beats.md",
        args.source,
        video,
        metadata,
        duration,
        frames,
        args.frame_interval,
        transcript_path,
        errors,
    )

    print(f"Wrote {out_dir / 'manifest.json'}")
    print(f"Wrote {out_dir / 'beats.md'}")
    if errors:
        print("Completed with notes:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    return 0 if video else 1


if __name__ == "__main__":
    raise SystemExit(main())
