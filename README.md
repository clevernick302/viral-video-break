# Viral Video Breakdown

`viral-video-breakdown` is a Codex skill for reverse-engineering viral short-form videos.

The core of this skill is not "download a video." The core is turning a request like:

```text
Break down this viral video:
https://www.instagram.com/reel/xxxxx/
```

into a repeatable analysis workflow that explains why the video worked and how the structure can be reused.

It supports Instagram Reels, TikTok, YouTube Shorts, X videos, or uploaded local MP4/MOV/WebM files.

## Who This Is For

This skill is designed for:

- creators studying viral videos
- editors analyzing pacing and hooks
- marketers reverse-engineering short-form ads
- growth teams building repeatable content formats
- AI agents that need a stable viral-video analysis workflow

## Input

The user can provide:

```text
Break down this viral video: https://www.instagram.com/reel/xxxxx/
```

Optional context improves the output:

```text
My niche: AI tools / fitness / beauty / local services
My goal: remix topics / study editing / rewrite the script / generate similar videos
```

If a public link cannot be accessed, the user can provide:

- an uploaded MP4
- screenshots
- caption text
- visible metrics
- transcript
- comments

For Instagram, prefer public information or uploaded media. Do not require credentials.

## Fixed Output Contract

Every full breakdown should produce six things:

1. **Viral verdict**: why the video qualifies as viral or outlier content.
2. **Timeline breakdown**: what happens every 1-3 seconds.
3. **Hook analysis**: how the first 3 seconds stop the scroll.
4. **Retention mechanism**: why viewers continue through the middle.
5. **Emotional and propagation logic**: why viewers like, comment, save, share, or rewatch.
6. **Reusable formula**: how to adapt the structure to the user's niche.

The underlying creative equation is:

```text
Viral video = topic momentum
  x first-3-second stop power
  x middle retention
  x emotional intensity
  x propagation reason
  x reusable structure
```

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

## Skill Workflow

### Step 1. Get The Source Material

- If the user provides a public video link, try to inspect public metadata such as title, caption, comments, views, likes, and creator context.
- If the link cannot be accessed, ask for an uploaded MP4, screenshots, visible metrics, transcript, or caption.
- For Instagram, prefer public information and uploaded media.

### Step 2. Convert Video To Text

- Extract spoken-word transcription.
- Extract visible subtitles or on-screen text when available.
- Organize speech and text into a timestamped script.

### Step 3. Extract Keyframes

- Capture one frame every 1-3 seconds.
- Mark the visual subject, action, camera movement, subtitle, scene change, and transition.
- Use the frames to avoid analyzing only the transcript.

### Step 4. Analyze The Timeline

- `0-3s`: hook, first frame, first sentence, pattern interrupt.
- `3-10s`: promise, conflict, problem setup, relevance confirmation.
- `middle`: information progression, proof, surprise, escalation, or transformation.
- `ending`: CTA, payoff, suspense, loop, rewatch trigger, or follow-up hook.

### Step 5. Analyze Viewer Psychology

Identify which psychological drivers are doing the work:

- curiosity
- anxiety
- payoff anticipation
- identity recognition
- practical value
- conflict
- aspiration
- humor
- relief
- social currency

Then answer:

- Why would viewers continue watching?
- Why would viewers interact?
- Why would viewers save or share?
- Why might viewers watch but not comment?

### Step 6. Extract The Remix Template

- Abstract the specific video into a structural formula.
- Generate 3-10 topic adaptations for the user's niche.
- Provide hook rewrites or opening script options when useful.

The final target sentence is:

```text
This video works because it uses [X] to stop [target viewer],
creates [Y] unfinished tension in the first 3 seconds,
sustains attention through [Z],
and ends with [W] to trigger save/share/comment/follow behavior.
```

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
|-- README.md
|-- requirements.txt
|-- .gitignore
`-- viral-video-breakdown/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- references/
    |   `-- breakdown-framework.md
    `-- scripts/
        `-- extract_video_beats.py
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
|-- manifest.json
|-- beats.md
|-- source.mp4
|-- audio.wav
|-- transcript.txt
`-- frames/
    |-- frame_0001.jpg
    |-- frame_0002.jpg
    `-- ...
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

## Hook, Retention, And Propagation Taxonomy

Common hook types:

- contrarian insight
- result first
- mistake warning
- secret reveal
- identity callout
- strong conflict
- before/after contrast
- challenge or experiment
- failure breakdown
- money, beauty, fitness, speed, or status gain

Common retention mechanisms:

- open loop
- step-by-step progression
- escalating proof
- delayed payoff
- pattern interrupt
- visual reset
- curiosity stacking
- emotional reversal

Common propagation mechanisms:

- saveable utility
- debate trigger
- share-with-a-friend relevance
- identity expression
- social currency
- strong resonance

## Minimum Viable Version

The first usable version of this skill does not need perfect automation.

It can work as:

```text
User provides link, screenshot, transcript, or MP4
-> Codex extracts visible information
-> Codex applies the breakdown framework
-> Codex outputs hook, timeline, retention, emotion, propagation, and remix formula
```

Automation improves speed and consistency, but the value of the skill is the analysis frame.

Use `scripts/extract_video_beats.py` when raw media extraction is useful:

1. Download public media with `yt-dlp`.
2. Extract frames with `ffmpeg`.
3. Extract audio and transcribe with Whisper.
4. Output `frames + transcript + metadata` for analysis.

Always keep a fallback path:

```text
If the link cannot be accessed:
1. Ask for an uploaded MP4.
2. Or ask for screenshots + caption + visible metrics.
3. Or do a lightweight breakdown from public page information only.
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
