# Viral Video Breakdown

`viral-video-breakdown` is a Codex skill for reverse-engineering viral short-form videos.

Give it an Instagram Reel, TikTok, YouTube Short, X video, or local MP4, and it helps turn the video into a structured creative breakdown:

- why the video likely worked
- what happens in the first 3 seconds
- how the timeline creates retention
- what emotional triggers are being used
- why viewers would like, save, share, comment, or rewatch
- how to extract a reusable formula for another niche

It is designed for creators, marketers, editors, growth teams, and AI agents that need to study viral videos instead of just describing them.

## What This Skill Does

The skill separates a viral video into three layers:

1. **Media extraction**
   - Download public URL media with `yt-dlp`
   - Copy local MP4/MOV/WebM files into a working folder
   - Extract fixed-interval keyframes
   - Extract audio
   - Optionally transcribe the audio

2. **Creative diagnosis**
   - Analyze the first frame and opening line
   - Segment the video into timestamped beats
   - Identify hook, tension, open loops, pacing, payoff, and CTA
   - Explain the likely viewer psychology behind each beat

3. **Reusable formula extraction**
   - Convert the specific video into a repeatable structure
   - Generate remix ideas for the user's niche
   - Separate like/save/share mechanics from comment mechanics

## Example Use Cases

Ask Codex:

```text
Use viral-video-breakdown to analyze this Instagram Reel:
https://www.instagram.com/reel/xxxxx/
```

```text
Break down this TikTok and tell me why it got 2M views but very few comments.
```

```text
Analyze this MP4 and extract a reusable hook formula for my fitness account.
```

```text
Why did this video work for a 2,000-follower creator, and how can I remix the structure?
```

## Repository Structure

```text
viral-video-breakdown-repo/
├── README.md
├── requirements.txt
├── .gitignore
└── viral-video-breakdown/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    │   └── breakdown-framework.md
    └── scripts/
        └── extract_video_beats.py
```

The actual Codex skill lives in `viral-video-breakdown/`.

## Install As A Codex Skill

If this repository is available on GitHub, install the skill with the Codex skill installer:

```bash
python "C:/Users/admin/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo <owner>/viral-video-breakdown \
  --path viral-video-breakdown \
  --name viral-video-breakdown
```

Replace `<owner>/viral-video-breakdown` with your GitHub repository name.

You can also copy the `viral-video-breakdown/` folder directly into your local Codex skills directory.

## Install Dependencies

The extraction script works best with:

```bash
pip install -r requirements.txt
```

Optional external tools:

- `yt-dlp`: downloads public videos and metadata
- `ffmpeg`: extracts frames/audio
- `openai-whisper`: transcribes audio
- `faster-whisper`: fallback transcription backend

On Windows, the script can discover:

- user-level `whisper.exe`
- `imageio-ffmpeg`'s bundled ffmpeg binary

This means a full system-level ffmpeg install is helpful but not strictly required if `imageio-ffmpeg` is installed.

## Run The Extractor

For a local MP4:

```bash
python viral-video-breakdown/scripts/extract_video_beats.py "path/to/video.mp4" --out work/video-beats --frame-interval 1
```

For a public short-video URL:

```bash
python viral-video-breakdown/scripts/extract_video_beats.py "https://www.tiktok.com/@user/video/xxxxx" --out work/video-beats --frame-interval 1
```

Skip transcription:

```bash
python viral-video-breakdown/scripts/extract_video_beats.py "path/to/video.mp4" --out work/video-beats --no-transcribe
```

Use a different Whisper model:

```bash
python viral-video-breakdown/scripts/extract_video_beats.py "path/to/video.mp4" --out work/video-beats --whisper-model small
```

## Extractor Outputs

The extractor writes:

```text
work/video-beats/
├── manifest.json
├── beats.md
├── source.mp4
├── audio.wav
├── transcript.txt
└── frames/
    ├── frame_0001.jpg
    ├── frame_0002.jpg
    └── ...
```

Key files:

- `manifest.json`: source, paths, tool availability, metadata, errors
- `beats.md`: human-readable packet for analysis
- `frames/`: fixed-interval keyframes for visual review
- `audio.wav`: extracted speech/audio
- `transcript.txt`: optional transcript

## Public URL Handling

For TikTok/Instagram-style public URLs, the script passes browser-like settings to `yt-dlp`:

- `User-Agent`
- `Referer`
- `--geo-bypass`
- retry count

Useful options:

```bash
--user-agent "<UA string>"
--referer "https://www.tiktok.com/"
--no-geo-bypass
--retries 3
```

Some platforms may still block downloads, require login, or restrict regions. In those cases, use an uploaded MP4 instead.

## Breakdown Framework

The skill uses this core equation:

```text
Viral potential = topic demand
  x first-3-second stop power
  x retention structure
  x emotional intensity
  x propagation reason
  x remixability
```

The default analysis output includes:

```text
Verdict
Timeline Breakdown
First 3 Seconds
Retention Logic
Emotional Triggers
Engagement Drivers
Reusable Formula
Remix Ideas
```

The most important final artifact is the reusable mechanism:

```text
This video works because it uses [hook] to stop [viewer],
creates [curiosity/tension],
sustains attention through [retention mechanism],
and triggers [engagement behavior].
```

## Example Analysis Pattern

For a home gym build video:

```text
Specific:
"Creator installs a large leg press/hack squat machine in a home gym."

Formula:
"Dream build series -> unbelievable upgrade hook -> complex solo challenge
-> product/space constraint explanation -> near-complete payoff
-> follow for the next bigger build."
```

This makes the video easier to remix for another niche:

```text
"You won't believe what I'm adding to my [space/project]."
"It's day [N], and today we finally move on to the big piece."
"Everyone says this needs two people, but I'm trying it alone."
"I chose this because [real constraint]."
"Follow along to see if it was worth it."
```

## Known Limitations

- Public URL downloads depend on platform availability and `yt-dlp` support.
- Instagram/TikTok links may fail behind login walls or regional restrictions.
- Whisper model downloads require network access the first time.
- The script does not log in to private accounts and does not ask for credentials.
- Performance metrics such as saves, shares, retention, and follower baseline must be provided by the user if they are not visible publicly.

## Notes

This project is a skill and analysis workflow, not a guarantee of virality.

The goal is to help creators identify transferable patterns: hooks, visual resets, open loops, emotional triggers, and propagation reasons.
