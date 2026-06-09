---
name: viral-video-breakdown
description: Analyze viral short-form videos from Instagram Reels, TikTok, YouTube Shorts, X, or uploaded MP4 files. Use when the user provides a viral video link/file and asks to reverse-engineer hooks, first 3 seconds, retention, pacing, editing, emotional triggers, engagement drivers, comments, or reusable remix formulas.
---

# Viral Video Breakdown

Reverse-engineer short-form videos into a timestamped creative diagnosis and a reusable formula for the user's niche.

## Quick Start

When the user provides a video URL or local MP4, first decide whether raw media is available.

- If a public URL or local file is available and media extraction is useful, run `scripts/extract_video_beats.py`.
- If extraction fails because the platform blocks access, ask for an uploaded MP4, screenshots, transcript, or visible metrics.
- If the user only wants conceptual advice, skip extraction and use the framework directly.

Use public data only. Do not ask for Instagram credentials. State uncertainty when follower count, saves, shares, retention, or account baseline are unavailable.

## Extraction

Run:

```bash
python scripts/extract_video_beats.py "<URL_OR_FILE>" --out work/video-beats
```

Useful options:

```bash
python scripts/extract_video_beats.py "<URL_OR_FILE>" --out work/video-beats --frame-interval 2 --no-transcribe
python scripts/extract_video_beats.py "<URL_OR_FILE>" --out work/video-beats --whisper-model small
```

The script produces:

- `manifest.json`: source, metadata, duration, tool availability, output paths
- `beats.md`: human-readable analysis packet
- `frames/`: extracted keyframes at a fixed interval
- `audio.wav`: extracted audio when `ffmpeg` is available
- `transcript.txt`: optional transcript when a local Whisper CLI is available

After extraction, inspect `beats.md`, sample frames, metadata, and transcript before writing the analysis.

## Analysis Workflow

1. Establish viral context.
   - Compare views to follower count or account baseline when available.
   - Treat comments, saves, shares, rewatches, and retention as stronger signals than likes.
   - If only public counts are visible, describe the analysis as a creative breakdown rather than a proven performance audit.

2. Build the timeline.
   - Segment into `0-3s`, `3-10s`, middle beats, and ending.
   - For each beat, identify visual action, spoken words, on-screen text, edit move, and viewer psychology.
   - Prefer 1-3 second granularity for videos under 60 seconds.

3. Diagnose the hook.
   - Evaluate first frame, first sentence, motion, text, promise, threat, contrast, and curiosity gap.
   - Answer: why would a scrolling viewer stop?

4. Diagnose retention.
   - Identify open loops, delayed payoff, escalating proof, pattern interrupts, visual resets, emotional turns, and pacing changes.
   - Answer: why would a viewer continue past 3 seconds and finish?

5. Diagnose propagation.
   - Explain why viewers would like, comment, save, share, or rewatch.
   - Separate practical value from identity value, debate value, and entertainment value.

6. Extract the formula.
   - Convert the specific video into a transferable structure.
   - Adapt the structure to the user's niche when known.

For detailed scoring rubrics and hook/retention taxonomies, read `references/breakdown-framework.md`.

## Output Format

Use this structure unless the user asks for another format:

```markdown
## Verdict
Why this video likely performed well, with uncertainty noted.

## Timeline Breakdown
| Time | Visual | Audio/Text | Editing | Viewer Psychology |

## First 3 Seconds
First frame, first line, pattern interrupt, relevance, curiosity gap.

## Retention Logic
How the middle keeps attention and where the payoff lands.

## Emotional Triggers
Curiosity, anxiety, aspiration, conflict, humor, identity, relief, or other drivers.

## Engagement Drivers
Why viewers would comment, save, share, like, or rewatch.

## Reusable Formula
One-line mechanism plus step-by-step structure.

## Remix Ideas
Niche-specific hooks, outlines, or scripts.
```

End with the compact formula:

```text
This video works because it uses [X] to stop [target viewer], creates [Y] curiosity/tension, sustains attention through [Z], and triggers [W] engagement.
```
