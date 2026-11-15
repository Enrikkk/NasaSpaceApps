#!/usr/bin/env bash
# Renders index.html to hook.mp4: 9.6 s, 1920x1080, 30 fps, no audio.
# Needs: chromium (or set CHROME=/path/to/chrome), node >= 22 (built-in fetch + WebSocket), ffmpeg/ffprobe.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf frames && mkdir -p frames
node render_frames.mjs frames 30 9.6            # one PNG per frame: frames/f0000.png ... f0287.png
ffmpeg -y -loglevel error -framerate 30 -i frames/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 hook.mp4
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames -of default=nw=1 hook.mp4
