# Viral Video Breakdown

Codex skill for reverse-engineering viral short-form videos from Instagram Reels, TikTok, YouTube Shorts, X, or local MP4 files.

The skill turns a video into:

- metadata
- fixed-interval keyframes
- extracted audio
- optional transcript
- a timestamped creative breakdown
- reusable hook, retention, and remix formulas

## Install

Install the skill from this repository path:

```bash
python "C:/Users/admin/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" --repo clevernick302/viral-video-breakdown --path viral-video-breakdown --name viral-video-breakdown
```

## Run The Extractor

```bash
python viral-video-breakdown/scripts/extract_video_beats.py "<URL_OR_MP4>" --out work/video-beats --frame-interval 1
```

For public TikTok or Instagram-style URLs, the script passes browser-like `User-Agent`, `Referer`, and `--geo-bypass` settings to `yt-dlp`.

Skip transcription:

```bash
python viral-video-breakdown/scripts/extract_video_beats.py "<URL_OR_MP4>" --out work/video-beats --no-transcribe
```

## Optional Dependencies

```bash
pip install -r requirements.txt
```

External tools:

- `yt-dlp` for public URL downloads
- `ffmpeg` for frames and audio extraction
- `openai-whisper` or `faster-whisper` for transcription

The extractor can also discover `imageio-ffmpeg` and user-level `whisper.exe` installations on Windows.
